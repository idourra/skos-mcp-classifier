# 🔗 Integration Guide: LangGraph Multi-Agent Classifier

This guide explains how to integrate the LangGraph Multi-Agent SKOS Classifier with your existing system or as a standalone service.

---

## 🏗️ Architecture Integration

### Option 1: Standalone Service (Recommended)

Deploy the LangGraph classifier as a separate microservice:

```
┌─────────────┐      ┌──────────────────┐      ┌─────────┐
│ Your App/   │─────▶│ LangGraph API    │─────▶│ Qdrant  │
│ Service     │      │ (Port 8001)      │      │ :6333   │
└─────────────┘      └──────────────────┘      └─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ SKOS Concepts    │
                     │ (Vector Index)   │
                     └──────────────────┘
```

**Advantages:**
- Independent scaling
- Easy deployment
- Clear API boundaries
- Can replace OpenAI classifier gradually

### Option 2: Library Integration

Import directly into your Python application:

```python
from core.langgraph_classifier import create_classifier

classifier = create_classifier(
    qdrant_url="http://localhost:6333",
    collection_name="concepts"
)

result = classifier.classify(
    text="product description",
    scheme_uri="https://treew.io/taxonomy/",
    lang="es"
)
```

**Advantages:**
- Lower latency
- Direct access to internals
- Easier debugging

---

## 🚀 Deployment Options

### Docker Compose (Easiest)

```bash
# Start everything
./start_langgraph.sh

# Check status
docker-compose -f docker-compose.langgraph.yml ps

# View logs
docker-compose -f docker-compose.langgraph.yml logs -f

# Stop
./stop_langgraph.sh
```

### Kubernetes

```yaml
# langgraph-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langgraph-classifier
spec:
  replicas: 3
  selector:
    matchLabels:
      app: langgraph-classifier
  template:
    metadata:
      labels:
        app: langgraph-classifier
    spec:
      containers:
      - name: classifier
        image: your-registry/langgraph-classifier:latest
        ports:
        - containerPort: 8001
        env:
        - name: QDRANT_URL
          value: "http://qdrant-service:6333"
        - name: QDRANT_COLLECTION
          value: "concepts"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 40
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: langgraph-service
spec:
  selector:
    app: langgraph-classifier
  ports:
  - port: 8001
    targetPort: 8001
  type: ClusterIP
```

### Railway / Render

1. Connect your GitHub repository
2. Set environment variables:
   ```
   QDRANT_URL=https://your-qdrant-instance.cloud
   QDRANT_COLLECTION=concepts
   PORT=8001
   ```
3. Deploy from `langgraph_api.py`

---

## 🔧 Integration with Existing System

### Migrating from OpenAI Classifier

You can run both classifiers in parallel and gradually migrate:

```python
from client.classify_standard_api import classify as openai_classify
from core.langgraph_classifier import create_classifier

# Initialize both
langgraph_classifier = create_classifier()

def hybrid_classify(text, scheme_uri, lang="es", use_langgraph=False):
    """
    Hybrid classifier that can use either backend
    """
    if use_langgraph:
        result = langgraph_classifier.classify(
            text=text,
            scheme_uri=scheme_uri,
            lang=lang
        )
        # Convert to compatible format
        return {
            "concept_uri": result["classification"]["uri"],
            "prefLabel": result["classification"]["prefLabel"],
            "confidence": result["confidence"],
            "trace_id": result["trace_id"]
        }
    else:
        # Use existing OpenAI classifier
        return openai_classify(text)
```

### A/B Testing Setup

```python
import random

def classify_with_ab_test(text, scheme_uri, lang="es"):
    """
    A/B test between OpenAI and LangGraph classifiers
    """
    # 50/50 split
    use_langgraph = random.random() < 0.5
    
    result = hybrid_classify(text, scheme_uri, lang, use_langgraph)
    result["classifier_used"] = "langgraph" if use_langgraph else "openai"
    
    # Log for analysis
    log_classification(result)
    
    return result
```

### Fallback Strategy

```python
def classify_with_fallback(text, scheme_uri, lang="es"):
    """
    Try LangGraph first, fallback to OpenAI on failure
    """
    try:
        result = langgraph_classifier.classify(
            text=text,
            scheme_uri=scheme_uri,
            lang=lang
        )
        
        # If not validated, fallback
        if not result["validated"]:
            return openai_classify(text)
        
        return format_result(result)
    
    except Exception as e:
        logger.warning(f"LangGraph failed: {e}, using OpenAI")
        return openai_classify(text)
```

---

