#!/usr/bin/env python3
"""
Prueba masiva del sistema asíncrono con 200 productos reales
"""
import requests
import json
import time

def test_massive_async_classification():
    """Prueba con los 200 productos del archivo JSON"""
    print("🚀 PRUEBA MASIVA DEL SISTEMA ASÍNCRONO - 200 PRODUCTOS")
    print("=" * 65)
    
    # Cargar productos del archivo JSON
    try:
        with open('data/input/sm23_searches_200_test.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            products = data['products']
            
        print(f"📂 Productos cargados del archivo: {len(products)}")
        
    except Exception as e:
        print(f"❌ Error cargando archivo: {e}")
        return
    
    # 1. Crear job asíncrono masivo
    print(f"\n📤 1. Creando job asíncrono con {len(products)} productos...")
    
    # Preparar payload para el endpoint async
    payload = {
        "products": [
            {
                "text": product["text"],
                "product_id": product["product_id"]
            }
            for product in products
        ],
        "priority": 1
    }
    
    start_time = time.time()
    
    try:
        response = requests.post("http://localhost:8000/classify/async", json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Error creando job: {response.status_code}")
            print(f"Response: {response.text}")
            return
            
        job_data = response.json()
        job_id = job_data["job_id"]
        
        print(f"✅ Job masivo creado exitosamente!")
        print(f"📋 Job ID: {job_id}")
        print(f"📊 Estado inicial: {job_data['status']}")
        print(f"📦 Total productos: {job_data['total_products']}")
        print(f"⏰ Estimación: {job_data.get('estimated_completion_time', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error creando job: {e}")
        return
    
    # 2. Monitorear progreso hasta completar
    print(f"\n🔍 2. Monitoreando progreso de {len(products)} productos...")
    print("=" * 60)
    
    last_percentage = 0
    check_count = 0
    max_checks = 300  # Máximo 5 minutos de monitoreo
    
    while check_count < max_checks:
        time.sleep(2)  # Esperar 2 segundos entre checks para no saturar
        check_count += 1
        
        try:
            status_response = requests.get(f"http://localhost:8000/classify/status/{job_id}")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data["status"]
                
                if status_data.get("progress"):
                    progress = status_data["progress"]
                    current_percentage = progress['percentage']
                    
                    # Solo mostrar progreso cuando hay cambios significativos
                    if current_percentage - last_percentage >= 5 or current_percentage == 100:
                        elapsed_time = time.time() - start_time
                        print(f"[{check_count:03d}] {status.upper()} - {progress['current']}/{progress['total']} ({current_percentage:.1f}%) | {elapsed_time:.1f}s")
                        last_percentage = current_percentage
                
                # Si terminó, salir del loop
                if status in ["completed", "failed", "cancelled"]:
                    final_elapsed = time.time() - start_time
                    print(f"\n🏁 Job terminado con estado: {status.upper()}")
                    print(f"⏱️ Tiempo total transcurrido: {final_elapsed:.1f} segundos")
                    break
                    
            else:
                print(f"❌ Error consultando status: {status_response.status_code}")
                return
                
        except Exception as e:
            print(f"❌ Error en monitoreo: {e}")
            return
    
    # 3. Obtener y analizar resultados finales
    if status == "completed":
        print(f"\n🎉 3. Analizando resultados finales...")
        
        try:
            result_response = requests.get(f"http://localhost:8000/classify/result/{job_id}")
            
            if result_response.status_code == 200:
                results = result_response.json()
                
                print(f"\n📊 ANÁLISIS DE RESULTADOS MASIVOS:")
                print("=" * 50)
                print(f"   📦 Total productos procesados: {results['total']}")
                print(f"   ✅ Clasificaciones exitosas: {results['successful']}")
                print(f"   ❌ Errores: {results['failed']}")
                print(f"   📈 Tasa de éxito: {(results['successful']/results['total']*100):.1f}%")
                print(f"   ⏱️ Tiempo total procesamiento: {results['processing_time_seconds']:.1f}s")
                
                if results['successful'] > 0:
                    avg_time = results['processing_time_seconds'] / results['successful']
                    print(f"   ⚡ Tiempo promedio por producto: {avg_time:.2f}s")
                
                # Análisis por categorías
                categories = {}
                for result in results.get('results', []):
                    if result.get('status') == 'success':
                        classification = result.get('classification', {})
                        category = classification.get('prefLabel', 'Sin categoría')
                        categories[category] = categories.get(category, 0) + 1
                
                print(f"\n🏷️ TOP 10 CATEGORÍAS ENCONTRADAS:")
                sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
                for i, (category, count) in enumerate(sorted_categories[:10], 1):
                    percentage = (count / results['successful']) * 100
                    print(f"   {i:2d}. {category}: {count} productos ({percentage:.1f}%)")
                
                # Información de costos si está disponible
                if results.get('openai_cost_info'):
                    cost = results['openai_cost_info']
                    print(f"\n💰 ANÁLISIS DE COSTOS:")
                    print(f"   🤖 Modelo: {cost.get('model', 'N/A')}")
                    print(f"   🔢 Total llamadas API: {cost.get('api_calls', 'N/A')}")
                    
                    if cost.get('usage'):
                        usage = cost['usage']
                        print(f"   📊 Tokens totales: {usage['total_tokens']:,}")
                        print(f"      • Prompt: {usage['prompt_tokens']:,}")
                        print(f"      • Completion: {usage['completion_tokens']:,}")
                    
                    if cost.get('cost_usd'):
                        total_cost = cost['cost_usd']['total']
                        print(f"   💵 Costo total: ${total_cost:.4f} USD")
                        
                        if results['successful'] > 0:
                            cost_per_product = total_cost / results['successful']
                            print(f"   📈 Costo por producto: ${cost_per_product:.4f} USD")
                
                # Mostrar algunas muestras de clasificaciones
                print(f"\n🔍 MUESTRA DE CLASIFICACIONES (primeras 10):")
                sample_results = results.get('results', [])[:10]
                for i, result in enumerate(sample_results, 1):
                    product_id = result.get('product_id', 'N/A')
                    text = result.get('search_text', 'N/A')
                    
                    if result.get('status') == 'success':
                        classification = result.get('classification', {})
                        category = classification.get('prefLabel', 'N/A')
                        confidence = classification.get('confidence', 'N/A')
                        print(f"   {i:2d}. [{product_id}] '{text}' → {category} (conf: {confidence})")
                    else:
                        error = result.get('error', 'Error desconocido')
                        print(f"   {i:2d}. [{product_id}] '{text}' → ERROR: {error}")
                
                print(f"\n🎉 ¡PRUEBA MASIVA COMPLETADA EXITOSAMENTE!")
                print(f"✅ Sistema asíncrono procesó {results['total']} productos en {results['processing_time_seconds']:.1f}s")
                
            else:
                print(f"❌ Error obteniendo resultados: {result_response.status_code}")
                
        except Exception as e:
            print(f"❌ Error analizando resultados: {e}")
            
    elif status == "failed":
        print(f"❌ El job falló. Consulta los logs para más detalles.")
    else:
        print(f"⏰ El job no completó en el tiempo esperado. Estado final: {status}")

if __name__ == "__main__":
    test_massive_async_classification()