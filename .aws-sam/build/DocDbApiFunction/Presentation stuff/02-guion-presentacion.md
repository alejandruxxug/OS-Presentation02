# Guion de Presentación — Amazon DocumentDB

> Tono natural y conversacional. Cada slide está pensada para hablarse en 30–45 segundos. Total estimado: ~10 minutos.

---

## Slide 1 — Portada

> Buenas a todos. Hoy vamos a hablarles de **Amazon DocumentDB**, un servicio de bases de datos que tal vez no han escuchado mencionar tanto como DynamoDB o RDS, pero que resuelve un problema súper común en el desarrollo moderno: cómo manejar datos que no caben bien en tablas. Vamos a ver qué es, cómo funciona, cuánto cuesta, y al final les traemos una demo en vivo con FastAPI y Lambda.

---

## Slide 2 — Contexto: ¿Qué es NoSQL?

> Antes de meternos en DocumentDB, vale la pena recordar de qué hablamos cuando decimos NoSQL. Las bases relacionales como PostgreSQL o MySQL guardan datos en **tablas con filas y columnas**, con un esquema fijo definido desde el inicio.
>
> Las bases NoSQL **documentales**, en cambio, guardan **documentos JSON o BSON** flexibles. Cada documento puede tener su propia estructura, datos anidados, listas adentro de listas. No hay que definir un esquema rígido antes de empezar.
>
> DocumentDB cae justamente en esta familia documental, igual que MongoDB. Esto es importante porque **DocumentDB es compatible con la API de MongoDB**, y vamos a ver por qué eso importa tanto.

---

## Slide 3 — ¿Qué es Amazon DocumentDB?

> DocumentDB es un **servicio totalmente administrado de bases de datos documentales** ofrecido por AWS, compatible con la API de MongoDB en sus versiones 3.6, 4.0 y 5.0.
>
> Para que vean qué significa eso en la práctica, miren esta comparación. La misma operación —buscar usuarios mayores de 25 años— en tres bases distintas:
>
> En **PostgreSQL** usan un `SELECT` con un `WHERE`, sintaxis SQL clásica.
> En **MongoDB** usan `db.users.find` con un objeto JSON y el operador `$gt`.
> Y en **DocumentDB**… exactamente lo mismo que en MongoDB. La sintaxis es idéntica.
>
> Esto es el gran atractivo: si su equipo ya sabe MongoDB, **no tienen que aprender nada nuevo**. Pueden tomar código existente y conectarlo a DocumentDB sin cambios.

---

## Slide 4 — Características principales

> DocumentDB trae seis características clave:
>
> Es **totalmente administrado** — AWS se encarga de los parches, los backups y el escalado. Es **compatible con MongoDB**, ya lo vimos. Es de **alto rendimiento**, soporta millones de lecturas por segundo. Es **seguro**, con cifrado en reposo usando KMS y cifrado en tránsito con TLS. Es **escalable**, hasta 15 réplicas de lectura y 128 TiB de almacenamiento. Y soporta **transacciones ACID**.
>
> Aprovechando que mencionamos ACID — para los que no estén familiarizados, son cuatro garantías que aseguran que tus datos no se corrompan: **Atomicity** significa que una transacción ocurre completa o no ocurre, nunca a medias. **Consistency** significa que los datos siempre quedan en un estado válido. **Isolation** significa que las transacciones no se pisan unas a otras. Y **Durability** significa que una vez guardado, queda guardado, incluso si se cae el servidor. Es lo que históricamente garantizaban las bases relacionales, y DocumentDB también las cumple.

---

## Slide 5 — Arquitectura: clústeres y almacenamiento

> Acá viene la parte interesante: cómo está construido por dentro. Un clúster de DocumentDB tiene una arquitectura particular.
>
> Hay **una instancia primaria** que es la única que escribe, y **hasta 15 réplicas de lectura** que solo leen. Pero lo realmente diferente es que **todas estas instancias comparten el mismo volumen de almacenamiento distribuido**. Ese volumen mantiene **6 copias de los datos repartidas en 3 zonas de disponibilidad**, dos copias por zona.
>
> En MongoDB tradicional el modelo es distinto: cada nodo de un *replica set* tiene una copia completa de los datos, y para escalar escrituras se usa **sharding** —partir los datos entre varios primarios—. DocumentDB toma otro enfoque: **separa cómputo de almacenamiento**. Las instancias son ligeras y el almacenamiento es un servicio aparte, distribuido y replicado automáticamente.
>
> Esto tiene una ventaja grande: agregar una réplica nueva toma minutos, no horas, porque no hay que copiar datos. Y si quieren sharding al estilo MongoDB, AWS lanzó hace poco **DocumentDB Elastic Clusters**, que sí permite particionado horizontal.

---

## Slide 6 — Ejemplos reales

