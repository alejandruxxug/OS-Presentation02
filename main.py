"""
Amazon DocumentDB Demo API
==========================
A RESTful FastAPI service that runs on AWS Lambda and connects to Amazon
DocumentDB to demonstrate every major MongoDB operation through HTTP verbs.

Stack:
    - FastAPI         : web framework
    - Mangum          : ASGI -> AWS Lambda adapter
    - PyMongo         : official MongoDB driver (works with DocumentDB)
    - Pydantic        : request/response validation

Endpoint map (HTTP method -> DocumentDB operation):
    POST   /products                     -> insert_one
    GET    /products                     -> find (all)
    GET    /products/{id}                -> find_one by _id
    GET    /products/search              -> find with filters ($gte, $lte, $regex)
    PATCH  /products/{id}                -> update_one with $set
    PUT    /products/{id}                -> replace_one
    DELETE /products/{id}                -> delete_one
    GET    /products/stats/by-category   -> aggregation pipeline ($group)
"""

import os
import logging
from datetime import datetime, timezone
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Path, status
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import PyMongoError, DuplicateKeyError
from mangum import Mangum

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration (read from environment variables set in the Lambda)
# ---------------------------------------------------------------------------
DOCDB_URI = os.environ.get("DOCDB_URI")  # mongodb://user:pass@host:27017/?...
DOCDB_DB_NAME = os.environ.get("DOCDB_DB_NAME", "demo")
DOCDB_COLLECTION = os.environ.get("DOCDB_COLLECTION", "products")
# DocumentDB requires TLS; AWS publishes a CA bundle that Lambda layers usually
# ship at /opt/global-bundle.pem or similar. Adjust path as needed.
TLS_CA_FILE = os.environ.get("TLS_CA_FILE", "/opt/global-bundle.pem")

# ---------------------------------------------------------------------------
# Mongo client (created once per Lambda container — re-used across invocations)
# ---------------------------------------------------------------------------
_client: Optional[MongoClient] = None


def get_collection():
    """Return the products collection, lazily creating the Mongo client."""
    global _client
    if _client is None:
        if not DOCDB_URI:
            raise RuntimeError("DOCDB_URI environment variable not set")
        logger.info("Creating new MongoClient for DocumentDB")
        _client = MongoClient(
            DOCDB_URI,
            tls=True,
            tlsCAFile=TLS_CA_FILE,
            retryWrites=False,           # DocumentDB requires retryWrites=false
            serverSelectionTimeoutMS=5000,
        )
    return _client[DOCDB_DB_NAME][DOCDB_COLLECTION]


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class ProductCreate(BaseModel):
    """Payload for creating a new product."""
    name: str = Field(..., examples=["Laptop ASUS ROG"])
    category: str = Field(..., examples=["electronics"])
    price: float = Field(..., gt=0, examples=[1299.99])
    stock: int = Field(..., ge=0, examples=[15])
    tags: List[str] = Field(default_factory=list, examples=[["gaming", "rgb"]])


class ProductUpdate(BaseModel):
    """Payload for partial updates (PATCH). All fields optional."""
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    tags: Optional[List[str]] = None


class Product(BaseModel):
    """Response model — uses string id (Mongo ObjectId converted to str)."""
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    name: str
    category: str
    price: float
    stock: int
    tags: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _to_object_id(raw_id: str) -> ObjectId:
    """Convert a string id from the URL to a MongoDB ObjectId, 404 on error."""
    try:
        return ObjectId(raw_id)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail=f"Invalid product id: {raw_id}")


def _serialize(doc: dict) -> dict:
    """Convert Mongo document to a JSON-serializable dict."""
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return doc


# ---------------------------------------------------------------------------
# FastAPI lifespan: warm up the Mongo connection on cold start
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        get_collection()  # triggers connection
        logger.info("DocumentDB connection ready")
    except Exception as exc:
        logger.error(f"Could not connect to DocumentDB: {exc}")
    yield


