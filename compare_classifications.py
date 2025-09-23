#!/usr/bin/env python3
# compare_classifications.py - Comparar clasificaciones de múltiples productos
import json
from client.classify_standard_api import classify

def compare_products(products, save_results=True):
    """Compara clasificaciones de múltiples productos y guarda resultados
    
    Args:
        products: Lista de strings o lista de dicts con keys 'text'/'product' e 'id'/'sku'
        save_results: Si guardar los resultados en archivo JSON
    """
    results = []
    
    print("🔄 Clasificando productos...")
    for i, product in enumerate(products, 1):
        # Soportar tanto strings como dicts
        if isinstance(product, dict):
            product_text = product.get('text', product.get('product', ''))
            product_id = product.get('id', product.get('sku', None))
        else:
            product_text = product
            product_id = None
            
        print(f"[{i}/{len(products)}] {product_text}" + (f" [ID: {product_id}]" if product_id else ""))
        
        try:
            result = classify(product_text, product_id)
            results.append({
                'product': product_text,
                'product_id': product_id,
                'classification': result,
                'success': True
            })
        except Exception as e:
            results.append({
                'product': product_text,
                'product_id': product_id,
                'error': str(e),
                'success': False
            })
    
    # Mostrar resumen
    print("\n📊 Resultados por categoría:")
    categories = {}
    for result in results:
        if result['success']:
            category = result['classification']['prefLabel']
            if category not in categories:
                categories[category] = []
            product_display = result['product']
            if result['product_id']:
                product_display += f" [{result['product_id']}]"
            categories[category].append(product_display)
    
    for category, products_list in categories.items():
        print(f"\n📂 {category}:")
        for product in products_list:
            print(f"   • {product}")
    
    # Guardar resultados si se solicita
    if save_results:
        filename = f"classification_results_{len(products)}_products.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Resultados guardados en: {filename}")
    
    return results

if __name__ == "__main__":
    # Lista de productos de prueba con IDs
    test_products_with_ids = [
        {"text": "yogur natural griego", "id": "YOG-001"},
        {"text": "pan de molde integral", "id": "PAN-002"},
        {"text": "aceite de oliva virgen", "id": "ACE-003"},
        {"text": "manzanas rojas", "id": "FRU-004"},
        {"text": "queso manchego", "id": "QUE-005"},
        {"text": "leche descremada", "id": "LEC-006"},
        {"text": "pollo pechuga", "id": "CAR-007"},
        {"text": "salmón fresco", "id": "PES-008"},
        {"text": "arroz integral", "id": "CER-009"},
        {"text": "pasta de trigo", "id": "PAS-010"},
        {"text": "cerveza rubia", "id": "BEB-011"},
        {"text": "agua mineral", "id": "AGU-012"},
        {"text": "café molido", "id": "CAF-013"},
        {"text": "té verde", "id": "TE-014"},
        {"text": "chocolate negro 70%", "id": "CHO-015"}
    ]
    
    # También ejemplo sin IDs para compatibilidad
    test_products_simple = [
        "yogur natural griego",
        "pan de molde integral",
        "aceite de oliva virgen",
        "manzanas rojas",
        "queso manchego"
    ]
    
    print("🔍 Comparando productos CON IDs:")
    compare_products(test_products_with_ids)
    
    print("\n" + "="*60)
    print("🔍 Comparando productos SIN IDs:")
    compare_products(test_products_simple, save_results=False)