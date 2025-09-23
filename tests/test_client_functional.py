#!/usr/bin/env python3
"""
test_client_functional.py - Tests funcionales para el cliente de clasificación
Prueba funciones del cliente sin necesidad de API REST corriendo
"""
import time
from unittest.mock import patch, Mock
from client.classify_standard_api import classify

class TestClientFunctional:
    """Tests funcionales para el cliente de clasificación"""
    
    @patch('client.classify_standard_api.client')
    def test_classify_function_basic_workflow(self, mock_client):
        """Test del flujo básico de clasificación con mocks"""
        # Arrange - Mock de respuesta OpenAI
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "search_text": "yogur natural",
            "concept_uri": "https://treew.io/taxonomy/concept/111206",
            "prefLabel": "Yogur y sustitutos",
            "notation": "111206",
            "level": 1,
            "confidence": 0.95,
            "product_id": "TEST-001"
        }
        '''
        mock_response.choices[0].message.function_call = None
        mock_response.model = "gpt-4o-mini-2024-07-18"
        mock_response.usage.prompt_tokens = 1000
        mock_response.usage.completion_tokens = 150
        mock_response.usage.total_tokens = 1150
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Act
        result = classify("yogur natural griego", "TEST-001")
        
        # Assert
        assert isinstance(result, dict)
        assert "search_text" in result
        assert "concept_uri" in result
        assert "prefLabel" in result
        assert "confidence" in result
        assert "product_id" in result
        assert "openai_cost" in result
        
        # Verificar contenido específico
        assert result["product_id"] == "TEST-001"
        assert result["search_text"] == "yogur natural"
        assert 0 <= result["confidence"] <= 1
        
        # Verificar información de costos
        cost_info = result["openai_cost"]
        assert "model" in cost_info
        assert "usage" in cost_info
        assert "cost_usd" in cost_info
        assert "api_calls" in cost_info
    
    @patch('client.classify_standard_api.client')
    def test_classify_without_product_id(self, mock_client):
        """Test de clasificación sin product_id"""
        # Arrange
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "search_text": "pan integral",
            "concept_uri": "https://treew.io/taxonomy/concept/111301",
            "prefLabel": "Pan y productos de panadería",
            "notation": "111301",
            "level": 1,
            "confidence": 0.88
        }
        '''
        mock_response.choices[0].message.function_call = None
        mock_response.model = "gpt-4o-mini"
        mock_response.usage.prompt_tokens = 800
        mock_response.usage.completion_tokens = 120
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Act
        result = classify("pan integral de centeno")
        
        # Assert
        # Cuando no se proporciona product_id, el resultado puede no incluir el campo
        assert "search_text" in result
        assert "concept_uri" in result
        assert result["search_text"] == "pan integral"
    
    @patch('client.classify_standard_api.client')
    @patch('client.classify_standard_api.search_concepts')
    def test_classify_with_function_calls(self, mock_search, mock_client):
        """Test de clasificación con llamadas a funciones"""
        # Arrange - Simular llamada a función search_concepts
        mock_search.return_value = [
            {
                "uri": "https://treew.io/taxonomy/concept/111206",
                "prefLabel": "Yogur y sustitutos",
                "score": 0.95
            }
        ]
        
        # Primera respuesta con function_call
        first_response = Mock()
        first_response.choices = [Mock()]
        first_response.choices[0].message.function_call = Mock()
        first_response.choices[0].message.function_call.name = "search_concepts"
        first_response.choices[0].message.function_call.arguments = '{"query": "yogur", "k": 10}'
        first_response.choices[0].message.content = None
        first_response.model = "gpt-4o-mini"
        first_response.usage.prompt_tokens = 500
        first_response.usage.completion_tokens = 25
        
        # Segunda respuesta con resultado final
        second_response = Mock()
        second_response.choices = [Mock()]
        second_response.choices[0].message.function_call = None
        second_response.choices[0].message.content = '''
        {
            "search_text": "yogur natural",
            "concept_uri": "https://treew.io/taxonomy/concept/111206",
            "prefLabel": "Yogur y sustitutos",
            "notation": "111206",
            "level": 1,
            "confidence": 0.95
        }
        '''
        second_response.model = "gpt-4o-mini"
        second_response.usage.prompt_tokens = 600
        second_response.usage.completion_tokens = 100
        
        # Configurar mock para devolver respuestas en secuencia
        mock_client.chat.completions.create.side_effect = [first_response, second_response]
        
        # Act
        result = classify("yogur natural griego")
        
        # Assert
        assert "concept_uri" in result
        assert result["concept_uri"] == "https://treew.io/taxonomy/concept/111206"
        
        # Verificar que se hicieron múltiples llamadas a la API
        cost_info = result["openai_cost"]
        assert cost_info["api_calls"] == 2
        
        # Verificar que search_concepts fue llamado
        mock_search.assert_called_once()
    
    @patch('client.classify_standard_api.client')
    def test_classify_error_handling(self, mock_client):
        """Test de manejo de errores en clasificación"""
        # Arrange - Simular error de OpenAI
        mock_client.chat.completions.create.side_effect = Exception("OpenAI API Error")
        
        # Act & Assert - El cliente actual no maneja errores, así que esperamos que la excepción se propague
        import pytest
        with pytest.raises(Exception, match="OpenAI API Error"):
            classify("producto de prueba", "ERROR-001")
    
    @patch('client.classify_standard_api.client')
    def test_classify_invalid_json_response(self, mock_client):
        """Test de manejo de respuesta JSON inválida"""
        # Arrange
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is not valid JSON"
        mock_response.choices[0].message.function_call = None
        mock_response.model = "gpt-4o-mini"
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Act
        result = classify("test product", "JSON-ERROR-001")
        
        # Assert
        assert "error" in result
        assert result["product_id"] == "JSON-ERROR-001"
        assert "JSON" in result["error"] or "parse" in result["error"].lower()
    
    @patch('client.classify_standard_api.client')
    def test_cost_tracking_accuracy(self, mock_client):
        """Test de precisión en el tracking de costos"""
        # Arrange
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"search_text": "test", "concept_uri": "test", "prefLabel": "Test", "confidence": 0.8}'
        mock_response.choices[0].message.function_call = None
        mock_response.model = "gpt-4o-mini-2024-07-18"
        mock_response.usage.prompt_tokens = 1000
        mock_response.usage.completion_tokens = 200
        mock_response.usage.total_tokens = 1200
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Act
        result = classify("producto de prueba")
        
        # Assert
        cost_info = result["openai_cost"]
        
        # Verificar estructura
        assert "model" in cost_info
        assert "usage" in cost_info
        assert "cost_usd" in cost_info
        assert "api_calls" in cost_info
        
        # Verificar valores
        assert cost_info["model"] == "gpt-4o-mini-2024-07-18"
        assert cost_info["usage"]["prompt_tokens"] == 1000
        assert cost_info["usage"]["completion_tokens"] == 200
        assert cost_info["usage"]["total_tokens"] == 1200
        assert cost_info["api_calls"] == 1
        
        # Verificar que los costos son calculados correctamente
        assert cost_info["cost_usd"]["total"] > 0
        assert cost_info["cost_usd"]["prompt"] > 0
        assert cost_info["cost_usd"]["completion"] > 0

