#!/usr/bin/env python3
"""
🚀 OUTPUT MANAGER - Punto Único de Salida del Sistema
==================================================== 
Maneja todas las salidas de forma unificada:
- Respuestas de clasificación
- Reportes y métricas
- Exportaciones (CSV, Excel, JSON)
- Logs estructurados
- Notificaciones
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
import uuid
import json
import csv
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class OutputType(str, Enum):
    """Tipos de salida del sistema"""
    CLASSIFICATION_RESPONSE = "classification_response"
    BATCH_RESPONSE = "batch_response"
    EXPORT_FILE = "export_file"
    REPORT = "report"
    METRICS = "metrics"
    NOTIFICATION = "notification"
    ERROR_RESPONSE = "error_response"

class OutputFormat(str, Enum):
    """Formatos de salida soportados"""
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    PDF = "pdf"
    XML = "xml"
    HTML = "html"
    TEXT = "text"

class DeliveryMethod(str, Enum):
    """Métodos de entrega de salida"""
    HTTP_RESPONSE = "http_response"
    FILE_DOWNLOAD = "file_download"
    EMAIL = "email"
    WEBHOOK = "webhook"
    STORAGE = "storage"
    STREAM = "stream"

class OutputDestination(BaseModel):
    """Destino de la salida"""
    method: DeliveryMethod = Field(..., description="Método de entrega")
    target: str = Field(..., description="Destino específico (URL, email, path, etc.)")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class OutputMetadata(BaseModel):
    """Metadatos de la salida"""
    output_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: OutputType = Field(..., description="Tipo de salida")
    format: OutputFormat = Field(..., description="Formato de salida")
    timestamp: datetime = Field(default_factory=datetime.now)
    source_request_id: Optional[str] = Field(None, description="ID de la petición origen")
    processing_time_ms: Optional[float] = Field(None, description="Tiempo de procesamiento en ms")
    size_bytes: Optional[int] = Field(None, description="Tamaño de la salida en bytes")
    destination: OutputDestination = Field(..., description="Destino de entrega")

class ClassificationOutput(BaseModel):
    """Salida de clasificación individual"""
    product_id: Optional[str] = Field(None, description="ID del producto")
    search_text: str = Field(..., description="Texto buscado")
    prefLabel: str = Field(..., description="Etiqueta preferida")
    notation: str = Field(..., description="Notación del concepto")
    uri: str = Field(..., description="URI del concepto")
    level: int = Field(..., description="Nivel en la jerarquía")
    score: float = Field(..., description="Puntuación de confianza")
    taxonomy_used: Dict[str, Any] = Field(..., description="Información de taxonomía")
    openai_cost: Optional[Dict[str, Any]] = Field(None, description="Información de costos")

class BatchClassificationOutput(BaseModel):
    """Salida de clasificación por lotes"""
    results: List[ClassificationOutput] = Field(..., description="Resultados individuales")
    summary: Dict[str, Any] = Field(..., description="Resumen de la operación")
    total_processed: int = Field(..., description="Total procesados")
    successful: int = Field(..., description="Procesados exitosamente")
    failed: int = Field(..., description="Fallos")
    cost_summary: Optional[Dict[str, Any]] = Field(None, description="Resumen de costos")

class ErrorOutput(BaseModel):
    """Salida de error"""
    error_code: str = Field(..., description="Código del error")
    error_message: str = Field(..., description="Mensaje del error")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales")
    request_data: Optional[Dict[str, Any]] = Field(None, description="Datos de la petición original")

class MetricsOutput(BaseModel):
    """Salida de métricas del sistema"""
    timestamp: datetime = Field(default_factory=datetime.now)
    period_start: datetime = Field(..., description="Inicio del período")
    period_end: datetime = Field(..., description="Fin del período")
    metrics: Dict[str, Any] = Field(..., description="Métricas recolectadas")

class ReportOutput(BaseModel):
    """Salida de reporte"""
    report_type: str = Field(..., description="Tipo de reporte")
    title: str = Field(..., description="Título del reporte")
    content: Union[Dict[str, Any], List[Dict[str, Any]], str] = Field(..., description="Contenido del reporte")
    generated_at: datetime = Field(default_factory=datetime.now)
    parameters: Dict[str, Any] = Field(default_factory=dict)

class OutputRequest(BaseModel):
    """Request para generar salida"""
    metadata: OutputMetadata = Field(..., description="Metadatos de salida")
    data: Union[
        ClassificationOutput, 
        BatchClassificationOutput, 
        ErrorOutput, 
        MetricsOutput, 
        ReportOutput,
        Dict[str, Any]
    ] = Field(..., description="Datos a entregar")
    template: Optional[str] = Field(None, description="Template a usar para formatting")
    options: Dict[str, Any] = Field(default_factory=dict)

class DeliveryResult(BaseModel):
    """Resultado de la entrega"""
    success: bool = Field(..., description="Si la entrega fue exitosa")
    output_id: str = Field(..., description="ID de la salida")
    delivery_info: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    file_path: Optional[str] = Field(None, description="Path del archivo generado")
    response_size: Optional[int] = Field(None, description="Tamaño de la respuesta")

class OutputFormatter(ABC):
    """Clase base para formateadores de salida"""
    
    @abstractmethod
    def format(self, data: Any, options: Dict[str, Any] = None) -> Any:
        """Formatear datos al formato específico"""
        pass

class JSONFormatter(OutputFormatter):
    """Formateador JSON"""
    
    def format(self, data: Any, options: Dict[str, Any] = None) -> str:
        options = options or {}
        indent = options.get('indent', 2)
        return json.dumps(data, indent=indent, default=str, ensure_ascii=False)

class CSVFormatter(OutputFormatter):
    """Formateador CSV"""
    
    def format(self, data: Any, options: Dict[str, Any] = None) -> str:
        options = options or {}
        
        if isinstance(data, dict):
            # Convertir dict a formato tabular
            if 'results' in data:  # BatchClassificationOutput
                df = pd.DataFrame([
                    {
                        'product_id': r.get('product_id', ''),
                        'search_text': r.get('search_text', ''),
                        'prefLabel': r.get('prefLabel', ''),
                        'notation': r.get('notation', ''),
                        'level': r.get('level', 0),
                        'score': r.get('score', 0.0),
                        'taxonomy': r.get('taxonomy_used', {}).get('name', '')
                    }
                    for r in data.get('results', [])
                ])
            else:  # ClassificationOutput individual
                df = pd.DataFrame([data])
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            raise ValueError("Datos no compatibles con formato CSV")
        
        return df.to_csv(index=False, encoding='utf-8')

class ExcelFormatter(OutputFormatter):
    """Formateador Excel"""
    
    def format(self, data: Any, options: Dict[str, Any] = None) -> bytes:
        options = options or {}
        
        if isinstance(data, dict) and 'results' in data:
            df = pd.DataFrame([
                {
                    'Product ID': r.get('product_id', ''),
                    'Search Text': r.get('search_text', ''),
                    'Category': r.get('prefLabel', ''),
                    'Notation': r.get('notation', ''),
                    'Level': r.get('level', 0),
                    'Confidence': r.get('score', 0.0),
                    'Taxonomy': r.get('taxonomy_used', {}).get('name', ''),
                    'URI': r.get('uri', ''),
                    'Timestamp': datetime.now().isoformat()
                }
                for r in data.get('results', [])
            ])
        else:
            df = pd.DataFrame([data] if isinstance(data, dict) else data)
        
        # Convertir a Excel en memoria
        from io import BytesIO
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Classification Results')
        
        return buffer.getvalue()

class OutputManager:
    """
    🚀 Manager centralizado para todas las salidas del sistema
    
    Responsabilidades:
    - Formatear datos según el tipo de salida requerido
    - Entregar mediante el método especificado
    - Logging centralizado de salidas
    - Métricas de uso y rendimiento
    - Manejo de errores en entregas
    """
    
    def __init__(self, base_export_path: str = "exports"):
        self.logger = logging.getLogger(f"{__name__}.OutputManager")
        self.base_export_path = Path(base_export_path)
        self.base_export_path.mkdir(exist_ok=True, parents=True)
        
        # Registrar formateadores
        self.formatters = {
            OutputFormat.JSON: JSONFormatter(),
            OutputFormat.CSV: CSVFormatter(),
            OutputFormat.EXCEL: ExcelFormatter()
        }
        
        # Estadísticas
        self.delivery_stats = {
            'total_outputs': 0,
            'successful_deliveries': 0,
            'failed_deliveries': 0,
            'bytes_delivered': 0
        }
    
    async def deliver_output(self, request: OutputRequest) -> DeliveryResult:
        """
        Entregar salida según especificaciones
        
        Args:
            request: Petición de salida con datos y metadatos
            
        Returns:
            DeliveryResult: Resultado de la entrega
        """
        output_id = request.metadata.output_id
        self.logger.info(f"🚀 Entregando salida {output_id} - Tipo: {request.metadata.type}")
        
        try:
            start_time = datetime.now()
            
            # 1. Formatear datos
            formatted_data = await self._format_data(request)
            
            # 2. Entregar según método
            delivery_info = await self._deliver_by_method(request, formatted_data)
            
            # 3. Calcular métricas
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds() * 1000
            
            # 4. Actualizar estadísticas
            self._update_stats(True, len(str(formatted_data)))
            
            self.logger.info(f"✅ Salida {output_id} entregada exitosamente en {processing_time:.2f}ms")
            
            return DeliveryResult(
                success=True,
                output_id=output_id,
                delivery_info=delivery_info,
                response_size=len(str(formatted_data))
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error entregando salida {output_id}: {str(e)}")
            self._update_stats(False, 0)
            
            return DeliveryResult(
                success=False,
                output_id=output_id,
                errors=[f"Error de entrega: {str(e)}"]
            )
    
    async def _format_data(self, request: OutputRequest) -> Any:
        """Formatear datos según el formato especificado"""
        formatter = self.formatters.get(request.metadata.format)
        if not formatter:
            raise ValueError(f"Formato {request.metadata.format} no soportado")
        
        # Convertir datos a diccionario si es necesario
        if hasattr(request.data, 'dict'):
            data_dict = request.data.dict()
        else:
            data_dict = request.data
        
        return formatter.format(data_dict, request.options)
    
    async def _deliver_by_method(self, request: OutputRequest, formatted_data: Any) -> Dict[str, Any]:
        """Entregar datos según el método especificado"""
        method = request.metadata.destination.method
        
        if method == DeliveryMethod.HTTP_RESPONSE:
            return {"method": "http_response", "data": formatted_data}
            
        elif method == DeliveryMethod.FILE_DOWNLOAD:
            file_path = await self._save_to_file(request, formatted_data)
            return {"method": "file_download", "file_path": str(file_path)}
            
        elif method == DeliveryMethod.STORAGE:
            storage_path = await self._store_data(request, formatted_data)
            return {"method": "storage", "storage_path": str(storage_path)}
            
        else:
            raise ValueError(f"Método de entrega {method} no implementado")
    
    async def _save_to_file(self, request: OutputRequest, formatted_data: Any) -> Path:
        """Guardar datos formateados en archivo"""
        # Crear nombre de archivo único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_type = request.metadata.type.value
        format_ext = self._get_file_extension(request.metadata.format)
        
        filename = f"{output_type}_{timestamp}_{request.metadata.output_id[:8]}.{format_ext}"
        file_path = self.base_export_path / filename
        
        # Guardar según formato
        if request.metadata.format == OutputFormat.JSON:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(formatted_data)
        elif request.metadata.format == OutputFormat.CSV:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(formatted_data)
        elif request.metadata.format == OutputFormat.EXCEL:
            with open(file_path, 'wb') as f:
                f.write(formatted_data)
        
        return file_path
    
    async def _store_data(self, request: OutputRequest, formatted_data: Any) -> Path:
        """Almacenar datos en sistema de archivos organizado"""
        # Organizar por fecha y tipo
        date_folder = datetime.now().strftime("%Y/%m/%d")
        type_folder = request.metadata.type.value
        
        storage_path = self.base_export_path / "storage" / date_folder / type_folder
        storage_path.mkdir(parents=True, exist_ok=True)
        
        # Usar timestamp + ID para unicidad
        timestamp = datetime.now().strftime("%H%M%S")
        format_ext = self._get_file_extension(request.metadata.format)
        filename = f"{timestamp}_{request.metadata.output_id[:8]}.{format_ext}"
        
        file_path = storage_path / filename
        
        # Guardar archivo
        if isinstance(formatted_data, bytes):
            with open(file_path, 'wb') as f:
                f.write(formatted_data)
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(str(formatted_data))
        
        return file_path
    
    def _get_file_extension(self, format: OutputFormat) -> str:
        """Obtener extensión de archivo para el formato"""
        extensions = {
            OutputFormat.JSON: "json",
            OutputFormat.CSV: "csv", 
            OutputFormat.EXCEL: "xlsx",
            OutputFormat.PDF: "pdf",
            OutputFormat.XML: "xml",
            OutputFormat.HTML: "html",
            OutputFormat.TEXT: "txt"
        }
        return extensions.get(format, "dat")
    
    def _update_stats(self, success: bool, bytes_count: int):
        """Actualizar estadísticas de entrega"""
        self.delivery_stats['total_outputs'] += 1
        if success:
            self.delivery_stats['successful_deliveries'] += 1
            self.delivery_stats['bytes_delivered'] += bytes_count
        else:
            self.delivery_stats['failed_deliveries'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de entregas"""
        total = self.delivery_stats['total_outputs']
        success_rate = (self.delivery_stats['successful_deliveries'] / total * 100) if total > 0 else 0
        
        return {
            **self.delivery_stats,
            'success_rate_percent': round(success_rate, 2),
            'average_bytes_per_delivery': round(
                self.delivery_stats['bytes_delivered'] / self.delivery_stats['successful_deliveries']
            ) if self.delivery_stats['successful_deliveries'] > 0 else 0
        }

