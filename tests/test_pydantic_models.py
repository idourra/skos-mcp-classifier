#!/usr/bin/env python3
"""
Unit tests for Pydantic models in classification_api.py
Testing request/response models and their field constraints
"""
import pytest
from pydantic import ValidationError
from classification_api import (
    ProductRequest,
    UnifiedProductRequest,
    OpenAIUsage,
    OpenAICostUSD,
    OpenAICostBreakdown,
    OpenAICostInfo,
    UnifiedClassificationResponse
)

class TestProductRequest:
    """Test ProductRequest model validation"""
    
    def test_valid_product_request(self):
        """Test valid product request creation"""
        product = ProductRequest(
            text="yogur natural griego 150g",
            product_id="YOGUR001"
        )
        
        assert product.text == "yogur natural griego 150g"
        assert product.product_id == "YOGUR001"
    
    def test_product_request_without_id(self):
        """Test product request without product_id (optional field)"""
        product = ProductRequest(text="yogur natural griego 150g")
        
        assert product.text == "yogur natural griego 150g"
        assert product.product_id is None
    
    def test_product_request_empty_text(self):
        """Test product request with empty text"""
        # Empty text should be allowed but might not be useful
        product = ProductRequest(text="", product_id="EMPTY001")
        
        assert product.text == ""
        assert product.product_id == "EMPTY001"
    
    def test_product_request_missing_text(self):
        """Test product request missing required text field"""
        with pytest.raises(ValidationError) as exc_info:
            ProductRequest(product_id="MISSING001")
        
        assert "text" in str(exc_info.value)
    
    def test_product_request_invalid_types(self):
        """Test product request with invalid field types"""
        with pytest.raises(ValidationError):
            ProductRequest(text=123, product_id="INVALID001")
        
        with pytest.raises(ValidationError):
            ProductRequest(text="valid text", product_id=123)

class TestUnifiedProductRequest:
    """Test UnifiedProductRequest model validation"""
    
    def test_valid_unified_request_single_product(self):
        """Test unified request with single product"""
        request = UnifiedProductRequest(
            products=[
                ProductRequest(text="yogur natural", product_id="YOGUR001")
            ]
        )
        
        assert len(request.products) == 1
        assert request.products[0].text == "yogur natural"
    
    def test_valid_unified_request_multiple_products(self):
        """Test unified request with multiple products"""
        products = [
            ProductRequest(text="yogur natural", product_id="YOGUR001"),
            ProductRequest(text="leche desnatada", product_id="LECHE001"),
            ProductRequest(text="pan integral")
        ]
        
        request = UnifiedProductRequest(products=products)
        
        assert len(request.products) == 3
        assert request.products[0].product_id == "YOGUR001"
        assert request.products[1].product_id == "LECHE001"
        assert request.products[2].product_id is None
    
    def test_unified_request_empty_products(self):
        """Test unified request with empty products array"""
        with pytest.raises(ValidationError) as exc_info:
            UnifiedProductRequest(products=[])
        
        # Should fail min_items=1 validation
        assert "at least 1 item" in str(exc_info.value).lower() or "min_items" in str(exc_info.value)
    
    def test_unified_request_missing_products(self):
        """Test unified request missing products field"""
        with pytest.raises(ValidationError) as exc_info:
            UnifiedProductRequest()
        
        assert "products" in str(exc_info.value)

class TestOpenAIUsage:
    """Test OpenAIUsage model validation"""
    
    def test_valid_usage(self):
        """Test valid usage data"""
        usage = OpenAIUsage(
            prompt_tokens=1796,
            completion_tokens=160,
            total_tokens=1956
        )
        
        assert usage.prompt_tokens == 1796
        assert usage.completion_tokens == 160
        assert usage.total_tokens == 1956
    
    def test_usage_zero_values(self):
        """Test usage with zero values"""
        usage = OpenAIUsage(
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0
        )
        
        assert usage.prompt_tokens == 0
        assert usage.completion_tokens == 0
        assert usage.total_tokens == 0
    
    def test_usage_missing_fields(self):
        """Test usage missing required fields"""
        with pytest.raises(ValidationError):
            OpenAIUsage(prompt_tokens=100, completion_tokens=50)  # Missing total_tokens
        
        with pytest.raises(ValidationError):
            OpenAIUsage(total_tokens=150)  # Missing prompt and completion tokens
    
    def test_usage_negative_values(self):
        """Test usage with negative values (should be invalid)"""
        with pytest.raises(ValidationError):
            OpenAIUsage(
                prompt_tokens=-100,
                completion_tokens=50,
                total_tokens=150
            )

