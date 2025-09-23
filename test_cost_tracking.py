#!/usr/bin/env python3
"""
Script de prueba para verificar el tracking de costos OpenAI
"""

from client.classify_standard_api import classify
import json

def test_cost_tracking():
    print('🧪 Probando clasificación con tracking de costos REAL de OpenAI...')
    print('=' * 60)
    
    result = classify('yogurt natural sin azúcar')
    
    print('📊 RESULTADO CON COSTOS:')
    print('=' * 40)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Mostrar solo la información de costos si existe
    if 'openai_cost' in result:
        print()
        print('💰 RESUMEN DE COSTOS:')
        print('=' * 30)
        cost = result['openai_cost']
        print(f'📱 Modelo: {cost["model"]}')
        print(f'🔢 API Calls: {cost.get("api_calls", "N/A")}')
        print(f'📥 Prompt tokens: {cost["usage"]["prompt_tokens"]:,}')
        print(f'📤 Completion tokens: {cost["usage"]["completion_tokens"]:,}')
        print(f'💳 Total cost: ${cost["cost_usd"]["total"]:.6f}')
    else:
        print('⚠️  No se encontró información de costos en la respuesta')
    
    return result

if __name__ == "__main__":
    test_cost_tracking()