## 📊 Monitoring & Observability

### Health Check Integration

```python
import requests

def check_classifier_health():
    """Check if classifier is healthy"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        data = response.json()
        
        return {
            "healthy": data["status"] == "healthy",
            "qdrant_connected": data["qdrant_connected"],
            "classifier_ready": data["classifier_initialized"]
        }
    except Exception as e:
        return {"healthy": False, "error": str(e)}
```

### Metrics Collection

```python
from prometheus_client import Counter, Histogram

# Define metrics
classifications_total = Counter(
    'langgraph_classifications_total',
    'Total classifications',
    ['status', 'language']
)

classification_latency = Histogram(
    'langgraph_classification_latency_seconds',
    'Classification latency',
    ['language']
)

# Use in your code
def monitored_classify(text, scheme_uri, lang="es"):
    start = time.time()
    
    try:
        result = langgraph_classifier.classify(text, scheme_uri, lang)
        status = "validated" if result["validated"] else "abstained"
        
    except Exception as e:
        status = "error"
        raise
    
    finally:
        # Record metrics
        latency = time.time() - start
        classifications_total.labels(status=status, language=lang).inc()
        classification_latency.labels(language=lang).observe(latency)
    
    return result
```

### Logging Integration

```python
import logging
import json

logger = logging.getLogger(__name__)

def log_classification(result):
    """Log classification for analysis"""
    log_entry = {
        "trace_id": result["trace_id"],
        "validated": result["validated"],
        "confidence": result["confidence"],
        "latency_ms": result["metrics"]["total_ms"],
        "language": result["detected_lang"],
        "classification": result["classification"]["prefLabel"] if result["classification"] else None,
        "abstain_reason": result.get("abstain_reason")
    }
    
    logger.info(json.dumps(log_entry))
```

---

## 🔐 Security Considerations

### API Authentication

Add authentication to the API:

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify API token"""
    token = credentials.credentials
    if token != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

# Add to endpoints
@app.post("/classify", dependencies=[Depends(verify_token)])
async def classify_text(request: ClassificationRequest):
    ...
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/classify")
@limiter.limit("100/minute")
async def classify_text(request: ClassificationRequest):
    ...
```

---

## 🧪 Testing Your Integration

### Basic Smoke Test

```bash
# Test health endpoint
curl http://localhost:8001/health

# Test classification
curl -X POST http://localhost:8001/classify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "test product",
    "scheme_uri": "https://treew.io/taxonomy/",
    "lang": "es"
  }'
```

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 -p test_payload.json \
   -T application/json \
   http://localhost:8001/classify

# Using wrk
wrk -t10 -c100 -d30s --latency \
    -s post_classify.lua \
    http://localhost:8001/classify
```

### Integration Test Suite

```python
import pytest
import requests

BASE_URL = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]

def test_single_classification():
    """Test single classification"""
    payload = {
        "text": "yogur natural",
        "scheme_uri": "https://treew.io/taxonomy/",
        "lang": "es"
    }
    response = requests.post(f"{BASE_URL}/classify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "classification" in data
    assert "confidence" in data

def test_batch_classification():
    """Test batch classification"""
    payload = {
        "items": [
            {"text": "aceite de oliva", "scheme_uri": "https://treew.io/taxonomy/"},
            {"text": "queso parmesano", "scheme_uri": "https://treew.io/taxonomy/"}
        ],
        "parallel": True
    }
    response = requests.post(f"{BASE_URL}/classify/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
```

---

## 📚 Additional Resources

- **Architecture**: See [LANGGRAPH_ARCHITECTURE.md](LANGGRAPH_ARCHITECTURE.md)
- **Quick Start**: See [README_LANGGRAPH.md](README_LANGGRAPH.md)
- **Examples**: See [examples/langgraph_example.py](examples/langgraph_example.py)
- **Tests**: See [tests/test_langgraph_classifier.py](tests/test_langgraph_classifier.py)

---

## 🆘 Troubleshooting

### Common Issues

1. **Qdrant connection failed**
   - Check Qdrant is running: `curl http://localhost:6333/`
   - Verify network connectivity
   - Check `QDRANT_URL` environment variable

2. **Slow classification**
   - Enable caching in config
   - Use GPU for embeddings
   - Optimize Qdrant parameters (ef_search)

3. **Low accuracy**
   - Verify embedding model matches indexing
   - Tune retrieval weights
   - Check SKOS data quality

---

## 💬 Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review example scripts

---

**✅ Integration complete! Your system is now powered by LangGraph multi-agent classification.**
