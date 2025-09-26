# 📖 SKOS MCP Classifier - Documentación Completa v3.0

## 🌟 Resumen Ejecutivo

El **SKOS MCP Classifier** es un sistema de clasificación inteligente que utiliza taxonomías SKOS (Simple Knowledge Organization System) y la API de OpenAI para proporcionar clasificaciones precisas y contextuales de productos. La versión 3.0 introduce una **arquitectura unificada** que mantiene compatibilidad total con versiones anteriores mientras añade capacidades avanzadas de procesamiento modular.

---

## 🏗️ Arquitectura del Sistema

### **Arquitectura Unificada v3.0**
```
┌─────────────────────────────────────────────────────────────────┐
│                    🌐 API LAYER                                  │
├─────────────────────────────────────────────────────────────────┤
│  unified_api.py (v3.0)          │  classification_api.py (v2.x)  │
│  • Compatibilidad v2.x          │  • API Legacy                  │
│  • Nuevas características       │  • Endpoints clásicos          │
│  • Procesamiento modular        │  • Funcionalidad completa      │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                   🔄 CORE PROCESSING LAYER                      │
├─────────────────────────────────────────────────────────────────┤
│  📥 DataGateway              │  ⚙️ ProcessingPipeline           │
│  • Unificación de fuentes   │  • Orquestación de flujos       │
│  • Validación de entrada    │  • Control de procesamiento     │
│  • Normalización de datos   │  • Gestión de errores           │
├─────────────────────────────────────────────────────────────────┤
│  📤 OutputManager           │  📁 FileManager                  │
│  • Formateo de salida       │  • Gestión de archivos          │
│  • Múltiples formatos       │  • Operaciones I/O               │
│  • Entrega estructurada     │  • Manejo de temporales         │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    🔗 INTEGRATION LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  🤖 MCP Server              │  🧠 OpenAI Integration           │
│  • Puerto 8080              │  • GPT-4o-mini                   │
│  • Protocolo MCP            │  • Function Calling              │
│  • Taxonomías SKOS          │  • Clasificación contextual      │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     💾 DATA LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  🗄️ SQLite Database         │  📚 SKOS Taxonomies              │
│  • Almacenamiento local     │  • 282 conceptos cargados        │
│  • Caché de taxonomías      │  • Estructura semántica          │
│  • Metadatos del sistema    │  • Relaciones jerárquicas        │
└─────────────────────────────────────────────────────────────────┘
```

### **Componentes Principales**

#### 🔄 **Core Modules**
- **`DataGateway`**: Punto de entrada unificado para todos los tipos de datos
- **`ProcessingPipeline`**: Orquestador central del flujo de procesamiento
- **`OutputManager`**: Gestor de formatos y entrega de resultados
- **`FileManager`**: Administrador de operaciones de archivo

#### 🌐 **API Layer**
- **`unified_api.py`**: Nueva API v3.0 con arquitectura modular
- **`classification_api.py`**: API v2.x mantenida para compatibilidad

#### 🔗 **Integration Layer**
- **MCP Server**: Servidor de protocolo MCP en puerto 8080
- **OpenAI Integration**: Integración con GPT-4o-mini para clasificación

---

## 🚀 Inicio Rápido

### **1. Activación del Sistema**
```bash
# Script optimizado (recomendado)
./start_system_optimized.sh

# Script tradicional
./start_system.sh
```

### **2. Verificación del Sistema**
```bash
# Verificar estado
curl http://localhost:8000/health

# Ver documentación interactiva
open http://localhost:8000/docs
```

### **3. Detención del Sistema**
```bash
# Script optimizado
./stop_system_optimized.sh

# Script tradicional
./stop_system.sh
```

---

## 📡 Endpoints Disponibles

### **🔗 Endpoints Principales**

| Endpoint | Método | Versión | Descripción |
|----------|--------|---------|-------------|
| `/health` | GET | v2.x/v3.0 | Estado del sistema |
| `/docs` | GET | v2.x/v3.0 | Documentación interactiva |
| `/classify` | POST | v2.x/v3.0 | Clasificación individual |
| `/classify/products` | POST | v2.x/v3.0 | Clasificación por lotes |
| `/classify/file` | POST | v3.0 | Clasificación desde archivo |
| `/classify/unified` | POST | v3.0 | Endpoint unificado |

