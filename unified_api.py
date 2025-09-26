#!/usr/bin/env python3
"""
🌟 UNIFIED CLASSIFICATION API - API Unificada con Arquitectura Centralizada
==========================================================================
Nueva API que utiliza el sistema unificado de entrada/salida:
- Data Gateway para ingesta
- Processing Pipeline para procesamiento
- Output Manager para salidas
- Compatibilidad completa con API anterior
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import logging
from datetime import datetime

# Imports de la nueva arquitectura
from core.data_gateway import (
    DataRequest, DataSource, DataType, InputFormat, ProductInput, 
    data_gateway, process_product, process_product_batch
)
from core.output_manager import (
    OutputFormat, DeliveryMethod, deliver_classification_result,
    deliver_batch_results, deliver_error, output_manager
)
from core.processing_pipeline import (
    processing_pipeline, process_product_request, process_batch_request
)

# Imports existentes para compatibilidad
from server.taxonomy_endpoints import taxonomy_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="🌟 Unified SKOS Classification API",
    description="API unificada con arquitectura centralizada para clasificación de productos SKOS",
    version="3.0.0"
)

# Incluir router de taxonomías (mantener compatibilidad)
app.include_router(taxonomy_router, prefix="/taxonomies", tags=["Taxonomies"])

# === MODELOS PYDANTIC UNIFICADOS ===

class UnifiedProductRequest(BaseModel):
    """Request unificado para producto individual"""
    text: str = Field(..., description="Descripción del producto a clasificar", min_length=1)
    product_id: Optional[str] = Field(None, description="ID único del producto")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos adicionales")

class UnifiedBatchRequest(BaseModel):
    """Request unificado para lote de productos"""
    products: List[UnifiedProductRequest] = Field(..., description="Lista de productos", min_items=1, max_items=1000)
    batch_id: Optional[str] = Field(None, description="ID único del lote")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos del lote")

class UnifiedResponse(BaseModel):
    """Respuesta unificada del sistema"""
    success: bool = Field(..., description="Si el procesamiento fue exitoso")
    pipeline_id: str = Field(..., description="ID del pipeline de procesamiento")
    processing_time_ms: float = Field(..., description="Tiempo de procesamiento en milisegundos")
    data: Any = Field(..., description="Datos de respuesta")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos adicionales")

class UnifiedErrorResponse(BaseModel):
    """Respuesta de error unificada"""
    success: bool = Field(False, description="Siempre false para errores")
    error_code: str = Field(..., description="Código del error")
    error_message: str = Field(..., description="Mensaje del error")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detalles adicionales")
    timestamp: datetime = Field(default_factory=datetime.now)

class SystemStats(BaseModel):
    """Estadísticas del sistema unificado"""
    pipeline_stats: Dict[str, Any] = Field(..., description="Estadísticas del pipeline")
    gateway_stats: Dict[str, Any] = Field(..., description="Estadísticas del gateway")
    output_stats: Dict[str, Any] = Field(..., description="Estadísticas de salida")
    uptime: str = Field(..., description="Tiempo de actividad")

# === ENDPOINTS PRINCIPALES ===

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Información de la API unificada"""
    return {
        "message": "🌟 Unified SKOS Classification API",
        "version": "3.0.0",
        "description": "API unificada con arquitectura centralizada",
        "features": [
            "Data Gateway único para entrada",
            "Processing Pipeline centralizado", 
            "Output Manager unificado",
            "Compatibilidad completa con v2.x",
            "Métricas integradas",
            "Manejo robusto de errores"
        ],
        "endpoints": {
            "/classify": "Clasificar producto individual",
            "/classify/batch": "Clasificar lote de productos",
            "/classify/async": "Clasificación asíncrona", 
            "/stats": "Estadísticas del sistema",
            "/health": "Estado del sistema",
            "/taxonomies/*": "Gestión de taxonomías"
        }
    }

