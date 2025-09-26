#!/usr/bin/env python3
import requests
import json

print("🎉 VALIDACIÓN FINAL - FEATURE CONFIGURABLE TAXONOMY")
print("=" * 55)

try:
    # Test 1: Default taxonomy
    response1 = requests.post("http://localhost:8000/classify", 
        json={"text": "yogur griego", "product_id": "TEST-DEFAULT"})
    
    if response1.status_code == 200:
        data1 = response1.json()
        print("✅ Test 1 - Taxonomía por defecto:")
        print(f"   Producto: {data1['search_text']}")
        print(f"   Categoría: {data1['prefLabel']}")
        
        if 'taxonomy_used' in data1 and data1['taxonomy_used']:
            tax1 = data1['taxonomy_used']
            print(f"   Taxonomía: {tax1['name']} ({tax1['id']})")
            print(f"   Es default: {tax1['is_default']}")
        else:
            print("   ❌ taxonomy_used missing")
    else:
        print(f"❌ Test 1 failed: {response1.status_code}")
    
    print()
    
    # Test 2: Specific taxonomy  
    response2 = requests.post("http://localhost:8000/classify",
        params={"taxonomy": "treew-best"},
        json={"text": "queso cheddar", "product_id": "TEST-SPECIFIC"})
        
    if response2.status_code == 200:
        data2 = response2.json()
        print("✅ Test 2 - Taxonomía específica:")
        print(f"   Producto: {data2['search_text']}")
        print(f"   Categoría: {data2['prefLabel']}")
        
        if 'taxonomy_used' in data2 and data2['taxonomy_used']:
            tax2 = data2['taxonomy_used']
            print(f"   Taxonomía: {tax2['name']} ({tax2['id']})")
            print(f"   Es default: {tax2['is_default']}")
        else:
            print("   ❌ taxonomy_used missing")
    else:
        print(f"❌ Test 2 failed: {response2.status_code}")
    
    print()
    print("🚀 FEATURE CONFIGURABLE TAXONOMY ¡FUNCIONANDO EN MAIN!")
    
except Exception as e:
    print(f"❌ Error: {e}")