class TestClientEdgeCases:
    """Tests de casos extremos para el cliente"""
    
    @patch('client.classify_standard_api.client')
    def test_empty_text_handling(self, mock_client):
        """Test de manejo de texto vacío"""
        # Arrange
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"search_text": "", "error": "Texto vacío"}'
        mock_response.choices[0].message.function_call = None
        mock_response.model = "gpt-4o-mini"
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 25
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Act
        result = classify("", "EMPTY-001")
        
        # Assert
        assert result["product_id"] == "EMPTY-001"
        # El resultado puede ser exitoso o con error, dependiendo de la implementación
        assert "search_text" in result
    
    @patch('client.classify_standard_api.client')
    def test_very_long_text_handling(self, mock_client):
        """Test de manejo de texto muy largo"""
        # Arrange
        long_text = "producto " * 1000  # Texto muy largo
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"search_text": "producto repetido", "concept_uri": "test", "prefLabel": "Test Product", "confidence": 0.7}'
        mock_response.choices[0].message.function_call = None
        mock_response.model = "gpt-4o-mini"
        mock_response.usage.prompt_tokens = 2000
        mock_response.usage.completion_tokens = 100
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Act
        result = classify(long_text, "LONG-001")
        
        # Assert
        assert result["product_id"] == "LONG-001"
        assert "concept_uri" in result
        
        # Verificar que el costo es proporcional al texto largo
        cost_info = result["openai_cost"]
        assert cost_info["usage"]["prompt_tokens"] > 1000  # Debería usar muchos tokens
    
    @patch('client.classify_standard_api.client')
    def test_special_characters_handling(self, mock_client):
        """Test de manejo de caracteres especiales"""
        # Arrange
        special_text = "café ñoño piña 100% orgánico & natural (premium)"
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = f'{{"search_text": "{special_text}", "concept_uri": "test", "prefLabel": "Café", "confidence": 0.9}}'
        mock_response.choices[0].message.function_call = None
        mock_response.model = "gpt-4o-mini"
        mock_response.usage.prompt_tokens = 200
        mock_response.usage.completion_tokens = 80
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Act
        result = classify(special_text, "SPECIAL-001")
        
        # Assert
        assert result["product_id"] == "SPECIAL-001"
        assert "concept_uri" in result
        # Verificar que maneja caracteres especiales correctamente
        assert special_text in result["search_text"]

