# Claude Design Prompt — Amazon DocumentDB Presentation

> Copy everything below the line into Claude Design.

---

Build me an 11-slide presentation about **Amazon DocumentDB**. The presentation is in **Spanish** for a university class. Audience: classmates with general AWS knowledge but no prior exposure to NoSQL document databases.

## Visual Direction

**Style:** Clean, modern, generous whitespace, calm and professional. Think "Azure documentation page meets a tech startup pitch deck." Avoid corporate stock photos and clip art. Avoid heavy drop shadows and gradients on text.

**Color palette (Azure-inspired light greenish-blues):**
- Background base: `#F8FCFB` (off-white with subtle green tint)
- Soft mint surface: `#E6F7F5` (for cards, callout boxes)
- Light teal: `#B3E0DC` (secondary elements, dividers)
- Primary teal: `#4FB3A9` (buttons, key accents, icon fills)
- Deep teal: `#0B6E6E` (headings, primary text emphasis)
- Charcoal text: `#0A2E2E` (body copy)
- Warm amber accent: `#FFB84D` (use sparingly — only to highlight critical numbers or key takeaways)
- Subtle teal gradient (top-left to bottom-right): `#E6F7F5` → `#B3E0DC` for hero areas

**Typography:**
- Headings: **Inter** or **Segoe UI**, weight 600–700
- Body: **Inter** or **Segoe UI**, weight 400
- Code/monospace: **JetBrains Mono** or **Fira Code**

**Iconography:** Line-style icons (Lucide / Heroicons outline), 1.5px stroke, primary teal `#4FB3A9`. No filled icons except for emphasis.

**Decorative elements:** Subtle organic shapes in the corners (soft blob curves in `#E6F7F5` at low opacity), thin teal dividers, occasional dotted-line accents. No heavy textures.

**Diagrams:** Flat, minimal, single accent color per diagram. Use rounded rectangles (8px radius), 2px strokes, plenty of label spacing.

---

## Slide-by-Slide Content

### Slide 1 — Portada (Cover)
- **Title:** "Amazon DocumentDB"
- **Subtitle:** "Base de datos documental, totalmente administrada y compatible con MongoDB"
- Course name, team members, date placeholder
- Visual: Large stylized document icon with subtle teal gradient, AWS logo small in corner, organic blob shape in background

### Slide 2 — Contexto: ¿Qué es NoSQL?
- **Title:** "Antes de empezar: ¿qué es NoSQL?"
- Two-column layout comparing **Relacional (SQL)** vs **Documental (NoSQL)**:
  - Left column (`#E6F7F5` background): "SQL / Relacional" — tablas con filas y columnas, esquema fijo, JOINs, ej: PostgreSQL, MySQL
  - Right column (slightly stronger teal): "NoSQL Documental" — documentos JSON/BSON flexibles, sin esquema rígido, datos anidados, ej: MongoDB, DocumentDB
- Small visual at bottom: a SQL table on the left morphing into a JSON document on the right with an arrow
- Footer note: "DocumentDB pertenece a la familia documental"

### Slide 3 — ¿Qué es Amazon DocumentDB?
- **Title:** "¿Qué es Amazon DocumentDB?"
- Top short paragraph (2 lines): "Servicio de base de datos documental totalmente administrado por AWS, compatible con la API de MongoDB (versiones 3.6, 4.0, 5.0)."
- **Three-column query comparison table** showing the same operation "Buscar usuarios mayores de 25 años":
  - Column 1 — **PostgreSQL**:
    ```sql
    SELECT * FROM users
    WHERE age > 25;
    ```
  - Column 2 — **MongoDB**:
    ```js
    db.users.find({
      age: { $gt: 25 }
    })
    ```
  - Column 3 — **DocumentDB** (highlighted with primary teal border):
    ```js
    db.users.find({
      age: { $gt: 25 }
    })
    ```
- Caption below the table: "DocumentDB usa la misma sintaxis que MongoDB → cero curva de aprendizaje si ya conoces MongoDB"
- Use monospace font with subtle code block background (`#F0F8F7`)

