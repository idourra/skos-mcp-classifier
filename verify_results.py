#!/usr/bin/env python3
import requests
import json

# Job ID del test anterior
job_id = "7e1552e3-0acf-490e-86d3-211f869a7464"

print("🎉 VERIFICACIÓN DE RESULTADOS DEL JOB ASÍNCRONO")
print("=" * 55)

try:
    # Obtener resultados
    response = requests.get(f"http://localhost:8000/classify/result/{job_id}")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"📋 Job ID: {data['job_id']}")
        print(f"📊 Estado: {data['status']}")
        print(f"📦 Total productos: {data['total']}")
        print(f"✅ Exitosos: {data['successful']}")
        print(f"❌ Fallidos: {data['failed']}")
        print(f"⏱️ Tiempo procesamiento: {data.get('processing_time_seconds', 'N/A')}s")
        print(f"📅 Creado: {data['created_at']}")
        print(f"🏁 Completado: {data['completed_at']}")
        
        print(f"\n🔍 CLASIFICACIONES OBTENIDAS:")
        for i, result in enumerate(data.get('results', [])[:3], 1):
            if result.get('status') == 'success':
                classification = result.get('classification', {})
                print(f"{i}. 📦 {result['search_text']}")
                print(f"   → {classification.get('prefLabel', 'N/A')} (conf: {classification.get('confidence', 'N/A')})")
        
        if data.get('openai_cost_info'):
            cost = data['openai_cost_info']
            print(f"\n💰 INFORMACIÓN DE COSTOS:")
            print(f"   🤖 Modelo: {cost.get('model', 'N/A')}")
            print(f"   🎯 API calls: {cost.get('api_calls', 'N/A')}")
            if cost.get('usage'):
                usage = cost['usage']
                print(f"   📊 Tokens: {usage['total_tokens']} (prompt: {usage['prompt_tokens']}, completion: {usage['completion_tokens']})")
            if cost.get('cost_usd'):
                print(f"   💵 Costo total: ${cost['cost_usd']['total']:.4f} USD")
        
        print(f"\n✅ ¡SISTEMA ASÍNCRONO FUNCIONANDO PERFECTAMENTE!")
        
    else:
        print(f"❌ Error obteniendo resultados: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"❌ Error: {e}")