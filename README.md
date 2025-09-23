# 🏷️ SKOS MCP Classifier# 🏷️ SKOS MCP Classifier



> Sistema de clasificación de productos usando ontologías SKOS y Model Context Protocol (MCP) con integración OpenAI> Sistema de clasificación de productos usando ontologías SKOS y Model Context Protocol (MCP) con integración OpenAI



[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)

[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange.svg)](https://openai.com)[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange.svg)](https://openai.com)

[![Status](https://img.shields.io/badge/Status-Stable-brightgreen.svg)](https://github.com/idourra/skos-mcp-classifier)[![Status](https://img.shields.io/badge/Status-Stable-brightgreen.svg)](#)



## 🚀 Activación Rápida## 🚀 Activación Rápida



```bash```bash

# Clonar repositorio# Clonar repositorio

git clone https://github.com/idourra/skos-mcp-classifier.gitgit clone https://github.com/idourra/skos-mcp-classifier.git

cd skos-mcp-classifiercd skos-mcp-classifier



# Configurar entorno# Configurar entorno

python -m venv .venvpython -m venv .venv

source .venv/bin/activate  # Linux/Macsource .venv/bin/activate  # Linux/Mac

pip install -r requirements.txtpip install -r requirements.txt



# Configurar OpenAI# Configurar OpenAI

echo "OPENAI_API_KEY=tu-api-key-aqui" > .envecho "OPENAI_API_KEY=tu-api-key-aqui" > .env



# ¡Activar sistema!# ¡Activar sistema!

./start_system.sh./start_system.sh

``````



## 📋 Características## 📋 Características



- ✅ **Clasificación automática** de productos usando IA- ✅ **Clasificación automática** de productos usando IA

- 🔍 **Búsqueda semántica** en taxonomías SKOS  - 🔍 **Búsqueda semántica** en taxonomías SKOS  

- 🌐 **API REST completa** con documentación Swagger- 🌐 **API REST completa** con documentación Swagger

- 📊 **Exportación** a CSV y Excel- 📊 **Exportación** a CSV y Excel

- 💰 **Tracking de costos** OpenAI en tiempo real- 💰 **Tracking de costos** OpenAI en tiempo real

- 🏷️ **282 categorías** treew-skos taxonomy- 🏷️ **282 categorías** treew-skos taxonomy

- ⚡ **Alta precisión** (confianza 1.0 en categorías principales)- ⚡ **Alta precisión** (confianza 1.0 en categorías principales)



## 🏗️ ArquitecturaUn clasificador de productos alimentarios basado en taxonomía SKOS que utiliza OpenAI y Model Context Protocol (MCP) para clasificar productos de manera inteligente y precisa.



```Repo de ejemplo para exponer una taxonomía **SKOS** como **servidor MCP** y conectarla a **OpenAI** (Responses API / Agents SDK) para clasificación de productos.

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐

│   Usuario/App   │────│   API REST      │────│   MCP Server    │## Características

│                 │    │  (Puerto 8000)  │    │  (Puerto 8080)  │

└─────────────────┘    └─────────────────┘    └─────────────────┘- 🤖 Clasificación inteligente usando GPT-4o-mini con function calling

                                │                        │- 🏷️ Taxonomía SKOS integrada para productos alimenticios

                                │                        │

                       ┌─────────────────┐    ┌─────────────────┐- 🔌 Protocolo MCP para integración semántica## 🌟 Características## Estructura

                       │     OpenAI      │    │   SKOS SQLite   │

                       │   GPT-4o-mini   │    │   282 concepts  │- 📊 Exportación a CSV y Excel con formato profesional

                       └─────────────────┘    └─────────────────┘

```- 🌐 API REST para integraciones externas```



## 📁 Estructura del Proyecto- 🧪 Herramientas de testing y validación



```- 📝 Soporte para IDs/SKUs personalizados- 🤖 **Clasificación Inteligente**: Utiliza OpenAI GPT-4o-mini con function callingskos-mcp-classifier/

skos-mcp-classifier/

├── 🚀 start_system.sh              # Script de activación automática

├── 🛑 stop_system.sh               # Script de desactivación automática

├── 📖 USAGE_GUIDE.md               # Guía completa de uso## Estructura del Proyecto- 📊 **Taxonomía SKOS**: Basado en estándares semánticos para alimentos├─ server/                     # servidor MCP (FastAPI)

├── server/

│   ├── main.py                     # MCP Server (FastAPI)

│   ├── skos_loader.py              # Cargador de taxonomías SKOS

│   └── db.py                       # Utilidades de base de datos```- 🆔 **Soporte para IDs**: Incluye SKUs, códigos de producto y identificadores personalizados├─ client/                     # clientes (Python y TS)

├── client/

│   ├── classify_standard_api.py    # Cliente principal con OpenAI├── client/                          # Cliente de clasificación

│   └── classify_agents_sdk.ts      # SDK para TypeScript

├── classification_api.py           # API REST principal│   ├── classify_standard_api.py     # Cliente principal con OpenAI- 📤 **Múltiples Formatos**: Exporta a CSV, Excel y JSON└─ data/taxonomy.jsonld        # tu SKOS JSON-LD (copiado)

├── taxonomies/

│   └── treew-skos/│   ├── test_classifier.py           # Herramienta de testing interactiva

│       └── original.jsonld         # Taxonomía SKOS base

└── skos.sqlite                     # Base de datos generada│   ├── csv_exporter.py             # Exportador a CSV- 🔌 **API REST**: Servidor FastAPI para integración```

```

│   ├── excel_exporter.py           # Exportador a Excel

## 🧪 Ejemplos de Uso

│   ├── classification_api.py       # Servidor API REST- 🧪 **Testing Completo**: Scripts para pruebas individuales y en lote

### 🏷️ Clasificación Simple

│   ├── examples_with_ids.py        # Ejemplos de uso con IDs

```bash

curl -X POST http://localhost:8000/classify \│   └── compare_classifications.py  # Comparador de resultados## Pasos rápidos

  -H 'Content-Type: application/json' \

  -d '{"text": "leche descremada", "product_id": "SKU001"}'├── server/                         # Servidor MCP

```

│   ├── main.py                     # Servidor FastAPI con endpoints SKOS## 🚀 Inicio Rápido1) Crea la DB a partir de tu SKOS:

**Respuesta:**

```json│   ├── skos_loader.py             # Cargador de taxonomía

{

  "product_id": "SKU001",│   ├── db.py                      # Configuración SQLite```

  "search_text": "leche descremada",

  "concept_uri": "https://treew.io/taxonomy/concept/111202",│   └── requirements.txt           # Dependencias del servidor

  "prefLabel": "Leches y sustitutos",

  "notation": "111202",├── data/### Prerrequisitosmake load

  "level": 1,

  "confidence": 1.0,│   └── taxonomy.jsonld           # Taxonomía SKOS en JSON-LD

  "timestamp": "2025-09-23T15:30:00"

}└── skos.sqlite                   # Base de datos SQLite```

```

```

### 📦 Clasificación Múltiple

- Python 3.8+2) Levanta el servidor MCP:

```bash

curl -X POST http://localhost:8000/classify/products \## Instalación y Configuración

  -H 'Content-Type: application/json' \

  -d '{- OpenAI API Key```

    "products": [

      {"text": "yogur natural", "product_id": "SKU001"},### Prerrequisitos

      {"text": "pan integral", "product_id": "SKU002"},

      {"text": "detergente", "product_id": "SKU003"}- Gitmake run

    ]

  }'- Python 3.8+

```- Git

- Clave API de OpenAI

## 📊 APIs Disponibles

## Instalación

| Endpoint | Método | Descripción |

|----------|--------|-------------|```bash

| `/health` | GET | Estado del sistema |# Clonar el repositorio

| `/classify` | POST | Clasificación individual |git clone https://github.com/idourra/skos-mcp-classifier.git

| `/classify/products` | POST | Clasificación múltiple |cd skos-mcp-classifier

| `/export/csv` | POST | Exportar a CSV |

| `/export/excel` | POST | Exportar a Excel |# Instalar dependencias

| `/docs` | GET | Documentación Swagger |make install



## 🌐 URLs del Sistema



- **API REST**: http://localhost:8000# Configurar variables de entorno

- **Documentación**: http://localhost:8000/docs

- **MCP Server**: http://localhost:8080cp .env.example .env# Crear entorno virtual## Docker

- **Health Check**: http://localhost:8000/health

# Edita .env y agrega tu OPENAI_API_KEY

## 🔧 Configuración

```python -m venv .venv```

### 📋 Requisitos



- Python 3.8+

- OpenAI API Key### Configuraciónsource .venv/bin/activate  # Linux/Macdocker build -t skos-mcp-server ./server

- 2GB RAM mínimo

- Puertos 8000 y 8080 disponibles



### 🔑 Variables de EntornoLa taxonomía incluida es la que nos compartiste, en formato JSON-LD dentro de `data/taxonomy.jsonld`.# o en Windows: .venv\Scripts\activatedocker run -p 8080:8080 --rm skos-mcp-server



```bash

# .env

OPENAI_API_KEY=sk-proj-...tu-clave-aqui1. **Edita el archivo `.env`**:```

MCP_SERVER_URL=http://localhost:8080  # Opcional

```



### 🗄️ Base de Datos```bash# Instalar dependencias



El sistema genera automáticamente `skos.sqlite` desde la taxonomía SKOS. Para regenerar:OPENAI_API_KEY=tu_clave_aqui



```bashMCP_SERVER_URL=http://localhost:8080pip install -r server/requirements.txt## Notas

rm -f skos.sqlite

python server/skos_loader.py taxonomies/treew-skos/original.jsonld```

```

pip install requests python-dotenv openai openpyxl- `server/skos_loader.py` detecta automáticamente JSON-LD (`.jsonld`) y TTL/RDF.

## 🧪 Testing

2. **Inicia el servidor MCP**:

### ✅ Health Check

```bash- Endpoints MCP expuestos:

curl http://localhost:8000/health

``````bash



### 🏷️ Clasificación de Pruebamake server# Configurar variables de entorno  - `POST /tools/search_concepts`

```bash

# Casos exitosos (confianza 1.0)```

curl -X POST http://localhost:8000/classify -H 'Content-Type: application/json' -d '{"text": "leche"}'

curl -X POST http://localhost:8000/classify -H 'Content-Type: application/json' -d '{"text": "deportivos"}'cp .env.example .env  - `POST /tools/get_context`

curl -X POST http://localhost:8000/classify -H 'Content-Type: application/json' -d '{"text": "vitaminas"}'

curl -X POST http://localhost:8000/classify -H 'Content-Type: application/json' -d '{"text": "detergente"}'3. **¡Ya está listo para usar!**

```

Edita .env y agrega tu OPENAI_API_KEY

## 📈 Categorías Principales

## Uso Rápido

La taxonomía treew-skos incluye **282 conceptos** organizados jerárquicamente:

- El archivo `server/mcp_tools.json` declara las herramientas MCP

- 🍞 **Alimentos**: Lácteos, carnes, bebidas, etc.- `POST /tools/validate_notation`

- 👔 **Ropa**: Vestimenta y accesorios

- 🏃 **Deportes**: Artículos y equipamiento deportivo### Clasificación Simple

- 💊 **Salud**: Vitaminas, medicamentos, cuidado personal

- 🧴 **Limpieza**: Detergentes y productos de aseo

- 🏠 **Hogar**: Electrodomésticos y accesorios

```python

## 🛠️ Solución de Problemas

from client.classify_standard_api import classify### Configuración> La taxonomía incluida es la que nos compartiste, en formato JSON-LD dentro de `data/taxonomy.jsonld`.

### 🚫 Puerto ocupado

```bash

# Verificar procesos

lsof -i:8000# Clasificar un producto

lsof -i:8080

result = classify("Yogur griego natural sin azúcar")1. **Edita el archivo `.env`**:

# Limpiar procesos

./stop_system.shprint(f"Categoría: {result['category']}")```bash

```

print(f"Confianza: {result['confidence']}%")OPENAI_API_KEY=sk-tu-clave-aqui

### 🗄️ Base de datos corrupta

```bash```MCP_SERVER_URL=http://localhost:8080

# Regenerar base de datos

rm -f skos.sqlite```

python server/skos_loader.py taxonomies/treew-skos/original.jsonld

```### Clasificación con ID/SKU



### 🔑 Error OpenAI2. **Inicia el servidor MCP**:

```bash

# Verificar API key```python

echo $OPENAI_API_KEY# Clasificar producto con ID personalizado

# O revisar archivo .envresult = classify("Aceite de oliva extra virgen", product_id="SKU-12345")

```print(f"ID: {result['product_id']}")

print(f"Categoría: {result['category']}")

## 📚 Documentación Adicional```



- 📖 [Guía de Uso Completa](USAGE_GUIDE.md)Para iniciar el servidor MCP:

- 🔧 [Reporte de Estabilización](SYSTEM_STABILIZATION_REPORT.md)

- 🛠️ [Reporte de Corrección de BD](DATABASE_FIX_REPORT.md)```bash

uvicorn server.main:app --host 0.0.0.0 --port 8080

## 🤝 Contribución```



1. Fork el repositorio3. **¡Ya está listo para usar!**

2. Crear rama: `git checkout -b feature/nueva-funcionalidad`

3. Commit: `git commit -m 'Agregar nueva funcionalidad'`## 📋 Uso

4. Push: `git push origin feature/nueva-funcionalidad`

5. Crear Pull Request### Testing Interactivo



## 📄 Licencia### 1. Clasificación Simple



Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.```bash



## 🏆 Estado del Proyectopython client/test_classifier.py```python



- ✅ **Sistema estable** y completamente funcional```from client.classify_standard_api import classify

- ✅ **API documentada** con Swagger/OpenAPI

- ✅ **Tests validados** en múltiples categorías

- ✅ **Producción ready** con scripts automatizados

### Exportación de Resultados# Sin ID

---

resultado = classify("yogur natural griego")

**Desarrollado con ❤️ usando SKOS, FastAPI y OpenAI**
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

```python

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