### **📊 Endpoints de Gestión (v3.0)**

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/system/status` | GET | Estado detallado del sistema |
| `/system/metrics` | GET | Métricas de rendimiento |
| `/taxonomies` | GET | Taxonomías disponibles |
| `/taxonomies/{id}` | GET | Detalles de taxonomía específica |

---

## 🔧 Configuración del Sistema

### **Archivo `config.yaml`**
```yaml
# Configuración principal del sistema
system:
  name: "SKOS MCP Classifier"
  version: "3.0.0"

api:
  host: "0.0.0.0"
  port: 8000

mcp:
  host: "0.0.0.0"
  port: 8080

openai:
  model: "gpt-4o-mini-2024-07-18"
  max_tokens: 4096
  temperature: 0.1
```

### **Variables de Entorno**
```bash
export OPENAI_API_KEY="your-api-key-here"
export PYTHONPATH="/workspaces/skos-mcp-classifier:$PYTHONPATH"
```

---

## 💻 Uso del Sistema

### **1. Clasificación Individual**
```python
import requests

# Clasificar un producto individual
response = requests.post("http://localhost:8000/classify", json={
    "product": "Manzana orgánica de Asturias",
    "taxonomy_id": "treew-skos"
})

print(response.json())
```

### **2. Clasificación por Lotes**
```python
# Clasificar múltiples productos
products = [
    "Aceite de oliva virgen extra",
    "Queso manchego curado",
    "Pan integral de centeno"
]

response = requests.post("http://localhost:8000/classify/products", json={
    "products": products,
    "taxonomy_id": "treew-skos"
})
```

### **3. Clasificación desde Archivo (v3.0)**
```python
# Subir y clasificar archivo CSV
with open("productos.csv", "rb") as f:
    response = requests.post(
        "http://localhost:8000/classify/file",
        files={"file": f},
        data={"taxonomy_id": "treew-skos"}
    )
```

---

## 📋 Formatos de Entrada y Salida

### **Entrada - Producto Individual**
```json
{
    "product": "string",
    "taxonomy_id": "treew-skos",
    "include_confidence": true,
    "include_reasoning": true
}
```

### **Salida - Clasificación**
```json
{
    "classification": {
        "product": "Manzana orgánica de Asturias",
        "taxonomy_id": "treew-skos",
        "skos_concept": "https://example.org/food-taxonomy/apple",
        "preferred_label": "Apple",
        "confidence": 0.95,
        "reasoning": "El producto es claramente una manzana...",
        "broader_concepts": ["Fruit", "Food"],
        "narrower_concepts": [],
        "related_concepts": ["Organic", "Regional"]
    },
    "metadata": {
        "processing_time": 0.45,
        "api_version": "3.0",
        "timestamp": "2024-01-15T10:30:00Z"
    }
}
```

### **Formatos de Archivo Soportados**
- **CSV**: Columnas con nombres de productos
- **JSON**: Arrays o objetos con productos
- **TXT**: Una línea por producto
- **Excel**: Hojas de cálculo con columnas de productos

---

## 📊 Taxonomías Disponibles

### **TreeW SKOS (Por Defecto)**
- **ID**: `treew-skos`
- **Conceptos**: 282 términos de alimentos
- **Estructura**: Jerárquica con relaciones semánticas
- **Idiomas**: Español, Inglés

### **TreeW Best (Mejorada)**
- **ID**: `treew-best`
- **Conceptos**: Taxonomía enriquecida y revisada
- **Estándar**: Compatible con W3C SKOS
- **Características**: Relaciones extendidas

---

## 🔍 Monitoreo y Logs

### **Ubicaciones de Logs**
```
logs/
├── main-api.log          # API principal
├── mcp-server.log        # Servidor MCP
└── system.log            # Logs del sistema
```

### **Monitoreo en Tiempo Real**
```bash
# Logs API principal
tail -f logs/main-api.log

