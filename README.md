# SKOS MCP Classifier# 🏷️ SKOS MCP Classifier# SKOS MCP Classifier (Treew)



Sistema de clasificación automática de productos usando OpenAI y taxonomías SKOS (Simple Knowledge Organization System) vía Model Context Protocol.



## CaracterísticasUn clasificador de productos alimentarios basado en taxonomía SKOS que utiliza OpenAI y Model Context Protocol (MCP) para clasificar productos de manera inteligente y precisa.Repo de ejemplo para exponer una taxonomía **SKOS** como **servidor MCP** y conectarla a **OpenAI** (Responses API / Agents SDK) para clasificación de productos.



- 🤖 Clasificación inteligente usando GPT-4o-mini con function calling

- 🏷️ Taxonomía SKOS integrada para productos alimenticios

- 🔌 Protocolo MCP para integración semántica## 🌟 Características## Estructura

- 📊 Exportación a CSV y Excel con formato profesional

- 🌐 API REST para integraciones externas```

- 🧪 Herramientas de testing y validación

- 📝 Soporte para IDs/SKUs personalizados- 🤖 **Clasificación Inteligente**: Utiliza OpenAI GPT-4o-mini con function callingskos-mcp-classifier/



## Estructura del Proyecto- 📊 **Taxonomía SKOS**: Basado en estándares semánticos para alimentos├─ server/                     # servidor MCP (FastAPI)



```- 🆔 **Soporte para IDs**: Incluye SKUs, códigos de producto y identificadores personalizados├─ client/                     # clientes (Python y TS)

├── client/                          # Cliente de clasificación

│   ├── classify_standard_api.py     # Cliente principal con OpenAI- 📤 **Múltiples Formatos**: Exporta a CSV, Excel y JSON└─ data/taxonomy.jsonld        # tu SKOS JSON-LD (copiado)

│   ├── test_classifier.py           # Herramienta de testing interactiva

│   ├── csv_exporter.py             # Exportador a CSV- 🔌 **API REST**: Servidor FastAPI para integración```

│   ├── excel_exporter.py           # Exportador a Excel

│   ├── classification_api.py       # Servidor API REST- 🧪 **Testing Completo**: Scripts para pruebas individuales y en lote

│   ├── examples_with_ids.py        # Ejemplos de uso con IDs

│   └── compare_classifications.py  # Comparador de resultados## Pasos rápidos

├── server/                         # Servidor MCP

│   ├── main.py                     # Servidor FastAPI con endpoints SKOS## 🚀 Inicio Rápido1) Crea la DB a partir de tu SKOS:

│   ├── skos_loader.py             # Cargador de taxonomía

│   ├── db.py                      # Configuración SQLite```

│   └── requirements.txt           # Dependencias del servidor

├── data/### Prerrequisitosmake load

│   └── taxonomy.jsonld           # Taxonomía SKOS en JSON-LD

└── skos.sqlite                   # Base de datos SQLite```

```

- Python 3.8+2) Levanta el servidor MCP:

## Instalación y Configuración

- OpenAI API Key```

### Prerrequisitos

- Gitmake run

- Python 3.8+

- Git```

- Clave API de OpenAI

### Instalación3) Prueba la clasificación con Responses API:

### Instalación

```

```bash

# Clonar el repositorio```bashexport OPENAI_API_KEY=...

git clone https://github.com/idourra/skos-mcp-classifier.git

cd skos-mcp-classifier# Clonar el repositorio

git clone https://github.com/idourra/skos-mcp-classifier.git

# Instalar dependenciascd skos-mcp-classifier```

make install



# Configurar variables de entorno

cp .env.example .env# Crear entorno virtual## Docker

# Edita .env y agrega tu OPENAI_API_KEY

```python -m venv .venv```



### Configuraciónsource .venv/bin/activate  # Linux/Macdocker build -t skos-mcp-server ./server



