"""
🎯 Enhanced Non-Classifiable Product Handler
===========================================
Mejora para manejar productos no clasificables de manera inteligente
en lugar de devolver errores genéricos.
"""

import re
import json
from typing import Dict, Any, Optional
from datetime import datetime


class NonClassifiableHandler:
    """Manejador especializado para productos no clasificables"""
    
    def __init__(self):
        self.taxonomy_domains = {
            'treew-skos': 'general',  # Taxonomía general multi-dominio
            'electronics-taxonomy': 'electrónica',
            'textile-taxonomy': 'textil',
            'automotive-taxonomy': 'automotriz'
        }
        
        # Dominios disponibles en treew-skos (basado en análisis real de la taxonomía)
        self.treew_domains = {
            'alimentario': ['alimentos', 'comida', 'bebida', 'yogur', 'pan', 'leche', 'queso', 'carne', 'fruta'],
            'textil': ['ropa', 'camiseta', 'camisa', 'pantalón', 'algodón', 'textil', 'vestido', 'calzado'],
            'electrodomésticos': ['electrodoméstico', 'plancha', 'nevera', 'horno', 'microondas', 'televisor'],
            'limpieza': ['detergente', 'jabón', 'limpieza', 'lavado', 'producto de limpieza'],
            'hogar': ['mueble', 'cama', 'colchón', 'textiles para el hogar', 'decoración'],
            'belleza': ['cosmético', 'crema', 'shampoo', 'producto de belleza', 'cuidado personal', 'higiene'],
            'joyería': ['joya', 'collar', 'anillo', 'pulsera', 'accesorio'],
            'automotriz': ['auto', 'carro', 'coche', 'vehículo', 'moto', 'motocicleta', 'bicicleta', 
                          'neumático', 'llanta', 'freno', 'aceite', 'motor', 'batería', 'automotive',
                          'piezas automotrices', 'accesorios para autos'],
            'electrónicos': ['teléfono', 'celular', 'smartphone', 'tablet', 'ordenador', 'televisor', 
                            'auriculares', 'cargador', 'cable', 'batería electrónica'],
            'farmacéuticos': ['medicina', 'medicamento', 'vitamina', 'suplemento', 'producto farmacéutico'],
            'mascotas': ['mascota', 'perro', 'gato', 'alimentación para mascotas', 'productos veterinarios']
        }
    
    def detect_product_domain(self, text: str) -> str:
        """Detectar el dominio probable del producto basado en treew-skos disponibles"""
        text_lower = text.lower()
        
        # Buscar coincidencias en los dominios de treew-skos
        for domain, keywords in self.treew_domains.items():
            if any(keyword in text_lower for keyword in keywords):
                return domain
                
        return 'desconocido'
    
    def analyze_taxonomy_mismatch(self, text: str, taxonomy_id: str) -> Dict[str, Any]:
        """Analizar compatibilidad entre producto y taxonomía"""
        product_domain = self.detect_product_domain(text)
        taxonomy_domain = self.taxonomy_domains.get(taxonomy_id or 'treew-skos', 'general')
        
        # Para taxonomía general, verificar si el dominio está disponible
        is_compatible = True
        if taxonomy_domain == 'general':
            # treew-skos es general, solo verificar si encontramos el dominio
            is_compatible = product_domain in self.treew_domains or product_domain == 'desconocido'
        else:
            # Para taxonomías específicas, debe coincidir el dominio
            is_compatible = product_domain == taxonomy_domain or product_domain == 'desconocido'
        
        return {
            'is_compatible': is_compatible,
            'product_domain': product_domain,
            'taxonomy_domain': taxonomy_domain,
            'available_domains': list(self.treew_domains.keys()) if taxonomy_domain == 'general' else [taxonomy_domain],
            'confidence': 0.8 if product_domain != 'desconocido' else 0.4
        }
    
    def create_non_classifiable_response(
        self, 
        text: str, 
        product_id: Optional[str], 
        taxonomy_id: Optional[str],
        ai_response: str,
        cost_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Crear respuesta estructurada para producto no clasificable"""
        
        # Analizar compatibilidad
        compatibility_analysis = self.analyze_taxonomy_mismatch(text, taxonomy_id)
        
        # Determinar la razón principal
        if not compatibility_analysis['is_compatible']:
            reason = "domain_mismatch"
            explanation = (f"El producto pertenece al dominio '{compatibility_analysis['product_domain']}' "
                          f"pero no está disponible en la taxonomía '{taxonomy_id or 'treew-skos'}'.")
        else:
            reason = "insufficient_specificity"
            explanation = ("El producto es compatible con la taxonomía pero requiere términos "
                          "más específicos para una clasificación precisa.")
        
        # Generar sugerencias
        suggestions = self._generate_suggestions(text, compatibility_analysis)
        
        return {
            "classification_result": "not_classifiable",
            "reason": reason,
            "explanation": explanation,
            "product_analysis": {
                "original_text": text,
                "detected_domain": compatibility_analysis['product_domain'],
                "confidence": compatibility_analysis['confidence']
            },
            "taxonomy_info": {
                "id": taxonomy_id or "treew-skos",
                "domain": compatibility_analysis['taxonomy_domain'],
                "available_domains": compatibility_analysis['available_domains'],
                "is_compatible": compatibility_analysis['is_compatible']
            },
            "ai_response": {
                "raw_message": ai_response,
                "interpretation": "El modelo AI confirmó que no puede clasificar este producto"
            },
            "suggestions": suggestions,
            "metadata": {
                "product_id": product_id,
                "timestamp": datetime.now().isoformat(),
                "processing_status": "completed_with_no_classification",
                "quality_indicators": {
                    "input_clarity": self._assess_input_clarity(text),
                    "domain_detection_confidence": compatibility_analysis['confidence']
                }
            },
            "openai_cost": cost_info
        }
    
    def _generate_suggestions(self, text: str, mismatch_analysis: Dict) -> Dict[str, Any]:
        """Generar sugerencias útiles para el usuario"""
        suggestions = {
            "immediate_actions": [],
            "taxonomy_recommendations": [],
            "product_description_improvements": []
        }
        
        if mismatch_analysis['is_mismatch']:
            # Sugerir taxonomía correcta
            product_domain = mismatch_analysis['product_domain']
            if product_domain == 'textil':
                suggestions["taxonomy_recommendations"].append(
                    "Considere usar una taxonomía de productos textiles o de moda"
                )
            elif product_domain == 'electrónica':
                suggestions["taxonomy_recommendations"].append(
                    "Considere usar una taxonomía de productos electrónicos"
                )
            
            suggestions["immediate_actions"].append(
                f"Cambiar a una taxonomía del dominio '{product_domain}'"
            )
        
        # Sugerir mejoras en descripción
        if len(text.split()) < 3:
            suggestions["product_description_improvements"].append(
                "Proporcione una descripción más detallada del producto"
            )
        
        if not any(char.isdigit() for char in text):
            suggestions["product_description_improvements"].append(
                "Incluya información técnica como tamaño, modelo o especificaciones"
            )
        
        return suggestions
    
    def _assess_input_clarity(self, text: str) -> float:
        """Evaluar la claridad del input del usuario"""
        score = 0.5  # Base
        
        # Bonus por longitud apropiada
        if 3 <= len(text.split()) <= 10:
            score += 0.2
        
        # Bonus por información específica
        if any(char.isdigit() for char in text):
            score += 0.1
        
        # Bonus por uso de términos descriptivos
        descriptive_words = ['natural', 'orgánico', 'premium', 'deluxe', 'extra']
        if any(word in text.lower() for word in descriptive_words):
            score += 0.1
        
        return min(1.0, score)


# Funciones de utilidad para integrar en el sistema existente

def is_non_classifiable_response(ai_response: str) -> bool:
    """Detectar si la respuesta de AI indica producto no clasificable"""
    non_classifiable_indicators = [
        'no se encontraron conceptos',
        'no puedo proporcionar una clasificación',
        'no hay conceptos relevantes',
        'fuera del dominio',
        'no está en la taxonomía',
        'no se puede clasificar'
    ]
    
    ai_response_lower = ai_response.lower()
    return any(indicator in ai_response_lower for indicator in non_classifiable_indicators)


def enhance_classification_error_handling(
    original_result: Dict[str, Any],
    text: str,
    product_id: Optional[str] = None,
    taxonomy_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Mejorar el manejo de errores de clasificación
    
    Args:
        original_result: Resultado original que contiene error
        text: Texto original del producto
        product_id: ID del producto
        taxonomy_id: ID de taxonomía usada
        
    Returns:
        Respuesta mejorada con análisis detallado
    """
    
    # Si no es un error de "No JSON found", devolver original
    if original_result.get('error') != 'No JSON found in response':
        return original_result
    
    raw_response = original_result.get('raw_response', '')
    
    # Si la respuesta indica producto no clasificable
    if is_non_classifiable_response(raw_response):
        handler = NonClassifiableHandler()
        
        return handler.create_non_classifiable_response(
            text=text,
            product_id=product_id,
            taxonomy_id=taxonomy_id,
            ai_response=raw_response,
            cost_info=original_result.get('openai_cost')
        )
    
    # Si no, mantener el error original pero con más contexto
    enhanced_result = original_result.copy()
    enhanced_result['error_analysis'] = {
        'type': 'parsing_error',
        'likely_cause': 'Respuesta AI en formato no estructurado',
        'suggestion': 'Revisar prompt del sistema o configuración del modelo'
    }
    
    return enhanced_result


# Instancia global del handler
non_classifiable_handler = NonClassifiableHandler()