# Logs MCP Server
tail -f logs/mcp-server.log

# Todos los logs
tail -f logs/*.log
```

### **Métricas del Sistema**
```bash
# Estado del sistema
curl http://localhost:8000/system/status

# Métricas de rendimiento
curl http://localhost:8000/system/metrics
```

---

## 🧪 Testing

### **Ejecutar Tests**
```bash
# Todos los tests
pytest

# Test específico
pytest test_unified_architecture.py

# Con cobertura
pytest --cov=core/
```

### **Tests Disponibles**
- **`test_unified_architecture.py`**: Tests de arquitectura unificada
- **`test_classifier.py`**: Tests de clasificación
- **`test_api_cost_tracking.py`**: Tests de costos
- **`test_multi_taxonomy.py`**: Tests multi-taxonomía

---

## 🛠️ Desarrollo

### **Estructura del Proyecto**
```
skos-mcp-classifier/
├── core/                    # Módulos centrales v3.0
│   ├── data_gateway.py     # Gateway de datos
│   ├── processing_pipeline.py # Pipeline de procesamiento
│   ├── output_manager.py   # Gestor de salida
│   └── file_manager.py     # Gestor de archivos
├── server/                 # Servidor MCP
│   └── main.py            # Punto de entrada MCP
├── unified_api.py         # API unificada v3.0
├── classification_api.py  # API clásica v2.x
├── config.yaml           # Configuración del sistema
├── start_system_optimized.sh # Script de inicio optimizado
└── stop_system_optimized.sh  # Script de parada optimizado
```

### **Extensión del Sistema**
1. **Nuevos Módulos**: Agregar en directorio `core/`
2. **Nuevas APIs**: Integrar con `unified_api.py`
3. **Nuevas Taxonomías**: Definir en `config.yaml`
4. **Nuevos Formatos**: Extender `OutputManager`

---

## 🔧 Resolución de Problemas

### **Problemas Comunes**

#### **Sistema no inicia**
```bash
# Verificar puertos
lsof -i :8000 -i :8080

# Verificar dependencias
pip install -r requirements.txt

# Revisar logs
tail -f logs/main-api.log
```

#### **Errores de clasificación**
```bash
# Verificar OpenAI API Key
echo $OPENAI_API_KEY

# Probar conectividad MCP
curl http://localhost:8080/health

# Verificar base de datos
sqlite3 skos.sqlite ".tables"
```

#### **Problemas de rendimiento**
- Revisar `config.yaml` para límites
- Verificar uso de memoria con `htop`
- Analizar logs para cuellos de botella

---

## 📈 Roadmap y Evolución

### **Versión Actual: 3.0.0**
- ✅ Arquitectura unificada implementada
- ✅ Compatibilidad v2.x mantenida
- ✅ Módulos core completados
- ✅ Testing comprehensivo
- ✅ Documentación completa

### **Próximas Versiones**

#### **v3.1.0 - Optimización**
- 🔄 Cache inteligente de clasificaciones
- 🔄 Procesamiento paralelo mejorado
- 🔄 Métricas avanzadas de rendimiento

#### **v3.2.0 - Extensibilidad**
- 🔄 Soporte para taxonomías personalizadas
- 🔄 Plugin system para nuevos clasificadores
- 🔄 API GraphQL

#### **v4.0.0 - Escalabilidad**
- 🔄 Arquitectura distribuida
- 🔄 Soporte para múltiples modelos LLM
- 🔄 Sistema de clustering automático

---

## 📞 Soporte y Contribución

### **Documentación Adicional**
- **`UNIFIED_ARCHITECTURE.md`**: Detalles de arquitectura
- **`DEVELOPMENT_ROADMAP.md`**: Plan de desarrollo
- **`USAGE_GUIDE.md`**: Guía de uso detallada

### **Contacto**
- **Repositorio**: GitHub Repository
- **Issues**: Usar GitHub Issues para reportar problemas
- **Discusiones**: GitHub Discussions para preguntas

---

**🎉 SKOS MCP Classifier v3.0 - Sistema de Clasificación Inteligente con Arquitectura Unificada**

*Documentación actualizada: Enero 2024*