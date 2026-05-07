# Demo en vivo — comandos para la presentación

> Reemplaza `$API` por la URL de tu API Gateway, p. ej.:
> ```
> export API="https://abc123.execute-api.us-east-1.amazonaws.com/Prod"
> ```

---

## 1. Health check (verificar que Lambda llega a DocumentDB)

```bash
curl $API/health
```

**Operación:** `db.runCommand({ ping: 1 })`

---

## 2. POST — crear un producto (`insert_one`)

```bash
curl -X POST $API/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Teclado Keychron K8",
    "category": "electronics",
    "price": 99.99,
    "stock": 30,
    "tags": ["keyboard", "mechanical", "wireless"]
  }'
```

**Guarden el `_id` que retorna**, lo van a usar en los siguientes pasos.

```bash
export PROD_ID="<pega-el-id-aqui>"
```

---

## 3. GET — listar todos (`find`)

```bash
curl $API/products
```

```bash
# Con paginación
curl "$API/products?limit=5&skip=0"
```

---

## 4. GET por id (`find_one`)

```bash
curl $API/products/$PROD_ID
```

---

## 5. GET search — filtros con operadores MongoDB

**Productos en electrónica entre $100 y $500:**
```bash
curl "$API/products/search/?category=electronics&min_price=100&max_price=500"
```

**Productos cuyo nombre contiene "laptop" (case-insensitive, `$regex`):**
```bash
curl "$API/products/search/?name_contains=laptop"
```

**Productos con el tag "gaming" (`$in`):**
```bash
curl "$API/products/search/?tag=gaming"
```

**Combinando todo:**
```bash
curl "$API/products/search/?category=electronics&min_price=300&tag=audio"
```

---

## 6. PATCH — actualización parcial (`update_one` con `$set`)

Cambiar solo el precio y el stock:
```bash
curl -X PATCH $API/products/$PROD_ID \
  -H "Content-Type: application/json" \
  -d '{
    "price": 89.99,
    "stock": 25
  }'
```

---

## 7. PUT — reemplazar el documento completo (`replace_one`)

```bash
curl -X PUT $API/products/$PROD_ID \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Teclado Keychron K8 Pro",
    "category": "electronics",
    "price": 129.99,
    "stock": 40,
    "tags": ["keyboard", "mechanical", "wireless", "hot-swappable"]
  }'
```

---

## 8. GET aggregation — estadísticas por categoría

```bash
curl $API/products/stats/by-category
```

**Pipeline ejecutado:**
```js
[
  { $group: {
      _id: "$category",
      product_count: { $sum: 1 },
      avg_price:     { $avg: "$price" },
      total_stock:   { $sum: "$stock" },
      min_price:     { $min: "$price" },
      max_price:     { $max: "$price" }
  }},
  { $sort: { product_count: -1 } }
]
```

---

## 9. DELETE — eliminar (`delete_one`)

```bash
curl -X DELETE $API/products/$PROD_ID -i
```

(El `-i` muestra el código `204 No Content`.)

---

## Orden recomendado durante la demo

1. `GET /health` — "está vivo"
2. `GET /products` — "miren los datos que ya cargué"
3. `POST /products` — "creo un producto nuevo"
4. `GET /products/{id}` — "lo recupero"
5. `GET /products/search?...` — "filtros con operadores MongoDB"
6. `PATCH /products/{id}` — "actualizo parcialmente"
7. `GET /products/stats/by-category` — "y miren esta agregación"
8. `DELETE /products/{id}` — "lo borro"

**Tiempo total:** ~2-3 minutos.
