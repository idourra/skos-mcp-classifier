"""
🚀 Enhanced Classification Engine v3.1
======================================
Motor de clasificación mejorado que genera respuestas enriquecidas
con análisis detallado, alternativas y metadatos completos.
"""

import time
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import re

from core.enhanced_models import (
    EnhancedClassificationResponse, ClassificationResult, PrimaryClassification,
    EnhancedConfidence, ConfidenceBreakdown, ConfidenceFactors, ReasoningInfo,
    AlternativeConcept, RelatedConcept, ProductInfo, DetectedAttributes,
    QualityIndicators, ProcessingInfo, PipelineInfo, ProcessingStep,
    AIInteractionInfo, FunctionCall, CostInfo, CostBreakdown, CostPerToken,
    TaxonomyInfo, EnhancedMetadata, QualityScore, Recommendations,
    DetailLevel, EnhancedErrorResponse, ErrorDetail
)

# Import existing classify function
from client.multi_taxonomy_classify import classify as base_classify


class EnhancedClassifier:
    """Motor de clasificación enriquecido"""
    
    def __init__(self):
        self.version = "3.1.0"
        self.processing_node = "enhanced-classifier-01"
    
    def classify_enhanced(
        self, 
        text: str, 
        product_id: Optional[str] = None,
        taxonomy_id: Optional[str] = None,
        detail_level: DetailLevel = DetailLevel.STANDARD
    ) -> EnhancedClassificationResponse:
        """
        Clasificación enriquecida con análisis detallado
        
        Args:
            text: Texto del producto a clasificar
            product_id: ID opcional del producto
            taxonomy_id: ID de taxonomía específica
            detail_level: Nivel de detalle de la respuesta
            
        Returns:
            Respuesta enriquecida con análisis completo
        """
        start_time = time.time()
        request_id = f"req_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        pipeline_id = f"pipeline_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        try:
            # Paso 1: Normalización y análisis de texto
            step1_start = time.time()
            normalized_text, detected_attributes, quality_indicators = self._analyze_product_text(text)
            step1_duration = (time.time() - step1_start) * 1000
            
            # Paso 2: Clasificación base
            step2_start = time.time()
            base_result = base_classify(text, product_id, taxonomy_id)
            step2_duration = (time.time() - step2_start) * 1000
            
            if 'error' in base_result:
                return self._create_error_response(base_result['error'], request_id)
            
            # Paso 3: Análisis de confianza enriquecido
            step3_start = time.time()
            enhanced_confidence = self._calculate_enhanced_confidence(
                text, normalized_text, base_result
            )
            step3_duration = (time.time() - step3_start) * 1000
            
            # Paso 4: Generación de alternativas
            step4_start = time.time()
            alternatives = self._generate_alternatives(text, base_result, taxonomy_id)
            step4_duration = (time.time() - step4_start) * 1000
            
            # Paso 5: Conceptos relacionados
            step5_start = time.time()
            related_concepts = self._find_related_concepts(base_result['concept_uri'])
            step5_duration = (time.time() - step5_start) * 1000
            
            # Paso 6: Razonamiento
            step6_start = time.time()
            reasoning = self._generate_reasoning(text, base_result, enhanced_confidence)
            step6_duration = (time.time() - step6_start) * 1000
            
            # Construir respuesta enriquecida
            total_duration = (time.time() - start_time) * 1000
            
            response = EnhancedClassificationResponse(
                classification=ClassificationResult(
                    primary=PrimaryClassification(
                        concept_uri=base_result['concept_uri'],
                        prefLabel=base_result['prefLabel'],
                        notation=base_result['notation'],
                        level=base_result.get('level'),
                        confidence=enhanced_confidence,
                        reasoning=reasoning
                    ),
                    alternatives=alternatives,
                    related_concepts=related_concepts
                ),
                product=ProductInfo(
                    original_text=text,
                    normalized_text=normalized_text,
                    product_id=product_id,
                    detected_attributes=detected_attributes,
                    quality_indicators=quality_indicators
                ),
                processing=ProcessingInfo(
                    pipeline=PipelineInfo(
                        id=pipeline_id,
                        version=self.version,
                        steps_completed=[
                            ProcessingStep(step="text_analysis", duration_ms=step1_duration, status="success"),
                            ProcessingStep(step="base_classification", duration_ms=step2_duration, status="success"),
                            ProcessingStep(step="confidence_analysis", duration_ms=step3_duration, status="success"),
                            ProcessingStep(step="alternatives_generation", duration_ms=step4_duration, status="success"),
                            ProcessingStep(step="related_concepts", duration_ms=step5_duration, status="success"),
                            ProcessingStep(step="reasoning_generation", duration_ms=step6_duration, status="success")
                        ],
                        total_duration_ms=total_duration
                    ),
                    ai_interaction=self._extract_ai_info(base_result)
                ),
                taxonomy=self._build_taxonomy_info(taxonomy_id, base_result),
                metadata=EnhancedMetadata(
                    api_version=self.version,
                    timestamp=datetime.now(),
                    request_id=request_id,
                    processing_node=self.processing_node,
                    quality_score=self._calculate_quality_score(quality_indicators, enhanced_confidence),
                    recommendations=self._generate_recommendations(enhanced_confidence)
                ),
                detail_level=detail_level
            )
            
            # Filtrar según nivel de detalle
            if detail_level == DetailLevel.BASIC:
                response = self._filter_to_basic(response)
            elif detail_level == DetailLevel.LEGACY:
                response.legacy_format = response.to_legacy_format()
                
            return response
            
        except Exception as e:
            return self._create_error_response(str(e), request_id)
    
    def _analyze_product_text(self, text: str) -> Tuple[str, DetectedAttributes, QualityIndicators]:
        """Analizar y normalizar el texto del producto"""
        # Normalización básica
        normalized = text.strip().lower()
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Detección de atributos
        attributes = DetectedAttributes()
        
        # Detectar tipos comunes
        food_types = ['yogur', 'queso', 'leche', 'pan', 'aceite', 'arroz', 'pollo']
        attributes.type = [t for t in food_types if t in normalized]
        
        # Detectar características
        characteristics = ['natural', 'orgánico', 'integral', 'descremado', 'light', 'extra', 'virgen']
        attributes.characteristics = [c for c in characteristics if c in normalized]
        
        # Detectar variedades
        varieties = ['griego', 'manchego', 'oliva', 'blanco', 'integral', 'congelado']
        attributes.variety = [v for v in varieties if v in normalized]
        
        # Detectar empaque/tamaño
        packaging_patterns = [
            r'(\d+)\s*g',
            r'(\d+)\s*ml',
            r'(\d+)\s*l',
            r'(\d+)\s*kg'
        ]
        for pattern in packaging_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            attributes.packaging.extend(matches)
        
        # Calcular indicadores de calidad
        quality = QualityIndicators(
            text_clarity=min(1.0, len(text.split()) / 10),  # Más palabras = más claridad (hasta un límite)
            information_completeness=min(1.0, (len(attributes.type) + len(attributes.characteristics)) / 3),
            ambiguity_level=max(0.0, 1.0 - len(attributes.type))  # Sin tipo = más ambigüedad
        )
        
        return normalized, attributes, quality
    
    def _calculate_enhanced_confidence(
        self, 
        original_text: str, 
        normalized_text: str, 
        base_result: Dict[str, Any]
    ) -> EnhancedConfidence:
        """Calcular confianza enriquecida con desglose detallado"""
        base_confidence = base_result.get('confidence', 0.5)
        
        # Calcular componentes de confianza
        semantic_match = base_confidence  # Usar como base
        
        # Ajustar por contexto
        context_keywords = ['natural', 'orgánico', 'integral', 'fresco']
        context_boost = sum(1 for word in context_keywords if word in normalized_text) * 0.05
        context_relevance = min(1.0, semantic_match + context_boost)
        
        # Ajustar por precisión taxonomica
        taxonomy_fit = semantic_match
        if 'notation' in base_result and base_result['notation']:
            taxonomy_fit = min(1.0, taxonomy_fit + 0.05)  # Bonus por tener notación
            
        # Precisión terminológica
        exact_match_bonus = 0.1 if any(word in base_result.get('prefLabel', '').lower() 
                                      for word in normalized_text.split()) else 0
        term_precision = min(1.0, semantic_match + exact_match_bonus)
        
        # Factores explicativos
        positive_factors = []
        concerns = []
        
        if semantic_match > 0.8:
            positive_factors.append("Alta coincidencia semántica")
        if context_relevance > semantic_match:
            positive_factors.append("Contexto alimentario refuerza clasificación")
        if exact_match_bonus > 0:
            positive_factors.append("Coincidencia directa de términos")
            
        if semantic_match < 0.7:
            concerns.append("Confianza base moderada")
        if len(normalized_text.split()) < 3:
            concerns.append("Información limitada en descripción")
            
        return EnhancedConfidence(
            overall=min(1.0, (semantic_match + context_relevance + taxonomy_fit + term_precision) / 4),
            breakdown=ConfidenceBreakdown(
                semantic_match=semantic_match,
                context_relevance=context_relevance,
                taxonomy_fit=taxonomy_fit,
                term_precision=term_precision
            ),
            factors=ConfidenceFactors(
                positive=positive_factors,
                concerns=concerns
            )
        )
    
    def _generate_alternatives(
        self, 
        text: str, 
        base_result: Dict[str, Any], 
        taxonomy_id: Optional[str]
    ) -> List[AlternativeConcept]:
        """Generar conceptos alternativos"""
        # Simulación de alternativas (en implementación real, buscaría en taxonomía)
        alternatives = []
        
        # Alternativa genérica por contexto
        if 'yogur' in text.lower():
            alternatives.append(AlternativeConcept(
                concept_uri="https://treew.io/taxonomy/concept/111204",
                prefLabel="Leche y productos lácteos líquidos",
                confidence=0.65,
                reason="Alternativa por contexto lácteo general"
            ))
        
        if 'natural' in text.lower():
            alternatives.append(AlternativeConcept(
                concept_uri="https://treew.io/taxonomy/concept/111299",
                prefLabel="Productos naturales y orgánicos",
                confidence=0.58,
                reason="Enfoque en características naturales"
            ))
            
        return alternatives[:2]  # Máximo 2 alternativas
    
    def _find_related_concepts(self, concept_uri: str) -> List[RelatedConcept]:
        """Encontrar conceptos relacionados"""
        # Simulación de conceptos relacionados
        related = []
        
        if "111206" in concept_uri:  # Yogur
            related.append(RelatedConcept(
                concept_uri="https://treew.io/taxonomy/concept/111200",
                prefLabel="Productos lácteos",
                relationship="broader",
                relevance=0.90
            ))
            
        return related
    
    def _generate_reasoning(
        self, 
        text: str, 
        base_result: Dict[str, Any], 
        confidence: EnhancedConfidence
    ) -> ReasoningInfo:
        """Generar información de razonamiento"""
        # Extraer indicadores clave
        words = text.lower().split()
        key_indicators = []
        
        for word in words:
            if word in ['yogur', 'queso', 'leche', 'pan']:
                key_indicators.append(f"Término principal: '{word}'")
            elif word in ['natural', 'orgánico', 'integral']:
                key_indicators.append(f"Calificador: '{word}'")
        
        # Generar descripción del proceso
        decision_process = f"Análisis identificó '{base_result.get('prefLabel', 'concepto')}' como la clasificación más apropiada basado en coincidencia semántica y contextual."
        
        # Generar ruta taxonómica (simplificada)
        taxonomy_path = [
            "Alimentos",
            "Productos específicos",
            base_result.get('prefLabel', 'Concepto clasificado')
        ]
        
        return ReasoningInfo(
            decision_process=decision_process,
            key_indicators=key_indicators,
            taxonomy_path=taxonomy_path
        )
    
    def _extract_ai_info(self, base_result: Dict[str, Any]) -> AIInteractionInfo:
        """Extraer información de interacciones con AI"""
        cost_data = base_result.get('openai_cost', {})
        
        return AIInteractionInfo(
            model_used=cost_data.get('model', 'gpt-4o-mini-2024-07-18'),
            function_calls=[
                FunctionCall(
                    function="search_concepts",
                    parameters={"query": "product_search", "k": 10},
                    duration_ms=200
                )
            ],
            cost_info=CostInfo(
                total_usd=cost_data.get('cost_usd', {}).get('total', 0.001),
                breakdown=CostBreakdown(
                    prompt_tokens=cost_data.get('usage', {}).get('prompt_tokens', 100),
                    completion_tokens=cost_data.get('usage', {}).get('completion_tokens', 50),
                    total_tokens=cost_data.get('usage', {}).get('total_tokens', 150)
                ),
                cost_per_token=CostPerToken(
                    input=0.00000015,
                    output=0.0000006
                )
            ),
            total_api_calls=cost_data.get('api_calls', 1)
        )
    
    def _build_taxonomy_info(self, taxonomy_id: Optional[str], base_result: Dict[str, Any]) -> TaxonomyInfo:
        """Construir información de taxonomía"""
        taxonomy_used = base_result.get('taxonomy_used', {})
        
        return TaxonomyInfo(
            id=taxonomy_used.get('id', taxonomy_id or 'treew-skos'),
            name=taxonomy_used.get('name', 'TreeW SKOS Food Taxonomy'),
            version="2.1",
            is_default=taxonomy_used.get('is_default', taxonomy_id is None),
            total_concepts=282,
            hierarchy_levels=4
        )
    
    def _calculate_quality_score(
        self, 
        quality_indicators: QualityIndicators, 
        confidence: EnhancedConfidence
    ) -> QualityScore:
        """Calcular puntuación de calidad global"""
        input_quality = (quality_indicators.text_clarity + 
                        quality_indicators.information_completeness + 
                        (1 - quality_indicators.ambiguity_level)) / 3
        
        processing_reliability = confidence.overall
        
        output_consistency = min(1.0, confidence.breakdown.semantic_match + 0.1)
        
        overall = (input_quality + processing_reliability + output_consistency) / 3
        
        return QualityScore(
            overall=overall,
            components={
                "input_quality": input_quality,
                "processing_reliability": processing_reliability,
                "output_consistency": output_consistency
            }
        )
    
    def _generate_recommendations(self, confidence: EnhancedConfidence) -> Recommendations:
        """Generar recomendaciones basadas en confianza"""
        overall_confidence = confidence.overall
        
        if overall_confidence >= 0.9:
            level = "very_high"
            actions = ["Resultado altamente confiable, usar sin revisión"]
            review_needed = False
        elif overall_confidence >= 0.75:
            level = "high"
            actions = ["Resultado confiable, usar directamente"]
            review_needed = False
        elif overall_confidence >= 0.6:
            level = "medium"
            actions = ["Resultado moderado, considerar revisar alternativas"]
            review_needed = True
        else:
            level = "low"
            actions = ["Resultado con baja confianza, requiere revisión manual"]
            review_needed = True
            
        return Recommendations(
            confidence_level=level,
            suggested_actions=actions,
            review_needed=review_needed
        )
    
    def _filter_to_basic(self, response: EnhancedClassificationResponse) -> EnhancedClassificationResponse:
        """Filtrar respuesta a formato básico"""
        # Mantener solo información esencial
        response.classification.alternatives = []
        response.classification.related_concepts = []
        response.processing.pipeline.steps_completed = response.processing.pipeline.steps_completed[:2]
        return response
    
    def _create_error_response(self, error_msg: str, request_id: str) -> EnhancedErrorResponse:
        """Crear respuesta de error enriquecida"""
        return EnhancedErrorResponse(
            error=ErrorDetail(
                error_code="CLASSIFICATION_ERROR",
                error_message=error_msg,
                error_category="processing",
                suggestions=["Verificar formato del texto", "Intentar con descripción más detallada"]
            ),
            request_info={"request_id": request_id},
            request_id=request_id
        )


# Instancia global del clasificador enriquecido
enhanced_classifier = EnhancedClassifier()