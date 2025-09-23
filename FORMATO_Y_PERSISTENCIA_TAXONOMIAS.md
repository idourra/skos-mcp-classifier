# 📋 FORMATO Y PERSISTENCIA DE TAXONOMÍAS SKOS

## 1. 📁 FORMATOS EXIGIDOS PARA UPLOAD

### 🔧 Formatos Soportados

El sistema acepta **4 formatos estándar RDF/SKOS**:

| Formato | Extensión | MIME Type | Descripción |
|---------|-----------|-----------|-------------|
| **JSON-LD** | `.jsonld` | `application/ld+json` | ✅ **RECOMENDADO** - Más legible |
| **RDF/XML** | `.rdf`, `.xml` | `application/rdf+xml` | ✅ Estándar W3C |
| **Turtle** | `.ttl` | `text/turtle` | ✅ Compacto y legible |
| **N-Triples** | `.nt` | `application/n-triples` | ✅ Simple línea por línea |

### 📋 Requisitos de Formato OBLIGATORIOS

#### 🏗️ **1. Estructura SKOS Compliant**
```jsonld
{
  "@context": {
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "dcterms": "http://purl.org/dc/terms/"
  },
  "@graph": [
    {
      "@type": "skos:ConceptScheme",
      "@id": "http://ejemplo.com/taxonomia",
      "dcterms:title": "Mi Taxonomía"
    },
    {
      "@type": "skos:Concept",
      "@id": "http://ejemplo.com/concept/1",
      "skos:inScheme": {"@id": "http://ejemplo.com/taxonomia"},
      "skos:prefLabel": "Concepto Principal"
    }
  ]
}
```

#### 📊 **2. Requisitos de Cantidad Mínima**
- **≥ 20 conceptos** SKOS con etiquetas válidas
- **≥ 1 ConceptScheme** como raíz de la taxonomía
- **≥ 60% calidad** para ser útil en clasificación

#### 🔗 **3. Elementos SKOS Obligatorios**
- `skos:prefLabel` en cada concepto
- `skos:inScheme` vinculando conceptos al esquema
- `skos:broader/narrower` para jerarquías
- URIs únicos para cada concepto

#### 🌟 **4. Características de Enriquecimiento (Recomendadas)**
- `skos:definition` - Definiciones descriptivas
- `skos:altLabel` - Etiquetas alternativas/sinónimos
- `skos:notation` - Códigos o identificadores
- `skos:related` - Relaciones semánticas
- `skos:example` - Ejemplos de uso

### ⚠️ Validaciones Automáticas

```python
# El sistema rechaza automáticamente taxonomías que:
❌ No son SKOS compliant
❌ Tienen < 20 conceptos
❌ Calidad < 60%
❌ Contienen ciclos en jerarquías
❌ Tienen conceptos huérfanos sin conexión
❌ Usan formatos no soportados
```

## 2. 🏛️ ARQUITECTURA DE PERSISTENCIA

### 📂 Estructura de Directorios

```
taxonomies/
├── metadata.json              # 📋 Registro global de taxonomías
├── treew-skos/               # 📁 Taxonomía individual
│   ├── original.jsonld       # 🔄 Archivo original subido
│   ├── taxonomy.sqlite       # 🗄️ BD optimizada para búsqueda
│   └── metadata.json         # 📊 Metadatos específicos
├── mi-taxonomia-retail/      # 📁 Otra taxonomía
│   ├── original.rdf
│   ├── taxonomy.sqlite
│   └── metadata.json
└── taxonomia-medicina/       # 📁 Especializada
    ├── original.ttl
    ├── taxonomy.sqlite
    └── metadata.json
```

### 🔑 Sistema de Identificación Única

#### **1. ID de Taxonomía**
```python
taxonomy_id = "mi-taxonomia-retail"  # Único en el sistema
```

#### **2. Hash de Integridad**
```python
file_hash = "sha256:45d5d8d1a30144b00a434d6eb19b0ca8a9574adcf69bee20ef498ae5797a7735"
```

#### **3. Versionado Semántico**
```python
version = "2.1.0"  # Major.Minor.Patch
```

### 📋 Metadatos de Persistencia

#### **metadata.json Global**
```json
{
  "version": "1.0",
  "updated_at": "2025-09-23T14:09:48.111905",
  "taxonomies_count": 3,
  "taxonomies": {
    "treew-skos": {
      "id": "treew-skos",
      "name": "TreeW SKOS Food Taxonomy",
      "description": "Taxonomía SKOS para productos alimentarios",
      "version": "1.0.0",
      "provider": "TreeW",
      "language": "es",
      "domain": "food",
      "created_at": "2025-09-23T14:09:48.111395",
      "updated_at": "2025-09-23T14:09:48.111408",
      "is_active": true,
      "is_default": true,
      "file_hash": "sha256:45d5d8d1a30144b00a434d6eb19b0ca8a9574adcf69bee20ef498ae5797a7735",
      "file_size_mb": 0.77,
      "schema_version": "1.0",
      "concepts_count": 1247,
      "quality_score": 0.85,
      "compliance_level": "very_good"
    }
  }
}
```

