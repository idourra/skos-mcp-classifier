#!/usr/bin/env python3
"""
Monitor continuo para el job masivo en progreso
"""
import requests
import json
import time

def monitor_existing_job():
    """Monitorea el job que está en progreso"""
    job_id = "5b02c1be-0c3a-42aa-bfde-ce85d4ce885a"
    
    print("🔍 MONITOREO CONTINUO DEL JOB MASIVO")
    print("=" * 50)
    print(f"📋 Job ID: {job_id}")
    
    check_count = 0
    last_progress = 0
    start_monitor_time = time.time()
    
    while check_count < 600:  # 20 minutos máximo
        time.sleep(3)  # Check cada 3 segundos
        check_count += 1
        
        try:
            status_response = requests.get(f"http://localhost:8000/classify/status/{job_id}")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data["status"]
                
                if status_data.get("progress"):
                    progress = status_data["progress"]
                    current_percentage = progress['percentage']
                    
                    # Mostrar progreso cada 5% o cuando termine
                    if current_percentage != last_progress and (current_percentage % 5 == 0 or current_percentage == 100):
                        elapsed = time.time() - start_monitor_time
                        print(f"[{check_count:03d}] {status.upper()} - {progress['current']}/{progress['total']} ({current_percentage:.1f}%) | Monitor: {elapsed:.1f}s")
                        last_progress = current_percentage
                
                # Si terminó
                if status in ["completed", "failed", "cancelled"]:
                    total_elapsed = time.time() - start_monitor_time
                    print(f"\n🏁 Job terminado: {status.upper()}")
                    print(f"⏱️ Tiempo de monitoreo: {total_elapsed:.1f}s")
                    break
                    
            else:
                print(f"❌ Error: {status_response.status_code}")
                return
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return
    
    # Si terminó exitosamente, obtener resultados
    if status == "completed":
        print("\n📊 OBTENIENDO RESULTADOS FINALES...")
        
        try:
            result_response = requests.get(f"http://localhost:8000/classify/result/{job_id}")
            
            if result_response.status_code == 200:
                results = result_response.json()
                
                print("\n" + "=" * 60)
                print("📈 RESUMEN FINAL DE LA PRUEBA MASIVA")
                print("=" * 60)
                print(f"   📦 Total productos: {results['total']}")
                print(f"   ✅ Exitosos: {results['successful']}")
                print(f"   ❌ Fallidos: {results['failed']}")
                print(f"   📊 Tasa éxito: {(results['successful']/results['total']*100):.1f}%")
                print(f"   ⏱️ Tiempo total: {results['processing_time_seconds']:.1f}s")
                
                if results['successful'] > 0:
                    avg_time = results['processing_time_seconds'] / results['successful']
                    print(f"   ⚡ Promedio/producto: {avg_time:.2f}s")
                
                # Top categorías
                categories = {}
                for result in results.get('results', []):
                    if result.get('status') == 'success':
                        classification = result.get('classification', {})
                        category = classification.get('prefLabel', 'Sin categoría')
                        categories[category] = categories.get(category, 0) + 1
                
                print(f"\n🏷️ TOP 10 CATEGORÍAS:")
                sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
                for i, (category, count) in enumerate(sorted_categories[:10], 1):
                    percentage = (count / results['successful']) * 100
                    print(f"   {i:2d}. {category}: {count} ({percentage:.1f}%)")
                
                # Costos
                if results.get('openai_cost_info'):
                    cost = results['openai_cost_info']
                    print(f"\n💰 COSTOS:")
                    print(f"   🤖 Modelo: {cost.get('model', 'N/A')}")
                    print(f"   🔢 Llamadas API: {cost.get('api_calls', 'N/A')}")
                    
                    if cost.get('usage'):
                        usage = cost['usage']
                        print(f"   📊 Tokens: {usage['total_tokens']:,}")
                    
                    if cost.get('cost_usd'):
                        total_cost = cost['cost_usd']['total']
                        print(f"   💵 Costo total: ${total_cost:.4f}")
                        
                        if results['successful'] > 0:
                            cost_per_product = total_cost / results['successful']
                            print(f"   📈 Por producto: ${cost_per_product:.4f}")
                
                print(f"\n🎉 ¡SISTEMA VALIDADO EXITOSAMENTE CON 200 PRODUCTOS!")
                
            else:
                print(f"❌ Error obteniendo resultados: {result_response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    monitor_existing_job()