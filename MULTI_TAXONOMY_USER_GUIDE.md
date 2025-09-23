# 🗂️ Guía del Usuario: Sistema Multi-Taxonomía SKOS

## Descripción General

El sistema SKOS MCP Classifier ahora soporta **múltiples taxonomías**, permitiéndote:

- 📚 **Gestionar múltiples taxonomías** SKOS (TreeW, Google Shopping, Amazon, etc.)
- 🎯 **Seleccionar taxonomía específica** para cada clasificación
- 🔄 **Migrar fácilmente** desde sistema de taxonomía única
- 🛠️ **Administrar taxonomías** vía API REST

## 🚀 Inicio Rápido

### 1. Verificar Taxonomías Disponibles

```python
from client.multi_taxonomy_classify import list_taxonomies

# Mostrar todas las taxonomías disponibles
taxonomies = list_taxonomies()
```

### 2. Clasificar con Taxonomía Por Defecto

```python
from client.multi_taxonomy_classify import classify

# Clasificación usando taxonomía por defecto
result = classify("yogur natural sin azúcar 125g")
print(f"Categoría: {result['prefLabel']}")
print(f"Código: {result['notation']}")
```

### 3. Clasificar con Taxonomía Específica

```python
# Clasificación usando taxonomía específica
result = classify(
    text="yogur natural sin azúcar 125g",
    taxonomy_id="treew-skos"  # ID de taxonomía específica
)
```

### 4. Clasificación en Lote con Taxonomía

```python
from client.multi_taxonomy_classify import classify_batch

products = [
    {"text": "leche descremada 1L", "product_id": "MILK001"},
    {"text": "pan integral 500g", "product_id": "BREAD001"}
]

# Clasificar todos con una taxonomía específica
results = classify_batch(products, taxonomy_id="google-shopping")
```

## 🛠️ Gestión de Taxonomías

### Listar Taxonomías Disponibles

```bash
# Usando la API REST
curl http://localhost:8080/taxonomies/available

# Usando el cliente Python
python -c "from client.multi_taxonomy_classify import list_taxonomies; list_taxonomies()"
```

### Subir Nueva Taxonomía

```bash
# Subir archivo SKOS (JSON-LD, RDF/XML, TTL)
curl -X POST http://localhost:8080/taxonomies/upload \
  -F "file=@mi_taxonomia.jsonld" \
  -F "name=Mi Taxonomía Custom" \
  -F "description=Taxonomía personalizada para productos específicos" \
  -F "language=es" \
  -F "domain=retail"
```

### Activar/Desactivar Taxonomía

```bash
# Activar taxonomía específica
curl -X POST http://localhost:8080/taxonomies/mi-taxonomia/activate

# Establecer como taxonomía por defecto
curl -X POST http://localhost:8080/taxonomies/mi-taxonomia/set-default
```

## 📊 API REST Endpoints

### Gestión de Taxonomías

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/taxonomies/available` | GET | Lista taxonomías disponibles |
| `/taxonomies/upload` | POST | Sube nueva taxonomía SKOS |
| `/taxonomies/{id}/activate` | POST | Activa taxonomía específica |
| `/taxonomies/{id}/deactivate` | POST | Desactiva taxonomía |
| `/taxonomies/{id}/set-default` | POST | Establece como por defecto |
| `/taxonomies/{id}/delete` | DELETE | Elimina taxonomía |

### Clasificación con Taxonomía

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/classify/products?taxonomy=ID` | POST | Clasifica con taxonomía específica |

**Ejemplo:**
```bash
curl -X POST http://localhost:8080/classify/products?taxonomy=treew-skos \
  -H "Content-Type: application/json" \
  -d '{
    "products": [
      {"text": "yogur natural", "product_id": "YOGURT001"}
    ]
  }'
```

## 🔧 Configuración Avanzada

### Variables de Entorno

```bash
# .env
MCP_SERVER_URL=http://localhost:8080
OPENAI_API_KEY=tu_api_key_aqui

# Configuración multi-taxonomía
DEFAULT_TAXONOMY_ID=treew-skos
TAXONOMIES_PATH=./taxonomies/
DATABASE_PATH=./databases/
```