class TestOpenAICostUSD:
    """Test OpenAICostUSD model validation"""
    
    def test_valid_cost_usd(self):
        """Test valid cost data"""
        cost = OpenAICostUSD(
            prompt=0.000269,
            completion=0.000096,
            total=0.000365
        )
        
        assert abs(cost.prompt - 0.000269) < 1e-6
        assert abs(cost.completion - 0.000096) < 1e-6
        assert abs(cost.total - 0.000365) < 1e-6
    
    def test_cost_usd_zero_values(self):
        """Test cost with zero values"""
        cost = OpenAICostUSD(
            prompt=0.0,
            completion=0.0,
            total=0.0
        )
        
        assert cost.prompt == 0.0
        assert cost.completion == 0.0
        assert cost.total == 0.0
    
    def test_cost_usd_precision(self):
        """Test cost with high precision values"""
        cost = OpenAICostUSD(
            prompt=0.000000123,
            completion=0.000000456,
            total=0.000000579
        )
        
        assert abs(cost.prompt - 0.000000123) < 1e-9
        assert abs(cost.completion - 0.000000456) < 1e-9
        assert abs(cost.total - 0.000000579) < 1e-9

class TestOpenAICostBreakdown:
    """Test OpenAICostBreakdown model validation"""
    
    def test_valid_cost_breakdown(self):
        """Test valid cost breakdown"""
        breakdown = OpenAICostBreakdown(
            base_model_for_pricing="gpt-4o-mini",
            prompt_cost_per_1m_tokens=0.15,
            completion_cost_per_1m_tokens=0.6,
            calculation_timestamp="2025-09-23T12:05:16.227619"
        )
        
        assert breakdown.base_model_for_pricing == "gpt-4o-mini"
        assert breakdown.prompt_cost_per_1m_tokens == 0.15
        assert breakdown.completion_cost_per_1m_tokens == 0.6
        assert breakdown.calculation_timestamp == "2025-09-23T12:05:16.227619"
    
    def test_cost_breakdown_missing_fields(self):
        """Test cost breakdown missing required fields"""
        with pytest.raises(ValidationError):
            OpenAICostBreakdown(
                base_model_for_pricing="gpt-4o-mini",
                prompt_cost_per_1m_tokens=0.15
                # Missing completion_cost_per_1m_tokens and calculation_timestamp
            )

class TestOpenAICostInfo:
    """Test complete OpenAICostInfo model validation"""
    
    def test_valid_complete_cost_info(self):
        """Test valid complete cost information"""
        usage = OpenAIUsage(
            prompt_tokens=1796,
            completion_tokens=160,
            total_tokens=1956
        )
        
        cost_usd = OpenAICostUSD(
            prompt=0.000269,
            completion=0.000096,
            total=0.000365
        )
        
        cost_breakdown = OpenAICostBreakdown(
            base_model_for_pricing="gpt-4o-mini",
            prompt_cost_per_1m_tokens=0.15,
            completion_cost_per_1m_tokens=0.6,
            calculation_timestamp="2025-09-23T12:05:16.227619"
        )
        
        cost_info = OpenAICostInfo(
            model="gpt-4o-mini-2024-07-18",
            usage=usage,
            cost_usd=cost_usd,
            cost_breakdown=cost_breakdown,
            api_calls=4
        )
        
        assert cost_info.model == "gpt-4o-mini-2024-07-18"
        assert cost_info.usage.total_tokens == 1956
        assert cost_info.cost_usd.total == 0.000365
        assert cost_info.cost_breakdown.base_model_for_pricing == "gpt-4o-mini"
        assert cost_info.api_calls == 4
    
    def test_cost_info_from_dict(self):
        """Test creating cost info from dictionary data"""
        cost_data = {
            "model": "gpt-4o-mini-2024-07-18",
            "usage": {
                "prompt_tokens": 1796,
                "completion_tokens": 160,
                "total_tokens": 1956
            },
            "cost_usd": {
                "prompt": 0.000269,
                "completion": 0.000096,
                "total": 0.000365
            },
            "cost_breakdown": {
                "base_model_for_pricing": "gpt-4o-mini",
                "prompt_cost_per_1m_tokens": 0.15,
                "completion_cost_per_1m_tokens": 0.6,
                "calculation_timestamp": "2025-09-23T12:05:16.227619"
            },
            "api_calls": 4
        }
        
        cost_info = OpenAICostInfo(**cost_data)
        
        assert cost_info.model == "gpt-4o-mini-2024-07-18"
        assert cost_info.api_calls == 4

