# 🚀 Guía de Uso del Sistema SKOS Classifier

## 📋 Activación del Sistema

### ✅ Activación Automática (Recomendada)
```bash
./start_system.sh
```

### 📋 Activación Manual
```bash
# 1. Activar entorno virtual
source .venv/bin/activate

# 2. Iniciar MCP Server (Terminal 1)
python -m uvicorn server.main:app --host 0.0.0.0 --port 8080 &

# 3. Iniciar API REST (Terminal 2)  
python classification_api.py &
```

## 🛑 Desactivación del Sistema

### ✅ Desactivación Automática (Recomendada)
```bash
./stop_system.sh
```

### 📋 Desactivación Manual
```bash
# Detener procesos específicos
kill <MCP_PID> <API_PID>

# O limpiar todos los procesos relacionados
pkill -f "uvicorn.*server.main"
pkill -f "classification_api.py"
```

## 🧪 Pruebas y Uso

### 🔍 Health Check
```bash
curl http://localhost:8000/health
```

### 🏷️ Clasificación Individual
```bash
curl -X POST http://localhost:8000/classify \
  -H 'Content-Type: application/json' \
  -d '{"text": "leche descremada", "product_id": "SKU001"}'
```

### 📦 Clasificación Múltiple
```bash
curl -X POST http://localhost:8000/classify/products \
  -H 'Content-Type: application/json' \
  -d '{
    "products": [
      {"text": "leche descremada", "product_id": "SKU001"},
      {"text": "pan integral", "product_id": "SKU002"},
      {"text": "detergente", "product_id": "SKU003"}
    ]
  }'
```

## 🌐 URLs de Acceso

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **API REST** | `http://localhost:8000` | API principal de clasificación |
| **API Docs** | `http://localhost:8000/docs` | Documentación interactiva (Swagger) |
| **Health Check** | `http://localhost:8000/health` | Verificación de estado del sistema |
| **MCP Server** | `http://localhost:8080` | Servidor interno SKOS |
| **MCP Docs** | `http://localhost:8080/docs` | Documentación del MCP Server |

## 📊 Endpoints Principales

### 🔍 Clasificación Simple
- **URL**: `POST /classify`
- **Descripción**: Clasifica un producto individual
- **Entrada**: `{"text": "descripción", "product_id": "opcional"}`

### 📦 Clasificación Múltiple  
- **URL**: `POST /classify/products`
- **Descripción**: Clasifica múltiples productos en una sola llamada
- **Entrada**: `{"products": [{"text": "...", "product_id": "..."}]}`

### 📥 Exportación CSV
- **URL**: `POST /export/csv`
- **Descripción**: Clasifica y exporta resultados a CSV
- **Entrada**: `{"products": [...], "filename": "opcional"}`

### 📊 Exportación Excel
- **URL**: `POST /export/excel`  
- **Descripción**: Clasifica y exporta resultados a Excel
- **Entrada**: `{"products": [...], "filename": "opcional"}`

## 🎯 Ejemplos de Respuesta

### ✅ Clasificación Exitosa
```json
{
  "product_id": "SKU001",
  "search_text": "leche descremada",
  "concept_uri": "https://treew.io/taxonomy/concept/111202",
  "prefLabel": "Leches y sustitutos",
  "notation": "111202",
  "level": 1,
  "confidence": 1.0,
  "timestamp": "2025-09-23T15:30:00"
}
```

### ⚠️ Error de Clasificación
```json
{
  "detail": "422: Error en clasificación: No JSON found in response"
}
```

## 🔧 Solución de Problemas

### 🚫 Puerto en uso
```bash
# Verificar qué procesos usan los puertos
lsof -i:8000
lsof -i:8080

# Detener procesos específicos
kill <PID>
```

### 🗄️ Base de datos corrupta
```bash
# Regenerar base de datos
rm -f skos.sqlite
python server/skos_loader.py taxonomies/treew-skos/original.jsonld
```

### 🔑 Error de OpenAI
```bash
# Verificar variable de entorno
echo $OPENAI_API_KEY

# O verificar archivo .env
cat .env | grep OPENAI_API_KEY
```

## 📈 Mejores Prácticas

### ✅ Términos que funcionan bien
- Categorías generales: "alimentos", "ropa", "deportivos"
- Productos específicos con nombres comunes: "leche", "pan", "detergente"

### ⚠️ Términos problemáticos  
- Productos muy específicos: "pelota de fútbol FIFA", "camiseta Nike"
- Marcas comerciales: puede clasificar por categoría general
- Palabras con acentos: usar sin tildes para mejor resultado

### 🎯 Optimización
- Usar términos sin acentos/tildes
- Preferir categorías generales sobre productos específicos
- Verificar confianza (confidence) en respuestas
- Valores cercanos a 1.0 indican alta precisión

---

**Sistema SKOS Classifier v2.0**  
**Última actualización**: Septiembre 2025  
**Estado**: ✅ Completamente operativo