app = FastAPI(
    title="Amazon DocumentDB Demo API",
    description="RESTful API demonstrating DocumentDB operations via HTTP verbs.",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/", tags=["health"])
def root():
    return {"service": "documentdb-demo", "status": "ok"}


@app.get("/health", tags=["health"])
def health():
    """Ping DocumentDB to verify connectivity."""
    try:
        get_collection().database.client.admin.command("ping")
        return {"status": "healthy", "database": DOCDB_DB_NAME}
    except PyMongoError as exc:
        raise HTTPException(status_code=503, detail=f"DocumentDB unreachable: {exc}")


# ---------------------------------------------------------------------------
# CREATE  ->  POST /products  ->  insert_one
# ---------------------------------------------------------------------------
@app.post(
    "/products",
    status_code=status.HTTP_201_CREATED,
    tags=["products"],
    summary="Create a new product",
)
def create_product(payload: ProductCreate):
    """Insert a new document into the products collection."""
    doc = payload.model_dump()
    doc["created_at"] = datetime.now(timezone.utc)
    doc["updated_at"] = doc["created_at"]

    result = get_collection().insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    logger.info(f"Inserted product {doc['_id']}")
    return doc


# ---------------------------------------------------------------------------
# LIST  ->  GET /products  ->  find()
# ---------------------------------------------------------------------------
@app.get("/products", tags=["products"], summary="List products (paginated)")
def list_products(
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
):
    """Return a page of products."""
    cursor = get_collection().find().skip(skip).limit(limit)
    items = [_serialize(d) for d in cursor]
    total = get_collection().count_documents({})
    return {"total": total, "limit": limit, "skip": skip, "items": items}


# ---------------------------------------------------------------------------
# READ ONE  ->  GET /products/{id}  ->  find_one
# ---------------------------------------------------------------------------
@app.get("/products/{product_id}", tags=["products"], summary="Get a product by id")
def get_product(product_id: str = Path(..., examples=["66f1a2b3c4d5e6f7a8b9c0d1"])):
    doc = get_collection().find_one({"_id": _to_object_id(product_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")
    return _serialize(doc)


# ---------------------------------------------------------------------------
# SEARCH  ->  GET /products/search  ->  find() with $gte / $lte / $regex
# ---------------------------------------------------------------------------
@app.get(
    "/products/search/",
    tags=["products"],
    summary="Search products with filters",
    description=(
        "Demonstrates MongoDB query operators: $gte, $lte, $regex, $in. "
        "All parameters are optional; combine them as you like."
    ),
)
def search_products(
    category: Optional[str] = Query(None, examples=["electronics"]),
    min_price: Optional[float] = Query(None, examples=[100]),
    max_price: Optional[float] = Query(None, examples=[2000]),
    name_contains: Optional[str] = Query(None, examples=["laptop"]),
    tag: Optional[str] = Query(None, examples=["gaming"]),
):
    """Build a MongoDB query dynamically from query-string parameters."""
    query: dict = {}

    if category:
        query["category"] = category

    # Price range with $gte / $lte  -- shows MongoDB comparison operators
    price_filter: dict = {}
    if min_price is not None:
        price_filter["$gte"] = min_price
    if max_price is not None:
        price_filter["$lte"] = max_price
    if price_filter:
        query["price"] = price_filter

    # Case-insensitive substring match  --  $regex
    if name_contains:
        query["name"] = {"$regex": name_contains, "$options": "i"}

    # Tag membership  --  $in
    if tag:
        query["tags"] = {"$in": [tag]}

    cursor = get_collection().find(query).limit(50)
    items = [_serialize(d) for d in cursor]
    return {"query": query, "count": len(items), "items": items}


# ---------------------------------------------------------------------------
# UPDATE (partial)  ->  PATCH /products/{id}  ->  update_one with $set
# ---------------------------------------------------------------------------
@app.patch("/products/{product_id}", tags=["products"], summary="Partially update a product")
def patch_product(product_id: str, payload: ProductUpdate):
    update_fields = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_fields["updated_at"] = datetime.now(timezone.utc)

    updated = get_collection().find_one_and_update(
        {"_id": _to_object_id(product_id)},
        {"$set": update_fields},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return _serialize(updated)


# ---------------------------------------------------------------------------
# REPLACE  ->  PUT /products/{id}  ->  replace_one
# ---------------------------------------------------------------------------
@app.put("/products/{product_id}", tags=["products"], summary="Replace a product")
def replace_product(product_id: str, payload: ProductCreate):
    """Replace the entire document (except _id and created_at)."""
    oid = _to_object_id(product_id)
    existing = get_collection().find_one({"_id": oid})
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")

    new_doc = payload.model_dump()
    new_doc["created_at"] = existing.get("created_at", datetime.now(timezone.utc))
    new_doc["updated_at"] = datetime.now(timezone.utc)

    get_collection().replace_one({"_id": oid}, new_doc)
    new_doc["_id"] = str(oid)
    return new_doc


# ---------------------------------------------------------------------------
# DELETE  ->  DELETE /products/{id}  ->  delete_one
# ---------------------------------------------------------------------------
@app.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["products"],
    summary="Delete a product",
)
def delete_product(product_id: str):
    result = get_collection().delete_one({"_id": _to_object_id(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return None


# ---------------------------------------------------------------------------
# AGGREGATION  ->  GET /products/stats/by-category  ->  aggregate pipeline
# ---------------------------------------------------------------------------
@app.get(
    "/products/stats/by-category",
    tags=["analytics"],
    summary="Aggregation pipeline: stats grouped by category",
)
def stats_by_category():
    """
    Demonstrates a MongoDB aggregation pipeline.
    Groups products by category and computes count, avg price, total stock.
    """
    pipeline = [
        {
            "$group": {
                "_id": "$category",
                "product_count": {"$sum": 1},
                "avg_price": {"$avg": "$price"},
                "total_stock": {"$sum": "$stock"},
                "min_price": {"$min": "$price"},
                "max_price": {"$max": "$price"},
            }
        },
        {"$sort": {"product_count": -1}},
        {
            "$project": {
                "_id": 0,
                "category": "$_id",
                "product_count": 1,
                "avg_price": {"$round": ["$avg_price", 2]},
                "total_stock": 1,
                "min_price": 1,
                "max_price": 1,
            }
        },
    ]
    results = list(get_collection().aggregate(pipeline))
    return {"groups": results}


# ---------------------------------------------------------------------------
# Lambda handler — Mangum wraps the FastAPI ASGI app
# ---------------------------------------------------------------------------
handler = Mangum(app, lifespan="off")