# Instancia global del output manager
output_manager = OutputManager()

# Funciones de conveniencia
async def deliver_classification_result(
    result: Dict[str, Any], 
    format: OutputFormat = OutputFormat.JSON,
    method: DeliveryMethod = DeliveryMethod.HTTP_RESPONSE
) -> DeliveryResult:
    """Entregar resultado de clasificación"""
    
    request = OutputRequest(
        metadata=OutputMetadata(
            type=OutputType.CLASSIFICATION_RESPONSE,
            format=format,
            destination=OutputDestination(method=method, target="")
        ),
        data=result
    )
    
    return await output_manager.deliver_output(request)

async def deliver_batch_results(
    results: List[Dict[str, Any]], 
    summary: Dict[str, Any],
    format: OutputFormat = OutputFormat.JSON,
    method: DeliveryMethod = DeliveryMethod.HTTP_RESPONSE
) -> DeliveryResult:
    """Entregar resultados de lote"""
    
    batch_data = {
        'results': results,
        'summary': summary,
        'total_processed': len(results),
        'successful': len([r for r in results if 'error' not in r]),
        'failed': len([r for r in results if 'error' in r])
    }
    
    request = OutputRequest(
        metadata=OutputMetadata(
            type=OutputType.BATCH_RESPONSE,
            format=format,
            destination=OutputDestination(method=method, target="")
        ),
        data=batch_data
    )
    
    return await output_manager.deliver_output(request)

async def deliver_error(
    error_code: str,
    error_message: str,
    details: Optional[Dict[str, Any]] = None,
    format: OutputFormat = OutputFormat.JSON
) -> DeliveryResult:
    """Entregar respuesta de error"""
    
    error_data = ErrorOutput(
        error_code=error_code,
        error_message=error_message,
        details=details or {}
    )
    
    request = OutputRequest(
        metadata=OutputMetadata(
            type=OutputType.ERROR_RESPONSE,
            format=format,
            destination=OutputDestination(
                method=DeliveryMethod.HTTP_RESPONSE,
                target=""
            )
        ),
        data=error_data
    )
    
    return await output_manager.deliver_output(request)