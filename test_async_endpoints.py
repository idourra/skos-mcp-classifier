#!/usr/bin/env python3
"""
Test script para los nuevos endpoints asíncronos
"""
import requests
import json
import time

def test_async_endpoints():
    """Probar los nuevos endpoints asíncronos"""
    print("🧪 PROBANDO ENDPOINTS ASÍNCRONOS")
    print("=" * 50)
    
    # Payload de prueba
    async_payload = {
        "products": [
            {"text": "Pelota de fútbol Nike oficial", "product_id": "NIKE-001"},
            {"text": "Manzanas rojas orgánicas", "product_id": "FRUIT-001"},
            {"text": "Laptop gaming ASUS ROG", "product_id": "TECH-001"}
        ],
        "priority": 1
    }
    
    try:
        # 1. Probar creación de job asíncrono
        print("📤 1. Creando job asíncrono...")
        response = requests.post("http://localhost:8000/classify/async", 
                               json=async_payload, 
                               timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Error creando job: {response.status_code}")
            print(f"Response: {response.text}")
            return
            
        job_data = response.json()
        job_id = job_data["job_id"]
        
        print(f"✅ Job creado exitosamente!")
        print(f"📋 Job ID: {job_id}")
        print(f"📊 Estado inicial: {job_data['status']}")
        print(f"📦 Total productos: {job_data['total_products']}")
        print(f"⏰ Estimación: {job_data.get('estimated_completion_time', 'N/A')}")
        
        # 2. Monitorear progreso del job
        print(f"\n🔍 2. Monitoreando progreso...")
        print("-" * 30)
        
        max_checks = 10
        for i in range(max_checks):
            time.sleep(1)  # Esperar 1 segundo entre checks
            
            status_response = requests.get(f"http://localhost:8000/classify/status/{job_id}")
            
            if status_response.status_code != 200:
                print(f"❌ Error consultando estado: {status_response.status_code}")
                break
                
            status_data = status_response.json()
            status = status_data["status"]
            
            print(f"[Check {i+1}] Estado: {status}", end="")
            
            if status_data.get("progress"):
                progress = status_data["progress"]
                print(f" - Progreso: {progress['current']}/{progress['total']} ({progress['percentage']:.1f}%)")
            else:
                print()
            
            # Si está completado, obtener resultados
            if status == "completed":
                print(f"\n🎉 3. Job completado! Obteniendo resultados...")
                
                result_response = requests.get(f"http://localhost:8000/classify/result/{job_id}")
                
                if result_response.status_code == 200:
                    result_data = result_response.json()
                    
                    print(f"📊 Resultados finales:")
                    print(f"   📦 Total procesados: {result_data['total']}")
                    print(f"   ✅ Exitosos: {result_data['successful']}")
                    print(f"   ❌ Fallidos: {result_data['failed']}")
                    print(f"   ⏱️ Tiempo procesamiento: {result_data.get('processing_time_seconds', 'N/A')}s")
                    
                    # Mostrar algunos resultados
                    if result_data.get('results'):
                        print(f"\n📋 Muestra de clasificaciones:")
                        for idx, result in enumerate(result_data['results'][:3]):  # Mostrar primeros 3
                            if result['status'] == 'success':
                                classification = result['classification']
                                print(f"   {idx+1}. {result['search_text'][:30]}...")
                                print(f"      → {classification.get('prefLabel', 'N/A')} (conf: {classification.get('confidence', 'N/A')})")
                    
                    # Información de costos OpenAI si disponible
                    if result_data.get('openai_cost_info'):
                        cost_info = result_data['openai_cost_info']
                        print(f"\n💰 Información de costos OpenAI:")
                        print(f"   🤖 Modelo: {cost_info.get('model', 'N/A')}")
                        print(f"   🎯 API calls: {cost_info.get('api_calls', 'N/A')}")
                        if cost_info.get('cost_usd'):
                            print(f"   💵 Costo total: ${cost_info['cost_usd']['total']:.4f} USD")
                
                else:
                    print(f"❌ Error obteniendo resultados: {result_response.status_code}")
                
                break
                
            elif status == "failed":
                print(f"\n❌ Job falló: {status_data.get('error_message', 'Error desconocido')}")
                break
                
            elif i == max_checks - 1:
                print(f"\n⏰ Timeout: Job aún procesando después de {max_checks} checks")
                break
        
        print(f"\n✅ Prueba completada!")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        print("🔧 Asegúrate de que la API esté corriendo en http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_async_endpoints()