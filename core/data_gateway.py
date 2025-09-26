#!/usr/bin/env python3
"""
🚪 DATA GATEWAY - Punto Único de Entrada al Sistema
==================================================
Maneja toda la ingesta de datos de forma unificada:
- Productos (individuales y lotes)
- Taxonomías SKOS 
- Configuraciones del sistema
- Validaciones de entrada
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
import uuid
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DataType(str, Enum):
    """Tipos de datos que pueden ingresar al sistema"""
    PRODUCT = "product"
    PRODUCT_BATCH = "product_batch"
    TAXONOMY = "taxonomy"
    CONFIGURATION = "configuration"
    FILE_UPLOAD = "file_upload"

class InputFormat(str, Enum):
    """Formatos de entrada soportados"""
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    JSONLD = "jsonld"
    XML = "xml"
    TEXT = "text"

class ValidationLevel(str, Enum):
    """Niveles de validación"""
    STRICT = "strict"
    MODERATE = "moderate"
    BASIC = "basic"
    NONE = "none"

class DataSource(BaseModel):
    """Información de la fuente de datos"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Nombre descriptivo de la fuente")
    type: DataType = Field(..., description="Tipo de datos")
    format: InputFormat = Field(..., description="Formato de los datos")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProductInput(BaseModel):
    """Datos de producto para clasificar"""
    text: str = Field(..., description="Descripción del producto")
    product_id: Optional[str] = Field(None, description="ID único del producto")
    category_hint: Optional[str] = Field(None, description="Pista de categoría opcional")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('El texto del producto no puede estar vacío')
        return v.strip()

class TaxonomyInput(BaseModel):
    """Datos de taxonomía SKOS para cargar"""
    id: str = Field(..., description="ID único de la taxonomía")
    name: str = Field(..., description="Nombre de la taxonomía")
    description: Optional[str] = Field(None, description="Descripción de la taxonomía")
    data: Union[str, Dict[str, Any]] = Field(..., description="Datos SKOS en JSON-LD")
    is_default: bool = Field(False, description="Si debe ser la taxonomía por defecto")
    is_active: bool = Field(True, description="Si debe estar activa")
    
class ConfigurationInput(BaseModel):
    """Configuración del sistema"""
    key: str = Field(..., description="Clave de configuración")
    value: Any = Field(..., description="Valor de la configuración")
    category: str = Field(default="general", description="Categoría de configuración")
    description: Optional[str] = Field(None, description="Descripción de la configuración")

class FileInput(BaseModel):
    """Archivo subido al sistema"""
    filename: str = Field(..., description="Nombre del archivo")
    content: bytes = Field(..., description="Contenido del archivo")
    content_type: str = Field(..., description="Tipo MIME del archivo")
    size: int = Field(..., description="Tamaño en bytes")

class DataRequest(BaseModel):
    """Request unificado para cualquier tipo de entrada"""
    source: DataSource = Field(..., description="Información de la fuente")
    data: Union[ProductInput, List[ProductInput], TaxonomyInput, ConfigurationInput, FileInput] = Field(
        ..., description="Datos a procesar"
    )
    validation_level: ValidationLevel = Field(ValidationLevel.MODERATE, description="Nivel de validación")
    processing_options: Dict[str, Any] = Field(default_factory=dict)
    taxonomy_id: Optional[str] = Field(None, description="ID de taxonomía específica a usar")

class ValidationResult(BaseModel):
    """Resultado de validación"""
    is_valid: bool = Field(..., description="Si los datos son válidos")
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProcessingResult(BaseModel):
    """Resultado del procesamiento en gateway"""
    request_id: str = Field(..., description="ID único de la petición")
    status: str = Field(..., description="Estado del procesamiento")
    data_processed: int = Field(..., description="Número de elementos procesados")
    validation_result: ValidationResult = Field(..., description="Resultado de validación")
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)
    next_stage: Optional[str] = Field(None, description="Siguiente etapa en el pipeline")

