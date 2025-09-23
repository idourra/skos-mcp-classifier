#!/usr/bin/env python3
# examples_with_ids.py - Ejemplos prácticos de uso con IDs
import json
from client.classify_standard_api import classify

def example_single_products():
    """Ejemplos de productos individuales con diferentes tipos de IDs"""
    print("🔍 EJEMPLOS DE PRODUCTOS INDIVIDUALES CON IDs")
    print("=" * 60)
    
    examples = [
        {"text": "yogur griego natural 0% grasa 500g", "id": "SKU-12345"},
        {"text": "aceite de oliva extra virgen 1L", "id": "PROD-ACEITE-001"},
        {"text": "pan integral centeno rebanado", "id": "BAKERY-PAN-789"},
        {"text": "leche sin lactosa descremada", "id": "DAIRY-MILK-456"},
        {"text": "pollo pechuga sin piel fileteada", "id": "MEAT-POL-123"}
    ]
    
    results = []
    for example in examples:
        print(f"\n📦 Producto: {example['text']}")
        print(f"🆔 ID: {example['id']}")
        print("-" * 40)
        
        result = classify(example['text'], example['id'])
        results.append(result)
        
        print(f"✅ Clasificado como: {result.get('prefLabel', 'N/A')}")
        print(f"📊 Confianza: {result.get('confidence', 'N/A')}")
        print(f"🔢 Notación: {result.get('notation', 'N/A')}")
    
    return results

def example_batch_sku_catalog():
    """Ejemplo de un catálogo de productos con SKUs"""
    print("\n🏪 EJEMPLO DE CATÁLOGO DE PRODUCTOS")
    print("=" * 60)
    
    catalog = [
        {"sku": "ALM-001", "product": "almendras naturales 200g"},
        {"sku": "ALM-002", "product": "almendras tostadas con sal 150g"},
        {"sku": "LEG-001", "product": "lentejas rojas secas 500g"},
        {"sku": "LEG-002", "product": "garbanzos cocidos lata 400g"},
        {"sku": "VEG-001", "product": "tomates cherry bandeja 250g"},
        {"sku": "VEG-002", "product": "espinacas baby bolsa 100g"},
        {"sku": "FRU-001", "product": "plátanos maduros kg"},
        {"sku": "FRU-002", "product": "fresas frescas bandeja 500g"}
    ]
    
    print("Clasificando catálogo completo...")
    results = []
    
    for item in catalog:
        print(f"\n[{item['sku']}] {item['product']}")
        
        result = classify(item['product'], item['sku'])
        results.append({
            'sku': item['sku'],
            'product': item['product'],
            'classification': result
        })
        
        print(f"  → {result.get('prefLabel', 'N/A')} (Conf: {result.get('confidence', 'N/A')})")
    
    # Guardar catálogo clasificado
    with open('catalog_classified.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Catálogo clasificado guardado en: catalog_classified.json")
    return results

def example_ecommerce_integration():
    """Ejemplo de integración para e-commerce"""
    print("\n🛒 EJEMPLO DE INTEGRACIÓN E-COMMERCE")
    print("=" * 60)
    
    # Simular productos de una tienda online
    ecommerce_products = [
        {
            "product_id": "PROD-2024-001",
            "name": "Quinoa roja orgánica grano entero 750g",
            "brand": "NaturalLife",
            "category_current": "Cereales",  # Categoría actual del sistema
            "price": 8.99
        },
        {
            "product_id": "PROD-2024-002", 
            "name": "Miel de abeja pura multifloral 500ml",
            "brand": "Apicola Premium",
            "category_current": "Endulzantes",
            "price": 12.50
        },
        {
            "product_id": "PROD-2024-003",
            "name": "Atún en aceite de oliva lata 160g",
            "brand": "OceanFresh", 
            "category_current": "Conservas",
            "price": 3.25
        }
    ]
    
    print("Validando/mejorando categorización existente...")
    
    for product in ecommerce_products:
        print(f"\n🏷️  Producto ID: {product['product_id']}")
        print(f"📦 Nombre: {product['name']}")
        print(f"🏭 Marca: {product['brand']}")
        print(f"📂 Categoría actual: {product['category_current']}")
        print(f"💰 Precio: ${product['price']}")
        print("-" * 50)
        
        # Clasificar con SKOS
        result = classify(product['name'], product['product_id'])
        
        print(f"🔍 Clasificación SKOS: {result.get('prefLabel', 'N/A')}")
        print(f"🎯 Confianza: {result.get('confidence', 'N/A')}")
        print(f"🔢 Código SKOS: {result.get('notation', 'N/A')}")
        
        # Comparar con categoría actual
        if result.get('prefLabel'):
            skos_category = result['prefLabel']
            current_category = product['category_current']
            
            if skos_category.lower() != current_category.lower():
                print(f"⚠️  DIFERENCIA detectada!")
                print(f"   Actual: {current_category}")
                print(f"   SKOS: {skos_category}")
                print(f"   Recomendación: Considerar actualizar categoría")
            else:
                print(f"✅ Categorización consistente")

def example_csv_export():
    """Ejemplo de exportación a CSV para uso posterior"""
    print("\n📊 EJEMPLO DE EXPORTACIÓN CSV")
    print("=" * 60)
    
    import csv
    
    products_data = [
        {"id": "ITEM-001", "description": "Galletas integrales avena y miel 200g"},
        {"id": "ITEM-002", "description": "Jugo de naranja natural sin pulpa 1L"},
        {"id": "ITEM-003", "description": "Pasta de dientes blanqueadora 100ml"},
        {"id": "ITEM-004", "description": "Arroz basmati grano largo 1kg"},
        {"id": "ITEM-005", "description": "Cerveza artesanal IPA 355ml"}
    ]
    
    # Clasificar y preparar para CSV
    csv_data = []
    for product in products_data:
        result = classify(product['description'], product['id'])
        
        csv_row = {
            'product_id': product['id'],
            'description': product['description'],
            'skos_category': result.get('prefLabel', ''),
            'skos_notation': result.get('notation', ''),
            'skos_uri': result.get('concept_uri', ''),
            'confidence': result.get('confidence', 0),
            'classification_timestamp': '2025-09-23'  # Timestamp para auditoria
        }
        csv_data.append(csv_row)
        
        print(f"✅ {product['id']}: {result.get('prefLabel', 'N/A')}")
    
    # Guardar CSV
    filename = 'products_classified.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['product_id', 'description', 'skos_category', 'skos_notation', 
                     'skos_uri', 'confidence', 'classification_timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in csv_data:
            writer.writerow(row)
    
    print(f"\n💾 Datos exportados a: {filename}")
    return csv_data

def main():
    """Ejecutar todos los ejemplos"""
    print("🚀 EJEMPLOS PRÁCTICOS DE USO DEL CLASIFICADOR SKOS")
    print("=" * 70)
    
    # Ejemplo 1: Productos individuales
    example_single_products()
    
    # Ejemplo 2: Catálogo por lotes  
    example_batch_sku_catalog()
    
    # Ejemplo 3: Integración e-commerce
    example_ecommerce_integration()
    
    # Ejemplo 4: Exportación CSV
    example_csv_export()
    
    print("\n🎉 ¡Todos los ejemplos completados!")
    print("📁 Archivos generados:")
    print("   • catalog_classified.json")
    print("   • products_classified.csv")

if __name__ == "__main__":
    main()