@app.get("/health")
async def health_check():
    """Verificación de salud del sistema unificado"""
    try:
        # Verificar componentes principales
        gateway_ok = hasattr(data_gateway, 'process_request')
        pipeline_ok = hasattr(processing_pipeline, 'process')
        output_ok = hasattr(output_manager, 'deliver_output')
        
        all_ok = gateway_ok and pipeline_ok and output_ok
        
        return {
            "status": "healthy" if all_ok else "degraded",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "data_gateway": "ok" if gateway_ok else "error",
                "processing_pipeline": "ok" if pipeline_ok else "error", 
                "output_manager": "ok" if output_ok else "error"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@app.post("/classify", response_model=UnifiedResponse)
async def classify_single_unified(
    request: UnifiedProductRequest,
    taxonomy: Optional[str] = Query(None, description="ID de taxonomía específica"),
    output_format: str = Query("json", description="Formato de salida: json, csv, excel"),
    include_metadata: bool = Query(True, description="Incluir metadatos detallados")
):
    """
    🎯 Clasificar producto individual usando arquitectura unificada
    
    Flujo completo: Data Gateway → Processing Pipeline → Output Manager
    """
    try:
        start_time = datetime.now()
        
        # Procesar a través del pipeline unificado
        result = await process_product_request(
            text=request.text,
            product_id=request.product_id,
            taxonomy_id=taxonomy
        )
        
        if result['success']:
            # Preparar respuesta unificada
            response_data = result['data']
            
            # Agregar metadatos si se solicita
            if include_metadata:
                response_data['processing_metadata'] = {
                    'pipeline_id': result['pipeline_id'],
                    'processing_time_ms': result['processing_time_ms'],
                    'taxonomy_used': taxonomy,
                    'api_version': '3.0.0'
                }
            
            return UnifiedResponse(
                success=True,
                pipeline_id=result['pipeline_id'],
                processing_time_ms=result['processing_time_ms'],
                data=response_data,
                metadata={
                    'format': output_format,
                    'total_time_ms': (datetime.now() - start_time).total_seconds() * 1000
                }
            )
        else:
            raise HTTPException(
                status_code=422,
                detail=UnifiedErrorResponse(
                    error_code="CLASSIFICATION_FAILED",
                    error_message="Error en clasificación",
                    details={'errors': result.get('errors', [])}
                ).dict()
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en clasificación unificada: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=UnifiedErrorResponse(
                error_code="INTERNAL_ERROR",
                error_message=f"Error interno del servidor: {str(e)}"
            ).dict()
        )

@app.post("/classify/batch", response_model=UnifiedResponse)
async def classify_batch_unified(
    request: UnifiedBatchRequest,
    taxonomy: Optional[str] = Query(None, description="ID de taxonomía específica"),
    output_format: str = Query("json", description="Formato de salida"),
    parallel_processing: bool = Query(True, description="Procesamiento paralelo")
):
    """
    📦 Clasificar lote de productos usando pipeline unificado
    
    Optimizado para grandes volúmenes con procesamiento paralelo opcional
    """
    try:
        start_time = datetime.now()
        
        # Convertir a formato para pipeline
        products_data = [
            {"text": p.text, "product_id": p.product_id}
            for p in request.products
        ]
        
        # Procesar lote a través del pipeline
        if parallel_processing and len(products_data) > 5:
            # Procesamiento paralelo para lotes grandes
            chunk_size = max(1, len(products_data) // 4)  # Dividir en 4 chunks
            chunks = [
                products_data[i:i + chunk_size] 
                for i in range(0, len(products_data), chunk_size)
            ]
            
            # Procesar chunks en paralelo
            tasks = [
                process_batch_request(chunk, taxonomy_id=taxonomy)
                for chunk in chunks
            ]
            
            chunk_results = await asyncio.gather(*tasks)
            
            # Consolidar resultados
            all_results = []
            total_successful = 0
            total_failed = 0
            
            for chunk_result in chunk_results:
                if chunk_result['success']:
                    all_results.extend(chunk_result['results'])
                    total_successful += chunk_result['summary']['successful']
                    total_failed += chunk_result['summary']['failed']
            
            result = {
                'success': True,
                'results': all_results,
                'summary': {
                    'total_processed': len(all_results),
                    'successful': total_successful,
                    'failed': total_failed,
                    'processing_mode': 'parallel'
                }
            }
        else:
            # Procesamiento secuencial
            result = await process_batch_request(products_data, taxonomy_id=taxonomy)
            result['summary']['processing_mode'] = 'sequential'
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return UnifiedResponse(
            success=True,
            pipeline_id=f"batch_{request.batch_id or 'auto'}",
            processing_time_ms=processing_time,
            data=result,
            metadata={
                'batch_size': len(request.products),
                'processing_mode': result['summary']['processing_mode'],
                'taxonomy_used': taxonomy
            }
        )
        
    except Exception as e:
        logger.error(f"Error en lote unificado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=UnifiedErrorResponse(
                error_code="BATCH_ERROR",
                error_message=f"Error procesando lote: {str(e)}"
            ).dict()
        )

@app.post("/classify/async")
async def classify_async_unified(
    request: UnifiedBatchRequest,
    background_tasks: BackgroundTasks,
    taxonomy: Optional[str] = Query(None, description="ID de taxonomía específica"),
    callback_url: Optional[str] = Query(None, description="URL para notificación de completado")
):
    """
    🔄 Clasificación asíncrona para lotes grandes
    
    Inicia procesamiento en background y retorna inmediatamente
    """
    try:
        # Generar ID único para seguimiento
        import uuid
        job_id = str(uuid.uuid4())
        
        # Agregar tarea al background
        background_tasks.add_task(
            _process_async_batch,
            job_id=job_id,
            products=request.products,
            taxonomy=taxonomy,
            callback_url=callback_url
        )
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Procesamiento iniciado en background",
            "estimated_completion": "5-10 minutos para lotes grandes",
            "status_endpoint": f"/status/{job_id}",
            "callback_url": callback_url
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error iniciando procesamiento asíncrono: {str(e)}"
        )

