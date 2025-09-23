#!/usr/bin/env python3
"""
Test script para validar el tracking de costos en la API REST
"""
import requests
import json

# URL base de la API
BASE_URL = "http://localhost:8001"

def test_single_product():
    """Probar clasificación de un solo producto"""
    print("🧪 Testing single product classification with cost tracking...")
    
    payload = {
        "products": [
            {
                "text": "yogur natural griego 150g",
                "product_id": "YOGUR001"
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/classify/products", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Single product classification successful!")
            print(f"  - Total products: {data['total']}")
            print(f"  - Successful: {data['successful']}")
            print(f"  - Processing time: {data['processing_time_seconds']}s")
            
            if data.get('openai_cost_info'):
                cost_info = data['openai_cost_info']
                print("💰 OpenAI Cost Information:")
                print(f"  - Model: {cost_info['model']}")
                print(f"  - Total tokens: {cost_info['usage']['total_tokens']}")
                print(f"  - Total cost: ${cost_info['cost_usd']['total']:.6f}")
                print(f"  - API calls: {cost_info['api_calls']}")
            else:
                print("⚠️ No cost information found")
                
            print()
            return data
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error testing single product: {e}")
        return None

def test_multiple_products():
    """Probar clasificación de múltiples productos"""
    print("🧪 Testing multiple products classification with cost tracking...")
    
    payload = {
        "products": [
            {
                "text": "leche desnatada 1L",
                "product_id": "LECHE001"
            },
            {
                "text": "pan integral de centeno 500g",
                "product_id": "PAN001"
            },
            {
                "text": "aceite de oliva virgen extra 250ml",
                "product_id": "ACEITE001"
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/classify/products", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Multiple products classification successful!")
            print(f"  - Total products: {data['total']}")
            print(f"  - Successful: {data['successful']}")
            print(f"  - Processing time: {data['processing_time_seconds']}s")
            
            if data.get('openai_cost_info'):
                cost_info = data['openai_cost_info']
                print("💰 Consolidated OpenAI Cost Information:")
                print(f"  - Model: {cost_info['model']}")
                print(f"  - Total tokens: {cost_info['usage']['total_tokens']}")
                print(f"  - Prompt tokens: {cost_info['usage']['prompt_tokens']}")
                print(f"  - Completion tokens: {cost_info['usage']['completion_tokens']}")
                print(f"  - Total cost: ${cost_info['cost_usd']['total']:.6f}")
                print(f"  - Prompt cost: ${cost_info['cost_usd']['prompt']:.6f}")
                print(f"  - Completion cost: ${cost_info['cost_usd']['completion']:.6f}")
                print(f"  - API calls: {cost_info['api_calls']}")
                print(f"  - Base model for pricing: {cost_info['cost_breakdown']['base_model_for_pricing']}")
            else:
                print("⚠️ No cost information found")
                
            print()
            return data
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error testing multiple products: {e}")
        return None

def test_api_health():
    """Verificar que la API esté funcionando"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API is running and accessible")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure the API is running with: uvicorn classification_api:app --reload")
        return False

if __name__ == "__main__":
    print("🚀 Testing API REST with OpenAI Cost Tracking")
    print("=" * 50)
    
    # Verificar que la API esté funcionando
    if not test_api_health():
        print("\n💡 Start the API with: uvicorn classification_api:app --reload")
        exit(1)
    
    print()
    
    # Probar un solo producto
    single_result = test_single_product()
    
    # Probar múltiples productos
    multiple_result = test_multiple_products()
    
    print("🎯 Test Summary:")
    print("=" * 30)
    
    if single_result:
        print("✅ Single product test: PASSED")
    else:
        print("❌ Single product test: FAILED")
        
    if multiple_result:
        print("✅ Multiple products test: PASSED")
        print(f"🔍 Cost comparison - Single vs Multiple:")
        if single_result and single_result.get('openai_cost_info') and multiple_result.get('openai_cost_info'):
            single_cost = single_result['openai_cost_info']['cost_usd']['total']
            multiple_cost = multiple_result['openai_cost_info']['cost_usd']['total']
            print(f"   - Single product: ${single_cost:.6f}")
            print(f"   - Multiple products: ${multiple_cost:.6f}")
            print(f"   - Cost ratio: {multiple_cost/single_cost:.2f}x" if single_cost > 0 else "   - Cannot calculate ratio")
    else:
        print("❌ Multiple products test: FAILED")