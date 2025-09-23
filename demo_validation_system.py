#!/usr/bin/env python3
"""
Demo del Sistema de Validación Riguroso de Taxonomías SKOS
Demuestra los requisitos mínimos y validaciones de calidad para taxonomías
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.taxonomy_manager import TaxonomyManager
import json
import tempfile
from pathlib import Path

def create_sample_taxonomies():
    """Crear taxonomías de ejemplo con diferentes niveles de calidad"""
    
    # 1. TAXONOMÍA MÍNIMA (Apenas cumple requisitos)
    minimal_skos = """
    {
        "@context": {
            "skos": "http://www.w3.org/2004/02/skos/core#",
            "dct": "http://purl.org/dc/terms/"
        },
        "@graph": [
            {
                "@type": "skos:ConceptScheme",
                "@id": "http://example.com/minimal-scheme",
                "skos:prefLabel": "Esquema Mínimo",
                "dct:title": "Taxonomía Mínima de Ejemplo"
            },
            {
                "@type": "skos:Concept",
                "@id": "http://example.com/concept/food",
                "skos:prefLabel": "Alimentos",
                "skos:topConceptOf": "http://example.com/minimal-scheme"
            },
            {
                "@type": "skos:Concept", 
                "@id": "http://example.com/concept/dairy",
                "skos:prefLabel": "Lácteos",
                "skos:broader": "http://example.com/concept/food"
            },
            {
                "@type": "skos:Concept",
                "@id": "http://example.com/concept/milk",
                "skos:prefLabel": "Leche",
                "skos:broader": "http://example.com/concept/dairy"
            }
        ]
    }
    """
    
    # Agregar más conceptos para llegar al mínimo de 20
    minimal_concepts = []
    for i in range(4, 25):  # Agregar 21 conceptos más
        concept = {
            "@type": "skos:Concept",
            "@id": f"http://example.com/concept/item{i}",
            "skos:prefLabel": f"Producto {i}",
            "skos:broader": "http://example.com/concept/food"
        }
        minimal_concepts.append(concept)
    
    minimal_data = json.loads(minimal_skos)
    minimal_data["@graph"].extend(minimal_concepts)
    
    # 2. TAXONOMÍA DE ALTA CALIDAD (Como TreeW)
    quality_skos = """
    {
        "@context": {
            "skos": "http://www.w3.org/2004/02/skos/core#",
            "dct": "http://purl.org/dc/terms/"
        },
        "@graph": [
            {
                "@type": "skos:ConceptScheme",
                "@id": "http://example.com/quality-scheme", 
                "skos:prefLabel": "Taxonomía de Alta Calidad",
                "dct:title": "Taxonomía Enriquecida para Clasificación",
                "dct:description": "Taxonomía con definiciones, etiquetas alternativas y relaciones semánticas"
            },
            {
                "@type": "skos:Concept",
                "@id": "http://example.com/concept/beverages",
                "skos:prefLabel": "Bebidas",
                "skos:altLabel": ["Drinks", "Líquidos"],
                "skos:definition": "Líquidos preparados para consumo humano, incluyendo bebidas alcohólicas y no alcohólicas",
                "skos:notation": "BEV",
                "skos:topConceptOf": "http://example.com/quality-scheme"
            },
            {
                "@type": "skos:Concept",
                "@id": "http://example.com/concept/alcoholic",
                "skos:prefLabel": "Bebidas Alcohólicas", 
                "skos:altLabel": ["Alcohol", "Bebidas con alcohol"],
                "skos:definition": "Bebidas que contienen etanol producido por fermentación o destilación",
                "skos:notation": "BEV-ALC",
                "skos:broader": "http://example.com/concept/beverages"
            },
            {
                "@type": "skos:Concept",
                "@id": "http://example.com/concept/wine",
                "skos:prefLabel": "Vino",
                "skos:altLabel": ["Wine", "Vinos"],
                "skos:definition": "Bebida alcohólica elaborada por fermentación de uvas",
                "skos:notation": "BEV-ALC-WIN",
                "skos:broader": "http://example.com/concept/alcoholic"
            },
            {
                "@type": "skos:Concept",
                "@id": "http://example.com/concept/beer",
                "skos:prefLabel": "Cerveza",
                "skos:altLabel": ["Beer", "Cervezas"],
                "skos:definition": "Bebida alcohólica elaborada con cereales malteados",
                "skos:notation": "BEV-ALC-BEE", 
                "skos:broader": "http://example.com/concept/alcoholic",
                "skos:related": "http://example.com/concept/wine"
            },
            {
                "@type": "skos:Concept",
                "@id": "http://example.com/concept/non-alcoholic",
                "skos:prefLabel": "Bebidas No Alcohólicas",
                "skos:altLabel": ["Sin alcohol", "Non-alcoholic drinks"],
                "skos:definition": "Bebidas que no contienen alcohol o contienen menos del 0.5% de alcohol",
                "skos:notation": "BEV-NON", 
                "skos:broader": "http://example.com/concept/beverages"
            },
            {
                "@type": "skos:Concept",
                "@id": "http://example.com/concept/soft-drinks",
                "skos:prefLabel": "Refrescos",
                "skos:altLabel": ["Soft drinks", "Bebidas gaseosas", "Sodas"],
                "skos:definition": "Bebidas no alcohólicas, generalmente carbonatadas y azucaradas",
                "skos:notation": "BEV-NON-SOF",
                "skos:broader": "http://example.com/concept/non-alcoholic"
            }
        ]
    }
    """
    
    # Agregar más conceptos de calidad
    quality_concepts = []
    base_concepts = [
        ("juices", "Jugos", "Bebidas elaboradas con frutas exprimidas", ["Zumos", "Fruit juices"]),
        ("water", "Agua", "Agua potable natural o procesada", ["Water", "Aqua"]),
        ("tea", "Té", "Infusión de hojas de Camellia sinensis", ["Tea", "Infusiones"]),
        ("coffee", "Café", "Bebida elaborada con granos de café", ["Coffee", "Cafés"])
    ]
    
    for i, (code, label, definition, alt_labels) in enumerate(base_concepts, 8):
        concept = {
            "@type": "skos:Concept",
            "@id": f"http://example.com/concept/{code}",
            "skos:prefLabel": label,
            "skos:altLabel": alt_labels,
            "skos:definition": definition,
            "skos:notation": f"BEV-NON-{code.upper()[:3]}",
            "skos:broader": "http://example.com/concept/non-alcoholic"
        }
        quality_concepts.append(concept)
    
    # Agregar conceptos adicionales para llegar a 30+
    for i in range(12, 35):
        concept = {
            "@type": "skos:Concept",
            "@id": f"http://example.com/concept/beverage{i}",
            "skos:prefLabel": f"Bebida Tipo {i}",
            "skos:altLabel": [f"Drink {i}", f"Beverage {i}"],
            "skos:definition": f"Tipo específico de bebida número {i} con características particulares",
            "skos:notation": f"BEV-{i}",
            "skos:broader": "http://example.com/concept/beverages"
        }
        quality_concepts.append(concept)
    
    quality_data = json.loads(quality_skos)
    quality_data["@graph"].extend(quality_concepts)
    
    # 3. TAXONOMÍA DEFICIENTE (No cumple requisitos)
    deficient_skos = """
    {
        "@context": {
            "skos": "http://www.w3.org/2004/02/skos/core#"
        },
        "@graph": [
            {
                "@type": "skos:Concept",
                "@id": "http://example.com/concept/product1"
            },
            {
                "@type": "skos:Concept", 
                "@id": "http://example.com/concept/product2"
            }
        ]
    }
    """
    
    return {
        "minimal": json.dumps(minimal_data, indent=2),
        "quality": json.dumps(quality_data, indent=2), 
        "deficient": deficient_skos
    }

def test_taxonomy_validation():
    """Probar el sistema de validación con diferentes taxonomías"""
    
    print("🧪 DEMO: Sistema de Validación Riguroso de Taxonomías SKOS")
    print("=" * 70)
    
    manager = TaxonomyManager()
    taxonomies = create_sample_taxonomies()
    
    test_cases = [
        ("📊 TAXONOMÍA MÍNIMA", "minimal", "Cumple apenas los requisitos básicos"),
        ("🌟 TAXONOMÍA DE ALTA CALIDAD", "quality", "Enriquecida como TreeW"),
        ("❌ TAXONOMÍA DEFICIENTE", "deficient", "No cumple requisitos mínimos")
    ]
    
    for title, key, description in test_cases:
        print(f"\n{title}")
        print(f"Descripción: {description}")
        print("-" * 60)
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonld', delete=False) as f:
            f.write(taxonomies[key])
            temp_path = f.name
        
        try:
            # Validar taxonomía
            result = manager.validate_skos_file(temp_path)
            
            print(f"🔍 RESULTADO DE VALIDACIÓN:")
            print(f"   ✅ Válida: {result['valid']}")
            print(f"   📊 Calidad: {result['quality_score']:.1%}")
            print(f"   🏆 Nivel: {result['compliance_level']}")
            
            print(f"\n📋 REQUISITOS:")
            for req, met in result.get('requirements_met', {}).items():
                status = "✅" if met else "❌"
                print(f"   {status} {req.replace('_', ' ').title()}")
            
            if result.get('statistics'):
                stats = result['statistics']
                print(f"\n📈 ESTADÍSTICAS:")
                print(f"   • Conceptos: {stats.get('total_concepts', 0)}")
                print(f"   • Esquemas: {stats.get('total_schemes', 0)}")
                print(f"   • Relaciones jerárquicas: {stats.get('hierarchical_relations', 0)}")
                print(f"   • Con definiciones: {stats.get('concepts_with_definitions', 0)}")
                print(f"   • Con etiquetas alt: {stats.get('concepts_with_altlabels', 0)}")
                print(f"   • Profundidad máxima: {stats.get('max_hierarchy_depth', 0)}")
            
            if result.get('enrichment_features'):
                print(f"\n⭐ CARACTERÍSTICAS DE ENRIQUECIMIENTO:")
                for feature in result['enrichment_features']:
                    print(f"   • {feature}")
            
            if result.get('errors'):
                print(f"\n❌ ERRORES:")
                for error in result['errors']:
                    print(f"   • {error}")
            
            if result.get('warnings'):
                print(f"\n⚠️ ADVERTENCIAS:")
                for warning in result['warnings']:
                    print(f"   • {warning}")
            
            if result.get('recommendations'):
                print(f"\n💡 RECOMENDACIONES:")
                for rec in result['recommendations']:
                    print(f"   • {rec}")
            
            # Simular intento de registro
            if result['valid']:
                print(f"\n✅ Esta taxonomía SERÍA ACEPTADA en el sistema")
            else:
                print(f"\n❌ Esta taxonomía SERÍA RECHAZADA")
        
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
        
        finally:
            # Limpiar archivo temporal
            Path(temp_path).unlink(missing_ok=True)
    
    print(f"\n🎯 RESUMEN DE REQUISITOS MÍNIMOS:")
    print("=" * 60)
    print("✅ OBLIGATORIOS para aceptar la taxonomía:")
    print("   • SKOS compliant (conceptos, esquemas, jerarquías)")
    print("   • Mínimo 20 conceptos con etiquetas (skos:prefLabel)")
    print("   • Estructura jerárquica coherente (skos:broader/narrower)")
    print("   • Calidad mínima 60% para clasificación efectiva")
    print()
    print("🌟 RECOMENDADOS para mejor clasificación:")
    print("   • Definiciones (skos:definition) en >60% conceptos")
    print("   • Etiquetas alternativas (skos:altLabel) para búsqueda")
    print("   • Notaciones (skos:notation) para códigos")
    print("   • Relaciones semánticas (skos:related)")
    print("   • Jerarquía profunda (3-5 niveles)")
    print()
    print("💡 La taxonomía TreeW actual cumple EXCELENTE nivel de calidad")

def test_api_validation():
    """Probar validación a través de la API"""
    print(f"\n🚀 PRUEBA DE API DE VALIDACIÓN")
    print("=" * 50)
    
    print("Para probar la API de validación:")
    print()
    print("1. Iniciar servidor:")
    print("   python server/multi_taxonomy_main.py")
    print()
    print("2. Validar archivo:")
    print('   curl -X POST "http://localhost:8080/taxonomies/validate" \\')
    print('     -F "file=@mi_taxonomia.jsonld"')
    print()
    print("3. Subir taxonomía válida:")
    print('   curl -X POST "http://localhost:8080/taxonomies/upload" \\')
    print('     -F "file=@mi_taxonomia.jsonld" \\')
    print('     -F \'metadata={"id":"mi-tax","name":"Mi Taxonomía"}\'')

if __name__ == "__main__":
    test_taxonomy_validation()
    test_api_validation()