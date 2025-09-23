#!/usr/bin/env python3
"""
Script de prueba para el endpoint unificado /classify/products

Prueba la clasificación de:
1. Un solo producto
2. Múltiples productos
3. Casos de error

Requiere que el servidor esté corriendo en localhost:8000
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000"

def test_single_product():
    """Prueba clasificación de un solo producto"""
    print("🧪 Probando clasificación de UN producto...")
    
    payload = {
        "products": [
            {
                "text": "leche descremada",
                "product_id": "SINGLE_001"
            }
        ]
    }
    
    try:
        response = requests.post(f"{API_BASE}/classify/products", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Éxito - Total: {result['total']}, Exitosos: {result['successful']}")
            print(f"📊 Tiempo de procesamiento: {result['processing_time_seconds']}s")
            
            if result['results']:
                first_result = result['results'][0]
                print(f"📱 Producto: {first_result['search_text']}")
                print(f"🎯 Clasificación: {first_result['prefLabel']}")
                print(f"📋 Notación: {first_result['notation']}")
                print(f"💯 Confianza: {first_result['confidence']}")
            
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def test_multiple_products():
    """Prueba clasificación de múltiples productos"""
    print("\n🧪 Probando clasificación de MÚLTIPLES productos...")
    
    payload = {
        "products": [
            {
                "text": "arroz blanco",
                "product_id": "MULTI_001"
            },
            {
                "text": "pollo congelado",
                "product_id": "MULTI_002"
            },
            {
                "text": "yogurt natural",
                "product_id": "MULTI_003"
            },
            {
                "text": "pan integral",
                "product_id": "MULTI_004"
            },
            {
                "text": "aceite de oliva",
                "product_id": "MULTI_005"
            }
        ]
    }
    
    try:
        response = requests.post(f"{API_BASE}/classify/products", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Éxito - Total: {result['total']}, Exitosos: {result['successful']}, Fallidos: {result['failed']}")
            print(f"📊 Tiempo de procesamiento: {result['processing_time_seconds']}s")
            
            print("\n📋 Resultados detallados:")
            for i, product_result in enumerate(result['results']):
                print(f"\n{i+1}. {product_result['search_text']}")
                if product_result['status'] == 'success':
                    print(f"   🎯 {product_result['prefLabel']} ({product_result['notation']})")
                    print(f"   💯 Confianza: {product_result['confidence']}")
                else:
                    print(f"   ❌ Error: {product_result.get('error', 'Unknown error')}")
            
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def test_empty_array():
    """Prueba con array vacío"""
    print("\n🧪 Probando con array vacío...")
    
    payload = {
        "products": []
    }
    
    try:
        response = requests.post(f"{API_BASE}/classify/products", json=payload)
        
        if response.status_code == 422:
            print("✅ Correcto - Array vacío rechazado con error 422")
            return True
        else:
            print(f"⚠️ Inesperado - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def test_invalid_data():
    """Prueba con datos inválidos"""
    print("\n🧪 Probando con datos inválidos...")
    
    payload = {
        "products": [
            {
                "text": "",  # Texto vacío
                "product_id": "INVALID_001"
            }
        ]
    }
    
    try:
        response = requests.post(f"{API_BASE}/classify/products", json=payload)
        
        if response.status_code in [200, 422]:
            result = response.json()
            if response.status_code == 200:
                print(f"✅ Manejo correcto - Status: success, pero puede tener errores internos")
                print(f"📊 Fallidos: {result.get('failed', 0)}")
            else:
                print(f"✅ Validación correcta - Datos inválidos rechazados")
            return True
        else:
            print(f"⚠️ Inesperado - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def test_api_info():
    """Prueba endpoint de información"""
    print("\n🧪 Probando endpoint de información...")
    
    try:
        response = requests.get(f"{API_BASE}/")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Version: {result.get('version', 'N/A')}")
            print(f"📝 Descripción: {result.get('description', 'N/A')}")
            
            # Verificar que el nuevo endpoint esté documentado
            if 'endpoints' in result and 'primary' in result['endpoints']:
                primary = result['endpoints']['primary']
                if 'classify_products' in primary:
                    print("✅ Nuevo endpoint /classify/products correctamente documentado")
                    return True
                else:
                    print("⚠️ Endpoint /classify/products no encontrado en documentación")
                    return False
            else:
                print("⚠️ Estructura de documentación inesperada")
                print(f"📋 Endpoints encontrados: {list(result.get('endpoints', {}).keys())}")
                return False
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("🚀 Iniciando pruebas del endpoint unificado /classify/products")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Verificar conectividad
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Servidor no disponible - Health check falló: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        print(f"💡 Asegúrate de que el servidor esté corriendo en {API_BASE}")
        return
    
    print("✅ Servidor disponible, iniciando pruebas...\n")
    
    # Ejecutar pruebas
    tests = [
        ("API Info", test_api_info),
        ("Single Product", test_single_product),
        ("Multiple Products", test_multiple_products),
        ("Empty Array", test_empty_array),
        ("Invalid Data", test_invalid_data)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Error en prueba {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\n📊 Resultado: {passed}/{len(results)} pruebas exitosas")
    
    if passed == len(results):
        print("🎉 ¡Todas las pruebas pasaron! El endpoint unificado funciona correctamente.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisar implementación.")

if __name__ == "__main__":
    main()