### Slide 4 — Características principales
- **Title:** "Características principales"
- **6 feature cards** in a 3×2 grid, each with an icon + short label + 1-line description:
  1. 🛡️ **Totalmente administrado** — AWS gestiona parches, backups y escalado
  2. 🔌 **Compatible con MongoDB** — usa los mismos drivers y herramientas
  3. ⚡ **Alto rendimiento** — millones de lecturas por segundo
  4. 🔒 **Seguro** — cifrado en reposo (KMS) y en tránsito (TLS)
  5. 📈 **Escalable** — hasta 15 réplicas de lectura y 128 TiB de almacenamiento
  6. ✅ **Transacciones ACID** — soporta transacciones multi-documento
- **Small callout box at bottom** (`#FFF7E6` background, amber border):
  > **¿Qué es ACID?** Cuatro garantías que aseguran que tus datos no se corrompan:
  > **A**tomicity (todo o nada) · **C**onsistency (datos válidos siempre) · **I**solation (transacciones no se pisan) · **D**urability (lo guardado, guardado queda)

### Slide 5 — Arquitectura: clústeres y almacenamiento
- **Title:** "Arquitectura: ¿cómo funciona un clúster?"
- **Main diagram** (centered, large): Show a DocumentDB cluster:
  - Top: 1 **Primary Instance** (writer) box in deep teal
  - Below it: 2-3 **Read Replica** boxes in primary teal
  - All instances connected with arrows down to a **shared Cluster Volume** at the bottom
  - The cluster volume box spans 3 vertical lanes labeled **AZ-1, AZ-2, AZ-3**, each containing 2 small "copy" disks → total 6 copies of data
  - Label arrows: "Hasta 15 réplicas de lectura", "1 sola escritura (primary)", "6 copias en 3 zonas de disponibilidad"
- **Right-side comparison callout** (small box):
  > **vs MongoDB clásico:**
  > MongoDB usa *replica sets* (cada nodo tiene copia completa) y *sharding* nativo (datos repartidos entre varios primarios). DocumentDB separa cómputo y almacenamiento: las réplicas comparten un mismo volumen distribuido.
- Bottom note in small text: "DocumentDB Elastic Clusters (modalidad nueva) sí permite sharding hash-based si necesitas escalar escrituras horizontalmente."

### Slide 6 — Ejemplos reales de uso
- **Title:** "¿Quién lo usa? Ejemplos reales"
- **4 example cards** in 2×2 grid, each with company/scenario icon + name + short description:
  1. **Dow Jones** — Migró su plataforma de contenido editorial a DocumentDB para gestionar millones de artículos JSON con metadatos flexibles
  2. **Samsung Electronics** — Almacena perfiles de usuario y preferencias de dispositivos para más de 1.1 mil millones de cuentas
  3. **BBC** — Catálogo de contenido y datos de programas de iPlayer
  4. **Rappi-style app** *(ejemplo conceptual)* — Catálogo de productos con categorías, precios y stock variable por restaurante, con búsquedas geo-espaciales
- Below the cards, a horizontal banner: **"Ideal para:"** *catálogos de productos · perfiles de usuario · gestión de contenido · datos de IoT · backends móviles · sistemas con esquemas que evolucionan*

### Slide 7 — Costos
- **Title:** "Costos: ¿cuánto cuesta?"
- Top: "DocumentDB se cobra en **4 dimensiones**:" followed by 4 small icon cards in a row:
  1. 💻 **Instancias (cómputo)** — por hora, según tipo
  2. 💾 **Almacenamiento** — $0.10 / GB-mes
  3. 🔄 **I/O** — $0.20 / millón de operaciones
  4. 📦 **Backup** — gratis hasta 100% del tamaño de la BD
- Below, **"Ejemplo práctico"** in a highlighted card (`#E6F7F5` background):
  - "Clúster de producción con 2 instancias `db.r5.large` + 50 GB datos + 200 millones I/O al mes:"
  - Breakdown:
    - Instancias: 2 × $0.277/h × 730h = **$404.42**
    - Almacenamiento: 50 GB × $0.10 = **$5.00**
    - I/O: 200M × $0.20 = **$40.00**
  - **Total: ~$449/mes** (in amber accent, larger font)
