#!/usr/bin/env python3
"""Simple test for API cost tracking"""
import requests
import json
import time

def simple_test():
    url = "http://localhost:8001/classify/products"
    payload = {
        "products": [
            {
                "text": "yogur natural griego 150g",
                "product_id": "YOGUR001"
            }
        ]
    }
    
    try:
        print("Making API request...")
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API request successful!")
            
            # Check cost information
            if 'openai_cost_info' in data:
                cost_info = data['openai_cost_info']
                print(f"\n💰 Cost info found:")
                print(f"  Model: {cost_info['model']}")
                print(f"  Total cost: ${cost_info['cost_usd']['total']:.6f}")
                print(f"  Total tokens: {cost_info['usage']['total_tokens']}")
                print(f"  API calls: {cost_info['api_calls']}")
                return True
            else:
                print("❌ No cost information in response")
                return False
        else:
            print(f"❌ API error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    simple_test()