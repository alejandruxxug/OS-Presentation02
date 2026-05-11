# DocumentDB Demo — FastAPI on Lambda

Demo RESTful API que se ejecuta en AWS Lambda y se conecta a Amazon DocumentDB.
Diseñada para mostrar en vivo cómo cada verbo HTTP corresponde a una operación
diferente de DocumentDB / MongoDB.

## Arquitectura

```
Cliente (curl)
    │ HTTP
    ▼
API Gateway
    │
    ▼
AWS Lambda (Python 3.11)
    │  FastAPI + Mangum + PyMongo
    │  (dentro de la VPC)
    ▼
Amazon DocumentDB Cluster
```

## Mapa de endpoints

| Método | Ruta | Operación DocumentDB |
|---|---|---|
| `POST` | `/products` | `insert_one` |
| `GET` | `/products` | `find` (lista paginada) |
| `GET` | `/products/{id}` | `find_one` |
| `GET` | `/products/search/` | `find` con `$gte`, `$lte`, `$regex`, `$in` |
| `PATCH` | `/products/{id}` | `update_one` con `$set` |
| `PUT` | `/products/{id}` | `replace_one` |
| `DELETE` | `/products/{id}` | `delete_one` |
| `GET` | `/products/stats/by-category` | `aggregate` con `$group` |

## Pre-requisitos

- Cuenta AWS con permisos para crear Lambda, API Gateway, IAM, VPC.
- **Clúster DocumentDB ya creado** en una VPC (la Lambda debe ir en la misma VPC).
- AWS CLI configurado.
- AWS SAM CLI instalado (`brew install aws-sam-cli` o `pip install aws-sam-cli`).
- Python 3.11 local para pruebas.

## Pasos de despliegue

### 1. Descargar el certificado CA de AWS RDS

DocumentDB requiere TLS. Descarga el bundle global:

```bash
mkdir -p layer/python  # estructura requerida por Lambda layers
curl -o layer/global-bundle.pem \
  https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
```

### 2. Subir el certificado como Lambda Layer

```bash
cd layer
zip -r ../ca-layer.zip .
cd ..
aws lambda publish-layer-version \
  --layer-name docdb-ca-bundle \
  --zip-file fileb://ca-layer.zip \
  --compatible-runtimes python3.11
```

Copia el `LayerVersionArn` que retorna y pégalo en `template.yaml` (sección `Layers`).

### 3. Construir y desplegar con SAM

```bash
sam build
sam deploy --guided
```

Cuando pregunte parámetros:

- `DocDbUri`: tu connection string completa de DocumentDB
  - Formato: `mongodb://USER:PASS@HOST:27017/?tls=true&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false`
- `DocDbName`: `demo` (o el que prefieras)
- `DocDbCollection`: `products`
- `VpcSubnetIds`: subnets privadas de tu VPC (separadas por coma, mínimo 2)
- `VpcSecurityGroupIds`: security group que tiene acceso al puerto 27017 de DocumentDB

Al finalizar, SAM imprime la URL del API Gateway. Guárdala:

```bash
export API="https://abc123.execute-api.us-east-1.amazonaws.com/Prod"
```

### 4. Cargar datos de prueba

Desde una EC2 dentro de la VPC (DocumentDB no es accesible desde Internet), o
configurando un túnel SSH:

```bash
export DOCDB_URI="mongodb://USER:PASS@HOST:27017/?tls=true&..."
export TLS_CA_FILE="./global-bundle.pem"
python seed_data.py
```

### 5. Verificar

```bash
curl $API/health
curl $API/products
```

## Probar localmente (opcional)

Con un MongoDB local (no DocumentDB) para desarrollo:

```bash
docker run -d -p 27017:27017 --name mongo-dev mongo:6
export DOCDB_URI="mongodb://localhost:27017"
export TLS_CA_FILE="/dev/null"  # no se usa con localhost
pip install -r requirements.txt
uvicorn main:app --reload
```

Luego abre `http://localhost:8000/docs` para ver la documentación interactiva
de FastAPI.

> ⚠️ Nota: para correr local sin TLS, edita `main.py` y comenta los parámetros
> `tls=True, tlsCAFile=...` del `MongoClient`.

## Comandos curl para la demo en vivo

Ver `demo-commands.md` — incluye los 9 comandos en orden, listos para
copiar y pegar durante la presentación.

## Estructura de archivos

```
demo-code/
├── main.py              # FastAPI app (handler de Lambda)
├── requirements.txt     # dependencias
├── template.yaml        # AWS SAM (Lambda + API Gateway + VPC config)
├── seed_data.py         # script para cargar productos de muestra
├── demo-commands.md     # comandos curl para la demo en vivo
└── README.md            # este archivo
```

## Troubleshooting

**`ServerSelectionTimeoutError`**: la Lambda no llega a DocumentDB.
- Verifica que la Lambda está en la misma VPC y subnets.
- Verifica que el security group permite tráfico saliente al puerto 27017
  hacia el security group de DocumentDB.

**`SSL: CERTIFICATE_VERIFY_FAILED`**: el CA bundle no está en `/opt/global-bundle.pem`.
- Verifica que el Lambda Layer está adjunto.
- Verifica el path en la variable `TLS_CA_FILE`.

**`OperationFailure: Retryable writes are not supported`**: incluye
`retryWrites=false` en la URI de DocumentDB.