La taxonomía incluida es la que nos compartiste, en formato JSON-LD dentro de `data/taxonomy.jsonld`.# o en Windows: .venv\Scripts\activatedocker run -p 8080:8080 --rm skos-mcp-server



1. **Edita el archivo `.env`**:```



```bash# Instalar dependencias

OPENAI_API_KEY=tu_clave_aqui

MCP_SERVER_URL=http://localhost:8080pip install -r server/requirements.txt## Notas

```

pip install requests python-dotenv openai openpyxl- `server/skos_loader.py` detecta automáticamente JSON-LD (`.jsonld`) y TTL/RDF.

2. **Inicia el servidor MCP**:

- Endpoints MCP expuestos:

```bash

make server# Configurar variables de entorno  - `POST /tools/search_concepts`

```

cp .env.example .env  - `POST /tools/get_context`

3. **¡Ya está listo para usar!**

# Edita .env y agrega tu OPENAI_API_KEY  - `POST /tools/validate_notation`

## Uso Rápido

```- El archivo `server/mcp_tools.json` declara las herramientas MCP.

### Clasificación Simple



```python

from client.classify_standard_api import classify### Configuración> La taxonomía incluida es la que nos compartiste, en formato JSON-LD dentro de `data/taxonomy.jsonld`.



# Clasificar un producto

result = classify("Yogur griego natural sin azúcar")1. **Edita el archivo `.env`**:

print(f"Categoría: {result['category']}")```bash

print(f"Confianza: {result['confidence']}%")OPENAI_API_KEY=sk-tu-clave-aqui

```MCP_SERVER_URL=http://localhost:8080

```

### Clasificación con ID/SKU

2. **Inicia el servidor MCP**:

```python```bash

# Clasificar producto con ID personalizadouvicorn server.main:app --host 0.0.0.0 --port 8080

result = classify("Aceite de oliva extra virgen", product_id="SKU-12345")```

print(f"ID: {result['product_id']}")

print(f"Categoría: {result['category']}")3. **¡Ya está listo para usar!**

```

## 📋 Uso

### Testing Interactivo

### 1. Clasificación Simple

```bash

python client/test_classifier.py```python

```from client.classify_standard_api import classify



### Exportación de Resultados# Sin ID

resultado = classify("yogur natural griego")

```python

from client.csv_exporter import export_to_csv# Con ID/SKU

from client.excel_exporter import export_to_excelresultado = classify("yogur natural griego", "SKU-12345")



# Exportar a CSVprint(resultado)

export_to_csv("resultados.csv", results)# {

#   "search_text": "yogur natural griego",

# Exportar a Excel con formato#   "product_id": "SKU-12345",

export_to_excel("resultados.xlsx", results)#   "concept_uri": "https://treew.io/taxonomy/concept/111206",

```#   "prefLabel": "Yogur y sustitutos",

#   "notation": "111206",

## API REST#   "confidence": 1.0

# }

El proyecto incluye un servidor API REST para integraciones externas:```



```bash### 2. Línea de Comandos

# Iniciar API REST

python client/classification_api.py```bash

```# Producto individual

python test_classifier.py "queso manchego curado"

La API estará disponible en `http://localhost:8001` con documentación automática en `/docs`.

# Con ID

### Endpoints Principalespython test_classifier.py "queso manchego|QUESO-001"



#### `POST /classify`# Modo interactivo

python test_classifier.py --interactive

```json

{# Lote sin IDs

  "text": "Yogur griego natural",python test_classifier.py --batch

  "product_id": "SKU-001"

}# Lote con IDs

```python test_classifier.py --batch-ids

```

Respuesta:

### 3. Exportación a CSV

```json

