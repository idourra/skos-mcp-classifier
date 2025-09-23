#!/usr/bin/env python3
"""
Extractor de resultados de clasificación para análisis
"""
import json

def extract_classification_summary():
    """Extrae y muestra un resumen de las clasificaciones exitosas"""
    
    with open('resultados_clasificacion_200_productos_formatted.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🏷️ RESUMEN DE PRODUCTOS CLASIFICADOS - 200 PRODUCTOS")
    print("=" * 65)
    
    # Estadísticas generales
    total = data['total']
    successful = data['successful']
    failed = data['failed']
    processing_time = data['processing_time_seconds']
    
    print(f"📊 ESTADÍSTICAS GENERALES:")
    print(f"   Total productos: {total}")
    print(f"   Exitosos: {successful} ({successful/total*100:.1f}%)")
    print(f"   Fallidos: {failed} ({failed/total*100:.1f}%)")
    print(f"   Tiempo procesamiento: {processing_time:.1f}s ({processing_time/60:.1f} min)")
    print(f"   Velocidad promedio: {processing_time/successful:.2f}s por producto")
    
    print(f"\n🎯 PRODUCTOS CLASIFICADOS EXITOSAMENTE ({successful}/200):")
    print("=" * 65)
    
    # Mostrar clasificaciones exitosas
    successful_count = 0
    failed_products = []
    
    for result in data['results']:
        if result['status'] == 'success':
            successful_count += 1
            classification = result['classification']
            product_id = result['product_id']
            search_text = result['search_text']
            category = classification['prefLabel']
            confidence = classification['confidence']
            notation = classification.get('notation', 'N/A')
            
            print(f"{successful_count:3d}. ID:{product_id:>3} | '{search_text:<25}' → {category} (conf: {confidence}) [{notation}]")
            
        else:
            failed_products.append({
                'id': result['product_id'],
                'text': result['search_text'],
                'error': result.get('error', 'Unknown error')
            })
    
    # Mostrar productos fallidos
    if failed_products:
        print(f"\n❌ PRODUCTOS QUE FALLARON ({len(failed_products)}/200):")
        print("=" * 50)
        for i, product in enumerate(failed_products, 1):
            print(f"{i:2d}. ID:{product['id']:>3} | '{product['text']:<25}' → ERROR: {product['error']}")
    
    # Análisis por categorías
    categories = {}
    for result in data['results']:
        if result['status'] == 'success':
            classification = result['classification']
            category = classification['prefLabel']
            categories[category] = categories.get(category, 0) + 1
    
    print(f"\n📈 TOP 15 CATEGORÍAS MÁS FRECUENTES:")
    print("=" * 50)
    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
    for i, (category, count) in enumerate(sorted_categories[:15], 1):
        percentage = (count / successful) * 100
        print(f"{i:2d}. {category:<45} : {count:2d} productos ({percentage:4.1f}%)")
    
    print(f"\n🎉 RESUMEN: {successful} productos clasificados exitosamente de {total} totales!")

if __name__ == "__main__":
    extract_classification_summary()