"""
🧪 Tests para el manejo mejorado de productos no clasificables
===========================================================
Tests que validan el correcto funcionamiento del sistema mejorado
para productos fuera del dominio de la taxonomía.
"""

import pytest
import requests
import json
from datetime import datetime


class TestNonClassifiableProducts:
    """Tests para productos no clasificables"""
    
    def setup_method(self):
        """Configuración inicial"""
        self.api_base = "http://localhost:8000"
        
    def test_textile_product_in_food_taxonomy(self):
        """Test del caso específico: camiseta de algodón en taxonomía alimentaria"""
        
        # Payload del caso reportado
        payload = {
            "products": [
                {
                    "text": "Camiseta de algodon",
                    "product_id": "sku-09876"
                }
            ]
        }
        
        # Hacer petición al endpoint mejorado
        response = requests.post(
            f"{self.api_base}/classify/products/enhanced?taxonomy=treew-skos",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Verificar estructura de respuesta
        assert "total" in result
        assert "successful" in result
        assert "not_classifiable" in result
        assert "domain_mismatches" in result
        assert "results" in result
        
        # Verificar que se detectó como no clasificable
        assert result["successful"] == 0
        assert result["not_classifiable"] == 1
        assert result["domain_mismatches"] == 1
        
        # Verificar análisis detallado
        product_result = result["results"][0]
        assert product_result["status"] == "not_classifiable"
        assert "enhanced_analysis" in product_result
        
        enhanced = product_result["enhanced_analysis"]
        assert enhanced["classification_result"] == "not_classifiable"
        assert enhanced["reason"] == "domain_mismatch"
        assert enhanced["product_analysis"]["detected_domain"] == "textil"
        assert enhanced["taxonomy_info"]["domain"] == "alimentaria"
        
        # Verificar sugerencias
        assert "suggestions" in enhanced
        assert len(enhanced["suggestions"]["taxonomy_recommendations"]) > 0
        
        print("✅ Test de incompatibilidad dominio/taxonomía exitoso")
        
    def test_multiple_domains_mixed(self):
        """Test con productos de múltiples dominios mezclados"""
        
        payload = {
            "products": [
                {"text": "Yogur natural griego", "product_id": "food-001"},
                {"text": "Camiseta de algodón", "product_id": "textile-001"},
                {"text": "Aceite de oliva virgen", "product_id": "food-002"},
                {"text": "Smartphone Android", "product_id": "electronics-001"},
                {"text": "Pan integral de centeno", "product_id": "food-003"}
            ]
        }
        
        response = requests.post(
            f"{self.api_base}/classify/products/enhanced?taxonomy=treew-skos",
            json=payload
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Debería haber algunos exitosos (alimentos) y otros no clasificables
        assert result["successful"] >= 2  # Al menos yogur, aceite, pan
        assert result["not_classifiable"] >= 2  # Al menos camiseta, smartphone
        assert result["total"] == 5
        
        # Verificar tasa de éxito
        success_rate = result["processing_summary"]["success_rate"]
        assert 40 <= success_rate <= 80  # Entre 40-80% de éxito esperado
        
        print("✅ Test de dominios mezclados exitoso")
        
    def test_enhanced_recommendations(self):
        """Test de generación de recomendaciones"""
        
        payload = {
            "products": [
                {"text": "Televisor LED 55 pulgadas", "product_id": "tv-001"},
                {"text": "Pantalón vaquero azul", "product_id": "jeans-001"},
                {"text": "Mesa de comedor madera", "product_id": "furniture-001"}
            ]
        }
        
        response = requests.post(
            f"{self.api_base}/classify/products/enhanced?taxonomy=treew-skos",
            json=payload
        )
        
        result = response.json()
        
        # Todos deberían ser no clasificables
        assert result["not_classifiable"] == 3
        assert result["successful"] == 0
        
        # Verificar recomendaciones del lote
        assert "recommendations" in result
        recommendations = result["recommendations"]["suggested_actions"]
        
        # Debería sugerir cambio de taxonomía por baja tasa de éxito
        assert any("taxonomía" in rec.lower() for rec in recommendations)
        
        print("✅ Test de recomendaciones exitoso")
        
    def test_single_product_enhanced_endpoint(self):
        """Test del endpoint individual mejorado"""
        
        payload = {
            "text": "Auriculares inalámbricos Bluetooth",
            "product_id": "headphones-001"
        }
        
        response = requests.post(
            f"{self.api_base}/classify/enhanced?taxonomy=treew-skos",
            json=payload
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Verificar que se detectó como no clasificable
        assert result["classification_result"] == "not_classifiable"
        assert result["reason"] == "domain_mismatch"
        assert result["product_analysis"]["detected_domain"] == "electrónica"
        
        # Verificar sugerencias específicas
        suggestions = result["suggestions"]
        assert "taxonomy_recommendations" in suggestions
        assert len(suggestions["taxonomy_recommendations"]) > 0
        
        print("✅ Test de endpoint individual mejorado exitoso")
        
    def test_comparison_with_original_endpoint(self):
        """Comparar respuesta original vs mejorada"""
        
        product_data = {
            "text": "Camiseta de algodón",
            "product_id": "test-comparison"
        }
        
        # Endpoint original
        original_response = requests.post(
            f"{self.api_base}/classify",
            json=product_data
        )
        
        # Endpoint mejorado
        enhanced_response = requests.post(
            f"{self.api_base}/classify/enhanced?taxonomy=treew-skos",
            json=product_data
        )
        
        original_result = original_response.json()
        enhanced_result = enhanced_response.json()
        
        # El original debería tener error genérico
        assert "error" in original_result
        
        # El mejorado debería tener análisis detallado
        assert enhanced_result["classification_result"] == "not_classifiable"
        assert "explanation" in enhanced_result
        assert "suggestions" in enhanced_result
        assert "product_analysis" in enhanced_result
        
        print("✅ Comparación original vs mejorado exitosa")
        print(f"Original: {original_result.get('error', 'N/A')}")
        print(f"Mejorado: {enhanced_result.get('explanation', 'N/A')}")


def test_api_availability():
    """Test básico de disponibilidad de API"""
    try:
        response = requests.get("http://localhost:8000/health")
        assert response.status_code == 200
        print("✅ API está disponible")
        return True
    except Exception as e:
        print(f"❌ API no disponible: {e}")
        return False


if __name__ == "__main__":
    print("🧪 EJECUTANDO TESTS DE PRODUCTOS NO CLASIFICABLES")
    print("=" * 60)
    
    # Verificar disponibilidad de API
    if not test_api_availability():
        print("❌ No se puede ejecutar tests - API no disponible")
        exit(1)
    
    # Ejecutar tests
    test_suite = TestNonClassifiableProducts()
    test_suite.setup_method()
    
    try:
        print("\n1️⃣ Probando caso específico: camiseta en taxonomía alimentaria...")
        test_suite.test_textile_product_in_food_taxonomy()
        
        print("\n2️⃣ Probando productos de múltiples dominios...")
        test_suite.test_multiple_domains_mixed()
        
        print("\n3️⃣ Probando generación de recomendaciones...")
        test_suite.test_enhanced_recommendations()
        
        print("\n4️⃣ Probando endpoint individual mejorado...")
        test_suite.test_single_product_enhanced_endpoint()
        
        print("\n5️⃣ Comparando endpoint original vs mejorado...")
        test_suite.test_comparison_with_original_endpoint()
        
        print("\n🎉 TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
        
    except Exception as e:
        print(f"\n❌ ERROR EN TESTS: {e}")
        import traceback
        traceback.print_exc()
        exit(1)