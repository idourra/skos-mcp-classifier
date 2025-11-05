#!/usr/bin/env python3
"""
Example script demonstrating LangGraph Multi-Agent SKOS Classifier usage
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.langgraph_classifier import create_classifier
from core.langgraph_config import load_config


def example_single_classification():
    """Example: Single text classification"""
    print("=" * 80)
    print("EXAMPLE 1: Single Text Classification")
    print("=" * 80)
    
    # Create classifier
    classifier = create_classifier(
        qdrant_url="http://localhost:6333",
        collection_name="concepts"
    )
    
    # Classify a text
    result = classifier.classify(
        text="yogur griego natural 0% grasa",
        scheme_uri="https://treew.io/taxonomy/",
        lang="es"
    )
    
    # Print results
    print(f"\n✅ Classification Result:")
    print(f"   Trace ID: {result['trace_id']}")
    
    if result['classification']:
        cls = result['classification']
        print(f"   Concept: {cls['prefLabel']}")
        print(f"   URI: {cls['uri']}")
        print(f"   Breadcrumb: {' > '.join(cls['breadcrumb'])}")
        print(f"   Confidence: {result['confidence']:.3f}")
        print(f"   Validated: {result['validated']}")
    else:
        print(f"   ⚠️ No classification")
        print(f"   Reason: {result['abstain_reason']}")
    
    # Print metrics
    print(f"\n📊 Metrics:")
    for key, value in result['metrics'].items():
        if key.endswith('_ms'):
            print(f"   {key}: {value}ms")
    
    print(f"\n💡 Explanation:")
    for exp in result['explanation']:
        print(f"   - {exp}")


def example_batch_classification():
    """Example: Batch classification"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Batch Classification")
    print("=" * 80)
    
    classifier = create_classifier()
    
    products = [
        "aceite de oliva extra virgen",
        "queso parmesano curado",
        "cereales integrales con miel",
        "leche desnatada sin lactosa",
        "pan integral de centeno"
    ]
    
    print(f"\n🔄 Classifying {len(products)} products...\n")
    
    results = []
    for i, product in enumerate(products, 1):
        print(f"{i}. '{product}'")
        
        result = classifier.classify(
            text=product,
            scheme_uri="https://treew.io/taxonomy/",
            lang="es"
        )
        
        if result['classification']:
            cls = result['classification']
            print(f"   ✅ {cls['prefLabel']} (confidence: {result['confidence']:.2f})")
        else:
            print(f"   ⚠️ Not classified: {result['abstain_reason']}")
        
        results.append(result)
    
    # Summary
    validated = sum(1 for r in results if r['validated'])
    avg_confidence = sum(r['confidence'] for r in results) / len(results)
    avg_latency = sum(r['metrics'].get('total_ms', 0) for r in results) / len(results)
    
    print(f"\n📈 Summary:")
    print(f"   Total: {len(results)}")
    print(f"   Validated: {validated} ({validated/len(results)*100:.1f}%)")
    print(f"   Avg Confidence: {avg_confidence:.3f}")
    print(f"   Avg Latency: {avg_latency:.1f}ms")


