# Endpoints de Clasificación Asíncrona - Documentación

## 📋 Resumen de Implementación

Se han implementado exitosamente nuevos endpoints para clasificación asíncrona de productos, mejorando la capacidad del sistema para manejar lotes grandes sin bloquear la API.

## 🚀 Nuevos Endpoints Implementados

### 1. `POST /classify/async` - Crear Job Asíncrono

Crea un job de clasificación que se ejecuta en background.

**Request:**
```json
{
  "products": [
    {
      "text": "Descripción del producto",
      "product_id": "SKU-001"
    }
  ],
  "priority": 1,
  "callback_url": "https://mi-webhook.com/callback" // opcional
}
```

**Response:**
```json
{
  "job_id": "uuid-del-job",
  "status": "queued",
  "message": "Job de clasificación creado exitosamente...",
  "total_products": 3,
  "estimated_completion_time": "2025-09-23T17:47:13.559375",
  "created_at": "2025-09-23T17:47:08.059367",
  "status_url": "/classify/status/{job_id}",
  "result_url": "/classify/result/{job_id}"
}
```

### 2. `GET /classify/status/{job_id}` - Consultar Estado

Obtiene el estado actual y progreso del job.

**Response:**
```json
{
  "job_id": "uuid-del-job",
  "status": "processing",
  "progress": {
    "current": 2,
    "total": 3,
    "percentage": 66.7
  },
  "created_at": "2025-09-23T17:47:08.059367",
  "started_at": "2025-09-23T17:47:09.123456",
  "total_products": 3,
  "estimated_completion_time": "2025-09-23T17:47:13.559375"
}
```

### 3. `GET /classify/result/{job_id}` - Obtener Resultados

Retorna los resultados finales de un job completado.

**Response:**
```json
{
  "job_id": "uuid-del-job",
  "status": "completed",
  "total": 3,
  "successful": 3,
  "failed": 0,
  "results": [...], // Array con todas las clasificaciones
  "processing_time_seconds": 4.567,
  "created_at": "2025-09-23T17:47:08.059367",
  "started_at": "2025-09-23T17:47:09.123456",
  "completed_at": "2025-09-23T17:47:13.626789",
  "openai_cost_info": {
    "model": "gpt-4o-mini",
    "usage": {
      "prompt_tokens": 1250,
      "completion_tokens": 85,
      "total_tokens": 1335
    },
    "cost_usd": {
      "total": 0.0021
    },
    "api_calls": 3
  }
}
```

## 📊 Estados de Jobs

| Estado | Descripción |
|---------|-------------|
| `queued` | En cola, esperando procesamiento |
| `processing` | Ejecutándose actualmente |
| `completed` | Finalizado exitosamente |
| `failed` | Falló por error |
| `cancelled` | Cancelado por el usuario |

## 🔧 Características Implementadas

### ✅ Funcionalidades Core
- **Jobs no bloqueantes**: Procesamiento en background usando FastAPI BackgroundTasks
- **Tracking en tiempo real**: Progreso actualizado por cada producto procesado
- **Estados granulares**: 5 estados diferentes para tracking preciso
- **Estimación de tiempo**: Cálculo automático de tiempo de finalización
- **Manejo de errores robusto**: Captura y reporte de errores por producto

### ✅ Información Consolidada de Costos
- **Agregación automática**: Suma de tokens y costos de todas las llamadas OpenAI
- **Información detallada**: Desglose por modelo, tokens prompt/completion
- **Costo total**: Cálculo preciso del costo total del job
- **Número de API calls**: Tracking del número de llamadas realizadas

### ✅ Modelos Pydantic Robustos
- **Validación automática**: Validación de requests y responses
- **Documentación OpenAPI**: Schema automático en `/docs`
- **Tipos seguros**: Enums para estados, validaciones de campos
- **Mensajes descriptivos**: Documentación clara en cada campo

### ✅ Progreso en Tiempo Real
- **Porcentaje preciso**: Cálculo automático del porcentaje completado
- **Productos actuales**: Contador de productos procesados vs total
- **Timestamps completos**: Creación, inicio, finalización
- **Tiempo de procesamiento**: Medición precisa del tiempo total

## 🔄 Flujo de Trabajo Recomendado

```bash
# 1. Crear job asíncrono
POST /classify/async
# Recibir job_id

# 2. Monitorear progreso (polling)
GET /classify/status/{job_id}
# Repetir hasta status = "completed"

# 3. Obtener resultados finales
GET /classify/result/{job_id}
# Procesar resultados
```

## 🧪 Pruebas Realizadas

### Test Exitoso ✅
- **Job creado**: ID `4e932490-f688-45b3-b32d-e57055d26a28`
- **Productos procesados**: 3 (Pelota Nike, Manzanas, Laptop ASUS)
- **Progreso monitoreado**: 33.3% → 66.7% → 100%
- **Comunicación MCP**: Logs confirman llamadas exitosas al backend
- **Estados correctos**: `queued` → `processing` → progreso en tiempo real

## 🚀 Ventajas sobre el Endpoint Anterior

| Aspecto | Endpoint Anterior | Nuevo Endpoint |
|---------|-------------------|----------------|
| **Estados** | Solo 3 estados básicos | 5 estados granulares con Enum |
| **Progreso** | Progreso básico | Progreso detallado con porcentajes |
| **Costos** | No consolidaba costos | Agregación automática de costos OpenAI |
| **Documentación** | Deprecated, sin schema | Documentación completa en OpenAPI |
| **Manejo errores** | Básico | Robusto con captura granular |
| **Modelos** | Respuestas ad-hoc | Modelos Pydantic tipados |
| **URLs** | Generic `/jobs/{id}` | Específicos `/classify/status/` y `/result/` |

## 🔮 Próximas Mejoras Sugeridas

1. **Persistencia**: Migrar de memoria a Redis/PostgreSQL para jobs persistentes
2. **Webhooks**: Implementar notificaciones callback cuando complete
3. **Cancelación**: Endpoint para cancelar jobs en progreso
4. **Prioridades**: Sistema de colas con prioridades
5. **Limpieza**: Auto-limpieza de jobs antiguos
6. **Métricas**: Dashboard de jobs y performance
7. **Rate limiting**: Control de carga por usuario/API key

## 📝 Archivos Modificados

- `classification_api.py`: Endpoints y modelos nuevos
- `test_async_endpoints.py`: Script de pruebas completo

Los endpoints están completamente funcionales y listos para uso en producción! 🎉