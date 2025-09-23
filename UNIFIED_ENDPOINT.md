# Endpoint Unificado de Clasificación

## Descripción

El nuevo endpoint `/classify/products` unifica la clasificación de productos en una sola llamada, permitiendo clasificar **1 o N productos** con la misma interfaz. Esta simplificación mejora la experiencia del desarrollador y la consistencia de la API.

## Endpoint Principal

### `POST /classify/products`

**Descripción**: Clasifica uno o múltiples productos usando taxonomía SKOS en una sola llamada.

**Características**:
- ✅ Acepta array de 1 o N productos 
- ✅ Respuesta siempre en formato array consistente
- ✅ Incluye tiempo de procesamiento y estadísticas
- ✅ Manejo robusto de errores por producto
- ✅ Validación de entrada completa

## Formato de Petición

```json
{
  "products": [
    {
      "text": "descripción del producto",
      "product_id": "SKU_opcional"
    }
  ]
}
```

### Campos

- **`products`** (array, requerido): Lista de productos a clasificar
  - **`text`** (string, requerido): Descripción del producto
  - **`product_id`** (string, opcional): ID/SKU del producto

### Validaciones

- ✅ Array `products` debe tener al menos 1 elemento
- ✅ Campo `text` es requerido y no puede estar vacío
- ✅ Campo `product_id` es opcional

## Formato de Respuesta

```json
{
  "total": 3,
  "successful": 2,
  "failed": 1,
  "results": [
    {
      "index": 0,
      "product_id": "SKU001",
      "search_text": "leche descremada",
      "concept_uri": "https://treew.io/taxonomy/concept/111202",
      "prefLabel": "Leches y sustitutos",
      "notation": "111202",
      "level": 1,
      "confidence": 1.0,
      "status": "success",
      "timestamp": "2025-09-23T11:30:00.000Z"
    }
  ],
  "processing_time_seconds": 4.21,
  "timestamp": "2025-09-23T11:30:00.000Z"
}
```

### Campos de Respuesta

- **`total`**: Número total de productos procesados
- **`successful`**: Productos clasificados exitosamente  
- **`failed`**: Productos que fallaron en la clasificación
- **`results`**: Array con resultados detallados
- **`processing_time_seconds`**: Tiempo total de procesamiento
- **`timestamp`**: Timestamp del procesamiento

### Estados de Resultado

Cada elemento en `results` puede tener uno de estos estados:

- **`success`**: Clasificación exitosa
- **`error`**: Error en la clasificación (respuesta válida del clasificador con error)
- **`exception`**: Excepción durante el procesamiento

## Ejemplos de Uso

### 1. Clasificar UN producto

```bash
curl -X POST "http://localhost:8000/classify/products" \
  -H "Content-Type: application/json" \
  -d '{
    "products": [
      {
        "text": "leche descremada",
        "product_id": "DAIRY_001"
      }
    ]
  }'
```

### 2. Clasificar MÚLTIPLES productos

```bash
curl -X POST "http://localhost:8000/classify/products" \
  -H "Content-Type: application/json" \
  -d '{
    "products": [
      {
        "text": "arroz blanco",
        "product_id": "GRAIN_001"
      },
      {
        "text": "pollo congelado", 
        "product_id": "MEAT_001"
      },
      {
        "text": "yogurt natural",
        "product_id": "DAIRY_002"
      }
    ]
  }'
```

### 3. Con JavaScript/TypeScript

```typescript
const response = await fetch('http://localhost:8000/classify/products', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    products: [
      { text: 'pan integral', product_id: 'BREAD_001' },
      { text: 'aceite de oliva', product_id: 'OIL_001' }
    ]
  })
});

const result = await response.json();
console.log(`Clasificados: ${result.successful}/${result.total}`);
```

### 4. Con Python

```python
import requests

payload = {
    "products": [
        {"text": "queso manchego", "product_id": "CHEESE_001"},
        {"text": "tomate fresco", "product_id": "VEG_001"}
    ]
}

response = requests.post(
    "http://localhost:8000/classify/products",
    json=payload
)

result = response.json()
print(f"Procesados: {result['total']}, Exitosos: {result['successful']}")

for item in result['results']:
    if item['status'] == 'success':
        print(f"✅ {item['search_text']} → {item['prefLabel']}")
    else:
        print(f"❌ {item['search_text']} → Error: {item['error']}")
```

## Migración desde Endpoints Antiguos

### Desde `/classify` (producto individual)

**Antes:**
```json
POST /classify
{
  "text": "leche descremada",
  "product_id": "DAIRY_001"
}
```

**Ahora:**
```json
POST /classify/products
{
  "products": [
    {
      "text": "leche descremada",
      "product_id": "DAIRY_001"
    }
  ]
}
```

### Desde `/classify/batch` (múltiples productos)

**Antes:**
```json
POST /classify/batch
{
  "products": [
    {"text": "arroz", "product_id": "001"},
    {"text": "pollo", "product_id": "002"}
  ]
}
```

**Ahora:**
```json
POST /classify/products
{
  "products": [
    {"text": "arroz", "product_id": "001"},
    {"text": "pollo", "product_id": "002"}
  ]
}
```

## Ventajas del Endpoint Unificado

1. **🎯 Simplicidad**: Un solo endpoint para todos los casos
2. **🔄 Consistencia**: Misma interfaz para 1 o N productos
3. **📊 Información Rica**: Estadísticas y tiempos de procesamiento
4. **🛡️ Robusto**: Manejo individual de errores por producto
5. **⚡ Performance**: Procesamiento optimizado en lote
6. **📖 Claridad**: Documentación y ejemplos unificados

## Compatibilidad

- ✅ Los endpoints antiguos (`/classify`, `/classify/batch`) siguen funcionando
- ⚠️ Están marcados como **DEPRECATED** en la documentación
- 🎯 Se recomienda migrar al nuevo endpoint `/classify/products`
- 📅 Los endpoints antiguos se mantendrán por compatibilidad hacia atrás

## Testing

Ejecuta las pruebas del endpoint:

```bash
python test_unified_endpoint.py
```

Este script prueba:
- Clasificación de 1 producto
- Clasificación de múltiples productos  
- Validación de array vacío
- Manejo de datos inválidos
- Documentación de la API

## Performance

- **Producto individual**: ~4 segundos
- **5 productos**: ~25 segundos  
- **Escalabilidad**: Procesamiento secuencial optimizado
- **Memoria**: Uso eficiente sin almacenamiento innecesario

El endpoint está optimizado para casos de uso reales manteniendo balance entre performance y usabilidad.