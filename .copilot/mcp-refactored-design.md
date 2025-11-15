# MCP Server - Arquitectura Refactorizada (Hexagonal + DDD)

## 🏗️ Estructura Propuesta

```
server/
├── mcp/                        # 🎯 MCP Server (Puerto de entrada)
│   ├── __init__.py
│   ├── server.py               # FastAPI app MCP
│   ├── tools.py                # Definición de MCP tools
│   ├── resources.py            # Definición de MCP resources
│   └── schemas.py              # Pydantic models para MCP
│
├── domain/                     # 🧠 Capa de Dominio (Lógica de negocio)
│   ├── __init__.py
│   ├── taxonomy_service.py     # Servicio de taxonomías
│   ├── search_service.py       # Servicio de búsqueda
│   ├── classification_service.py # Servicio de clasificación
│   └── models.py               # Modelos de dominio
│
├── adapters/                   # 🔌 Adaptadores (Infraestructura)
│   ├── __init__.py
│   ├── taxonomy_repository.py  # Repositorio de taxonomías
│   ├── embedding_client.py     # Cliente de embeddings
│   └── db_adapter.py           # Adaptador de BD
│
└── config/                     # ⚙️ Configuración
    ├── __init__.py
    ├── settings.py             # Configuración del sistema
    └── policies.py             # Políticas de clasificación
```

## 🎯 MCP Tools - Especificación Completa

### 1. search_taxonomy_concepts
**Descripción:** Buscar conceptos en taxonomías SKOS
```python
{
  "name": "search_taxonomy_concepts",
  "description": "Buscar conceptos SKOS por texto. Retorna conceptos relevantes con sus metadatos.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {"type": "string", "description": "Texto a buscar"},
      "top_k": {"type": "integer", "default": 10, "description": "Número de resultados"},
      "taxonomy_id": {"type": "string", "description": "ID de taxonomía (opcional)"}
    },
    "required": ["query"]
  }
}
```

**Capa de servicio:** `domain/search_service.py::search_concepts()`
- No accede a BD directamente
- Usa `adapters/taxonomy_repository.py`
- Retorna modelos de dominio

### 2. embed_text
**Descripción:** Generar embedding de texto
```python
{
  "name": "embed_text",
  "description": "Generar embedding vectorial de un texto para búsqueda semántica.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "text": {"type": "string", "description": "Texto a convertir en embedding"}
    },
    "required": ["text"]
  }
}
```

**Capa de servicio:** `domain/search_service.py::embed_text()`
- Usa `adapters/embedding_client.py`
- NO expone detalles del modelo

### 3. get_taxonomy_concept
**Descripción:** Obtener detalles de un concepto específico
```python
{
  "name": "get_taxonomy_concept",
  "description": "Obtener información completa de un concepto SKOS por su URI o notation.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "concept_id": {"type": "string", "description": "URI o notation del concepto"},
      "taxonomy_id": {"type": "string", "description": "ID de taxonomía (opcional)"}
    },
    "required": ["concept_id"]
  }
}
```

**Capa de servicio:** `domain/taxonomy_service.py::get_concept()`

### 4. list_taxonomies
**Descripción:** Listar taxonomías disponibles
```python
{
  "name": "list_taxonomies",
  "description": "Obtener lista de taxonomías SKOS disponibles en el sistema.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "active_only": {"type": "boolean", "default": true}
    }
  }
}
```

**Capa de servicio:** `domain/taxonomy_service.py::list_taxonomies()`

### 5. get_taxonomy_metadata
**Descripción:** Obtener metadatos de una taxonomía
```python
{
  "name": "get_taxonomy_metadata",
  "description": "Obtener información detallada de una taxonomía específica.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "taxonomy_id": {"type": "string", "description": "ID de la taxonomía"}
    },
    "required": ["taxonomy_id"]
  }
}
```

**Capa de servicio:** `domain/taxonomy_service.py::get_metadata()`

### 6. classify_text
**Descripción:** Clasificar texto usando taxonomía
```python
{
  "name": "classify_text",
  "description": "Clasificar un texto en conceptos de la taxonomía SKOS.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "text": {"type": "string", "description": "Texto a clasificar"},
      "lang": {"type": "string", "default": "es", "description": "Idioma"},
      "taxonomy_id": {"type": "string", "description": "ID de taxonomía (opcional)"}
    },
    "required": ["text"]
  }
}
```

**Capa de servicio:** `domain/classification_service.py::classify()`
- Integra con OpenAI
- NO expone detalles del modelo
- Retorna solo resultado de clasificación

## 📚 MCP Resources - Especificación Completa

### 1. resource://taxonomy_schema
**Descripción:** Estructura SKOS oficial
```json
{
  "uri": "taxonomy://schema",
  "mimeType": "application/json",
  "description": "Esquema SKOS usado en el proyecto"
}
```

