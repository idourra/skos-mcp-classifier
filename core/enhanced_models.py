"""
🎯 Enhanced Classifier Response Models v3.1
=============================================
Modelos Pydantic para el nuevo formato de respuestas enriquecidas
del sistema de clasificación SKOS.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union, Literal
from datetime import datetime
from enum import Enum


class DetailLevel(str, Enum):
    """Niveles de detalle para las respuestas"""
    BASIC = "basic"
    STANDARD = "standard" 
    FULL = "full"
    DEBUG = "debug"


class ConfidenceBreakdown(BaseModel):
    """Desglose detallado de confianza"""
    semantic_match: float = Field(..., ge=0.0, le=1.0, description="Coincidencia semántica")
    context_relevance: float = Field(..., ge=0.0, le=1.0, description="Relevancia contextual")
    taxonomy_fit: float = Field(..., ge=0.0, le=1.0, description="Ajuste taxonómico")
    term_precision: float = Field(..., ge=0.0, le=1.0, description="Precisión terminológica")


class ConfidenceFactors(BaseModel):
    """Factores que afectan la confianza"""
    positive: List[str] = Field(default_factory=list, description="Factores positivos")
    concerns: List[str] = Field(default_factory=list, description="Factores de preocupación")


class EnhancedConfidence(BaseModel):
    """Información de confianza enriquecida"""
    overall: float = Field(..., ge=0.0, le=1.0, description="Confianza global")
    breakdown: ConfidenceBreakdown = Field(..., description="Desglose detallado")
    factors: ConfidenceFactors = Field(..., description="Factores explicativos")


class ReasoningInfo(BaseModel):
    """Información de razonamiento del proceso"""
    decision_process: str = Field(..., description="Descripción del proceso de decisión")
    key_indicators: List[str] = Field(..., description="Indicadores clave identificados")
    taxonomy_path: List[str] = Field(..., description="Ruta en la taxonomía")


class AlternativeConcept(BaseModel):
    """Concepto alternativo de clasificación"""
    concept_uri: str = Field(..., description="URI del concepto alternativo")
    prefLabel: str = Field(..., description="Etiqueta preferida")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confianza en esta alternativa")
    reason: str = Field(..., description="Razón por la cual es alternativa")


class RelatedConcept(BaseModel):
    """Concepto relacionado en la taxonomía"""
    concept_uri: str = Field(..., description="URI del concepto relacionado")
    prefLabel: str = Field(..., description="Etiqueta preferida")
    relationship: Literal["broader", "narrower", "related"] = Field(..., description="Tipo de relación")
    relevance: float = Field(..., ge=0.0, le=1.0, description="Relevancia de la relación")


class PrimaryClassification(BaseModel):
    """Clasificación principal enriquecida"""
    concept_uri: str = Field(..., description="URI del concepto SKOS")
    prefLabel: str = Field(..., description="Etiqueta preferida")
    notation: str = Field(..., description="Notación del concepto")
    level: Optional[int] = Field(None, description="Nivel en la jerarquía")
    confidence: EnhancedConfidence = Field(..., description="Información de confianza")
    reasoning: ReasoningInfo = Field(..., description="Razonamiento del proceso")


class ClassificationResult(BaseModel):
    """Resultado completo de clasificación"""
    primary: PrimaryClassification = Field(..., description="Clasificación principal")
    alternatives: List[AlternativeConcept] = Field(default_factory=list, description="Alternativas")
    related_concepts: List[RelatedConcept] = Field(default_factory=list, description="Conceptos relacionados")


class DetectedAttributes(BaseModel):
    """Atributos detectados en el texto del producto"""
    type: List[str] = Field(default_factory=list, description="Tipos identificados")
    variety: List[str] = Field(default_factory=list, description="Variedades")
    characteristics: List[str] = Field(default_factory=list, description="Características")
    packaging: List[str] = Field(default_factory=list, description="Información de empaque")
    brand: List[str] = Field(default_factory=list, description="Marcas identificadas")
    size: List[str] = Field(default_factory=list, description="Tamaños")


class QualityIndicators(BaseModel):
    """Indicadores de calidad del input"""
    text_clarity: float = Field(..., ge=0.0, le=1.0, description="Claridad del texto")
    information_completeness: float = Field(..., ge=0.0, le=1.0, description="Completitud de información")
    ambiguity_level: float = Field(..., ge=0.0, le=1.0, description="Nivel de ambigüedad")


class ProductInfo(BaseModel):
    """Información procesada del producto"""
    original_text: str = Field(..., description="Texto original del producto")
    normalized_text: str = Field(..., description="Texto normalizado")
    product_id: Optional[str] = Field(None, description="ID del producto")
    detected_attributes: DetectedAttributes = Field(..., description="Atributos detectados")
    quality_indicators: QualityIndicators = Field(..., description="Indicadores de calidad")


class ProcessingStep(BaseModel):
    """Información de un paso del pipeline"""
    step: str = Field(..., description="Nombre del paso")
    duration_ms: float = Field(..., description="Duración en milisegundos")
    status: Literal["success", "warning", "error"] = Field(..., description="Estado del paso")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales")


class PipelineInfo(BaseModel):
    """Información del pipeline de procesamiento"""
    id: str = Field(..., description="ID único del pipeline")
    version: str = Field(..., description="Versión del pipeline")
    steps_completed: List[ProcessingStep] = Field(..., description="Pasos completados")
    total_duration_ms: float = Field(..., description="Duración total")


class FunctionCall(BaseModel):
    """Información de una llamada a función"""
    function: str = Field(..., description="Nombre de la función")
    parameters: Dict[str, Any] = Field(..., description="Parámetros de la función")
    duration_ms: float = Field(..., description="Duración de la llamada")
    result_size: Optional[int] = Field(None, description="Tamaño del resultado")


class CostBreakdown(BaseModel):
    """Desglose de costos de OpenAI"""
    prompt_tokens: int = Field(..., description="Tokens de prompt")
    completion_tokens: int = Field(..., description="Tokens de completación")
    total_tokens: int = Field(..., description="Total de tokens")


class CostPerToken(BaseModel):
    """Costo por token"""
    input: float = Field(..., description="Costo por token de entrada")
    output: float = Field(..., description="Costo por token de salida")


class CostInfo(BaseModel):
    """Información de costos de AI"""
    total_usd: float = Field(..., description="Costo total en USD")
    breakdown: CostBreakdown = Field(..., description="Desglose de tokens")
    cost_per_token: CostPerToken = Field(..., description="Costo por token")


class AIInteractionInfo(BaseModel):
    """Información de interacciones con AI"""
    model_used: str = Field(..., description="Modelo utilizado")
    function_calls: List[FunctionCall] = Field(..., description="Llamadas a funciones")
    cost_info: CostInfo = Field(..., description="Información de costos")
    total_api_calls: int = Field(..., description="Total de llamadas API")


class ProcessingInfo(BaseModel):
    """Información completa del procesamiento"""
    pipeline: PipelineInfo = Field(..., description="Información del pipeline")
    ai_interaction: AIInteractionInfo = Field(..., description="Interacciones con AI")


class TaxonomyInfo(BaseModel):
    """Información de la taxonomía utilizada"""
    id: str = Field(..., description="ID de la taxonomía")
    name: str = Field(..., description="Nombre de la taxonomía")
    version: str = Field(..., description="Versión de la taxonomía")
    is_default: bool = Field(..., description="Si es la taxonomía por defecto")
    total_concepts: int = Field(..., description="Total de conceptos")
    hierarchy_levels: int = Field(..., description="Niveles de jerarquía")


class QualityScore(BaseModel):
    """Puntuación de calidad global"""
    overall: float = Field(..., ge=0.0, le=1.0, description="Calidad global")
    components: Dict[str, float] = Field(..., description="Componentes de calidad")


class Recommendations(BaseModel):
    """Recomendaciones basadas en el resultado"""
    confidence_level: Literal["low", "medium", "high", "very_high"] = Field(..., description="Nivel de confianza")
    suggested_actions: List[str] = Field(..., description="Acciones sugeridas")
    review_needed: bool = Field(..., description="Si requiere revisión")
    alternative_approaches: List[str] = Field(default_factory=list, description="Enfoques alternativos")


class EnhancedMetadata(BaseModel):
    """Metadatos enriquecidos"""
    api_version: str = Field(..., description="Versión de la API")
    timestamp: datetime = Field(..., description="Timestamp del procesamiento")
    request_id: str = Field(..., description="ID único de la petición")
    session_id: Optional[str] = Field(None, description="ID de sesión")
    processing_node: str = Field(..., description="Nodo de procesamiento")
    quality_score: QualityScore = Field(..., description="Puntuación de calidad")
    recommendations: Recommendations = Field(..., description="Recomendaciones")


class EnhancedClassificationResponse(BaseModel):
    """Respuesta completa enriquecida del clasificador"""
    classification: ClassificationResult = Field(..., description="Resultado de clasificación")
    product: ProductInfo = Field(..., description="Información del producto")
    processing: ProcessingInfo = Field(..., description="Información de procesamiento")
    taxonomy: TaxonomyInfo = Field(..., description="Información de taxonomía")
    metadata: EnhancedMetadata = Field(..., description="Metadatos enriquecidos")
    detail_level: DetailLevel = Field(default=DetailLevel.STANDARD, description="Nivel de detalle")
    
    # Campo legacy para compatibilidad backward
    legacy_format: Optional[Dict[str, Any]] = Field(None, description="Formato legacy para compatibilidad")

    @field_validator('detail_level', mode='before')
    @classmethod
    def validate_detail_level(cls, v):
        if isinstance(v, str):
            try:
                return DetailLevel(v)
            except ValueError:
                return DetailLevel.STANDARD
        return v

    def to_legacy_format(self) -> Dict[str, Any]:
        """Convierte a formato legacy para compatibilidad"""
        return {
            "search_text": self.product.normalized_text,
            "concept_uri": self.classification.primary.concept_uri,
            "prefLabel": self.classification.primary.prefLabel,
            "notation": self.classification.primary.notation,
            "level": self.classification.primary.level,
            "confidence": self.classification.primary.confidence.overall,
            "product_id": self.product.product_id,
            "timestamp": self.metadata.timestamp.isoformat(),
            "taxonomy_used": {
                "id": self.taxonomy.id,
                "name": self.taxonomy.name,
                "is_default": self.taxonomy.is_default
            }
        }

    def to_basic_format(self) -> Dict[str, Any]:
        """Formato básico simplificado"""
        return {
            "concept_uri": self.classification.primary.concept_uri,
            "prefLabel": self.classification.primary.prefLabel,
            "confidence": self.classification.primary.confidence.overall,
            "product_id": self.product.product_id
        }


class BatchEnhancedResponse(BaseModel):
    """Respuesta para lotes de clasificación enriquecida"""
    total: int = Field(..., description="Total de productos procesados")
    successful: int = Field(..., description="Clasificaciones exitosas")
    failed: int = Field(..., description="Clasificaciones fallidas")
    results: List[EnhancedClassificationResponse] = Field(..., description="Resultados individuales")
    batch_id: str = Field(..., description="ID del lote")
    processing_summary: Dict[str, Any] = Field(..., description="Resumen de procesamiento")
    aggregated_costs: CostInfo = Field(..., description="Costos agregados")
    detail_level: DetailLevel = Field(default=DetailLevel.STANDARD, description="Nivel de detalle usado")


class ErrorDetail(BaseModel):
    """Detalle de error enriquecido"""
    error_code: str = Field(..., description="Código del error")
    error_message: str = Field(..., description="Mensaje del error")
    error_category: Literal["input", "processing", "ai", "system"] = Field(..., description="Categoría del error")
    suggestions: List[str] = Field(default_factory=list, description="Sugerencias para resolver")
    technical_details: Optional[Dict[str, Any]] = Field(None, description="Detalles técnicos")


class EnhancedErrorResponse(BaseModel):
    """Respuesta de error enriquecida"""
    success: bool = Field(False, description="Siempre false para errores")
    error: ErrorDetail = Field(..., description="Detalle del error")
    request_info: Dict[str, Any] = Field(..., description="Información de la petición")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del error")
    request_id: str = Field(..., description="ID de la petición")