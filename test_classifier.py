#!/usr/bin/env python3
# test_classifier.py - Script para probar el clasificador SKOS
import sys
from client.classify_standard_api import classify

def test_single_product(product_text, product_id=None):
    """Prueba un solo producto"""
    id_display = f" [ID: {product_id}]" if product_id else ""
    print(f"\n🔍 Clasificando: '{product_text}'{id_display}")
    print("-" * 50)
    
    try:
        result = classify(product_text, product_id)
        
        print("✅ Resultado exitoso:")
        print(f"   📝 Texto: {result.get('search_text', 'N/A')}")
        if 'product_id' in result:
            print(f"   🆔 ID Producto: {result.get('product_id', 'N/A')}")
        print(f"   📂 Etiqueta: {result.get('prefLabel', 'N/A')}")
        print(f"   🔢 Notación: {result.get('notation', 'N/A')}")
        print(f"   🎯 Confianza: {result.get('confidence', 'N/A')}")
        print(f"   🔗 URI: {result.get('concept_uri', 'N/A')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_batch_products(products):
    """Prueba múltiples productos - puede ser lista de strings o lista de dicts con 'text' e 'id'"""
    print("\n🧪 PRUEBAS EN LOTE")
    print("=" * 60)
    
    results = []
    for i, product in enumerate(products, 1):
        print(f"\n[{i}/{len(products)}]", end="")
        
        # Soportar tanto strings como dicts
        if isinstance(product, dict):
            product_text = product.get('text', product.get('product', ''))
            product_id = product.get('id', product.get('sku', None))
        else:
            product_text = product
            product_id = None
            
        result = test_single_product(product_text, product_id)
        results.append({
            'input': product_text,
            'product_id': product_id,
            'output': result,
            'success': result is not None
        })
    
    # Resumen
    successful = sum(1 for r in results if r['success'])
    print(f"\n📊 RESUMEN: {successful}/{len(products)} clasificaciones exitosas")
    
    return results

def interactive_mode():
    """Modo interactivo para probar productos uno por uno"""
    print("\n🎮 MODO INTERACTIVO")
    print("=" * 40)
    print("Escribe productos para clasificar (o 'quit' para salir)")
    print("Formato: 'producto' o 'producto|ID123' para incluir ID")
    
    while True:
        try:
            user_input = input("\n📦 Producto: ").strip()
            if user_input.lower() in ['quit', 'exit', 'salir', 'q']:
                print("👋 ¡Hasta luego!")
                break
            if user_input:
                # Verificar si incluye ID después de '|'
                if '|' in user_input:
                    product_text, product_id = user_input.split('|', 1)
                    product_text = product_text.strip()
                    product_id = product_id.strip()
                else:
                    product_text = user_input
                    product_id = None
                    
                test_single_product(product_text, product_id)
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break

def test_batch_with_ids():
    """Prueba productos con IDs predefinidos"""
    test_products = [
        {"text": "yogur natural griego 0% grasa", "id": "SKU001"},
        {"text": "pan integral de avena", "id": "SKU002"},
        {"text": "aceite de girasol refinado", "id": "PROD-123"},
        {"text": "manzanas verdes", "id": "FRESH-456"},
        {"text": "queso fresco de cabra", "id": "DAIRY-789"},
        {"text": "arroz basmati integral", "id": "GRAIN-001"},
        {"text": "pollo pechuga sin piel", "id": "MEAT-002"},
        {"text": "atún en lata en aceite", "id": "CAN-003"},
        {"text": "cereales avena con miel", "id": "CEREAL-004"},
        {"text": "agua mineral con gas", "id": "DRINK-005"}
    ]
    return test_batch_products(test_products)

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive" or sys.argv[1] == "-i":
            interactive_mode()
        elif sys.argv[1] == "--batch" or sys.argv[1] == "-b":
            # Productos de prueba sin IDs
            test_products = [
                "yogur natural griego 0% grasa",
                "pan integral de avena",
                "aceite de girasol refinado",
                "manzanas verdes",
                "queso fresco de cabra",
                "arroz basmati integral",
                "pollo pechuga sin piel",
                "atún en lata en aceite",
                "cereales avena con miel",
                "agua mineral con gas"
            ]
            test_batch_products(test_products)
        elif sys.argv[1] == "--batch-ids" or sys.argv[1] == "-bid":
            # Productos de prueba con IDs
            test_batch_with_ids()
        else:
            # Clasificar el texto proporcionado, verificar si incluye ID
            user_input = " ".join(sys.argv[1:])
            if '|' in user_input:
                product_text, product_id = user_input.split('|', 1)
                product_text = product_text.strip()
                product_id = product_id.strip()
            else:
                product_text = user_input
                product_id = None
            test_single_product(product_text, product_id)
    else:
        print("🔧 CLASIFICADOR SKOS - Opciones de uso:")
        print()
        print("1. Producto específico:")
        print("   python test_classifier.py 'yogur natural sin azúcar'")
        print("   python test_classifier.py 'yogur natural|SKU123'  # Con ID")
        print()
        print("2. Modo interactivo:")
        print("   python test_classifier.py --interactive")
        print("   (Usar formato: 'producto|ID' para incluir ID)")
        print()
        print("3. Pruebas en lote (sin IDs):")
        print("   python test_classifier.py --batch")
        print()
        print("4. Pruebas en lote (con IDs):")
        print("   python test_classifier.py --batch-ids")
        print()
        print("5. Sin argumentos (esta ayuda):")
        print("   python test_classifier.py")

if __name__ == "__main__":
    main()