class DataGateway:
    """
    🚪 Gateway único para toda la entrada de datos al sistema
    
    Responsabilidades:
    - Validar todos los datos de entrada
    - Normalizar formatos diferentes 
    - Enrutar a los procesadores correctos
    - Aplicar políticas de seguridad
    - Logging centralizado de entrada
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.DataGateway")
        self.supported_formats = {
            DataType.PRODUCT: [InputFormat.JSON, InputFormat.TEXT],
            DataType.PRODUCT_BATCH: [InputFormat.JSON, InputFormat.CSV, InputFormat.EXCEL],
            DataType.TAXONOMY: [InputFormat.JSONLD, InputFormat.JSON],
            DataType.CONFIGURATION: [InputFormat.JSON],
            DataType.FILE_UPLOAD: [InputFormat.JSON, InputFormat.CSV, InputFormat.EXCEL, InputFormat.JSONLD]
        }
    
    async def process_request(self, request: DataRequest) -> ProcessingResult:
        """
        Procesar una petición de datos unificada
        
        Args:
            request: Petición con datos a procesar
            
        Returns:
            ProcessingResult: Resultado del procesamiento
        """
        request_id = str(uuid.uuid4())
        self.logger.info(f"🚪 Procesando request {request_id} - Tipo: {request.source.type}")
        
        try:
            # 1. Validación de formato
            format_validation = await self._validate_format(request)
            if not format_validation.is_valid:
                return ProcessingResult(
                    request_id=request_id,
                    status="format_error",
                    data_processed=0,
                    validation_result=format_validation
                )
            
            # 2. Validación de datos
            data_validation = await self._validate_data(request)
            if not data_validation.is_valid and request.validation_level in [ValidationLevel.STRICT, ValidationLevel.MODERATE]:
                return ProcessingResult(
                    request_id=request_id,
                    status="validation_error", 
                    data_processed=0,
                    validation_result=data_validation
                )
            
            # 3. Normalización
            normalized_data = await self._normalize_data(request)
            
            # 4. Enrutamiento
            next_stage = self._determine_next_stage(request.source.type)
            
            # 5. Contar elementos procesados
            data_count = self._count_data_elements(normalized_data)
            
            self.logger.info(f"✅ Request {request_id} procesado exitosamente - {data_count} elementos")
            
            return ProcessingResult(
                request_id=request_id,
                status="processed",
                data_processed=data_count,
                validation_result=data_validation,
                processing_metadata={
                    "normalized_data": normalized_data,
                    "source_info": request.source.dict(),
                    "processing_timestamp": datetime.now().isoformat()
                },
                next_stage=next_stage
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error procesando request {request_id}: {str(e)}")
            return ProcessingResult(
                request_id=request_id,
                status="error",
                data_processed=0,
                validation_result=ValidationResult(
                    is_valid=False,
                    errors=[f"Error interno: {str(e)}"]
                )
            )
    
    async def _validate_format(self, request: DataRequest) -> ValidationResult:
        """Validar que el formato sea compatible con el tipo de datos"""
        data_type = request.source.type
        data_format = request.source.format
        
        if data_format not in self.supported_formats.get(data_type, []):
            return ValidationResult(
                is_valid=False,
                errors=[f"Formato {data_format} no soportado para tipo {data_type}"]
            )
        
        return ValidationResult(is_valid=True)
    
    async def _validate_data(self, request: DataRequest) -> ValidationResult:
        """Validar los datos según el nivel de validación configurado"""
        errors = []
        warnings = []
        
        if request.validation_level == ValidationLevel.NONE:
            return ValidationResult(is_valid=True)
        
        # Validaciones específicas por tipo
        if request.source.type == DataType.PRODUCT:
            if isinstance(request.data, ProductInput):
                if len(request.data.text.strip()) < 3:
                    errors.append("Descripción de producto muy corta (mínimo 3 caracteres)")
        
        elif request.source.type == DataType.PRODUCT_BATCH:
            if isinstance(request.data, list):
                if len(request.data) == 0:
                    errors.append("El lote de productos no puede estar vacío")
                elif len(request.data) > 1000:
                    warnings.append(f"Lote grande ({len(request.data)} productos). Considere procesamiento asíncrono.")
        
        elif request.source.type == DataType.TAXONOMY:
            if isinstance(request.data, TaxonomyInput):
                if not request.data.id.strip():
                    errors.append("ID de taxonomía requerido")
                if not request.data.name.strip():
                    errors.append("Nombre de taxonomía requerido")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    async def _normalize_data(self, request: DataRequest) -> Any:
        """Normalizar datos a formato interno estándar"""
        # Por ahora retorna los datos tal como están
        # Aquí se implementarían las transformaciones de formato
        return request.data
    
    def _determine_next_stage(self, data_type: DataType) -> str:
        """Determinar la siguiente etapa del pipeline según el tipo de datos"""
        routing_map = {
            DataType.PRODUCT: "classification_pipeline",
            DataType.PRODUCT_BATCH: "batch_classification_pipeline", 
            DataType.TAXONOMY: "taxonomy_management_pipeline",
            DataType.CONFIGURATION: "configuration_pipeline",
            DataType.FILE_UPLOAD: "file_processing_pipeline"
        }
        return routing_map.get(data_type, "unknown_pipeline")
    
    def _count_data_elements(self, data: Any) -> int:
        """Contar elementos de datos para métricas"""
        if isinstance(data, list):
            return len(data)
        return 1

# Instancia global del gateway
data_gateway = DataGateway()

# Funciones de conveniencia para uso directo
async def process_product(text: str, product_id: Optional[str] = None, taxonomy_id: Optional[str] = None) -> ProcessingResult:
    """Procesar un producto individual"""
    request = DataRequest(
        source=DataSource(
            name="Single Product Input",
            type=DataType.PRODUCT,
            format=InputFormat.JSON
        ),
        data=ProductInput(text=text, product_id=product_id),
        taxonomy_id=taxonomy_id
    )
    return await data_gateway.process_request(request)

async def process_product_batch(products: List[Dict[str, str]], taxonomy_id: Optional[str] = None) -> ProcessingResult:
    """Procesar un lote de productos"""
    product_inputs = [
        ProductInput(text=p.get("text", ""), product_id=p.get("product_id"))
        for p in products
    ]
    
    request = DataRequest(
        source=DataSource(
            name="Batch Product Input",
            type=DataType.PRODUCT_BATCH,
            format=InputFormat.JSON
        ),
        data=product_inputs,
        taxonomy_id=taxonomy_id
    )
    return await data_gateway.process_request(request)

async def process_taxonomy_upload(taxonomy_data: Dict[str, Any]) -> ProcessingResult:
    """Procesar carga de taxonomía"""
    taxonomy_input = TaxonomyInput(**taxonomy_data)
    
    request = DataRequest(
        source=DataSource(
            name="Taxonomy Upload",
            type=DataType.TAXONOMY,
            format=InputFormat.JSONLD
        ),
        data=taxonomy_input
    )
    return await data_gateway.process_request(request)