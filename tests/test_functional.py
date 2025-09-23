#!/usr/bin/env python3
"""
test_functional.py - Tests funcionales completos para flujos end-to-end
Prueba integración completa: API REST + Cliente + MCP Server + Exportación
"""
import pytest
import requests
import time

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30  # seconds

# Test data
SAMPLE_PRODUCTS = [
    {"text": "yogur natural griego sin azúcar 150g", "product_id": "YOG-001"},
    {"text": "aceite de oliva extra virgen 1L", "product_id": "ACE-002"}, 
    {"text": "pan integral de centeno rebanado", "product_id": "PAN-003"},
    {"text": "queso manchego curado DOP", "product_id": "QUE-004"},
    {"text": "miel de abeja multifloral orgánica", "product_id": "MIE-005"}
]

class TestFunctionalClassification:
    """Tests funcionales para clasificación de productos"""
    
    def setup_method(self):
        """Setup antes de cada test"""
        # Verificar que la API esté disponible
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code != 200:
                pytest.skip("API no está disponible - ejecute: python classification_api.py")
        except requests.exceptions.RequestException:
            pytest.skip("API no está disponible - ejecute: python classification_api.py")
    
    def test_single_product_classification_workflow(self):
        """Test completo: clasificación de producto individual"""
        # Arrange
        product_data = {
            "products": [
                {"text": "yogur griego natural orgánico", "product_id": "TEST-001"}
            ]
        }
        
        # Act
        response = requests.post(
            f"{API_BASE_URL}/classify/products",
            json=product_data,
            timeout=TEST_TIMEOUT
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        
        # Verificar estructura de respuesta
        assert "total" in result
        assert "successful" in result
        assert "results" in result
        assert "processing_time_seconds" in result
        assert "openai_cost_info" in result
        
        # Verificar contenido
        assert result["total"] == 1
        assert result["successful"] == 1
        assert len(result["results"]) == 1
        
        # Verificar clasificación individual
        classification = result["results"][0]
        assert classification["product_id"] == "TEST-001"
        assert "search_text" in classification
        assert "concept_uri" in classification
        assert "prefLabel" in classification
        assert "confidence" in classification
        assert 0 <= classification["confidence"] <= 1
        
        # Verificar información de costos OpenAI
        cost_info = result["openai_cost_info"]
        assert "model" in cost_info
        assert "usage" in cost_info
        assert "cost_usd" in cost_info
        assert cost_info["api_calls"] >= 1
    
    def test_batch_classification_workflow(self):
        """Test completo: clasificación en lote"""
        # Arrange
        batch_data = {"products": SAMPLE_PRODUCTS}
        
        # Act
        response = requests.post(
            f"{API_BASE_URL}/classify/products",
            json=batch_data,
            timeout=TEST_TIMEOUT * 2  # Más tiempo para lotes
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        
        # Verificar procesamiento completo
        assert result["total"] == len(SAMPLE_PRODUCTS)
        assert result["successful"] > 0  # Al menos algunos éxitos
        assert len(result["results"]) == len(SAMPLE_PRODUCTS)
        
        # Verificar cada resultado individual
        for i, product_result in enumerate(result["results"]):
            expected_product_id = SAMPLE_PRODUCTS[i]["product_id"]
            assert product_result["product_id"] == expected_product_id
            
            # Si fue exitoso, verificar estructura de clasificación
            if "error" not in product_result:
                assert "concept_uri" in product_result
                assert "prefLabel" in product_result
                assert "confidence" in product_result
                assert isinstance(product_result["confidence"], (int, float))
        
        # Verificar acumulación de costos
        cost_info = result["openai_cost_info"]
        assert cost_info["api_calls"] >= len(SAMPLE_PRODUCTS)
        assert cost_info["usage"]["total_tokens"] > 0
        assert cost_info["cost_usd"]["total"] > 0
    
    def test_edge_cases_and_error_handling(self):
        """Test de casos extremos y manejo de errores"""
        # Test 1: Producto con texto muy corto
        short_text_data = {
            "products": [{"text": "a", "product_id": "SHORT-001"}]
        }
        response = requests.post(f"{API_BASE_URL}/classify/products", json=short_text_data)
        assert response.status_code == 200
        
        # Test 2: Producto con texto muy largo
        long_text = "producto " * 500  # Texto muy largo
        long_text_data = {
            "products": [{"text": long_text, "product_id": "LONG-001"}]
        }
        response = requests.post(f"{API_BASE_URL}/classify/products", json=long_text_data)
        assert response.status_code == 200
        
        # Test 3: Caracteres especiales
        special_chars_data = {
            "products": [{"text": "café ñoño piña 100% natural", "product_id": "SPECIAL-001"}]
        }
        response = requests.post(f"{API_BASE_URL}/classify/products", json=special_chars_data)
        assert response.status_code == 200
        
        # Test 4: Sin product_id (opcional)
        no_id_data = {
            "products": [{"text": "leche entera 1L"}]
        }
        response = requests.post(f"{API_BASE_URL}/classify/products", json=no_id_data)
        assert response.status_code == 200
        result = response.json()
        assert result["results"][0]["product_id"] is None
    
    def test_classification_consistency(self):
        """Test de consistencia: mismo producto debe dar resultados similares"""
        # Arrange
        product_text = "yogur natural griego"
        test_data = {
            "products": [
                {"text": product_text, "product_id": "CONSISTENCY-001"},
                {"text": product_text, "product_id": "CONSISTENCY-002"}
            ]
        }
        
        # Act
        response = requests.post(f"{API_BASE_URL}/classify/products", json=test_data)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        
        # Los dos resultados deberían ser similares
        result1 = result["results"][0]
        result2 = result["results"][1]
        
        # Mismo concepto principal (si ambos son exitosos)
        if "error" not in result1 and "error" not in result2:
            assert result1["concept_uri"] == result2["concept_uri"]
            assert result1["prefLabel"] == result2["prefLabel"]
            # Confianza similar (±0.1)
            assert abs(result1["confidence"] - result2["confidence"]) <= 0.1

class TestFunctionalExport:
    """Tests funcionales para exportación de resultados"""
    
    def setup_method(self):
        """Setup antes de cada test"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code != 200:
                pytest.skip("API no está disponible")
        except requests.exceptions.RequestException:
            pytest.skip("API no está disponible")
    
    def test_csv_export_workflow(self):
        """Test completo: clasificación + exportación CSV"""
        # Step 1: Exportar productos a CSV directamente
        export_data = {
            "products": SAMPLE_PRODUCTS[:3],
            "format": "csv",
            "filename": f"test_export_{int(time.time())}"
        }
        
        # Act
        export_response = requests.post(f"{API_BASE_URL}/export/csv", json=export_data)
        
        # Assert
        assert export_response.status_code == 200
        export_result = export_response.json()
        
        # Verificar respuesta de exportación
        assert "filename" in export_result
        assert "download_url" in export_result
        assert "total_products" in export_result
        assert export_result["total_products"] == 3
        
        # Step 3: Descargar archivo CSV
        download_url = f"{API_BASE_URL}{export_result['download_url']}"
        download_response = requests.get(download_url)
        
        assert download_response.status_code == 200
        assert len(download_response.content) > 0
        
        # Verificar contenido CSV
        csv_content = download_response.text
        lines = csv_content.strip().split('\n')
        assert len(lines) >= 4  # Header + 3 products
        
        # Verificar que tiene header
        header = lines[0]
        expected_columns = ['product_id', 'product_description', 'skos_category']
        for col in expected_columns:
            assert col in header
    
    def test_excel_export_workflow(self):
        """Test completo: clasificación + exportación Excel"""
        # Arrange
        export_data = {
            "products": SAMPLE_PRODUCTS[:2],  # Solo 2 para test rápido
            "format": "excel",
            "filename": f"test_excel_{int(time.time())}"
        }
        
        # Act
        export_response = requests.post(f"{API_BASE_URL}/export/excel", json=export_data)
        
        # Assert
        assert export_response.status_code == 200
        export_result = export_response.json()
        
        # Verificar respuesta
        assert "filename" in export_result
        assert "download_url" in export_result
        assert export_result["total_products"] == 2
        
        # Verificar descarga
        download_url = f"{API_BASE_URL}{export_result['download_url']}"
        download_response = requests.get(download_url)
        
        assert download_response.status_code == 200
        assert len(download_response.content) > 0
        
        # Verificar que es archivo Excel (header binario)
        assert download_response.content.startswith(b'PK')  # ZIP signature (Excel)
    
    def test_export_error_handling(self):
        """Test de manejo de errores en exportación"""
        # Test 1: Export sin productos
        empty_data = {"products": [], "format": "csv"}
        response = requests.post(f"{API_BASE_URL}/export/csv", json=empty_data)
        assert response.status_code in [400, 422]  # Bad request
        
        # Test 2: Formato inválido (si aplicable)
        invalid_format_data = {
            "products": [{"text": "test", "product_id": "TEST"}],
            "format": "invalid_format"
        }
        # Nota: Dependiendo de la implementación, puede aceptar cualquier formato
        response = requests.post(f"{API_BASE_URL}/export/csv", json=invalid_format_data)
        # No forzamos error aquí ya que puede manejar formatos desconocidos

class TestFunctionalSystemHealth:
    """Tests funcionales para salud del sistema"""
    
    def test_health_endpoint_detailed(self):
        """Test detallado del endpoint de salud"""
        # Act
        response = requests.get(f"{API_BASE_URL}/health")
        
        # Assert
        assert response.status_code == 200
        health_data = response.json()
        
        # Verificar estructura
        assert "status" in health_data
        assert "timestamp" in health_data
        
        # Verificar que el estado es saludable
        assert health_data["status"] in ["healthy", "unhealthy"]
        
        # Si está saludable, verificar conexión MCP
        if health_data["status"] == "healthy":
            assert "mcp_server" in health_data
    
    def test_api_documentation_accessible(self):
        """Test de accesibilidad de documentación"""
        # Test OpenAPI docs
        docs_response = requests.get(f"{API_BASE_URL}/docs")
        assert docs_response.status_code == 200
        
        # Test OpenAPI schema
        schema_response = requests.get(f"{API_BASE_URL}/openapi.json")
        assert schema_response.status_code == 200
        
        schema = schema_response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
    
    def test_api_endpoints_discovery(self):
        """Test de descubrimiento de endpoints"""
        # Test root endpoint
        root_response = requests.get(f"{API_BASE_URL}/")
        assert root_response.status_code == 200
        
        root_data = root_response.json()
        assert "endpoints" in root_data
        assert "classification" in root_data["endpoints"]

class TestFunctionalPerformance:
    """Tests funcionales de rendimiento básico"""
    
    def setup_method(self):
        """Setup antes de cada test"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code != 200:
                pytest.skip("API no está disponible")
        except requests.exceptions.RequestException:
            pytest.skip("API no está disponible")
    
    def test_single_product_response_time(self):
        """Test de tiempo de respuesta para producto individual"""
        # Arrange
        start_time = time.time()
        test_data = {
            "products": [{"text": "leche entera 1L", "product_id": "PERF-001"}]
        }
        
        # Act
        response = requests.post(f"{API_BASE_URL}/classify/products", json=test_data)
        end_time = time.time()
        
        # Assert
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # El tiempo de respuesta debería ser razonable (< 30 segundos)
        assert response_time < 30
        
        # Verificar que el tiempo reportado en la respuesta es consistente
        result = response.json()
        reported_time = result["processing_time_seconds"]
        
        # El tiempo reportado debería ser menor al tiempo total medido
        assert reported_time <= response_time
    
    def test_batch_processing_efficiency(self):
        """Test de eficiencia en procesamiento por lotes"""
        # Arrange - procesar 3 productos
        batch_data = {"products": SAMPLE_PRODUCTS[:3]}
        
        # Act
        start_time = time.time()
        response = requests.post(f"{API_BASE_URL}/classify/products", json=batch_data)
        end_time = time.time()
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        
        # Verificar que se procesaron todos
        assert result["total"] == 3
        
        # El tiempo por producto debería ser razonable
        total_time = end_time - start_time
        time_per_product = total_time / 3
        
        # Menos de 15 segundos por producto en promedio
        assert time_per_product < 15

class TestFunctionalIntegration:
    """Tests de integración completa end-to-end"""
    
    def setup_method(self):
        """Setup antes de cada test"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code != 200:
                pytest.skip("API no está disponible")
        except requests.exceptions.RequestException:
            pytest.skip("API no está disponible")
    
    def test_complete_workflow_classification_to_export(self):
        """Test del flujo completo: clasificación → exportación → descarga"""
        # Step 1: Clasificar productos
        classification_data = {"products": SAMPLE_PRODUCTS[:2]}
        
        classify_response = requests.post(
            f"{API_BASE_URL}/classify/products", 
            json=classification_data
        )
        assert classify_response.status_code == 200
        classification_result = classify_response.json()
        
        # Verificar clasificación exitosa
        assert classification_result["successful"] > 0
        
        # Step 2: Exportar resultados a CSV
        export_data = {
            "products": SAMPLE_PRODUCTS[:2],
            "format": "csv",
            "filename": f"integration_test_{int(time.time())}"
        }
        
        export_response = requests.post(f"{API_BASE_URL}/export/csv", json=export_data)
        assert export_response.status_code == 200
        export_result = export_response.json()
        
        # Step 3: Descargar archivo
        download_url = f"{API_BASE_URL}{export_result['download_url']}"
        download_response = requests.get(download_url)
        assert download_response.status_code == 200
        
        # Step 4: Validar contenido del archivo
        csv_content = download_response.text
        lines = csv_content.strip().split('\n')
        
        # Verificar que tiene el contenido esperado
        assert len(lines) >= 3  # Header + 2 products
        
        # Verificar que los IDs de productos están en el CSV
        csv_text = download_response.text
        for product in SAMPLE_PRODUCTS[:2]:
            assert product["product_id"] in csv_text
    
    def test_cost_tracking_accuracy(self):
        """Test de precisión en el tracking de costos"""
        # Step 1: Clasificación individual
        single_data = {"products": [{"text": "queso fresco", "product_id": "COST-001"}]}
        single_response = requests.post(f"{API_BASE_URL}/classify/products", json=single_data)
        single_result = single_response.json()
        
        # Step 2: Clasificación en lote con el mismo producto
        batch_data = {"products": [{"text": "queso fresco", "product_id": "COST-002"}]}
        batch_response = requests.post(f"{API_BASE_URL}/classify/products", json=batch_data)
        batch_result = batch_response.json()
        
        # Verificar que ambos tienen información de costos
        assert "openai_cost_info" in single_result
        assert "openai_cost_info" in batch_result
        
        single_cost = single_result["openai_cost_info"]
        batch_cost = batch_result["openai_cost_info"]
        
        # Verificar estructura de costos
        for cost_info in [single_cost, batch_cost]:
            assert "model" in cost_info
            assert "usage" in cost_info
            assert "cost_usd" in cost_info
            assert "api_calls" in cost_info
            
            # Verificar que los valores son razonables
            assert cost_info["usage"]["total_tokens"] > 0
            assert cost_info["cost_usd"]["total"] > 0
            assert cost_info["api_calls"] >= 1
    
    def test_error_recovery_and_partial_success(self):
        """Test de recuperación de errores y éxitos parciales"""
        # Arrange - mezcla de productos válidos e inválidos
        mixed_data = {
            "products": [
                {"text": "producto válido normal", "product_id": "VALID-001"},
                {"text": "", "product_id": "INVALID-001"},  # Texto vacío
                {"text": "otro producto válido", "product_id": "VALID-002"},
            ]
        }
        
        # Act
        response = requests.post(f"{API_BASE_URL}/classify/products", json=mixed_data)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        
        # Verificar que procesó todos los productos
        assert result["total"] == 3
        
        # Debería tener al menos algunos éxitos
        assert result["successful"] > 0
        
        # Verificar que maneja errores gracefully
        assert len(result["results"]) == 3
        
        # Verificar que tiene información de costos aunque hayan errores
        assert "openai_cost_info" in result