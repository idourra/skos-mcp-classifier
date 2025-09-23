#!/usr/bin/env python3
"""
test_export_api.py - Script para probar los endpoints de exportación de la API
"""
import requests
import json
import time
from datetime import datetime

# Configuración
API_BASE_URL = "http://localhost:8000"

def test_export_endpoints():
    """Prueba los endpoints de exportación de la API"""
    print("🧪 Testing API Export Endpoints")
    print("=" * 60)
    
    # Productos de prueba
    test_products = [
        {"text": "yogur griego natural sin azúcar", "product_id": "YOG-001"},
        {"text": "aceite de oliva extra virgen 1L", "product_id": "ACE-002"},
        {"text": "pan integral centeno", "product_id": "PAN-003"},
        {"text": "queso manchego curado", "product_id": "QUE-004"},
        {"text": "miel de abeja multifloral", "product_id": "MIE-005"}
    ]
    
    print(f"📊 Testing con {len(test_products)} productos")
    
    # Test 1: Exportación CSV
    print("\n1️⃣  Testing CSV Export...")
    csv_payload = {
        "products": test_products,
        "format": "csv",
        "filename": "test_export"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/export/csv", json=csv_payload)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ CSV Export exitoso!")
            print(f"   📁 Archivo: {result['filename']}")
            print(f"   🔗 URL descarga: {result['download_url']}")
            print(f"   📊 Total: {result['total_products']}, Exitosos: {result['successful']}")
            
            # Test descarga CSV
            download_url = f"{API_BASE_URL}{result['download_url']}"
            download_response = requests.get(download_url)
            if download_response.status_code == 200:
                print(f"   ✅ Descarga CSV exitosa ({len(download_response.content)} bytes)")
            else:
                print(f"   ❌ Error descargando CSV: {download_response.status_code}")
        else:
            print(f"   ❌ Error en CSV export: {response.status_code}")
            print(f"   📄 Detalle: {response.text}")
    except Exception as e:
        print(f"   ❌ Excepción en CSV export: {e}")
    
    # Test 2: Exportación Excel  
    print("\n2️⃣  Testing Excel Export...")
    excel_payload = {
        "products": test_products,
        "format": "excel",
        "filename": "test_export"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/export/excel", json=excel_payload)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Excel Export exitoso!")
            print(f"   📁 Archivo: {result['filename']}")
            print(f"   🔗 URL descarga: {result['download_url']}")
            print(f"   📊 Total: {result['total_products']}, Exitosos: {result['successful']}")
            
            # Test descarga Excel
            download_url = f"{API_BASE_URL}{result['download_url']}"
            download_response = requests.get(download_url)
            if download_response.status_code == 200:
                print(f"   ✅ Descarga Excel exitosa ({len(download_response.content)} bytes)")
            else:
                print(f"   ❌ Error descargando Excel: {download_response.status_code}")
        else:
            print(f"   ❌ Error en Excel export: {response.status_code}")
            print(f"   📄 Detalle: {response.text}")
    except Exception as e:
        print(f"   ❌ Excepción en Excel export: {e}")
    
    # Test 3: Clasificación + exportación combinada
    print("\n3️⃣  Testing Batch Classification + Export...")
    
    batch_payload = {"products": test_products}
    
    try:
        # Primero clasificar en lote
        batch_response = requests.post(f"{API_BASE_URL}/classify/batch", json=batch_payload)
        if batch_response.status_code == 200:
            batch_result = batch_response.json()
            print(f"   ✅ Batch classification exitoso!")
            print(f"   📊 Procesados: {batch_result['total']}, Exitosos: {batch_result['successful']}")
            
            # Luego exportar los mismos productos
            export_payload = {
                "products": test_products,
                "format": "csv",
                "filename": f"batch_export_{datetime.now().strftime('%H%M%S')}"
            }
            
            export_response = requests.post(f"{API_BASE_URL}/export/csv", json=export_payload)
            if export_response.status_code == 200:
                export_result = export_response.json()
                print(f"   ✅ Export post-batch exitoso!")
                print(f"   📁 Archivo: {export_result['filename']}")
        else:
            print(f"   ❌ Error en batch classification: {batch_response.status_code}")
    except Exception as e:
        print(f"   ❌ Excepción en batch + export: {e}")
    
    # Test 4: Health check
    print("\n4️⃣  Testing Health Check...")
    try:
        health_response = requests.get(f"{API_BASE_URL}/health")
        if health_response.status_code == 200:
            health_result = health_response.json()
            print(f"   ✅ Health check: {health_result['status']}")
            print(f"   🔗 MCP Server: {health_result.get('mcp_server', 'unknown')}")
        else:
            print(f"   ❌ Health check failed: {health_response.status_code}")
    except Exception as e:
        print(f"   ❌ Excepción en health check: {e}")
    
    print("\n🎉 Testing completado!")

def test_api_endpoints_info():
    """Muestra información de todos los endpoints disponibles"""
    print("\n📖 API Endpoints Information")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            info = response.json()
            print(f"📋 API: {info['message']}")
            print(f"🔢 Versión: {info['version']}")
            print("\n🔗 Endpoints disponibles:")
            for name, endpoint in info.get('endpoints', {}).items():
                print(f"   • {name}: {endpoint}")
        else:
            print(f"❌ Error obteniendo info: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 SKOS API Export Testing")
    print(f"🌐 API URL: {API_BASE_URL}")
    print(f"🕐 Timestamp: {datetime.now().isoformat()}")
    
    # Verificar si la API está accesible
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API no está accesible. ¿Está corriendo el servidor?")
            print("💡 Ejecuta: python classification_api.py")
            exit(1)
    except Exception as e:
        print(f"❌ No se puede conectar a la API: {e}")
        print("💡 Ejecuta: python classification_api.py")
        exit(1)
    
    # Ejecutar tests
    test_api_endpoints_info()
    test_export_endpoints()