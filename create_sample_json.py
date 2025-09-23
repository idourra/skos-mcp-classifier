#!/usr/bin/env python3
"""
Crea un JSON de muestra con productos específicos y sus clasificaciones
"""
import json

def create_sample_json():
    """Crea un JSON de muestra con productos interesantes"""
    
    # Cargar el resultado completo
    with open('resultados_clasificacion_200_productos_formatted.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Productos de interés para mostrar
    interesting_products = {
        "1": "pollo",
        "2": "aceite", 
        "24": "pan",
        "28": "cerveza",
        "32": "pescado",
        "75": "refrigerador",
        "105": "lavadora",
        "166": "televisor",
        "176": "pinturas",
        "198": "cafetera",
        "200": "muebles",
        "177": "pasta de dientes",  # Error example
        "189": "jabon de baño"      # Error example
    }
    
    sample_results = []
    
    for result in data['results']:
        product_id = result['product_id']
        if product_id in interesting_products:
            sample_results.append(result)
    
    # Crear JSON de muestra
    sample_data = {
        "metadata": {
            "description": "Muestra de clasificaciones del sistema SKOS-MCP",
            "total_products_in_full_test": data['total'],
            "successful_classifications": data['successful'],
            "failed_classifications": data['failed'],
            "success_rate_percentage": round((data['successful'] / data['total']) * 100, 1),
            "processing_time_seconds": data['processing_time_seconds'],
            "average_time_per_product": round(data['processing_time_seconds'] / data['successful'], 2)
        },
        "sample_classifications": sample_results
    }
    
    # Guardar muestra
    with open('muestra_clasificaciones.json', 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    print("📄 MUESTRA DE CLASIFICACIONES CREADA")
    print("=" * 50)
    print("Archivo: muestra_clasificaciones.json")
    print(f"Productos incluidos: {len(sample_results)}")
    print(f"Exitosos: {len([r for r in sample_results if r['status'] == 'success'])}")
    print(f"Fallidos: {len([r for r in sample_results if r['status'] == 'failed'])}")

if __name__ == "__main__":
    create_sample_json()