def example_with_filters():
    """Example: Classification with filters"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Classification with Filters")
    print("=" * 80)
    
    classifier = create_classifier()
    
    # Classify with ancestor filter
    result = classifier.classify(
        text="manzanas golden",
        scheme_uri="https://treew.io/taxonomy/",
        lang="es",
        ancestor_filter="https://treew.io/taxonomy/concept/100000"  # Example: Alimentos
    )
    
    print(f"\n🔍 Classification with ancestor filter:")
    if result['classification']:
        cls = result['classification']
        print(f"   Concept: {cls['prefLabel']}")
        print(f"   Breadcrumb: {' > '.join(cls['breadcrumb'])}")
    else:
        print(f"   No match within filtered ancestor")


def example_low_confidence():
    """Example: Handling low confidence / abstention"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Low Confidence / Abstention")
    print("=" * 80)
    
    # Create classifier with high confidence threshold
    classifier = create_classifier(tau_low=0.9)
    
    ambiguous_texts = [
        "producto genérico",
        "artículo varios",
        "item no especificado"
    ]
    
    print(f"\n⚠️ Testing with high confidence threshold (τ_low=0.9):\n")
    
    for text in ambiguous_texts:
        result = classifier.classify(
            text=text,
            scheme_uri="https://treew.io/taxonomy/",
            lang="es"
        )
        
        print(f"'{text}'")
        if result['validated']:
            print(f"   ✅ Classified: {result['classification']['prefLabel']}")
        else:
            print(f"   ⛔ Abstained: {result['abstain_reason']}")
            print(f"   Confidence was: {result['confidence']:.3f}")


def example_short_query():
    """Example: Short query with lexical boost"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Short Query (Lexical Boost Activated)")
    print("=" * 80)
    
    classifier = create_classifier()
    
    short_queries = [
        "yogur",
        "pan",
        "SKU-12345",
        "EAN-7890123456789"
    ]
    
    print(f"\n🔤 Testing short queries (triggers lexical boost):\n")
    
    for query in short_queries:
        result = classifier.classify(
            text=query,
            scheme_uri="https://treew.io/taxonomy/",
            lang="es"
        )
        
        # Check if N3 was activated
        n3_activated = 'n3_ms' in result['metrics']
        
        print(f"'{query}'")
        if result['classification']:
            print(f"   ✅ {result['classification']['prefLabel']}")
        print(f"   Lexical Boost: {'✓ Activated' if n3_activated else '✗ Not needed'}")
        print(f"   Latency: {result['metrics'].get('total_ms', 0)}ms")


def example_config_loading():
    """Example: Loading configuration from file"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Configuration Loading")
    print("=" * 80)
    
    # Load from YAML
    try:
        config = load_config(config_path="langgraph_config.yaml")
        print(f"\n✅ Configuration loaded from langgraph_config.yaml")
        print(f"   Qdrant URL: {config.qdrant.url}")
        print(f"   Collection: {config.qdrant.collection_name}")
        print(f"   Embedding Model: {config.embedding.model_name}")
        print(f"   Retrieval Limit: {config.retrieval.retrieval_limit}")
        print(f"   Confidence Threshold: {config.thresholds.tau_low}")
        print(f"   Cross-Encoder: {'Enabled' if config.features.cross_encoder_enabled else 'Disabled'}")
    except Exception as e:
        print(f"⚠️ Could not load config: {e}")
        print("   Using default configuration")


def example_top_k():
    """Example: Getting top-K results"""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Top-K Results")
    print("=" * 80)
    
    classifier = create_classifier(top_k_output=3)
    
    result = classifier.classify(
        text="producto lácteo",
        scheme_uri="https://treew.io/taxonomy/",
        lang="es"
    )
    
    print(f"\n🏆 Top-{len(result['top_k'])} Results:\n")
    
    for i, candidate in enumerate(result['top_k'], 1):
        score = candidate['scores'].get('ce', candidate['scores'].get('merge', 0))
        print(f"{i}. {candidate['prefLabel']}")
        print(f"   Score: {score:.3f}")
        print(f"   URI: {candidate['uri']}")
        if candidate.get('explanation'):
            print(f"   Reasoning: {', '.join(candidate['explanation'])}")
        print()


def main():
    """Run all examples"""
    print("\n" + "🤖" * 40)
    print("LangGraph Multi-Agent SKOS Classifier - Examples")
    print("🤖" * 40)
    
    try:
        # Run examples
        example_single_classification()
        example_batch_classification()
        example_with_filters()
        example_low_confidence()
        example_short_query()
        example_config_loading()
        example_top_k()
        
        print("\n" + "=" * 80)
        print("✅ All examples completed!")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
