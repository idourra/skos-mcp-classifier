# 🗂️ Sistema de Múltiples Taxonomías SKOS

## 📋 Objetivo

Permitir que el sistema maneje múltiples taxonomías SKOS, donde los usuarios pueden:
1. **Subir nuevas taxonomías** en formato SKOS normalizado
2. **Seleccionar taxonomía** para clasificación específica
3. **Gestionar taxonomías** (activar/desactivar, metadatos)
4. **Clasificar con taxonomía específica** a través de API y cliente

## 🏗️ Arquitectura Propuesta

### 1. Estructura de Datos

```
taxonomies/
├── metadata.json          # Registro de todas las taxonomías
├── treew-skos/           # Taxonomía actual (renombrada)
│   ├── taxonomy.sqlite   # Base de datos específica
│   ├── metadata.json     # Metadatos de esta taxonomía
│   └── original.jsonld   # Archivo original
├── google-shopping/      # Nueva taxonomía ejemplo
│   ├── taxonomy.sqlite
│   ├── metadata.json
│   └── original.jsonld
└── amazon-categories/    # Otra taxonomía ejemplo
    ├── taxonomy.sqlite
    ├── metadata.json
    └── original.jsonld
```

### 2. Metadatos de Taxonomía

```json
{
  "id": "treew-skos",
  "name": "TreeW SKOS Food Taxonomy",
  "description": "Taxonomía SKOS para productos alimentarios",
  "version": "1.0.0",
  "provider": "TreeW",
  "language": "es",
  "domain": "food",
  "concepts_count": 2547,
  "created_at": "2025-09-23T10:00:00Z",
  "updated_at": "2025-09-23T10:00:00Z",
  "is_active": true,
  "is_default": true,
  "file_hash": "sha256:...",
  "file_size_mb": 2.1,
  "schema_version": "1.0"
}
```

### 3. APIs Nuevas

#### Gestión de Taxonomías
- `POST /taxonomies/upload` - Subir nueva taxonomía
- `GET /taxonomies` - Listar taxonomías disponibles
- `GET /taxonomies/{taxonomy_id}` - Detalles de taxonomía
- `PUT /taxonomies/{taxonomy_id}/activate` - Activar/desactivar
- `PUT /taxonomies/{taxonomy_id}/default` - Establecer como default
- `DELETE /taxonomies/{taxonomy_id}` - Eliminar taxonomía

#### Clasificación con Taxonomía
- `POST /classify/products?taxonomy={id}` - Clasificar con taxonomía específica
- `POST /classify/batch?taxonomy={id}` - Lote con taxonomía específica

### 4. Modificaciones MCP Server

```python
# Nuevo sistema de conexión dinámica
class TaxonomyManager:
    def __init__(self):
        self.taxonomies = {}
        self.load_taxonomies()
    
    def load_taxonomies(self):
        # Cargar metadatos de todas las taxonomías
        pass
    
    def get_connection(self, taxonomy_id: str):
        # Retornar conexión específica a taxonomía
        pass
    
    def search_concepts(self, query: str, taxonomy_id: str = None):
        # Buscar en taxonomía específica o default
        pass
```

## 🔄 Flujo de Implementación

### Fase 1: Infraestructura Base
1. **Migrar taxonomía actual** a nueva estructura
2. **Crear TaxonomyManager** para gestión centralizada
3. **Actualizar conexiones** de base de datos

### Fase 2: APIs de Gestión
1. **Endpoint de upload** con validación SKOS
2. **Endpoints de gestión** (listar, activar, etc.)
3. **Validación y procesamiento** de taxonomías

### Fase 3: Clasificación Multi-Taxonomía
1. **Modificar clasificación** para aceptar parámetro taxonomy
2. **Actualizar MCP tools** para manejar múltiples DBs
3. **Cliente actualizado** con selección de taxonomía

### Fase 4: Testing y Validación
1. **Tests comprehensivos** para cada taxonomía
2. **Validación de accuracy** cross-taxonomy
3. **Tests de performance** con múltiples taxonomías

## 📝 Especificación Técnica

### Upload de Taxonomía

```json
POST /taxonomies/upload
Content-Type: multipart/form-data

{
  "file": "taxonomy.jsonld",           # Archivo SKOS
  "metadata": {
    "id": "google-shopping",
    "name": "Google Shopping Categories",
    "description": "Taxonomía de Google Shopping",
    "provider": "Google",
    "language": "en",
    "domain": "general"
  }
}
```

### Respuesta de Upload

```json
{
  "success": true,
  "taxonomy_id": "google-shopping",
  "message": "Taxonomía procesada exitosamente",
  "stats": {
    "concepts_processed": 5127,
    "concepts_imported": 5127,
    "processing_time_seconds": 12.5
  },
  "validation": {
    "skos_valid": true,
    "warnings": [],
    "errors": []
  }
}
```

### Clasificación con Taxonomía

```json
POST /classify/products?taxonomy=google-shopping

{
  "products": [
    {
      "text": "organic greek yogurt 150g",
      "product_id": "YOGURT001"
    }
  ]
}
```

## 🔧 Componentes a Desarrollar

### 1. `utils/taxonomy_manager.py`
- Gestión de múltiples taxonomías
- Validación de archivos SKOS
- Procesamiento e importación

### 2. `server/taxonomy_endpoints.py`
- APIs de gestión de taxonomías
- Upload y validación
- Activación/desactivación

### 3. `server/multi_db_manager.py`
- Conexiones dinámicas a bases de datos
- Pool de conexiones por taxonomía
- Fallback a taxonomía default

### 4. `client/multi_taxonomy_client.py`
- Cliente con selección de taxonomía
- Listado de taxonomías disponibles
- Clasificación con taxonomía específica

## 🚀 Beneficios

1. **Flexibilidad**: Usar diferentes taxonomías según necesidad
2. **Escalabilidad**: Agregar nuevas taxonomías sin código
3. **Especialización**: Taxonomías específicas por dominio/región
4. **Compatibilidad**: Mantener funcionalidad actual como default
5. **Validación**: Asegurar calidad de taxonomías importadas

## 🧪 Testing Strategy

### Tests Unitarios
- Validación de formato SKOS
- Procesamiento de taxonomías
- Gestión de metadatos

### Tests de Integración
- Upload completo de taxonomía
- Clasificación cross-taxonomy
- Performance con múltiples DBs

### Tests de Carga
- Múltiples taxonomías simultáneas
- Upload de taxonomías grandes
- Clasificación masiva multi-taxonomy

---

**Nota**: Este diseño mantiene compatibilidad total con la implementación actual, usando la taxonomía TreeW como default cuando no se especifica taxonomía.