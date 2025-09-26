#!/usr/bin/env python3
"""
⚙️ PROCESSING PIPELINE - Flujo Central de Procesamiento
====================================================
Conecta todos los componentes en un flujo unificado:
Ingesta → Validación → Procesamiento → Taxonomías → Salida

Flujo lineal y controlado que asegura:
- Trazabilidad completa
- Manejo de errores consistente  
- Métricas centralizadas
- Recuperación ante fallos
"""

from typing import Dict, Any, Optional, List, Callable
from pydantic import BaseModel, Field
from enum import Enum
import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Imports de nuestros componentes
from core.data_gateway import DataRequest, ProcessingResult, data_gateway
from core.output_manager import OutputRequest, OutputMetadata, OutputType, OutputFormat, DeliveryMethod, OutputDestination, output_manager

logger = logging.getLogger(__name__)

class PipelineStage(str, Enum):
    """Etapas del pipeline de procesamiento"""
    INGESTION = "ingestion"
    VALIDATION = "validation"
    PREPROCESSING = "preprocessing"
    CLASSIFICATION = "classification"  
    POST_PROCESSING = "post_processing"
    OUTPUT_FORMATTING = "output_formatting"
    DELIVERY = "delivery"
    COMPLETED = "completed"
    FAILED = "failed"

class PipelineStatus(str, Enum):
    """Estados del pipeline"""
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ProcessingMode(str, Enum):
    """Modos de procesamiento"""
    SYNC = "sync"          # Procesamiento síncrono
    ASYNC = "async"        # Procesamiento asíncrono
    BATCH = "batch"        # Procesamiento por lotes
    STREAM = "stream"      # Procesamiento en stream

@dataclass
class StageResult:
    """Resultado de una etapa del pipeline"""
    stage: PipelineStage
    success: bool
    data: Any = None
    metadata: Dict[str, Any] = None
    processing_time_ms: float = 0
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

class PipelineContext(BaseModel):
    """Contexto que viaja a través del pipeline"""
    pipeline_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = Field(..., description="ID de la petición original")
    user_id: Optional[str] = Field(None, description="ID del usuario")
    mode: ProcessingMode = Field(ProcessingMode.SYNC, description="Modo de procesamiento")
    current_stage: PipelineStage = Field(PipelineStage.INGESTION, description="Etapa actual")
    status: PipelineStatus = Field(PipelineStatus.QUEUED, description="Estado del pipeline")
    
    # Datos que fluyen por el pipeline
    original_request: Optional[Dict[str, Any]] = Field(None, description="Petición original")
    current_data: Any = Field(None, description="Datos en la etapa actual")
    
    # Configuración
    taxonomy_id: Optional[str] = Field(None, description="ID de taxonomía específica")
    output_format: OutputFormat = Field(OutputFormat.JSON, description="Formato de salida")
    delivery_method: DeliveryMethod = Field(DeliveryMethod.HTTP_RESPONSE, description="Método de entrega")
    
    # Métricas y tracking
    started_at: datetime = Field(default_factory=datetime.now)
    stage_results: List[StageResult] = Field(default_factory=list)
    total_processing_time_ms: float = Field(0, description="Tiempo total de procesamiento")
    
    # Configuración de retry
    max_retries: int = Field(3, description="Máximo número de reintentos")
    current_retries: int = Field(0, description="Reintentos actuales")
    
    class Config:
        arbitrary_types_allowed = True

class PipelineStageProcessor(ABC):
    """Clase base para procesadores de etapa"""
    
    @abstractmethod
    async def process(self, context: PipelineContext) -> StageResult:
        """Procesar una etapa específica"""
        pass
    
    @abstractmethod
    def can_handle(self, context: PipelineContext) -> bool:
        """Verificar si puede manejar el contexto"""
        pass

