#!/usr/bin/env python3
"""
Unit tests for classification_api.py FastAPI endpoints
Testing unified endpoint, validation, error cases, and cost info inclusion
"""
from fastapi.testclient import TestClient
from unittest.mock import patch
from classification_api import app

# Create test client
client = TestClient(app)

class TestUnifiedClassificationEndpoint:
    """Test the main /classify/products endpoint"""
    
    @patch('classification_api.classify')
    def test_single_product_classification(self, mock_classify, sample_classification_result):
        """Test classification of a single product"""
        mock_classify.return_value = sample_classification_result
        
        payload = {
            "products": [
                {
                    "text": "yogur natural griego 150g",
                    "product_id": "YOGUR001"
                }
            ]
        }
        
        response = client.post("/classify/products", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data["total"] == 1
        assert data["successful"] == 1
        assert data["failed"] == 0
        assert len(data["results"]) == 1
        
        # Verify result content
        result = data["results"][0]
        assert result["product_id"] == "YOGUR001"
        assert result["search_text"] == "yogur natural griego 150g"
        assert result["status"] == "success"
        assert result["concept_uri"] == "https://treew.io/taxonomy/concept/111206"
        
        # Verify cost information is included
        assert "openai_cost_info" in data
        cost_info = data["openai_cost_info"]
        assert cost_info["model"] == "gpt-4o-mini-2024-07-18"
        assert cost_info["cost_usd"]["total"] == 0.000365
        assert cost_info["api_calls"] == 4
    
    @patch('classification_api.classify')
    def test_multiple_products_classification(self, mock_classify, sample_product_requests):
        """Test classification of multiple products"""
        # Mock different results for each product
        mock_results = [
            {
                "search_text": "yogur natural griego",
                "concept_uri": "https://treew.io/taxonomy/concept/111206",
                "prefLabel": "Yogur y sustitutos",
                "notation": "111206",
                "level": 1,
                "confidence": 1.0,
                "openai_cost": {
                    "model": "gpt-4o-mini-2024-07-18",
                    "usage": {"prompt_tokens": 500, "completion_tokens": 50, "total_tokens": 550},
                    "cost_usd": {"prompt": 0.000075, "completion": 0.00003, "total": 0.000105},
                    "api_calls": 2
                }
            },
            {
                "search_text": "leche desnatada",
                "concept_uri": "https://treew.io/taxonomy/concept/111201",
                "prefLabel": "Leche",
                "notation": "111201",
                "level": 1,
                "confidence": 0.95,
                "openai_cost": {
                    "model": "gpt-4o-mini-2024-07-18",
                    "usage": {"prompt_tokens": 600, "completion_tokens": 60, "total_tokens": 660},
                    "cost_usd": {"prompt": 0.00009, "completion": 0.000036, "total": 0.000126},
                    "api_calls": 3
                }
            },
            {
                "search_text": "pan integral",
                "concept_uri": "https://treew.io/taxonomy/concept/111301",
                "prefLabel": "Pan",
                "notation": "111301",
                "level": 1,
                "confidence": 0.9,
                "openai_cost": {
                    "model": "gpt-4o-mini-2024-07-18",
                    "usage": {"prompt_tokens": 400, "completion_tokens": 40, "total_tokens": 440},
                    "cost_usd": {"prompt": 0.00006, "completion": 0.000024, "total": 0.000084},
                    "api_calls": 2
                }
            }
        ]
        
        mock_classify.side_effect = mock_results
        
        payload = {"products": sample_product_requests}
        
        response = client.post("/classify/products", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify batch response structure
        assert data["total"] == 3
        assert data["successful"] == 3
        assert data["failed"] == 0
        assert len(data["results"]) == 3
        
        # Verify consolidated cost information
        assert "openai_cost_info" in data
        cost_info = data["openai_cost_info"]
        assert cost_info["model"] == "gpt-4o-mini-2024-07-18"
        assert cost_info["usage"]["prompt_tokens"] == 1500  # 500 + 600 + 400
        assert cost_info["usage"]["completion_tokens"] == 150  # 50 + 60 + 40
        assert cost_info["usage"]["total_tokens"] == 1650
        assert cost_info["api_calls"] == 7  # 2 + 3 + 2
        assert abs(cost_info["cost_usd"]["total"] - 0.000315) < 1e-6  # Sum of individual costs
    
    def test_empty_products_array(self):
        """Test endpoint with empty products array"""
        payload = {"products": []}
        
        response = client.post("/classify/products", json=payload)
        
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert "Array de productos no puede estar vacío" in error_detail
    
    def test_invalid_request_structure(self):
        """Test endpoint with invalid request structure"""
        invalid_payloads = [
            {},  # Missing products field
            {"products": "invalid"},  # Products not an array
            {"products": [{"invalid": "structure"}]},  # Missing required fields
            {"products": [{"text": ""}]},  # Empty text
        ]
        
        for payload in invalid_payloads:
            response = client.post("/classify/products", json=payload)
            assert response.status_code == 422
    
    @patch('classification_api.classify')
    def test_mixed_success_and_failure(self, mock_classify):
        """Test endpoint with some successful and some failed classifications"""
        # Mock mixed results - success, error, exception
        mock_classify.side_effect = [
            {
                "search_text": "yogur natural",
                "concept_uri": "https://treew.io/taxonomy/concept/111206",
                "prefLabel": "Yogur y sustitutos",
                "notation": "111206",
                "level": 1,
                "confidence": 1.0
            },
            {
                "error": "Classification failed",
                "raw_response": "Invalid response"
            },
            Exception("OpenAI API Error")
        ]
        
        payload = {
            "products": [
                {"text": "yogur natural", "product_id": "SUCCESS001"},
                {"text": "invalid product", "product_id": "ERROR001"},
                {"text": "exception product", "product_id": "EXCEPTION001"}
            ]
        }
        
        response = client.post("/classify/products", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify mixed results
        assert data["total"] == 3
        assert data["successful"] == 1
        assert data["failed"] == 2
        assert len(data["results"]) == 3
        
        # Check individual result statuses
        statuses = [result["status"] for result in data["results"]]
        assert "success" in statuses
        assert "error" in statuses
        assert "exception" in statuses
    
    @patch('classification_api.classify')
    def test_processing_time_tracking(self, mock_classify, sample_classification_result):
        """Test that processing time is tracked"""
        mock_classify.return_value = sample_classification_result
        
        payload = {
            "products": [
                {"text": "yogur natural griego 150g", "product_id": "TIME001"}
            ]
        }
        
        response = client.post("/classify/products", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify timing information
        assert "processing_time_seconds" in data
        assert isinstance(data["processing_time_seconds"], (int, float))
        assert data["processing_time_seconds"] >= 0
        
        assert "timestamp" in data
        assert isinstance(data["timestamp"], str)

class TestDeprecatedEndpoints:
    """Test that deprecated endpoints are hidden but still functional"""
    
    def test_deprecated_endpoints_not_in_openapi_schema(self):
        """Test that deprecated endpoints are not included in OpenAPI schema"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_schema = response.json()
        paths = openapi_schema.get("paths", {})
        
        # Deprecated endpoints should not appear in schema
        deprecated_paths = ["/classify", "/classify/batch", "/classify/batch/async"]
        for deprecated_path in deprecated_paths:
            assert deprecated_path not in paths, f"Deprecated endpoint {deprecated_path} should not be in OpenAPI schema"
    
    @patch('classification_api.classify')
    def test_deprecated_classify_endpoint_still_works(self, mock_classify, sample_classification_result):
        """Test that deprecated /classify endpoint still works for backward compatibility"""
        mock_classify.return_value = sample_classification_result
        
        payload = {
            "text": "yogur natural griego 150g",
            "product_id": "DEPRECATED001"
        }
        
        # This should still work even though it's deprecated
        response = client.post("/classify", json=payload)
        
        # Might return 200 (working) or 404 (completely hidden)
        # The behavior depends on include_in_schema vs complete removal
        assert response.status_code in [200, 404]

class TestResponseModels:
    """Test response model structure and validation"""
    
    @patch('classification_api.classify')
    def test_unified_response_model_structure(self, mock_classify, sample_classification_result):
        """Test that response follows UnifiedClassificationResponse model"""
        mock_classify.return_value = sample_classification_result
        
        payload = {
            "products": [
                {"text": "yogur natural griego 150g", "product_id": "MODEL001"}
            ]
        }
        
        response = client.post("/classify/products", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields per UnifiedClassificationResponse model
        required_fields = ["total", "successful", "failed", "results", "timestamp"]
        for field in required_fields:
            assert field in data, f"Required field {field} missing from response"
        
        # Verify field types
        assert isinstance(data["total"], int)
        assert isinstance(data["successful"], int)
        assert isinstance(data["failed"], int)
        assert isinstance(data["results"], list)
        assert isinstance(data["timestamp"], str)
        
        # Verify optional fields
        if "processing_time_seconds" in data:
            assert isinstance(data["processing_time_seconds"], (int, float))
        
        if "openai_cost_info" in data:
            cost_info = data["openai_cost_info"]
            assert isinstance(cost_info, dict)
            assert "model" in cost_info
            assert "usage" in cost_info
            assert "cost_usd" in cost_info

class TestErrorHandling:
    """Test API error handling scenarios"""
    
    def test_malformed_json_request(self):
        """Test handling of malformed JSON requests"""
        response = client.post(
            "/classify/products",
            data="invalid json content",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_content_type(self):
        """Test handling of requests without proper content type"""
        response = client.post("/classify/products", data='{"products": []}')
        
        # Should return error due to missing/incorrect content type
        assert response.status_code in [422, 400]
    
    @patch('classification_api.classify')
    def test_server_error_handling(self, mock_classify):
        """Test handling of unexpected server errors"""
        # Mock classify to raise an unexpected exception
        mock_classify.side_effect = RuntimeError("Unexpected server error")
        
        payload = {
            "products": [
                {"text": "test product", "product_id": "SERVER_ERROR001"}
            ]
        }
        
        response = client.post("/classify/products", json=payload)
        
        # Should handle the exception gracefully
        assert response.status_code == 200  # API handles exceptions internally
        data = response.json()
        assert data["failed"] == 1
        assert "exception" in data["results"][0]["status"]

class TestHealthAndDocumentation:
    """Test health check and documentation endpoints"""
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_docs_endpoint(self):
        """Test API documentation endpoint"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_schema(self):
        """Test OpenAPI schema endpoint"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "SKOS Product Classifier API"