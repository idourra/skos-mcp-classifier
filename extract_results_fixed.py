#!/usr/bin/env python3
"""
Extractor corregido de resultados de clasificación para análisis
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
    
    print("📊 ESTADÍSTICAS GENERALES:")
    print(f"   Total productos: {total}")
    print(f"   Exitosos: {successful} ({successful/total*100:.1f}%)")
    print(f"   Fallidos: {failed} ({failed/total*100:.1f}%)")
    print(f"   Tiempo procesamiento: {processing_time:.1f}s ({processing_time/60:.1f} min)")
    print(f"   Velocidad promedio: {processing_time/successful:.2f}s por producto")
    
    print(f"\n📋 PRODUCTOS CLASIFICADOS (primeros 50 exitosos):")
    print("=" * 80)
    
    # Mostrar solo los primeros 50 productos exitosos para no saturar
    successful_count = 0
    failed_products = []
    categories = {}
    
    for result in data['results']:
        if result['status'] == 'success':
            classification = result['classification']
            product_id = result['product_id']
            search_text = result['search_text']
            
            # Manejar el prefLabel que puede ser dict o string
            if isinstance(classification['prefLabel'], dict):
                category = classification['prefLabel'].get('es', 'Categoría sin nombre')
            else:
                category = classification['prefLabel']
            
            confidence = classification['confidence']
            notation = classification.get('notation', 'N/A')
            
            # Solo mostrar los primeros 50
            if successful_count < 50:
                print(f"{successful_count+1:2d}. ID:{product_id:>3} '{search_text:<25}' → {category[:45]} (conf: {confidence})")
            
            successful_count += 1
            
            # Contar categorías para estadísticas
            categories[category] = categories.get(category, 0) + 1
            
        else:
            failed_products.append({
                'id': result['product_id'],
                'text': result['search_text'],
                'error': result.get('error', 'Unknown error')
            })
    
    print(f"\n... y {successful_count - 50} productos más clasificados exitosamente.")
    
    # Top categorías
    print(f"\n📈 TOP 15 CATEGORÍAS MÁS FRECUENTES:")
    print("=" * 60)
    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
    for i, (category, count) in enumerate(sorted_categories[:15], 1):
        percentage = (count / successful) * 100
        category_name = category[:50] if len(category) > 50 else category
        print(f"{i:2d}. {category_name:<50} : {count:2d} ({percentage:4.1f}%)")
    
    # Productos fallidos
    if failed_products:
        print(f"\n❌ PRODUCTOS QUE FALLARON ({len(failed_products)}/200):")
        print("=" * 60)
        for i, product in enumerate(failed_products, 1):
            print(f"{i:2d}. ID:{product['id']:>3} '{product['text']:<30}' → {product['error']}")
    
    print(f"\n🎉 RESUMEN EJECUTIVO:")
    print(f"   ✅ {successful} productos clasificados exitosamente")
    print(f"   ❌ {failed} productos fallaron (principalmente productos de higiene)")
    print(f"   ⚡ Velocidad promedio: {processing_time/successful:.2f}s por producto") 
    print(f"   📊 Tasa de éxito: {successful/total*100:.1f}%")
    print(f"   💰 Costo estimado total: ~${successful * 0.0005:.3f} USD")

if __name__ == "__main__":
    extract_classification_summary()