@app.get("/stats", response_model=SystemStats)
async def get_system_stats():
    """📊 Estadísticas completas del sistema unificado"""
    try:
        return SystemStats(
            pipeline_stats=processing_pipeline.get_stats(),
            gateway_stats={"message": "Gateway stats not implemented yet"},
            output_stats=output_manager.get_stats(),
            uptime="Sistema activo"  # Simplificado por ahora
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )

# === ENDPOINTS DE COMPATIBILIDAD ===

@app.post("/classify/products")  # Mantener compatibilidad con v2.x
async def classify_products_compatibility(
    request: dict,
    taxonomy: Optional[str] = Query(None)
):
    """🔄 Endpoint de compatibilidad con API v2.x"""
    try:
        # Convertir formato v2.x a v3.0
        if "products" in request:
            unified_request = UnifiedBatchRequest(
                products=[
                    UnifiedProductRequest(
                        text=p.get("text", ""),
                        product_id=p.get("product_id")
                    )
                    for p in request["products"]
                ]
            )
            return await classify_batch_unified(unified_request, taxonomy)
        else:
            # Producto individual
            unified_request = UnifiedProductRequest(
                text=request.get("text", ""),
                product_id=request.get("product_id")
            )
            return await classify_single_unified(unified_request, taxonomy)
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en compatibilidad: {str(e)}"
        )

# === FUNCIONES DE BACKGROUND ===

async def _process_async_batch(
    job_id: str,
    products: List[UnifiedProductRequest],
    taxonomy: Optional[str] = None,
    callback_url: Optional[str] = None
):
    """Procesar lote de forma asíncrona"""
    try:
        logger.info(f"🔄 Iniciando procesamiento asíncrono {job_id}")
        
        # Simular procesamiento (aquí iría la lógica real)
        await asyncio.sleep(2)  # Simular trabajo
        
        # Procesar usando pipeline unificado
        products_data = [
            {"text": p.text, "product_id": p.product_id}
            for p in products
        ]
        
        result = await process_batch_request(products_data, taxonomy_id=taxonomy)
        
        # Si hay callback URL, enviar notificación
        if callback_url:
            # Aquí se implementaría el envío del webhook
            logger.info(f"📤 Enviando resultado a {callback_url}")
        
        logger.info(f"✅ Procesamiento asíncrono {job_id} completado")
        
    except Exception as e:
        logger.error(f"❌ Error en procesamiento asíncrono {job_id}: {str(e)}")

# === MANEJO DE ERRORES GLOBAL ===

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejo global de excepciones"""
    logger.error(f"❌ Error no manejado: {str(exc)}")
    
    # Entregar error usando Output Manager
    error_result = await deliver_error(
        error_code="UNHANDLED_ERROR",
        error_message=str(exc),
        details={"request_path": str(request.url.path)}
    )
    
    return HTTPException(
        status_code=500,
        detail=error_result.delivery_info if error_result.success else "Error crítico del sistema"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)