class TestUnifiedClassificationResponse:
    """Test UnifiedClassificationResponse model validation"""
    
    def test_valid_unified_response_single_result(self):
        """Test valid unified response with single result"""
        response = UnifiedClassificationResponse(
            total=1,
            successful=1,
            failed=0,
            results=[
                {
                    "index": 0,
                    "product_id": "YOGUR001",
                    "search_text": "yogur natural",
                    "concept_uri": "https://treew.io/taxonomy/concept/111206",
                    "prefLabel": "Yogur y sustitutos",
                    "status": "success"
                }
            ],
            timestamp="2025-09-23T12:05:16.227619"
        )
        
        assert response.total == 1
        assert response.successful == 1
        assert response.failed == 0
        assert len(response.results) == 1
    
    def test_unified_response_with_cost_info(self):
        """Test unified response including cost information"""
        cost_info = OpenAICostInfo(
            model="gpt-4o-mini-2024-07-18",
            usage=OpenAIUsage(prompt_tokens=1796, completion_tokens=160, total_tokens=1956),
            cost_usd=OpenAICostUSD(prompt=0.000269, completion=0.000096, total=0.000365),
            cost_breakdown=OpenAICostBreakdown(
                base_model_for_pricing="gpt-4o-mini",
                prompt_cost_per_1m_tokens=0.15,
                completion_cost_per_1m_tokens=0.6,
                calculation_timestamp="2025-09-23T12:05:16.227619"
            ),
            api_calls=4
        )
        
        response = UnifiedClassificationResponse(
            total=1,
            successful=1,
            failed=0,
            results=[{"status": "success"}],
            timestamp="2025-09-23T12:05:16.227619",
            openai_cost_info=cost_info
        )
        
        assert response.openai_cost_info is not None
        assert response.openai_cost_info.model == "gpt-4o-mini-2024-07-18"
        assert response.openai_cost_info.api_calls == 4
    
    def test_unified_response_consistency_validation(self):
        """Test that totals are consistent in unified response"""
        # This would be a business logic validation, not Pydantic validation
        response = UnifiedClassificationResponse(
            total=3,
            successful=2,
            failed=1,
            results=[
                {"status": "success"},
                {"status": "success"},
                {"status": "error"}
            ],
            timestamp="2025-09-23T12:05:16.227619"
        )
        
        # Verify that total = successful + failed
        assert response.total == response.successful + response.failed
        assert len(response.results) == response.total
    
    def test_unified_response_missing_required_fields(self):
        """Test unified response missing required fields"""
        with pytest.raises(ValidationError):
            UnifiedClassificationResponse(
                total=1,
                successful=1
                # Missing failed, results, timestamp
            )

class TestModelSerialization:
    """Test model serialization and deserialization"""
    
    def test_cost_info_json_serialization(self):
        """Test that cost info can be serialized to JSON and back"""
        cost_info = OpenAICostInfo(
            model="gpt-4o-mini-2024-07-18",
            usage=OpenAIUsage(prompt_tokens=1796, completion_tokens=160, total_tokens=1956),
            cost_usd=OpenAICostUSD(prompt=0.000269, completion=0.000096, total=0.000365),
            cost_breakdown=OpenAICostBreakdown(
                base_model_for_pricing="gpt-4o-mini",
                prompt_cost_per_1m_tokens=0.15,
                completion_cost_per_1m_tokens=0.6,
                calculation_timestamp="2025-09-23T12:05:16.227619"
            ),
            api_calls=4
        )
        
        # Serialize to dict
        cost_dict = cost_info.model_dump()
        assert isinstance(cost_dict, dict)
        assert cost_dict["model"] == "gpt-4o-mini-2024-07-18"
        
        # Deserialize back
        cost_info_restored = OpenAICostInfo(**cost_dict)
        assert cost_info_restored.model == cost_info.model
        assert cost_info_restored.api_calls == cost_info.api_calls
    
    def test_unified_response_json_serialization(self):
        """Test unified response JSON serialization"""
        response = UnifiedClassificationResponse(
            total=1,
            successful=1,
            failed=0,
            results=[{"status": "success", "product_id": "TEST001"}],
            timestamp="2025-09-23T12:05:16.227619"
        )
        
        # Should be serializable to JSON
        response_dict = response.model_dump()
        assert isinstance(response_dict, dict)
        assert response_dict["total"] == 1
        assert len(response_dict["results"]) == 1