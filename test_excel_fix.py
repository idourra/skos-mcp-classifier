#!/usr/bin/env python3
"""
test_excel_fix.py - Prueba específica para el Excel export
"""
import requests
import json

def test_excel_export():
    """Prueba específica para el endpoint de Excel"""
    
    # Test con un solo producto
    test_product = {
        "products": [
            {"text": "yogur griego natural", "product_id": "YOG-TEST"}
        ],
        "format": "excel",
        "filename": "test_excel_simple"
    }
    
    print("🧪 Testing Excel Export (Simple)")
    print("=" * 40)
    
    try:
        response = requests.post("http://localhost:8000/export/excel", 
                               json=test_product, 
                               timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Excel Export exitoso!")
            print(f"📁 Archivo: {result['filename']}")
            print(f"🔗 URL: {result['download_url']}")
            print(f"📊 Productos: {result['total_products']}")
            print(f"✅ Exitosos: {result['successful']}")
            
            # Test de descarga
            download_url = f"http://localhost:8000{result['download_url']}"
            print(f"\n📥 Probando descarga: {download_url}")
            
            download_response = requests.get(download_url)
            if download_response.status_code == 200:
                print(f"✅ Descarga exitosa: {len(download_response.content)} bytes")
                
                # Verificar que es un archivo Excel válido
                if download_response.content.startswith(b'PK'):
                    print("✅ Archivo Excel válido (ZIP signature)")
                else:
                    print("❌ No parece ser un archivo Excel válido")
            else:
                print(f"❌ Error en descarga: {download_response.status_code}")
                print(f"Detail: {download_response.text}")
        else:
            print(f"❌ Error en export: {response.status_code}")
            print(f"Detail: {response.text}")
            
    except Exception as e:
        print(f"❌ Excepción: {e}")

if __name__ == "__main__":
    test_excel_export()