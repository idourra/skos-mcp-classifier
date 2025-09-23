#!/usr/bin/env python3
"""
Test script para el sistema multi-taxonomía SKOS
Prueba la funcionalidad completa de gestión y clasificación con múltiples taxonomías
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from client.multi_taxonomy_classify import list_taxonomies, classify, get_available_taxonomies
from client.classify_standard_api import classify as classify_standard
import json

def test_multi_taxonomy_system():
    """Prueba completa del sistema multi-taxonomía"""
    
    print("🧪 PRUEBA DEL SISTEMA MULTI-TAXONOMÍA")
    print("=" * 60)
    
    # 1. Verificar taxonomías disponibles
    print("\n1️⃣ Verificando taxonomías disponibles...")
    try:
        available = get_available_taxonomies()
        print(f"✅ Conexión exitosa al servidor MCP")
        print(f"📊 Taxonomías activas: {available.get('total_active', 0)}")
        print(f"📚 Taxonomía por defecto: {available.get('default_taxonomy', 'N/A')}")
        
        if available["taxonomies"]:
            print("\n📋 Lista de taxonomías:")
            for tax in available["taxonomies"]:
                default_flag = " (DEFAULT)" if tax.get("is_default", False) else ""
                print(f"   • {tax['name']}{default_flag} [{tax['id']}]")
                print(f"     Conceptos: {tax.get('concepts_count', 0):,} | Idioma: {tax.get('language', 'N/A')}")
        else:
            print("⚠️  No hay taxonomías disponibles")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False
    
    # 2. Probar clasificación con taxonomía por defecto
    print("\n2️⃣ Probando clasificación con taxonomía por defecto...")
    test_product = "yogur natural sin azúcar 125g"
    
    try:
        result_default = classify(test_product)
        if "error" not in result_default:
            print(f"✅ Clasificación exitosa")
            print(f"   📦 Producto: {test_product}")
            print(f"   🏷️  Categoría: {result_default.get('prefLabel', 'N/A')}")
            print(f"   🔢 Código: {result_default.get('notation', 'N/A')}")
            print(f"   📊 Confianza: {result_default.get('confidence', 0):.2f}")
            print(f"   🗂️  Taxonomía: {result_default.get('taxonomy_used', 'N/A')}")
        else:
            print(f"❌ Error en clasificación: {result_default['error']}")
    except Exception as e:
        print(f"❌ Error en clasificación: {e}")
    
    # 3. Probar clasificación con taxonomía específica (si hay más de una)
    if len(available["taxonomies"]) > 1:
        print("\n3️⃣ Probando clasificación con taxonomía específica...")
        
        # Seleccionar una taxonomía diferente a la default
        target_taxonomy = None
        for tax in available["taxonomies"]:
            if not tax.get("is_default", False):
                target_taxonomy = tax
                break
        
        if target_taxonomy:
            try:
                result_specific = classify(test_product, taxonomy_id=target_taxonomy["id"])
                if "error" not in result_specific:
                    print(f"✅ Clasificación con taxonomía específica exitosa")
                    print(f"   📦 Producto: {test_product}")
                    print(f"   🗂️  Taxonomía: {target_taxonomy['name']} [{target_taxonomy['id']}]")
                    print(f"   🏷️  Categoría: {result_specific.get('prefLabel', 'N/A')}")
                    print(f"   🔢 Código: {result_specific.get('notation', 'N/A')}")
                    print(f"   📊 Confianza: {result_specific.get('confidence', 0):.2f}")
                else:
                    print(f"❌ Error: {result_specific['error']}")
            except Exception as e:
                print(f"❌ Error en clasificación específica: {e}")
        else:
            print("⚠️  No hay taxonomías alternativas para probar")
    else:
        print("\n3️⃣ Solo hay una taxonomía disponible, saltando prueba específica")
    
    # 4. Comparar con cliente estándar
    print("\n4️⃣ Comparando con cliente estándar...")
    try:
        result_standard = classify_standard(test_product)
        if "error" not in result_standard:
            print(f"✅ Cliente estándar funcionando")
            print(f"   🏷️  Categoría: {result_standard.get('prefLabel', 'N/A')}")
            print(f"   🔢 Código: {result_standard.get('notation', 'N/A')}")
        else:
            print(f"❌ Error en cliente estándar: {result_standard['error']}")
    except Exception as e:
        print(f"❌ Error en cliente estándar: {e}")
    
    # 5. Prueba de clasificación en lote
    print("\n5️⃣ Probando clasificación en lote...")
    test_products = [
        {"text": "leche descremada 1L", "product_id": "MILK001"},
        {"text": "pan integral 500g", "product_id": "BREAD001"},
        {"text": "manzanas rojas kg", "product_id": "APPLE001"}
    ]
    
    try:
        from client.multi_taxonomy_classify import classify_batch
        batch_results = classify_batch(test_products)
        
        successful = sum(1 for r in batch_results if "error" not in r)
        print(f"✅ Clasificación en lote completada")
        print(f"   📊 Exitosos: {successful}/{len(test_products)}")
        
        for i, result in enumerate(batch_results):
            product = test_products[i]
            if "error" not in result:
                print(f"   {i+1}. {product['text']} → {result.get('prefLabel', 'N/A')}")
            else:
                print(f"   {i+1}. {product['text']} → ERROR: {result['error']}")
                
    except Exception as e:
        print(f"❌ Error en clasificación en lote: {e}")
    
    # 6. Resumen y recomendaciones
    print("\n6️⃣ Resumen de la prueba")
    print("📋 Estado del sistema:")
    print(f"   • Servidor MCP: {'✅ Conectado' if available else '❌ Error'}")
    print(f"   • Taxonomías disponibles: {available.get('total_active', 0)}")
    print(f"   • Multi-taxonomía: {'✅ Habilitado' if len(available['taxonomies']) > 1 else '⚠️ Solo una taxonomía'}")
    print(f"   • Cliente estándar: {'✅ Compatible' if 'result_standard' in locals() and 'error' not in result_standard else '❌ Error'}")
    
    if len(available["taxonomies"]) == 1:
        print("\n💡 Recomendaciones:")
        print("   • Considere agregar más taxonomías usando los endpoints de /taxonomies")
        print("   • Use POST /taxonomies/upload para subir nuevas taxonomías SKOS")
        print("   • Configure taxonomías específicas por dominio (TreeW, Google Shopping, etc.)")
    
    print("\n✅ Prueba completada")
    return True

def interactive_demo():
    """Demo interactivo del sistema multi-taxonomía"""
    print("\n🎮 DEMO INTERACTIVO MULTI-TAXONOMÍA")
    print("=" * 50)
    
    while True:
        print("\n🎯 Opciones:")
        print("1. Listar taxonomías disponibles")
        print("2. Clasificar producto (taxonomía por defecto)")
        print("3. Clasificar producto (taxonomía específica)")
        print("4. Clasificar múltiples productos")
        print("5. Ejecutar prueba completa")
        print("0. Salir")
        
        choice = input("\nSeleccione opción (0-5): ").strip()
        
        if choice == "0":
            print("👋 ¡Hasta luego!")
            break
        elif choice == "1":
            print("\n📚 Taxonomías disponibles:")
            list_taxonomies()
        elif choice == "2":
            product = input("\n🛍️ Ingrese descripción del producto: ").strip()
            if product:
                print("🔄 Clasificando...")
                result = classify(product)
                print(f"\n📋 Resultado:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "3":
            taxonomies = get_available_taxonomies()["taxonomies"]
            if not taxonomies:
                print("❌ No hay taxonomías disponibles")
                continue
            
            print("\n📚 Taxonomías disponibles:")
            for i, tax in enumerate(taxonomies, 1):
                print(f"{i}. {tax['name']} [{tax['id']}]")
            
            try:
                tax_idx = int(input(f"\nSeleccione taxonomía (1-{len(taxonomies)}): ")) - 1
                if 0 <= tax_idx < len(taxonomies):
                    selected_tax = taxonomies[tax_idx]["id"]
                    product = input("🛍️ Ingrese descripción del producto: ").strip()
                    if product:
                        print(f"🔄 Clasificando con taxonomía {taxonomies[tax_idx]['name']}...")
                        result = classify(product, taxonomy_id=selected_tax)
                        print(f"\n📋 Resultado:")
                        print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print("❌ Selección inválida")
            except ValueError:
                print("❌ Entrada inválida")
        elif choice == "4":
            products = []
            print("\n📦 Ingrese productos (escriba 'fin' para terminar):")
            while True:
                product = input(f"Producto {len(products)+1}: ").strip()
                if product.lower() == 'fin':
                    break
                if product:
                    products.append({"text": product, "product_id": f"DEMO{len(products)+1:03d}"})
            
            if products:
                from client.multi_taxonomy_classify import classify_batch
                print(f"\n🔄 Clasificando {len(products)} productos...")
                results = classify_batch(products)
                
                print("\n📋 Resultados:")
                for i, result in enumerate(results):
                    product = products[i]
                    if "error" not in result:
                        print(f"{i+1}. {product['text']} → {result.get('prefLabel', 'Sin clasificar')}")
                    else:
                        print(f"{i+1}. {product['text']} → ERROR")
        elif choice == "5":
            test_multi_taxonomy_system()
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test sistema multi-taxonomía SKOS")
    parser.add_argument("--demo", action="store_true", help="Ejecutar demo interactivo")
    parser.add_argument("--test", action="store_true", help="Ejecutar prueba completa")
    
    args = parser.parse_args()
    
    if args.demo:
        interactive_demo()
    elif args.test:
        test_multi_taxonomy_system()
    else:
        print("🚀 Iniciando prueba automática...")
        success = test_multi_taxonomy_system()
        
        if success:
            print("\n🎮 ¿Quiere probar el demo interactivo? (s/n):")
            if input().lower().startswith('s'):
                interactive_demo()