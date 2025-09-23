# 🏷️ SKOS MCP Classifier# SKOS MCP Classifier (Treew)



Un clasificador de productos alimentarios basado en taxonomía SKOS que utiliza OpenAI y Model Context Protocol (MCP) para clasificar productos de manera inteligente y precisa.Repo de ejemplo para exponer una taxonomía **SKOS** como **servidor MCP** y conectarla a **OpenAI** (Responses API / Agents SDK) para clasificación de productos.



## 🌟 Características## Estructura

```

- 🤖 **Clasificación Inteligente**: Utiliza OpenAI GPT-4o-mini con function callingskos-mcp-classifier/

- 📊 **Taxonomía SKOS**: Basado en estándares semánticos para alimentos├─ server/                     # servidor MCP (FastAPI)

- 🆔 **Soporte para IDs**: Incluye SKUs, códigos de producto y identificadores personalizados├─ client/                     # clientes (Python y TS)

- 📤 **Múltiples Formatos**: Exporta a CSV, Excel y JSON└─ data/taxonomy.jsonld        # tu SKOS JSON-LD (copiado)

- 🔌 **API REST**: Servidor FastAPI para integración```

- 🧪 **Testing Completo**: Scripts para pruebas individuales y en lote

## Pasos rápidos

## 🚀 Inicio Rápido1) Crea la DB a partir de tu SKOS:

```

### Prerrequisitosmake load

```

- Python 3.8+2) Levanta el servidor MCP:

- OpenAI API Key```

- Gitmake run

```

### Instalación3) Prueba la clasificación con Responses API:

```

```bashexport OPENAI_API_KEY=...

# Clonar el repositorioexport MCP_SERVER_URL=http://localhost:8080

git clone https://github.com/tuusuario/skos-mcp-classifier.gitmake classify

cd skos-mcp-classifier```



# Crear entorno virtual## Docker

python -m venv .venv```

source .venv/bin/activate  # Linux/Macdocker build -t skos-mcp-server ./server

# o en Windows: .venv\Scripts\activatedocker run -p 8080:8080 --rm skos-mcp-server

```

# Instalar dependencias

pip install -r server/requirements.txt## Notas

pip install requests python-dotenv openai openpyxl- `server/skos_loader.py` detecta automáticamente JSON-LD (`.jsonld`) y TTL/RDF.

- Endpoints MCP expuestos:

# Configurar variables de entorno  - `POST /tools/search_concepts`

cp .env.example .env  - `POST /tools/get_context`

# Edita .env y agrega tu OPENAI_API_KEY  - `POST /tools/validate_notation`

```- El archivo `server/mcp_tools.json` declara las herramientas MCP.



### Configuración> La taxonomía incluida es la que nos compartiste, en formato JSON-LD dentro de `data/taxonomy.jsonld`.


1. **Edita el archivo `.env`**:
```bash
OPENAI_API_KEY=sk-tu-clave-aqui
MCP_SERVER_URL=http://localhost:8080
```

2. **Inicia el servidor MCP**:
```bash
uvicorn server.main:app --host 0.0.0.0 --port 8080
```

3. **¡Ya está listo para usar!**

## 📋 Uso

### 1. Clasificación Simple

```python
from client.classify_standard_api import classify

# Sin ID
resultado = classify("yogur natural griego")

# Con ID/SKU
resultado = classify("yogur natural griego", "SKU-12345")

print(resultado)
# {
#   "search_text": "yogur natural griego",
#   "product_id": "SKU-12345",
#   "concept_uri": "https://treew.io/taxonomy/concept/111206",
#   "prefLabel": "Yogur y sustitutos",
#   "notation": "111206",
#   "confidence": 1.0
# }
```

### 2. Línea de Comandos

```bash
# Producto individual
python test_classifier.py "queso manchego curado"

# Con ID
python test_classifier.py "queso manchego|QUESO-001"

# Modo interactivo
python test_classifier.py --interactive

# Lote sin IDs
python test_classifier.py --batch

# Lote con IDs
python test_classifier.py --batch-ids
```

### 3. Exportación a CSV

```python
from csv_exporter import export_to_csv

productos = [
    {"text": "manzanas rojas", "id": "FRUTA-001"},
    {"text": "leche descremada", "id": "LACTEO-002"}
]

export_to_csv(productos, "mi_catalogo.csv")
```

### 4. Exportación a Excel

```python
from excel_exporter import export_to_excel

export_to_excel(productos, "mi_catalogo.xlsx")
```

### 5. API REST

```bash
# Iniciar API
python classification_api.py

# Usar API
curl -X POST "http://localhost:8001/classify" \
     -H "Content-Type: application/json" \
     -d '{"text": "cerveza IPA", "product_id": "BEB-001"}'
```

## 📁 Estructura del Proyecto

```
skos-mcp-classifier/
├── client/                          # Cliente de clasificación
│   ├── classify_standard_api.py     # Cliente principal
│   ├── classify_agents_sdk.ts       # Cliente TypeScript
│   └── classify_responses_api.py    # Cliente legacy
├── server/                          # Servidor MCP
│   ├── main.py                      # FastAPI server
│   ├── db.py                        # Base de datos
│   ├── skos_loader.py              # Cargador SKOS
│   └── requirements.txt
├── data/
│   └── taxonomy.jsonld             # Taxonomía SKOS
├── test_classifier.py              # Script de pruebas
├── csv_exporter.py                 # Exportador CSV
├── excel_exporter.py              # Exportador Excel
├── classification_api.py           # API REST
├── examples_with_ids.py            # Ejemplos completos
├── compare_classifications.py      # Comparación
├── skos.sqlite                    # Base de datos SQLite
├── .env.example                   # Plantilla configuración
└── README.md                      # Esta documentación
```

## 🔧 Scripts Disponibles

| Script | Descripción | Ejemplo |
|--------|-------------|---------|
| `test_classifier.py` | Pruebas interactivas | `python test_classifier.py --batch` |
| `csv_exporter.py` | Exportar a CSV | `python csv_exporter.py` |
| `excel_exporter.py` | Exportar a Excel | `python excel_exporter.py` |
| `classification_api.py` | Servidor API REST | `python classification_api.py` |
| `examples_with_ids.py` | Ejemplos completos | `python examples_with_ids.py` |

## 🌐 API REST

### Endpoints

#### `POST /classify`
Clasifica un producto individual.

**Request:**
```json
{
  "text": "queso parmesano",
  "product_id": "QUESO-001"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "search_text": "queso parmesano",
    "product_id": "QUESO-001",
    "prefLabel": "Quesos",
    "notation": "111203",
    "confidence": 1.0
  }
}
```

#### `POST /classify/batch`
Clasifica múltiples productos.

#### `GET /health`
Verificar estado de la API.

#### `GET /docs`
Documentación interactiva (Swagger UI).

## 🧪 Testing

### Ejemplos de Prueba
```bash
# Productos individuales
python test_classifier.py "cerveza IPA|BEB-001"

# Modo interactivo
python test_classifier.py --interactive

# Lote completo
python test_classifier.py --batch-ids
```

## 🚀 Casos de Uso

### E-commerce
- Clasificación automática de catálogos
- Normalización de categorías
- Mejora de búsquedas

### Inventarios
- Organización automática
- Trazabilidad por SKU
- Reportes por categoría

### APIs de Terceros
- Integración con ERPs
- Middleware de clasificación
- Servicios de datos

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

## 🔗 Enlaces

- [Documentación SKOS](https://www.w3.org/2004/02/skos/)
- [OpenAI API](https://platform.openai.com/docs)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)