#!/usr/bin/env python3
import requests
import json

def test_taxonomy_feature():
    print("🧪 TESTING CONFIGURABLE TAXONOMY FEATURE")
    print("="*50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Sin taxonomía (debería usar por defecto)
    print("\n1️⃣ Test: Sin taxonomía específica")
    response = requests.post(f"{base_url}/classify", 
        json={"text": "yogur natural", "product_id": "TEST-1"})
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data.get('prefLabel', 'N/A')}")
        if 'taxonomy_used' in data:
            tax = data['taxonomy_used']
            print(f"🔧 Taxonomy: {tax['name']} ({tax['id']})")
            print(f"📌 Is Default: {tax['is_default']}")
        else:
            print("❌ No taxonomy_used in response")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Test 2: Con taxonomía específica
    print("\n2️⃣ Test: Con taxonomía treew-best")
    response = requests.post(f"{base_url}/classify", 
        params={"taxonomy": "treew-best"},
        json={"text": "aceite de oliva", "product_id": "TEST-2"})
        
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data.get('prefLabel', 'N/A')}")
        if 'taxonomy_used' in data:
            tax = data['taxonomy_used']
            print(f"🔧 Taxonomy: {tax['name']} ({tax['id']})")
            print(f"📌 Is Default: {tax['is_default']}")
        else:
            print("❌ No taxonomy_used in response")
    else:
        print(f"❌ Error: {response.status_code}")

if __name__ == "__main__":
    test_taxonomy_feature()