#### **metadata.json Individual**
```json
{
  "taxonomy_id": "mi-taxonomia-retail",
  "processing_stats": {
    "concepts_processed": 456,
    "relationships_created": 892,
    "labels_indexed": 1203,
    "processing_time_seconds": 2.45
  },
  "validation_results": {
    "skos_compliant": true,
    "quality_score": 0.72,
    "compliance_level": "good",
    "enrichment_features": [
      "Rich definitions",
      "Alternative labels",
      "Notation codes"
    ]
  },
  "usage_statistics": {
    "classifications_count": 1205,
    "last_used": "2025-09-23T15:30:00.000Z",
    "avg_response_time_ms": 45
  }
}
```

### 🗄️ Base de Datos SQLite Individual

Cada taxonomía tiene su propia BD optimizada:

```sql
-- Estructura de taxonomy.sqlite
CREATE TABLE concepts (
    id TEXT PRIMARY KEY,
    uri TEXT UNIQUE,
    pref_label TEXT,
    definition TEXT,
    notation TEXT,
    scheme_id TEXT
);

CREATE TABLE labels (
    concept_id TEXT,
    label TEXT,
    label_type TEXT,  -- 'pref', 'alt', 'hidden'
    language TEXT
);

CREATE TABLE relationships (
    subject_id TEXT,
    predicate TEXT,   -- 'broader', 'narrower', 'related'
    object_id TEXT
);

CREATE TABLE hierarchy (
    concept_id TEXT,
    parent_id TEXT,
    level INTEGER,
    path TEXT         -- Para búsquedas jerárquicas
);

-- Índices para rendimiento
CREATE INDEX idx_labels_text ON labels(label);
CREATE INDEX idx_concepts_pref ON concepts(pref_label);
CREATE INDEX idx_hierarchy_level ON hierarchy(level);
```

## 3. 🔄 FLUJO DE INTEGRACIÓN

### **Paso 1: Upload con Validación**
```bash
curl -X POST "http://localhost:8080/taxonomies/upload" \
  -F "file=@mi_taxonomia.jsonld" \
  -F 'metadata={
    "id": "retail-taxonomy-v2",
    "name": "Retail Products Taxonomy",
    "description": "Clasificación para productos retail",
    "provider": "MiEmpresa",
    "language": "es",
    "domain": "retail",
    "version": "2.0.0"
  }'
```

### **Paso 2: Procesamiento Automático**
```python
# 1. Validación SKOS rigurosa
validation = validate_skos_file(file_path)
if not validation["valid"]:
    raise ValueError("Taxonomía rechazada")

# 2. Creación de directorio único
taxonomy_dir = f"taxonomies/{taxonomy_id}/"

# 3. Almacenamiento archivo original
shutil.copy(file_path, f"{taxonomy_dir}/original.jsonld")

# 4. Procesamiento a SQLite optimizada
process_taxonomy_to_sqlite(original_file, db_path)

# 5. Actualización metadatos globales
update_global_metadata(taxonomy_id, metadata)
```

### **Paso 3: Activación y Uso**
```python
# Listar taxonomías disponibles
taxonomies = list_taxonomies()

# Activar taxonomía específica
activate_taxonomy("retail-taxonomy-v2")

# Clasificar con taxonomía específica
result = classify(
    text="smartphone samsung galaxy",
    taxonomy_id="retail-taxonomy-v2"
)
```

## 4. 🎯 GESTIÓN DE ESTADO

### **Estado de Taxonomías**
```python
# Estados posibles
STATES = {
    "active": True,      # ✅ Lista para clasificación
    "inactive": False,   # ⏸️ Disponible pero no activa
    "default": True,     # 🏠 Taxonomía por defecto
    "processing": True,  # ⏳ Siendo procesada
    "error": False       # ❌ Error en validación
}
```

### **Garantías del Sistema**
- **Siempre hay una taxonomía por defecto activa**
- **No se pueden eliminar taxonomías en uso**
- **Rollback automático si upload falla**
- **Validación antes de activación**

### **Selección Dinámica**
```python
# El usuario especifica qué taxonomía usar
classify(text="producto", taxonomy_id="retail-taxonomy-v2")
classify(text="comida", taxonomy_id="treew-skos")
classify(text="medicina", taxonomy_id="pharma-taxonomy")

# Respuesta incluye taxonomía usada
{
  "classification": "Electronics > Smartphones",
  "confidence": 0.95,
  "taxonomy_used": "retail-taxonomy-v2",  # ✅ Transparencia total
  "taxonomy_version": "2.0.0"
}
```

## 5. 🚀 VENTAJAS DE ESTA ARQUITECTURA

### ✅ **Escalabilidad**
- Taxonomías independientes en paralelo
- BD optimizada por dominio
- Sin límite en cantidad de taxonomías

### ✅ **Integridad**
- Validación SKOS rigurosa antes de persistir
- Hash para detectar cambios
- Metadatos de auditoría completos

### ✅ **Performance**
- SQLite optimizada por taxonomía
- Índices específicos para búsqueda
- Carga bajo demanda

### ✅ **Flexibilidad**
- Soporte multi-formato (JSON-LD, RDF, TTL)
- Metadatos extensibles
- Versionado granular

### ✅ **Transparencia**
- Cada clasificación especifica qué taxonomía usa
- Estadísticas de uso por taxonomía
- Trazabilidad completa

**🎯 Esta arquitectura garantiza que solo taxonomías SKOS de alta calidad persistan en el sistema, mientras permite gestión flexible y transparente de múltiples dominios de clasificación.**