{```python

  "product_id": "SKU-001",from csv_exporter import export_to_csv

  "text": "Yogur griego natural",

  "category": "Productos lácteos fermentados",productos = [

  "notation": "04.2.2.5",    {"text": "manzanas rojas", "id": "FRUTA-001"},

  "confidence": 95,    {"text": "leche descremada", "id": "LACTEO-002"}

  "timestamp": "2024-01-15T10:30:00Z"]

}

```export_to_csv(productos, "mi_catalogo.csv")

```

#### `POST /classify/batch`

### 4. Exportación a Excel

Clasificación por lotes (síncrona y asíncrona).

```python

#### `GET /health`from excel_exporter import export_to_excel



Estado del sistema.export_to_excel(productos, "mi_catalogo.xlsx")

```

## Comandos Make Disponibles

### 5. API REST

```bash

make install    # Instalar todas las dependencias```bash

make server     # Iniciar servidor MCP# Iniciar API

make api        # Iniciar API REST  python classification_api.py

make test       # Ejecutar tests

make classify   # Clasificar productos interactivamente# Usar API

make export     # Exportar resultadoscurl -X POST "http://localhost:8001/classify" \

make clean      # Limpiar archivos temporales     -H "Content-Type: application/json" \

```     -d '{"text": "cerveza IPA", "product_id": "BEB-001"}'

```

## Ejemplos Avanzados

## 📁 Estructura del Proyecto

### Procesamiento por Lotes

```

```pythonskos-mcp-classifier/

productos = [├── client/                          # Cliente de clasificación

    {"text": "Yogur griego", "id": "P001"},│   ├── classify_standard_api.py     # Cliente principal

    {"text": "Aceite oliva", "id": "P002"},│   ├── classify_agents_sdk.ts       # Cliente TypeScript

    {"text": "Pan integral", "id": "P003"}│   └── classify_responses_api.py    # Cliente legacy

]├── server/                          # Servidor MCP

│   ├── main.py                      # FastAPI server

for producto in productos:│   ├── db.py                        # Base de datos

    result = classify(producto["text"], producto["id"])│   ├── skos_loader.py              # Cargador SKOS

    print(f"{producto['id']}: {result['category']}")│   └── requirements.txt

```├── data/

│   └── taxonomy.jsonld             # Taxonomía SKOS

### Comparación de Resultados├── test_classifier.py              # Script de pruebas

├── csv_exporter.py                 # Exportador CSV

```bash├── excel_exporter.py              # Exportador Excel

python client/compare_classifications.py archivo1.json archivo2.json├── classification_api.py           # API REST

```├── examples_with_ids.py            # Ejemplos completos

├── compare_classifications.py      # Comparación

## Servidor MCP├── skos.sqlite                    # Base de datos SQLite

├── .env.example                   # Plantilla configuración

El servidor MCP expone los siguientes endpoints:└── README.md                      # Esta documentación

```

- `POST /tools/search_concepts` - Buscar conceptos en la taxonomía

- `POST /tools/get_context` - Obtener contexto de un concepto## 🔧 Scripts Disponibles

- `POST /tools/validate_notation` - Validar notación SKOS

| Script | Descripción | Ejemplo |

## Contribuciones|--------|-------------|---------|

| `test_classifier.py` | Pruebas interactivas | `python test_classifier.py --batch` |

Las contribuciones son bienvenidas. Por favor:| `csv_exporter.py` | Exportar a CSV | `python csv_exporter.py` |

| `excel_exporter.py` | Exportar a Excel | `python excel_exporter.py` |

1. Haz fork del repositorio| `classification_api.py` | Servidor API REST | `python classification_api.py` |

2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)| `examples_with_ids.py` | Ejemplos completos | `python examples_with_ids.py` |

3. Commit tus cambios (`git commit -am 'Agrega nueva característica'`)

4. Push a la rama (`git push origin feature/nueva-caracteristica`)## 🌐 API REST

5. Abre un Pull Request

### Endpoints

## Licencia

#### `POST /classify`

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.Clasifica un producto individual.



## Soporte**Request:**

```json

Para reportar bugs o solicitar features, abre un issue en GitHub:{

https://github.com/idourra/skos-mcp-classifier/issues  "text": "queso parmesano",

  "product_id": "QUESO-001"

---}

```

*Desarrollado con ❤️ para la clasificación inteligente de productos*
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