#!/usr/bin/env python3
"""
Prueba completa del sistema asíncrono con múltiples productos
"""
import requests
import time

def test_complete_async_system():
    """Prueba integral del sistema asíncrono"""
    print("🚀 PRUEBA COMPLETA DEL SISTEMA ASÍNCRONO")
    print("=" * 55)
    
    # Productos de prueba más diversos
    test_products = [
        {"text": "yogur natural griego sin azúcar", "product_id": "YOG-001"},
        {"text": "aceite de oliva extra virgen", "product_id": "ACE-002"},
        {"text": "pan integral de centeno", "product_id": "PAN-003"},
        {"text": "queso manchego curado", "product_id": "QUE-004"},
        {"text": "cerveza artesanal IPA", "product_id": "BEB-005"}
    ]
    
    # 1. Crear job asíncrono
    print("📤 1. Creando job asíncrono con 5 productos...")
    
    payload = {
        "products": test_products,
        "priority": 1
    }
    
    response = requests.post("http://localhost:8000/classify/async", json=payload)
    
    if response.status_code != 200:
        print(f"❌ Error creando job: {response.status_code}")
        return
        
    job_data = response.json()
    job_id = job_data["job_id"]
    
    print(f"✅ Job creado: {job_id}")
    print(f"📊 Estado inicial: {job_data['status']}")
    print(f"📦 Productos a procesar: {job_data['total_products']}")
    
    # 2. Monitorear progreso hasta completar
    print(f"\n🔍 2. Monitoreando progreso hasta finalización...")
    print("-" * 50)
    
    max_checks = 30
    for i in range(max_checks):
        time.sleep(1)
        
        status_response = requests.get(f"http://localhost:8000/classify/status/{job_id}")
        if status_response.status_code == 200:
            status_data = status_response.json()
            status = status_data["status"]
            
            if status_data.get("progress"):
                progress = status_data["progress"]
                print(f"[{i+1:02d}] {status.upper()} - {progress['current']}/{progress['total']} ({progress['percentage']:.1f}%)")
            else:
                print(f"[{i+1:02d}] {status.upper()}")
            
            if status in ["completed", "failed"]:
                break
        else:
            print(f"❌ Error consultando status: {status_response.status_code}")
            return
    
    # 3. Obtener y mostrar resultados finales
    print(f"\n🎉 3. Obteniendo resultados finales...")
    
    if status == "completed":
        result_response = requests.get(f"http://localhost:8000/classify/result/{job_id}")
        
        if result_response.status_code == 200:
            results = result_response.json()
            
            print(f"\n📊 RESUMEN DE RESULTADOS:")
            print(f"   📦 Total productos: {results['total']}")
            print(f"   ✅ Exitosos: {results['successful']}")
            print(f"   ❌ Fallidos: {results['failed']}")
            print(f"   ⏱️ Tiempo total: {results['processing_time_seconds']}s")
            
            print(f"\n🔍 CLASIFICACIONES DETALLADAS:")
            for i, result in enumerate(results.get('results', []), 1):
                product_id = result.get('product_id', f'PROD-{i}')
                search_text = result.get('search_text', 'N/A')
                
                if result.get('status') == 'success':
                    classification = result.get('classification', {})
                    category = classification.get('prefLabel', 'N/A')
                    confidence = classification.get('confidence', 'N/A')
                    notation = classification.get('notation', 'N/A')
                    
                    print(f"   {i}. ✅ [{product_id}] {search_text}")
                    print(f"      → {category} (conf: {confidence}) [{notation}]")
                else:
                    error = result.get('error', 'Error desconocido')
                    print(f"   {i}. ❌ [{product_id}] {search_text}")
                    print(f"      → Error: {error}")
            
            # Información de costos
            if results.get('openai_cost_info'):
                cost = results['openai_cost_info']
                print(f"\n💰 INFORMACIÓN DE COSTOS:")
                print(f"   🤖 Modelo usado: {cost.get('model', 'N/A')}")
                print(f"   🔢 Llamadas API: {cost.get('api_calls', 'N/A')}")
                
                if cost.get('usage'):
                    usage = cost['usage']
                    print(f"   📊 Tokens totales: {usage['total_tokens']}")
                    print(f"      • Prompt: {usage['prompt_tokens']}")
                    print(f"      • Completion: {usage['completion_tokens']}")
                
                if cost.get('cost_usd'):
                    total_cost = cost['cost_usd']['total']
                    print(f"   💵 Costo total: ${total_cost:.4f} USD")
                    
                    # Calcular costo promedio por producto
                    if results['successful'] > 0:
                        cost_per_product = total_cost / results['successful']
                        print(f"   📈 Costo por producto: ${cost_per_product:.4f} USD")
            
            print(f"\n🎉 ¡PRUEBA COMPLETA EXITOSA!")
            print(f"✅ El sistema asíncrono está funcionando perfectamente")
            
        else:
            print(f"❌ Error obteniendo resultados: {result_response.status_code}")
    else:
        print(f"❌ Job terminó con estado: {status}")

if __name__ == "__main__":
    test_complete_async_system()