> ¿Y quién usa esto? Algunos casos públicos:
>
> **Dow Jones** migró su plataforma editorial completa a DocumentDB para gestionar millones de artículos en formato JSON con metadatos que cambian todo el tiempo.
>
> **Samsung** lo usa para almacenar perfiles de usuario y preferencias de dispositivos para más de **1.100 millones** de cuentas a nivel global.
>
> La **BBC** lo usa para el catálogo de contenido de iPlayer.
>
> Y un caso conceptual súper colombiano: imagínense un app tipo **Rappi**. Cada restaurante tiene su menú, con productos que cambian, precios variables, categorías distintas. Una base relacional tendría que crear tablas y JOINs complejos. Con DocumentDB, cada producto es un documento JSON con la estructura que necesite, y listo.
>
> En general DocumentDB brilla en: **catálogos, perfiles de usuario, gestión de contenido, datos de IoT, y backends móviles** —cualquier escenario donde el esquema evoluciona.

---

## Slide 7 — Costos

> Hablemos de plata. DocumentDB cobra en **cuatro dimensiones**:
>
> Primero, las **instancias de cómputo**, que se cobran por hora. Segundo, el **almacenamiento**, a 10 centavos de dólar por gigabyte al mes. Tercero, las **operaciones de I/O**, a 20 centavos por millón. Y cuarto, el **backup**, que es gratis hasta el 100% del tamaño de tu base.
>
> Un ejemplo concreto para que se hagan idea: un clúster de producción con dos instancias `db.r5.large`, 50 GB de datos y 200 millones de operaciones de I/O al mes les sale en aproximadamente **449 dólares mensuales**. Las instancias se llevan la mayor parte —unos 404—, el almacenamiento son 5 dólares, y el I/O son 40.
>
> Para desarrollo o pruebas pueden usar `db.t3.medium`, que sale alrededor de **69 dólares mensuales**. Y AWS ofrece una **capa gratuita el primer mes** con 750 horas de t3.medium incluidas.

---

## Slide 8 — Pros y contras

> Para terminar la parte teórica: cuándo sí y cuándo no.
>
> **A favor**: si ya tienen código MongoDB, lo migran sin reescribir nada. AWS les administra toda la infra. Se integra nativamente con VPC, IAM, KMS y CloudWatch. La alta disponibilidad multi-AZ es automática. Y pueden agregar réplicas de lectura sin overhead.
>
> **En contra**: en cargas pequeñas sale más caro que un MongoDB en EC2 o que MongoDB Atlas. No soporta el 100% de la API de MongoDB —algunos operadores avanzados no funcionan—. El escalado horizontal de escrituras solo está disponible con Elastic Clusters. Solo es accesible dentro de una VPC, lo cual complica conectarse desde local. Y un failover puede tardar **entre 60 y 120 segundos**, lo cual para algunas apps es mucho.
>
> En resumen: **DocumentDB es ideal cuando ya usan MongoDB y quieren que AWS se encargue de la operación**, no cuando arrancan desde cero buscando lo más barato.

---

## Slide 9 — Demo: Arquitectura

> Listo, vamos con la demo. Construimos lo siguiente:
>
> El cliente —en nuestro caso, `curl` o Postman— manda peticiones HTTP a un **API Gateway** de AWS. El API Gateway las enruta a una **función Lambda**, donde corre una aplicación de **FastAPI** envuelta con una librería que se llama **Mangum**, que adapta FastAPI para que funcione en Lambda. Esa Lambda está dentro de una **VPC**, lo que le permite conectarse al **clúster de DocumentDB** que también vive dentro de la misma VPC, usando TLS.
>
> Toda la conexión se hace con **PyMongo**, el driver oficial de MongoDB para Python. DocumentDB no se da cuenta de que no está hablando con un MongoDB real.

---

## Slide 10 — Demo: endpoints REST

> La API expone un recurso `/products` totalmente RESTful. Cada método HTTP corresponde a una operación distinta de DocumentDB. Vamos a recorrerlos en vivo:
>
> Un `POST` crea un producto nuevo —usa `insert_one`. Un `GET` sin parámetros lista todos los productos —usa `find`. Un `GET` con un ID busca uno específico. Un `GET` a `/search` con filtros muestra los operadores `$gte` y `$lte` para rangos. Un `PATCH` actualiza campos puntuales con `$set`. Un `PUT` reemplaza el documento completo. Un `DELETE` elimina. Y al final tenemos un `GET` a `/stats/by-category` que muestra una **aggregation pipeline** completa, agrupando productos por categoría y calculando totales.
>
> *(Aquí cambian a la terminal y corren los comandos que tienen preparados en `demo-commands.md`.)*

---

## Slide 11 — Cierre

> Para cerrar, los tres puntos clave: **DocumentDB es MongoDB administrado por AWS**. Su arquitectura **separa cómputo de almacenamiento**, replicando los datos seis veces en tres zonas. Y se paga **por uso en cuatro dimensiones**: cómputo, almacenamiento, I/O y backup.
>
> Muchas gracias. ¿Preguntas?

---

## Tips para presentar

- **Slide 3**: Pausen un par de segundos en la comparación de queries — es el momento "ajá" de la presentación.
- **Slide 5**: Si pueden, señalen con el cursor el diagrama mientras explican. Es la parte más densa.
- **Slide 7**: Los $449 son el número que la gente recuerda — díganlo con énfasis.
- **Demo**: Tengan los comandos `curl` en una terminal grande y visible. Si algo falla en vivo, tengan capturas de pantalla de respaldo.
- **Tiempo total**: ~7-8 minutos de slides + ~2-3 minutos de demo = ~10 minutos.