**Contenido estático:**
```json
{
  "name": "SKOS Core Schema",
  "version": "1.0",
  "concepts": {
    "skos:Concept": "Unidad de conocimiento",
    "skos:prefLabel": "Etiqueta preferida",
    "skos:altLabel": "Etiqueta alternativa",
    "skos:broader": "Concepto más general",
    "skos:narrower": "Concepto más específico",
    "skos:notation": "Código identificador"
  },
  "hierarchy_levels": {
    "0": "Raíz",
    "1": "Categoría principal",
    "2": "Subcategoría",
    "3+": "Conceptos específicos"
  }
}
```

### 2. resource://active_taxonomies
**Descripción:** Taxonomías activas
```json
{
  "uri": "taxonomy://active",
  "mimeType": "application/json",
  "description": "Lista de taxonomías activas"
}
```

**Contenido dinámico (generado por servicio):**
- Lista de taxonomías activas
- Metadatos básicos de cada una
- Taxonomía por defecto marcada

### 3. resource://classification_policy
**Descripción:** Políticas de clasificación
```json
{
  "uri": "taxonomy://classification-policy",
  "mimeType": "application/json",
  "description": "Reglas y umbrales de clasificación"
}
```

**Contenido estático:**
```json
{
  "confidence_thresholds": {
    "high": 0.8,
    "medium": 0.6,
    "low": 0.4
  },
  "classification_rules": {
    "prefer_specific_concepts": true,
    "max_alternatives": 3,
    "require_minimum_confidence": 0.4
  },
  "openai_model": "gpt-4o-mini",
  "max_retries": 3,
  "search_top_k": 10
}
```

### 4. resource://project_overview
**Descripción:** Descripción del proyecto
```json
{
  "uri": "taxonomy://project",
  "mimeType": "application/json",
  "description": "Información general del proyecto"
}
```

**Contenido estático:**
```json
{
  "name": "SKOS MCP Classifier",
  "version": "2.0",
  "description": "Sistema de clasificación de productos usando taxonomías SKOS",
  "capabilities": [
    "Búsqueda semántica en taxonomías SKOS",
    "Clasificación inteligente con IA",
    "Soporte multi-taxonomía",
    "Embeddings de texto"
  ],
  "usage": {
    "classification": "Usar classify_text para clasificar productos",
    "search": "Usar search_taxonomy_concepts para buscar conceptos",
    "metadata": "Usar get_taxonomy_metadata para información de taxonomías"
  }
}
```

## 🔄 Flujo de Datos (Hexagonal)

```
┌─────────────────────────────────────────────────┐
│           MCP Tool (Puerto de Entrada)          │
│  ┌───────────────────────────────────────────┐  │
│  │  POST /tools/classify_text                │  │
│  │  Request: {text: "yogur griego"}          │  │
│  └───────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│          Capa de Aplicación (Servicio)          │
│  ┌───────────────────────────────────────────┐  │
│  │  ClassificationService.classify()         │  │
│  │  - Valida entrada                         │  │
│  │  - Ejecuta lógica de negocio              │  │
│  │  - Orquesta repositorios                  │  │
│  └───────────────────────────────────────────┘  │
└─────────────┬────────────────┬──────────────────┘
              │                │
              ▼                ▼
┌──────────────────┐  ┌─────────────────────────┐
│   Repositorio    │  │   Embedding Client      │
│   (Adapter)      │  │   (Adapter)             │
├──────────────────┤  ├─────────────────────────┤
│ - Acceso a BD    │  │ - Cliente OpenAI        │
│ - SQL queries    │  │ - Generación embeddings │
│ - Mapeo datos    │  │                         │
└──────────────────┘  └─────────────────────────┘
       │                      │
       ▼                      ▼
┌──────────────────┐  ┌─────────────────────────┐
│   SQLite DB      │  │   OpenAI API            │
│   (Infra)        │  │   (Infra Externa)       │
└──────────────────┘  └─────────────────────────┘
```

## ✅ Principios Aplicados

### 1. Hexagonal Architecture
- ✅ MCP tools = Puertos de entrada
- ✅ Servicios = Lógica de aplicación
- ✅ Repositorios = Puertos de salida
- ✅ Adapters = Implementaciones de infraestructura

### 2. Domain-Driven Design
- ✅ Servicios de dominio bien definidos
- ✅ Modelos de dominio separados de infraestructura
- ✅ Lenguaje ubicuo (Taxonomy, Concept, Classification)
- ✅ Bounded contexts claros

### 3. Encapsulación
- ✅ NO se expone SQLite
- ✅ NO se expone OpenAI directamente
- ✅ NO se exponen modelos internos
- ✅ Solo se exponen capacidades de alto nivel

### 4. Single Responsibility
- ✅ Cada servicio tiene una responsabilidad
- ✅ Tools solo mapean requests
- ✅ Repositorios solo acceden a datos
- ✅ Servicios solo contienen lógica de negocio

## 📝 Checklist de Implementación

- [ ] Crear estructura de directorios
- [ ] Implementar modelos de dominio
- [ ] Implementar servicios (taxonomy, search, classification)
- [ ] Implementar repositorios (adapters)
- [ ] Crear MCP tools usando servicios
- [ ] Crear MCP resources
- [ ] Configurar FastAPI MCP server
- [ ] Migrar funcionalidad existente
- [ ] Tests unitarios por capa
- [ ] Documentación de APIs
