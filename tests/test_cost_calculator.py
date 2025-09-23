#!/usr/bin/env python3
"""
Unit tests for utils/openai_cost_calculator.py
Testing cost calculation logic, model pricing, and edge cases
"""
from utils.openai_cost_calculator import (
    calculate_openai_cost,
    format_cost_info,
    extract_usage_from_response,
    get_model_pricing,
    OPENAI_PRICING
)

class TestModelPricing:
    """Test model pricing functionality"""
    
    def test_get_pricing_for_known_models(self):
        """Test getting pricing for known models"""
        known_models = ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"]
        
        for model in known_models:
            pricing = get_model_pricing(model)
            assert pricing is not None, f"Pricing should be available for {model}"
            assert "prompt" in pricing, f"Prompt pricing missing for {model}"
            assert "completion" in pricing, f"Completion pricing missing for {model}"
            assert pricing["prompt"] > 0, f"Prompt price should be positive for {model}"
            assert pricing["completion"] > 0, f"Completion price should be positive for {model}"
    
    def test_get_pricing_for_unknown_model(self):
        """Test getting pricing for unknown model"""
        unknown_models = ["claude-3", "llama-2", "unknown-model"]
        
        for model in unknown_models:
            pricing = get_model_pricing(model)
            assert pricing is None, f"Unknown model {model} should return None pricing"
    
    def test_pricing_constants(self):
        """Test that pricing constants are properly defined"""
        assert isinstance(OPENAI_PRICING, dict)
        assert len(OPENAI_PRICING) > 0
        
        # Verify gpt-4o-mini pricing (most commonly used)
        assert "gpt-4o-mini" in OPENAI_PRICING
        gpt4o_mini = OPENAI_PRICING["gpt-4o-mini"]
        assert gpt4o_mini["prompt"] == 0.15
        assert gpt4o_mini["completion"] == 0.60

class TestCostCalculation:
    """Test OpenAI cost calculation functionality"""
    
    def test_calculate_gpt4o_mini_cost(self):
        """Test cost calculation for gpt-4o-mini model"""
        cost_info = calculate_openai_cost("gpt-4o-mini", 1000, 500)
        
        assert cost_info is not None
        assert cost_info.model == "gpt-4o-mini"
        assert cost_info.prompt_tokens == 1000
        assert cost_info.completion_tokens == 500
        assert cost_info.total_tokens == 1500
        
        # gpt-4o-mini: $0.15/1M prompt, $0.60/1M completion
        expected_prompt_cost = (1000 / 1_000_000) * 0.15  # 0.00015
        expected_completion_cost = (500 / 1_000_000) * 0.60  # 0.0003
        expected_total = expected_prompt_cost + expected_completion_cost
        
        assert abs(cost_info.prompt_cost_usd - expected_prompt_cost) < 1e-6
        assert abs(cost_info.completion_cost_usd - expected_completion_cost) < 1e-6
        assert abs(cost_info.total_cost_usd - expected_total) < 1e-6
    
    def test_calculate_gpt4o_cost(self):
        """Test cost calculation for gpt-4o model"""
        cost_info = calculate_openai_cost("gpt-4o", 1000, 500)
        
        assert cost_info is not None
        assert cost_info.model == "gpt-4o"
        
        # gpt-4o: $2.50/1M prompt, $10.0/1M completion
        expected_prompt_cost = (1000 / 1_000_000) * 2.50  # 0.0025
        expected_completion_cost = (500 / 1_000_000) * 10.0  # 0.005
        
        assert abs(cost_info.prompt_cost_usd - expected_prompt_cost) < 1e-6
        assert abs(cost_info.completion_cost_usd - expected_completion_cost) < 1e-6
    
    def test_calculate_unknown_model_cost(self):
        """Test cost calculation for unknown model raises ValueError"""
        import pytest
        with pytest.raises(ValueError, match="Modelo 'unknown-model'"):
            calculate_openai_cost("unknown-model", 1000, 500)
    
    def test_calculate_cost_zero_tokens(self):
        """Test cost calculation with zero tokens"""
        cost_info = calculate_openai_cost("gpt-4o-mini", 0, 0)
        
        assert cost_info is not None
        assert cost_info.prompt_cost_usd == 0.0
        assert cost_info.completion_cost_usd == 0.0
        assert cost_info.total_cost_usd == 0.0