### Estructura de Directorios

```
proyecto/
├── taxonomies/          # Archivos SKOS fuente
│   ├── treew.jsonld
│   ├── google_shopping.jsonld
│   └── amazon_taxonomy.rdf
├── databases/           # Bases de datos SQLite por taxonomía
│   ├── treew-skos.db
│   ├── google-shopping.db
│   └── amazon-taxonomy.db
└── config/
    └── taxonomy_metadata.json
```

## 🧪 Testing y Validación

### Ejecutar Pruebas Completas

```bash
# Prueba automática del sistema
python test_multi_taxonomy.py --test

# Demo interactivo
python test_multi_taxonomy.py --demo
```

### Validar Taxonomía Nueva

```python
from utils.taxonomy_manager import TaxonomyManager

manager = TaxonomyManager()

# Validar archivo SKOS antes de subir
validation_result = manager.validate_skos_file("mi_taxonomia.jsonld")
if validation_result["valid"]:
    print("✅ Taxonomía válida")
else:
    print(f"❌ Errores: {validation_result['errors']}")
```

## 📈 Casos de Uso

### 1. E-commerce Multi-Regional
```python
# Clasificar productos para diferentes mercados
result_us = classify("organic yogurt", taxonomy_id="google-shopping-us")
result_es = classify("yogur orgánico", taxonomy_id="treew-skos-es")
```

### 2. Migración de Sistemas Legacy
```python
# Comparar clasificaciones entre taxonomías
old_result = classify(product, taxonomy_id="legacy-taxonomy")
new_result = classify(product, taxonomy_id="new-taxonomy")

# Análisis de migración
migration_score = compare_classifications(old_result, new_result)
```

### 3. A/B Testing de Taxonomías
```python
import random

# Selección aleatoria para A/B testing
taxonomy_id = random.choice(["taxonomy-a", "taxonomy-b"])
result = classify(product, taxonomy_id=taxonomy_id)

# Tracking de performance por taxonomía
track_classification_performance(result, taxonomy_id)
```

## 🔍 Troubleshooting

### Problemas Comunes

**1. "Taxonomía no disponible"**
```python
# Verificar taxonomías activas
from client.multi_taxonomy_classify import get_available_taxonomies
available = get_available_taxonomies()
print("Taxonomías activas:", [t["id"] for t in available["taxonomies"]])
```

**2. "Error de conexión MCP"**
```bash
# Verificar que el servidor esté ejecutándose
curl http://localhost:8080/health

# Verificar configuración
echo $MCP_SERVER_URL
```

**3. "Formato SKOS inválido"**
```python
# Validar archivo antes de subir
from utils.taxonomy_manager import TaxonomyManager
manager = TaxonomyManager()
validation = manager.validate_skos_file("archivo.jsonld")
```

### Logs y Debug

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Las llamadas a classify mostrarán logs detallados
result = classify("producto test", taxonomy_id="debug-taxonomy")
```

## 🚀 Próximas Características

- 🔄 **Sincronización automática** de taxonomías
- 📊 **Métricas de performance** por taxonomía
- 🌐 **Soporte multi-idioma** mejorado
- 🧠 **Recomendaciones inteligentes** de taxonomía
- 🔗 **Mapping automático** entre taxonomías

## 📞 Soporte

Para problemas o sugerencias:

1. 🐛 **Issues**: Reportar en el repositorio GitHub
2. 📖 **Documentación**: Ver `MULTI_TAXONOMY_DESIGN.md` para detalles técnicos
3. 🧪 **Testing**: Ejecutar `python test_multi_taxonomy.py` para diagnóstico
4. 💬 **Comunidad**: Participar en discusiones del proyecto

---

**¡El sistema multi-taxonomía está listo para usar! 🎉**

Comienza subiendo tu primera taxonomía personalizada y experimenta con clasificaciones específicas por dominio.