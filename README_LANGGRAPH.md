# 🤖 LangGraph Multi-Agent SKOS Classifier

## Quick Start Guide

### Installation

```bash
# Install core dependencies
pip install -r server/requirements.txt

# Install LangGraph multi-agent dependencies
pip install -r langgraph_requirements.txt
```

### Required Dependencies

```
langgraph>=0.0.30
qdrant-client>=1.7.0
sentence-transformers>=2.2.0
numpy>=1.24.0
fasttext-langdetect>=0.1.0
```

---

## 🚀 Running the LangGraph Classifier

### 1. Start Qdrant Vector Database

```bash
# Using Docker
docker run -p 6333:6333 qdrant/qdrant:latest

# Or using Docker Compose (see docker-compose.yml)
docker-compose up -d qdrant
```

### 2. Index Your SKOS Taxonomy in Qdrant

Before using the classifier, you need to index your SKOS concepts in Qdrant with multivector embeddings:

```python
# Example: Index SKOS concepts (implementation needed)
from qdrant_indexer import index_skos_taxonomy

index_skos_taxonomy(
    taxonomy_file="data/taxonomy.jsonld",
    collection_name="concepts",
    qdrant_url="http://localhost:6333"
)
```

### 3. Start the API Server

```bash
# Start LangGraph API on port 8001
python langgraph_api.py

# Or with custom config
QDRANT_URL=http://localhost:6333 python langgraph_api.py
```

The API will be available at:
- **API**: http://localhost:8001
- **Docs**: http://localhost:8001/docs
- **Health**: http://localhost:8001/health

---

## 📖 Usage Examples

### Python API

```python
from core.langgraph_classifier import create_classifier

# Create classifier instance
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
print(f"Classification: {result['classification']['prefLabel']}")
print(f"Confidence: {result['confidence']:.2f}")
print(f"Validated: {result['validated']}")
```

### REST API

#### Single Classification

```bash
curl -X POST "http://localhost:8001/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "yogur griego natural 0% grasa",
    "scheme_uri": "https://treew.io/taxonomy/",
    "lang": "es"
  }'
```

#### Batch Classification

```bash
curl -X POST "http://localhost:8001/classify/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"text": "aceite de oliva", "scheme_uri": "https://treew.io/taxonomy/"},
      {"text": "queso parmesano", "scheme_uri": "https://treew.io/taxonomy/"}
    ],
    "parallel": true
  }'
```

### Response Format

```json
{
  "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "classification": {
    "uri": "https://treew.io/taxonomy/concept/111206",
    "prefLabel": "Yogur y sustitutos",
    "breadcrumb": ["Alimentos", "Lácteos", "Yogur y sustitutos"],
    "scores": {
      "comp_vec": 0.89,
      "lexical_vec": 0.75,
      "merge": 0.86,
      "graph": 0.02
    }
  },
  "confidence": 0.88,
  "validated": true,
  "explanation": ["Multivector fusion + SKOS hierarchy adjustment"],
  "metrics": {
    "n0_ms": 2,
    "n1_ms": 45,
    "n2_ms": 120,
    "n4_ms": 8,
    "n5_ms": 15,
    "n7_ms": 5,
    "total_ms": 195
  }
}
```

---

## ⚙️ Configuration

### YAML Configuration File

Create `langgraph_config.yaml`:

```yaml
qdrant:
  url: "http://localhost:6333"
  collection_name: "concepts"
  m: 32
  ef_search: 96

retrieval:
  retrieval_limit: 50
  top_k_output: 5
  weight_comp: 1.0
  weight_lex: 0.3
  weight_path: 0.2
  weight_graph: 0.02

thresholds:
  tau_low: 0.55
  epsilon_tie: 0.03

features:
  cross_encoder_enabled: false
  lexical_boost_enabled: true
  graph_reasoning_enabled: true
```

### Environment Variables

```bash
export QDRANT_URL="http://localhost:6333"
export QDRANT_COLLECTION="concepts"
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
export EMBEDDING_DEVICE="cpu"  # or "cuda" for GPU
export CROSS_ENCODER_ENABLED="false"
export LOG_LEVEL="INFO"
```

---

## 🏗️ Architecture Overview

The LangGraph Multi-Agent Classifier consists of 10 specialized nodes:

1. **N0: Ingest & Normalize** - Text cleaning and language detection
2. **N1: Query Embeddings Builder** - Generate multivector embeddings
3. **N2: Vector Retrieval** - ANN search in Qdrant
4. **N3: Lexical Booster** - Additional lexical matching (conditional)
5. **N4: Hybrid Merger** - Fuse candidates from multiple sources
6. **N5: SKOS Graph Reasoner** - Hierarchy-aware re-ranking
7. **N6: Cross-Encoder Re-rank** - LLM-based reranking (optional)
8. **N7: Decision & Calibration** - Final classification selection
9. **N8: Policy & Constraints Validator** - Validation and abstention
10. **N9: Persist & Telemetry** - Metrics and logging
11. **N10: Error Handler** - Exception handling