class TestUsageExtraction:
    """Test usage extraction from OpenAI responses"""
    
    def test_extract_usage_from_valid_response(self, mock_openai_response):
        """Test extracting usage from valid OpenAI response"""
        # The mock response is a dict, but the function expects an object with .usage attribute
        # Create a simple object to match the expected API
        class MockResponse:
            def __init__(self, usage_data):
                self.usage = type('obj', (object,), usage_data)()
        
        mock_response = MockResponse({
            'prompt_tokens': 1796,
            'completion_tokens': 160
        })
        
        prompt_tokens, completion_tokens = extract_usage_from_response(mock_response)
        
        assert prompt_tokens == 1796
        assert completion_tokens == 160
    
    def test_extract_usage_from_response_missing_usage(self):
        """Test extracting usage from response missing usage field"""
        response_without_usage = {
            "id": "test123",
            "choices": [{"message": {"content": "test"}}]
        }
        
        prompt_tokens, completion_tokens = extract_usage_from_response(response_without_usage)
        assert prompt_tokens == 0
        assert completion_tokens == 0
    
    def test_extract_usage_from_invalid_response(self):
        """Test extracting usage from invalid response"""
        invalid_responses = [
            None,
            {},
            {"usage": None},
            {"usage": {"incomplete": "data"}}
        ]
        
        for invalid_response in invalid_responses:
            prompt_tokens, completion_tokens = extract_usage_from_response(invalid_response)
            assert prompt_tokens == 0
            assert completion_tokens == 0

class TestCostFormatting:
    """Test cost information formatting"""
    
    def test_format_cost_info_complete(self):
        """Test formatting complete cost information"""
        cost_info = calculate_openai_cost("gpt-4o-mini", 1796, 160)
        assert cost_info is not None
        
        formatted = format_cost_info(cost_info)
        
        assert formatted["model"] == "gpt-4o-mini"
        assert formatted["usage"]["prompt_tokens"] == 1796
        assert formatted["usage"]["completion_tokens"] == 160
        assert formatted["usage"]["total_tokens"] == 1956
        assert "cost_usd" in formatted
        assert "cost_breakdown" in formatted
        assert "calculation_timestamp" in formatted["cost_breakdown"]
    
    def test_format_cost_info_structure(self):
        """Test formatted cost info has correct structure"""
        cost_info = calculate_openai_cost("gpt-4o-mini", 1000, 500)
        assert cost_info is not None
        
        formatted = format_cost_info(cost_info)
        
        # Verify required top-level keys
        required_keys = ["model", "usage", "cost_usd", "cost_breakdown"]
        for key in required_keys:
            assert key in formatted, f"Missing required key: {key}"
        
        # Verify usage structure
        usage_keys = ["prompt_tokens", "completion_tokens", "total_tokens"]
        for key in usage_keys:
            assert key in formatted["usage"], f"Missing usage key: {key}"
        
        # Verify cost_usd structure
        cost_keys = ["prompt", "completion", "total"]
        for key in cost_keys:
            assert key in formatted["cost_usd"], f"Missing cost_usd key: {key}"

class TestIntegrationScenarios:
    """Test realistic integration scenarios"""
    
    def test_full_cost_calculation_workflow(self, mock_openai_response):
        """Test complete workflow from OpenAI response to formatted cost info"""
        # Create a mock response object that matches the expected API
        class MockResponse:
            def __init__(self, usage_data):
                self.usage = type('obj', (object,), usage_data)()
        
        mock_response = MockResponse({
            'prompt_tokens': 1796,
            'completion_tokens': 160
        })
        
        # Extract usage
        prompt_tokens, completion_tokens = extract_usage_from_response(mock_response)
        assert prompt_tokens > 0 and completion_tokens > 0
        
        # Calculate costs
        model = "gpt-4o-mini"  # Use a known model instead of mock response model
        cost_info = calculate_openai_cost(model, prompt_tokens, completion_tokens)
        assert cost_info is not None
        
        # Format final result
        formatted = format_cost_info(cost_info)
        assert formatted is not None
        
        # Verify end-to-end consistency
        assert formatted["model"] == model
        assert formatted["usage"]["prompt_tokens"] == prompt_tokens
        assert formatted["usage"]["completion_tokens"] == completion_tokens
    
    def test_multiple_api_calls_cost_accumulation(self):
        """Test cost accumulation across multiple API calls"""
        # Simulate multiple API calls
        calls = [
            ("gpt-4o-mini", 500, 100),
            ("gpt-4o-mini", 300, 50), 
            ("gpt-4o-mini", 996, 10)
        ]
        
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_cost = 0.0
        
        for model, prompt_tokens, completion_tokens in calls:
            total_prompt_tokens += prompt_tokens
            total_completion_tokens += completion_tokens
            
            cost_info = calculate_openai_cost(model, prompt_tokens, completion_tokens)
            if cost_info:
                total_cost += cost_info.total_cost_usd
        
        # Verify accumulated totals
        assert total_prompt_tokens == 1796  # 500 + 300 + 996
        assert total_completion_tokens == 160  # 100 + 50 + 10
        
        # Verify cost is calculated correctly for the total
        expected_total_cost = (total_prompt_tokens / 1_000_000) * 0.15 + (total_completion_tokens / 1_000_000) * 0.60
        assert abs(total_cost - expected_total_cost) < 1e-6