class IngestionProcessor(PipelineStageProcessor):
    """Procesador de ingesta de datos"""
    
    async def process(self, context: PipelineContext) -> StageResult:
        """Procesar ingesta usando DataGateway"""
        start_time = datetime.now()
        
        try:
            # Crear request para DataGateway desde contexto
            if context.original_request:
                # Reconstruir DataRequest desde el contexto
                from core.data_gateway import DataRequest
                data_request = DataRequest.parse_obj(context.original_request)
                
                # Procesar a través del gateway
                processing_result = await data_gateway.process_request(data_request)
                
                if processing_result.status == "processed":
                    context.current_data = processing_result.processing_metadata.get('normalized_data')
                    
                    return StageResult(
                        stage=PipelineStage.INGESTION,
                        success=True,
                        data=context.current_data,
                        metadata={'gateway_result': processing_result.dict()},
                        processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
                    )
                else:
                    return StageResult(
                        stage=PipelineStage.INGESTION,
                        success=False,
                        errors=[f"Gateway error: {processing_result.status}"],
                        processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
                    )
            else:
                return StageResult(
                    stage=PipelineStage.INGESTION,
                    success=False,
                    errors=["No original request data in context"],
                    processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
                )
                
        except Exception as e:
            logger.error(f"Error en ingesta: {str(e)}")
            return StageResult(
                stage=PipelineStage.INGESTION,
                success=False,
                errors=[f"Ingestion error: {str(e)}"],
                processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
    
    def can_handle(self, context: PipelineContext) -> bool:
        return context.current_stage == PipelineStage.INGESTION

class ClassificationProcessor(PipelineStageProcessor):
    """Procesador de clasificación"""
    
    async def process(self, context: PipelineContext) -> StageResult:
        """Procesar clasificación usando el sistema existente"""
        start_time = datetime.now()
        
        try:
            # Import aquí para evitar circular imports
            from client.classify_standard_api import classify
            
            results = []
            
            # Determinar si es clasificación individual o lote
            if isinstance(context.current_data, list):
                # Procesamiento por lote
                for item in context.current_data:
                    if hasattr(item, 'text'):
                        result = classify(item.text, item.product_id, context.taxonomy_id)
                        results.append(result)
                    elif isinstance(item, dict):
                        result = classify(item.get('text', ''), item.get('product_id'), context.taxonomy_id)
                        results.append(result)
                
                classification_result = {
                    'results': results,
                    'summary': {
                        'total_processed': len(results),
                        'successful': len([r for r in results if 'error' not in r]),
                        'failed': len([r for r in results if 'error' in r])
                    }
                }
            else:
                # Clasificación individual
                if hasattr(context.current_data, 'text'):
                    classification_result = classify(
                        context.current_data.text, 
                        context.current_data.product_id, 
                        context.taxonomy_id
                    )
                elif isinstance(context.current_data, dict):
                    classification_result = classify(
                        context.current_data.get('text', ''), 
                        context.current_data.get('product_id'), 
                        context.taxonomy_id
                    )
                else:
                    raise ValueError("Formato de datos no válido para clasificación")
            
            context.current_data = classification_result
            
            return StageResult(
                stage=PipelineStage.CLASSIFICATION,
                success=True,
                data=classification_result,
                metadata={'classification_type': 'batch' if isinstance(context.current_data, list) else 'single'},
                processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
            
        except Exception as e:
            logger.error(f"Error en clasificación: {str(e)}")
            return StageResult(
                stage=PipelineStage.CLASSIFICATION,
                success=False,
                errors=[f"Classification error: {str(e)}"],
                processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
    
    def can_handle(self, context: PipelineContext) -> bool:
        return context.current_stage == PipelineStage.CLASSIFICATION

class OutputProcessor(PipelineStageProcessor):
    """Procesador de salida usando OutputManager"""
    
    async def process(self, context: PipelineContext) -> StageResult:
        """Procesar salida usando OutputManager"""
        start_time = datetime.now()
        
        try:
            # Determinar tipo de output
            if isinstance(context.current_data, dict) and 'results' in context.current_data:
                output_type = OutputType.BATCH_RESPONSE
            else:
                output_type = OutputType.CLASSIFICATION_RESPONSE
            
            # Crear request de output
            output_request = OutputRequest(
                metadata=OutputMetadata(
                    type=output_type,
                    format=context.output_format,
                    source_request_id=context.request_id,
                    destination=OutputDestination(
                        method=context.delivery_method,
                        target=""
                    )
                ),
                data=context.current_data
            )
            
            # Entregar a través del OutputManager
            delivery_result = await output_manager.deliver_output(output_request)
            
            if delivery_result.success:
                return StageResult(
                    stage=PipelineStage.DELIVERY,
                    success=True,
                    data=delivery_result.delivery_info,
                    metadata={'output_id': delivery_result.output_id, 'response_size': delivery_result.response_size},
                    processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
                )
            else:
                return StageResult(
                    stage=PipelineStage.DELIVERY,
                    success=False,
                    errors=delivery_result.errors,
                    processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
                )
                
        except Exception as e:
            logger.error(f"Error en output: {str(e)}")
            return StageResult(
                stage=PipelineStage.DELIVERY,
                success=False,
                errors=[f"Output error: {str(e)}"],
                processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
    
    def can_handle(self, context: PipelineContext) -> bool:
        return context.current_stage == PipelineStage.DELIVERY

class ProcessingPipeline:
    """
    ⚙️ Pipeline central de procesamiento que orquesta todo el flujo
    
    Flujo: Ingesta → Validación → Clasificación → Salida
    
    Características:
    - Procesamiento asíncrono y por lotes
    - Manejo robusto de errores
    - Métricas detalladas
    - Trazabilidad completa
    - Recuperación ante fallos
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ProcessingPipeline")
        
        # Registrar procesadores por etapa
        self.stage_processors = {
            PipelineStage.INGESTION: IngestionProcessor(),
            PipelineStage.CLASSIFICATION: ClassificationProcessor(),
            PipelineStage.DELIVERY: OutputProcessor()
        }
        
        # Definir flujo de etapas
        self.stage_flow = [
            PipelineStage.INGESTION,
            PipelineStage.CLASSIFICATION,
            PipelineStage.DELIVERY,
            PipelineStage.COMPLETED
        ]
        
        # Estadísticas del pipeline
        self.pipeline_stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'average_processing_time_ms': 0,
            'total_processing_time_ms': 0
        }
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """
        Procesar contexto completo a través del pipeline
        
        Args:
            context: Contexto con datos y configuración
            
        Returns:
            PipelineContext: Contexto actualizado con resultados
        """
        pipeline_id = context.pipeline_id
        self.logger.info(f"⚙️ Iniciando pipeline {pipeline_id}")
        
        context.status = PipelineStatus.RUNNING
        pipeline_start = datetime.now()
        
        try:
            # Procesar cada etapa en secuencia
            for stage in self.stage_flow:
                if stage == PipelineStage.COMPLETED:
                    break
                
                context.current_stage = stage
                processor = self.stage_processors.get(stage)
                
                if processor and processor.can_handle(context):
                    stage_result = await self._process_stage_with_retry(processor, context)
                    context.stage_results.append(stage_result)
                    
                    if not stage_result.success:
                        context.status = PipelineStatus.FAILED
                        context.current_stage = PipelineStage.FAILED
                        break
                else:
                    self.logger.warning(f"No processor found for stage {stage}")
            
            # Calcular tiempo total
            total_time = (datetime.now() - pipeline_start).total_seconds() * 1000
            context.total_processing_time_ms = total_time
            
            if context.status != PipelineStatus.FAILED:
                context.status = PipelineStatus.COMPLETED
                context.current_stage = PipelineStage.COMPLETED
            
            # Actualizar estadísticas
            self._update_stats(context)
            
            self.logger.info(f"✅ Pipeline {pipeline_id} completado en {total_time:.2f}ms")
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Error crítico en pipeline {pipeline_id}: {str(e)}")
            context.status = PipelineStatus.FAILED
            context.current_stage = PipelineStage.FAILED
            context.stage_results.append(StageResult(
                stage=PipelineStage.FAILED,
                success=False,
                errors=[f"Critical pipeline error: {str(e)}"]
            ))
            return context
    
    async def _process_stage_with_retry(self, processor: PipelineStageProcessor, context: PipelineContext) -> StageResult:
        """Procesar etapa con lógica de retry"""
        last_error = None
        
        for attempt in range(context.max_retries + 1):
            try:
                if attempt > 0:
                    self.logger.info(f"Reintentando {context.current_stage} - Intento {attempt + 1}")
                    # Espera exponencial
                    await asyncio.sleep(2 ** attempt)
                
                result = await processor.process(context)
                
                if result.success:
                    if attempt > 0:
                        self.logger.info(f"✅ Etapa {context.current_stage} exitosa después de {attempt + 1} intentos")
                    return result
                else:
                    last_error = result.errors[0] if result.errors else "Unknown error"
                    
            except Exception as e:
                last_error = str(e)
                self.logger.error(f"Error en intento {attempt + 1} de {context.current_stage}: {str(e)}")
        
        # Si llegamos aquí, todos los intentos fallaron
        return StageResult(
            stage=context.current_stage,
            success=False,
            errors=[f"Stage failed after {context.max_retries + 1} attempts. Last error: {last_error}"]
        )
    
    def _update_stats(self, context: PipelineContext):
        """Actualizar estadísticas del pipeline"""
        self.pipeline_stats['total_processed'] += 1
        
        if context.status == PipelineStatus.COMPLETED:
            self.pipeline_stats['successful'] += 1
        else:
            self.pipeline_stats['failed'] += 1
        
        # Actualizar tiempo promedio
        total_time = self.pipeline_stats['total_processing_time_ms'] + context.total_processing_time_ms
        self.pipeline_stats['total_processing_time_ms'] = total_time
        
        if self.pipeline_stats['total_processed'] > 0:
            self.pipeline_stats['average_processing_time_ms'] = round(
                total_time / self.pipeline_stats['total_processed'], 2
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del pipeline"""
        total = self.pipeline_stats['total_processed']
        success_rate = (self.pipeline_stats['successful'] / total * 100) if total > 0 else 0
        
        return {
            **self.pipeline_stats,
            'success_rate_percent': round(success_rate, 2)
        }
    
    async def process_single_product(self, text: str, product_id: Optional[str] = None, taxonomy_id: Optional[str] = None) -> Dict[str, Any]:
        """Procesar un producto individual a través del pipeline completo"""
        
        # Crear contexto para producto individual
        from core.data_gateway import DataRequest, DataSource, DataType, InputFormat, ProductInput
        
        data_request = DataRequest(
            source=DataSource(
                name="Single Product Pipeline",
                type=DataType.PRODUCT,
                format=InputFormat.JSON
            ),
            data=ProductInput(text=text, product_id=product_id),
            taxonomy_id=taxonomy_id
        )
        
        context = PipelineContext(
            request_id=str(uuid.uuid4()),
            original_request=data_request.dict(),
            taxonomy_id=taxonomy_id,
            mode=ProcessingMode.SYNC
        )
        
        # Procesar a través del pipeline
        result_context = await self.process(context)
        
        # Extraer resultado final
        if result_context.status == PipelineStatus.COMPLETED:
            delivery_result = None
            for stage_result in result_context.stage_results:
                if stage_result.stage == PipelineStage.DELIVERY and stage_result.success:
                    delivery_result = stage_result.data
                    break
            
            return {
                'success': True,
                'pipeline_id': result_context.pipeline_id,
                'processing_time_ms': result_context.total_processing_time_ms,
                'data': delivery_result
            }
        else:
            errors = []
            for stage_result in result_context.stage_results:
                if not stage_result.success:
                    errors.extend(stage_result.errors)
            
            return {
                'success': False,
                'pipeline_id': result_context.pipeline_id,
                'errors': errors
            }

# Instancia global del pipeline
processing_pipeline = ProcessingPipeline()

# Funciones de conveniencia
async def process_product_request(text: str, product_id: Optional[str] = None, taxonomy_id: Optional[str] = None) -> Dict[str, Any]:
    """Procesar petición de producto usando pipeline unificado"""
    return await processing_pipeline.process_single_product(text, product_id, taxonomy_id)

async def process_batch_request(products: List[Dict[str, str]], taxonomy_id: Optional[str] = None) -> Dict[str, Any]:
    """Procesar lote de productos usando pipeline unificado"""
    # Implementación similar para lotes
    # Por simplicidad, se procesa como múltiples productos individuales
    results = []
    for product in products:
        result = await process_product_request(
            product.get('text', ''),
            product.get('product_id'),
            taxonomy_id
        )
        results.append(result)
    
    return {
        'success': True,
        'results': results,
        'summary': {
            'total_processed': len(results),
            'successful': len([r for r in results if r.get('success', False)]),
            'failed': len([r for r in results if not r.get('success', False)])
        }
    }