- Right-side small note: "Para pruebas: `db.t3.medium` desde ~$69/mes. Capa gratuita: 750h del primer mes."

### Slide 8 — Pros y contras
- **Title:** "Pros y contras"
- Two-column layout:
  - **✅ Ventajas** (left, soft teal background):
    - Compatible con código MongoDB existente
    - AWS gestiona toda la infraestructura
    - Integración nativa con VPC, IAM, KMS, CloudWatch
    - Alta disponibilidad automática (multi-AZ)
    - Hasta 15 réplicas de lectura sin overhead de replicación
  - **⚠️ Desventajas** (right, light amber background):
    - Más caro que MongoDB self-hosted o Atlas en cargas pequeñas
    - No soporta el 100% de la API de MongoDB (compatibilidad parcial)
    - Solo escala escrituras horizontalmente con Elastic Clusters
    - Solo accesible dentro de una VPC (o vía túnel)
    - Failover puede tomar hasta 60-120 segundos
- Bottom one-liner: **"¿Cuándo elegirlo?** Cuando ya usas MongoDB y quieres delegar la operación a AWS sin reescribir tu código."

### Slide 9 — Demo: Arquitectura
- **Title:** "Demo: arquitectura de la solución"
- **Large horizontal architecture diagram** (left to right flow):
  1. 👤 **Cliente** (curl / Postman) icon
  2. → **API Gateway** (AWS icon)
  3. → **Lambda** box containing "FastAPI + Mangum + PyMongo"
  4. → Dashed line entering a "VPC" rounded box that contains:
  5. → **Amazon DocumentDB Cluster** (with primary + replica icons)
- Caption: "El cliente envía requests HTTP → API Gateway las enruta a Lambda → Lambda ejecuta FastAPI y se conecta a DocumentDB dentro de la VPC con TLS"
- Small bullet at bottom: "Stack: Python 3.11 · FastAPI · Mangum · PyMongo · AWS SAM"

### Slide 10 — Demo: endpoints REST
- **Title:** "Demo: endpoints REST → operaciones MongoDB"
- **Table mapping HTTP methods to MongoDB operations** with monospace font, with code blocks. Each row colored alternately:

| Método HTTP | Endpoint | Operación DocumentDB |
|---|---|---|
| `POST` | `/products` | `insert_one()` — crea un documento |
| `GET` | `/products` | `find()` — lista todo |
| `GET` | `/products/{id}` | `find_one({_id})` — busca por ID |
| `GET` | `/products/search?...` | `find()` con `$gte`, `$lte` — filtros |
| `PATCH` | `/products/{id}` | `update_one({$set})` — actualiza campos |
| `PUT` | `/products/{id}` | `replace_one()` — reemplaza completo |
| `DELETE` | `/products/{id}` | `delete_one()` — elimina |
| `GET` | `/products/stats/by-category` | aggregation `$group` — agrega |

- Below the table, a small "Demo en vivo" badge in amber

### Slide 11 — Cierre y preguntas
- **Title:** "Gracias 🙌"
- Three key takeaways in horizontal cards:
  1. 📄 "DocumentDB = MongoDB administrado por AWS"
  2. 🏗️ "Almacenamiento distribuido + cómputo separado"
  3. 💰 "Pago por uso en 4 dimensiones"
- "¿Preguntas?" centered below in large deep-teal text
- Footer with team names + a small AWS DocumentDB icon

---

## Final design notes for Claude Design
- Slide dimensions: 16:9
- Maintain consistent margin (around 60px) on all slides
- Page numbers in bottom-right corner (small, `#B3E0DC`)
- Small DocumentDB/AWS icon top-right corner of every slide except cover
- Don't fill every pixel — let breathing room do the work
- For code blocks: subtle background `#F0F8F7`, rounded corners 6px, 12px padding
- Diagrams should never feel cramped — better to enlarge nodes than to shrink labels
