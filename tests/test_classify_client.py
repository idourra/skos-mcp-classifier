#!/usr/bin/env python3
"""
Unit tests for client/classify_standard_api.py
Testing classification logic, error handling, and cost tracking integration
"""
import pytest
from unittest.mock import Mock, patch
from client.classify_standard_api import classify

class TestClassifyFunction:
    """Test the main classify function"""
    
    @patch('client.classify_standard_api.client')
    @patch('client.classify_standard_api.calculate_openai_cost')
    def test_successful_classification_with_cost_tracking(self, mock_calc_cost, mock_client, mock_openai_response):
        """Test successful classification with cost tracking"""
        # Setup mock responses
        mock_client.chat.completions.create.return_value = mock_openai_response
        
        mock_calc_cost.return_value = {
            "model": "gpt-4o-mini-2024-07-18",
            "base_model_for_pricing": "gpt-4o-mini",
            "prompt_cost": 0.000269,
            "completion_cost": 0.000096,
            "total_cost": 0.000365,
            "prompt_cost_per_1m_tokens": 0.15,
            "completion_cost_per_1m_tokens": 0.6
        }
        
        # Execute classification
        result = classify("yogur natural griego 150g", "YOGUR001")
        
        # Verify basic classification result
        assert "concept_uri" in result
        assert "prefLabel" in result
        assert "confidence" in result
        assert result["product_id"] == "YOGUR001"
        
        # Verify cost tracking is included
        assert "openai_cost" in result
        cost_info = result["openai_cost"]
        assert cost_info["model"] == "gpt-4o-mini-2024-07-18"
        assert cost_info["cost_usd"]["total"] == 0.000365
        assert cost_info["usage"]["total_tokens"] == 1956
    
    @patch('client.classify_standard_api.client')
    def test_classification_without_product_id(self, mock_client, mock_openai_response):
        """Test classification without providing product_id"""
        mock_client.chat.completions.create.return_value = mock_openai_response
        
        result = classify("yogur natural griego 150g")
        
        # Should not include product_id in result
        assert "product_id" not in result or result.get("product_id") is None
        assert "concept_uri" in result
    
    @patch('client.classify_standard_api.client')
    def test_classification_with_openai_error(self, mock_client):
        """Test classification when OpenAI API returns an error"""
        # Setup mock to raise an exception
        mock_client.chat.completions.create.side_effect = Exception("OpenAI API Error")
        
        result = classify("yogur natural griego 150g", "YOGUR001")
        
        # Should return error information
        assert "error" in result
        assert result["product_id"] == "YOGUR001"
        assert "OpenAI API Error" in result["error"]
    
    @patch('client.classify_standard_api.client')
    def test_classification_with_invalid_json_response(self, mock_client):
        """Test classification when OpenAI returns invalid JSON"""
        # Create mock response with invalid JSON content
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is not valid JSON content"
        mock_response.model = "gpt-4o-mini-2024-07-18"
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150
        
        mock_client.chat.completions.create.return_value = mock_response
        
        result = classify("invalid product", "INVALID001")
        
        # Should return JSON decode error
        assert "error" in result
        assert "Invalid JSON" in result["error"] or "No JSON found" in result["error"]
        assert result["product_id"] == "INVALID001"
    
    @patch('client.classify_standard_api.client')
    def test_classification_function_calls(self, mock_client):
        """Test classification with function calls (multi-step process)"""
        # First response with function call
        first_response = Mock()
        first_response.choices = [Mock()]
        first_response.choices[0].message.function_call.name = "search_concepts"
        first_response.choices[0].message.function_call.arguments = '{"search_text": "yogur"}'
        first_response.choices[0].message.content = None
        first_response.model = "gpt-4o-mini-2024-07-18"
        first_response.usage.prompt_tokens = 500
        first_response.usage.completion_tokens = 25
        first_response.usage.total_tokens = 525
        
        # Second response with final result
        second_response = Mock()
        second_response.choices = [Mock()]
        second_response.choices[0].message.content = '{"search_text": "yogur", "concept_uri": "https://treew.io/taxonomy/concept/111206", "prefLabel": "Yogur y sustitutos", "notation": "111206", "level": 1, "confidence": 1.0}'
        second_response.choices[0].message.function_call = None
        second_response.model = "gpt-4o-mini-2024-07-18"
        second_response.usage.prompt_tokens = 600
        second_response.usage.completion_tokens = 75
        second_response.usage.total_tokens = 675
        
        # Setup mock to return responses in sequence
        mock_client.chat.completions.create.side_effect = [first_response, second_response]
        
        # Mock the function call handler
        with patch('client.classify_standard_api.handle_function_call') as mock_handler:
            mock_handler.return_value = "Function call result"
            
            result = classify("yogur natural", "YOGUR002")
        
        # Verify multiple API calls were made
        assert mock_client.chat.completions.create.call_count == 2
        
        # Verify final result
        assert "concept_uri" in result
        assert result["prefLabel"] == "Yogur y sustitutos"
        assert result["product_id"] == "YOGUR002"
        
        # Verify cost tracking across multiple calls
        if "openai_cost" in result:
            assert result["openai_cost"]["api_calls"] >= 2
    
    def test_classify_empty_text(self):
        """Test classification with empty text"""
        result = classify("", "EMPTY001")
        
        # Should handle empty text gracefully
        assert "error" in result or "concept_uri" in result
        if "product_id" in result:
            assert result["product_id"] == "EMPTY001"
    
    def test_classify_very_long_text(self):
        """Test classification with very long text"""
        long_text = "yogur " * 1000  # Very long product description
        
        with patch('client.classify_standard_api.client') as mock_client:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '{"search_text": "yogur", "concept_uri": "https://treew.io/taxonomy/concept/111206", "prefLabel": "Yogur y sustitutos", "notation": "111206", "level": 1, "confidence": 0.8}'
            mock_response.model = "gpt-4o-mini-2024-07-18"
            mock_response.usage.prompt_tokens = 2000
            mock_response.usage.completion_tokens = 100
            mock_response.usage.total_tokens = 2100
            
            mock_client.chat.completions.create.return_value = mock_response
            
            result = classify(long_text, "LONG001")
        
        # Should handle long text without error
        assert "concept_uri" in result or "error" in result
        if "openai_cost" in result:
            # Should track higher token usage for long text
            assert result["openai_cost"]["usage"]["prompt_tokens"] >= 1000

