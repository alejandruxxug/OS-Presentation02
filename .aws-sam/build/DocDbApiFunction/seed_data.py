"""
Seed script: populate the DocumentDB collection with sample products.

Run locally (with port-forwarding or from an EC2 inside the VPC):
    DOCDB_URI="mongodb://user:pass@host:27017/?tls=true&..." \
    TLS_CA_FILE=./global-bundle.pem \
    python seed_data.py
"""

import os
from datetime import datetime, timezone
from pymongo import MongoClient

DOCDB_URI = os.environ["DOCDB_URI"]
DOCDB_DB_NAME = os.environ.get("DOCDB_DB_NAME", "demo")
DOCDB_COLLECTION = os.environ.get("DOCDB_COLLECTION", "products")
TLS_CA_FILE = os.environ.get("TLS_CA_FILE", "./global-bundle.pem")

SAMPLE_PRODUCTS = [
    {
        "name": "Laptop ASUS ROG Strix",
        "category": "electronics",
        "price": 1899.99,
        "stock": 12,
        "tags": ["gaming", "laptop", "rgb"],
    },
    {
        "name": "iPhone 15 Pro",
        "category": "electronics",
        "price": 1199.00,
        "stock": 25,
        "tags": ["smartphone", "apple"],
    },
    {
        "name": "Sony WH-1000XM5",
        "category": "electronics",
        "price": 399.99,
        "stock": 40,
        "tags": ["audio", "headphones", "noise-cancelling"],
    },
    {
        "name": "Cafetera Oster Prima Latte",
        "category": "appliances",
        "price": 249.50,
        "stock": 18,
        "tags": ["kitchen", "coffee"],
    },
    {
        "name": "Aspiradora Robot Roomba i3",
        "category": "appliances",
        "price": 349.00,
        "stock": 7,
        "tags": ["home", "smart", "cleaning"],
    },
    {
        "name": "Camiseta Adidas Originals",
        "category": "clothing",
        "price": 39.99,
        "stock": 100,
        "tags": ["clothing", "casual", "unisex"],
    },
    {
        "name": "Tenis Nike Air Max 90",
        "category": "clothing",
        "price": 129.99,
        "stock": 55,
        "tags": ["shoes", "sneakers", "running"],
    },
    {
        "name": "Libro: Clean Code",
        "category": "books",
        "price": 34.99,
        "stock": 30,
        "tags": ["programming", "book", "robert-martin"],
    },
    {
        "name": "Libro: Designing Data-Intensive Applications",
        "category": "books",
        "price": 49.99,
        "stock": 22,
        "tags": ["programming", "book", "databases"],
    },
    {
        "name": "Monitor LG UltraWide 34''",
        "category": "electronics",
        "price": 599.00,
        "stock": 9,
        "tags": ["monitor", "ultrawide", "office"],
    },
]


def main():
    print(f"Connecting to {DOCDB_DB_NAME}.{DOCDB_COLLECTION} ...")
    client = MongoClient(
        DOCDB_URI,
        tls=True,
        tlsCAFile=TLS_CA_FILE,
        retryWrites=False,
    )
    coll = client[DOCDB_DB_NAME][DOCDB_COLLECTION]

    # Clear existing demo data
    deleted = coll.delete_many({}).deleted_count
    print(f"Deleted {deleted} existing documents")

    now = datetime.now(timezone.utc)
    for p in SAMPLE_PRODUCTS:
        p["created_at"] = now
        p["updated_at"] = now

    result = coll.insert_many(SAMPLE_PRODUCTS)
    print(f"Inserted {len(result.inserted_ids)} products")
    print("Sample IDs:", [str(_id) for _id in result.inserted_ids[:3]], "...")


if __name__ == "__main__":
    main()