### Pipeline Flow

```
N0 → N1 → N2 → [N3?] → N4 → N5 → [N6?] → N7 → N8 → N9
                ↓                           ↓
            (short query)            (cross-encoder)
```

See [LANGGRAPH_ARCHITECTURE.md](LANGGRAPH_ARCHITECTURE.md) for detailed documentation.

---

## 🧪 Testing

### Run Unit Tests

```bash
# Run all LangGraph tests
pytest tests/test_langgraph_classifier.py -v

# Run specific test
pytest tests/test_langgraph_classifier.py::TestMultiAgentClassifier::test_n0_ingest -v

# Run with coverage
pytest tests/test_langgraph_classifier.py --cov=core.langgraph_classifier
```

### Run Example Scripts

```bash
# Run comprehensive examples
python examples/langgraph_example.py

# This will demonstrate:
# - Single classification
# - Batch classification
# - Filtered classification
# - Low confidence handling
# - Short query optimization
# - Configuration loading
# - Top-K results
```

---

## 📊 Performance Tuning

### Qdrant Optimization

```yaml
# In langgraph_config.yaml
qdrant:
  m: 32              # HNSW parameter (higher = better recall, more memory)
  ef_construct: 128  # Index construction (higher = better quality)
  ef_search: 96      # Search parameter (higher = better recall, slower)
  use_quantization: true  # Enable for memory savings
  on_disk_payload: true   # Store payload on disk
```

### Embedding Configuration

```yaml
embedding:
  device: "cuda"      # Use GPU if available
  batch_size: 32      # Batch size for encoding
  use_cache: true     # Enable LRU cache
  cache_size: 10000   # Cache size (entries)
```

### Retrieval Weights

Adjust fusion weights based on your use case:

```yaml
retrieval:
  weight_comp: 1.0   # Composite vector (main signal)
  weight_lex: 0.3    # Lexical matching (exact terms)
  weight_path: 0.2   # Hierarchy context
  weight_graph: 0.02 # SKOS graph boost
```

---

## 🔍 Observability

### Metrics Available

Each classification returns detailed metrics:

```python
{
  "metrics": {
    "n0_ms": 2,        # Ingest & normalize
    "n1_ms": 45,       # Embedding generation
    "n2_ms": 120,      # Qdrant search
    "n3_ms": 30,       # Lexical boost (if triggered)
    "n4_ms": 8,        # Hybrid merge
    "n5_ms": 15,       # Graph reasoning
    "n7_ms": 5,        # Decision
    "n8_ms": 2,        # Validation
    "n9_ms": 1,        # Persistence
    "total_ms": 195    # Total latency
  }
}
```

### Health Check

```bash
curl http://localhost:8001/health
```

Response:
```json
{
  "status": "healthy",
  "classifier_initialized": true,
  "qdrant_connected": true,
  "timestamp": "2025-01-05T10:00:00Z"
}
```

---

## 🚨 Troubleshooting

### Qdrant Connection Issues

```bash
# Check if Qdrant is running
curl http://localhost:6333/collections

# Verify collection exists
curl http://localhost:6333/collections/concepts
```

### Missing Dependencies

```bash
# Reinstall all dependencies
pip install -r langgraph_requirements.txt --force-reinstall
```

### Low Classification Quality

1. **Check embedding model**: Ensure the same model used for indexing
2. **Adjust retrieval weights**: Tune based on your data
3. **Enable cross-encoder**: For better accuracy (slower)
4. **Verify SKOS data**: Check that concepts are properly indexed

### High Latency

1. **Enable caching**: Set `use_cache: true` in config
2. **Use GPU**: Set `device: cuda` for embeddings
3. **Optimize Qdrant**: Increase `ef_search` parameter
4. **Disable cross-encoder**: Set `cross_encoder_enabled: false`

---

## 📚 Additional Resources

- **Architecture Documentation**: [LANGGRAPH_ARCHITECTURE.md](LANGGRAPH_ARCHITECTURE.md)
- **API Documentation**: http://localhost:8001/docs (when running)
- **LangGraph**: https://github.com/langchain-ai/langgraph
- **Qdrant**: https://qdrant.tech/documentation/
- **SKOS**: https://www.w3.org/2004/02/skos/

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Implement actual embedding models (sentence-transformers)
- [ ] Add cross-encoder re-ranking
- [ ] Implement confidence calibration (Platt/Isotonic)
- [ ] Add SKOS taxonomy indexer for Qdrant
- [ ] Create Docker deployment templates
- [ ] Add more comprehensive tests
- [ ] Implement metrics collection backend

---

## 📄 License

This project is licensed under the MIT License.

---

**🎉 Ready to classify with multi-agent intelligence!**