class TestClientPerformance:
    """Tests de rendimiento del cliente"""
    
    @patch('client.classify_standard_api.client')
    def test_response_time_tracking(self, mock_client):
        """Test de tracking del tiempo de respuesta"""
        # Arrange
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"search_text": "test", "concept_uri": "test", "prefLabel": "Test", "confidence": 0.8}'
        mock_response.choices[0].message.function_call = None
        mock_response.model = "gpt-4o-mini"
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        
        # Simular un pequeño delay
        def mock_create_with_delay(*args, **kwargs):
            import time
            time.sleep(0.1)  # 100ms delay
            return mock_response
        
        mock_client.chat.completions.create.side_effect = mock_create_with_delay
        
        # Act
        start_time = time.time()
        result = classify("test product")
        end_time = time.time()
        
        # Assert
        actual_time = end_time - start_time
        assert actual_time >= 0.1  # Al menos el delay simulado
        
        # Verificar que la clasificación fue exitosa
        assert "concept_uri" in result
        assert "openai_cost" in result
    
    @patch('client.classify_standard_api.client')
    def test_multiple_classifications_consistency(self, mock_client):
        """Test de consistencia en múltiples clasificaciones"""
        # Arrange
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"search_text": "yogur", "concept_uri": "test-uri", "prefLabel": "Yogur", "confidence": 0.9}'
        mock_response.choices[0].message.function_call = None
        mock_response.model = "gpt-4o-mini"
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Act - Clasificar el mismo producto múltiples veces
        results = []
        for i in range(3):
            result = classify("yogur natural", f"CONSISTENCY-{i:03d}")
            results.append(result)
        
        # Assert
        assert len(results) == 3
        
        # Verificar que todos fueron exitosos
        for result in results:
            assert "concept_uri" in result
            assert "openai_cost" in result
            assert result["concept_uri"] == "test-uri"
        
        # Verificar que los IDs son diferentes
        product_ids = [r["product_id"] for r in results]
        assert len(set(product_ids)) == 3  # Todos únicos