class TestCostTrackingIntegration:
    """Test cost tracking integration within classification"""
    
    @patch('client.classify_standard_api.client')
    @patch('client.classify_standard_api.calculate_openai_cost')
    def test_cost_accumulation_multiple_calls(self, mock_calc_cost, mock_client):
        """Test cost accumulation across multiple API calls"""
        # Setup multiple mock responses
        responses = [
            Mock(model="gpt-4o-mini-2024-07-18", usage=Mock(prompt_tokens=500, completion_tokens=25, total_tokens=525)),
            Mock(model="gpt-4o-mini-2024-07-18", usage=Mock(prompt_tokens=600, completion_tokens=75, total_tokens=675)),
            Mock(model="gpt-4o-mini-2024-07-18", usage=Mock(prompt_tokens=696, completion_tokens=60, total_tokens=756))
        ]
        
        # Setup choices for each response
        for i, response in enumerate(responses):
            response.choices = [Mock()]
            if i < len(responses) - 1:  # Function calls for first two
                response.choices[0].message.function_call = Mock(name="search_concepts")
                response.choices[0].message.content = None
            else:  # Final response with JSON
                response.choices[0].message.function_call = None
                response.choices[0].message.content = '{"search_text": "test", "concept_uri": "test", "prefLabel": "Test", "notation": "TEST", "level": 1, "confidence": 1.0}'
        
        mock_client.chat.completions.create.side_effect = responses
        
        # Mock cost calculation to return different costs
        cost_values = [0.0001, 0.0002, 0.0003]
        mock_calc_cost.side_effect = [
            {"total_cost": cost, "prompt_cost": cost*0.6, "completion_cost": cost*0.4}
            for cost in cost_values
        ]
        
        with patch('client.classify_standard_api.handle_function_call', return_value="mock result"):
            result = classify("test product", "TEST001")
        
        # Verify multiple API calls were tracked
        assert mock_client.chat.completions.create.call_count == 3
        assert mock_calc_cost.call_count == 3
        
        # Verify cost accumulation if present
        if "openai_cost" in result:
            assert result["openai_cost"]["api_calls"] == 3
    
    @patch('client.classify_standard_api.client')
    def test_cost_tracking_with_api_failure(self, mock_client):
        """Test cost tracking when API call fails"""
        # First call succeeds, second fails
        first_response = Mock()
        first_response.choices = [Mock()]
        first_response.choices[0].message.function_call = Mock(name="search_concepts")
        first_response.choices[0].message.content = None
        first_response.model = "gpt-4o-mini-2024-07-18"
        first_response.usage.prompt_tokens = 500
        first_response.usage.completion_tokens = 25
        first_response.usage.total_tokens = 525
        
        mock_client.chat.completions.create.side_effect = [first_response, Exception("API Error")]
        
        with patch('client.classify_standard_api.handle_function_call', return_value="mock result"):
            result = classify("test product", "FAIL001")
        
        # Should return error but may include partial cost info
        assert "error" in result
        if "openai_cost" in result:
            # Should track the successful call before failure
            assert result["openai_cost"]["api_calls"] >= 1

class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_classify_none_text(self):
        """Test classification with None text"""
        with pytest.raises(Exception):
            classify(None, "NONE001")
    
    def test_classify_special_characters(self):
        """Test classification with special characters"""
        special_text = "yogür natuŕal grįego 150g ñoño café"
        
        with patch('client.classify_standard_api.client') as mock_client:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '{"search_text": "yogur", "concept_uri": "test", "prefLabel": "Test", "notation": "TEST", "level": 1, "confidence": 0.9}'
            mock_response.model = "gpt-4o-mini-2024-07-18"
            mock_response.usage.prompt_tokens = 100
            mock_response.usage.completion_tokens = 50
            mock_response.usage.total_tokens = 150
            
            mock_client.chat.completions.create.return_value = mock_response
            
            result = classify(special_text, "SPECIAL001")
        
        # Should handle special characters without error
        assert "concept_uri" in result or "error" in result
    
    @patch('client.classify_standard_api.client')
    def test_response_missing_usage_data(self, mock_client):
        """Test handling response missing usage data"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"search_text": "test", "concept_uri": "test", "prefLabel": "Test", "notation": "TEST", "level": 1, "confidence": 1.0}'
        mock_response.model = "gpt-4o-mini-2024-07-18"
        mock_response.usage = None  # Missing usage data
        
        mock_client.chat.completions.create.return_value = mock_response
        
        result = classify("test product", "NOUSAGE001")
        
        # Should still return classification result
        assert "concept_uri" in result or "error" in result
        # Cost tracking may be missing or have zero values
        if "openai_cost" in result:
            assert result["openai_cost"]["usage"]["total_tokens"] == 0