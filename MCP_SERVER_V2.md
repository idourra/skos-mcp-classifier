# 🎯 MCP Server v2.0 - Agent-Oriented Interface

## Quick Start

### Start the MCP Server

```bash
cd server/mcp
python server.py
```

Server will be available at: **http://localhost:8080**

### Documentation

- **Swagger UI:** http://localhost:8080/docs
- **ReDoc:** http://localhost:8080/redoc
- **Health Check:** http://localhost:8080/health

---

## 🏗️ Architecture

The MCP server follows **Hexagonal Architecture + Domain-Driven Design** principles:

```
server/
├── mcp/              # Entry Point (Ports)
│   ├── server.py     # FastAPI MCP server
│   ├── tools.py      # 6 MCP tools
│   ├── resources.py  # 4 MCP resources
│   └── schemas.py    # Pydantic models
├── domain/           # Business Logic
│   ├── models.py
│   ├── taxonomy_service.py
│   ├── search_service.py
│   └── classification_service.py
├── adapters/         # Infrastructure
│   ├── taxonomy_repository.py
│   └── embedding_client.py
└── config/           # Configuration
    ├── policies.py
    └── schema.py
```

### Key Principles

✅ **No infrastructure exposure** - Only high-level capabilities  
✅ **Domain-driven design** - Business logic in pure domain services  
✅ **Hexagonal architecture** - Clean separation of concerns  
✅ **Agent-oriented** - Designed for LLM agent consumption

---

## 🛠️ MCP Tools (6)

### 1. search_taxonomy_concepts
Search for SKOS concepts by text query.

```bash
POST /tools/search_taxonomy_concepts
{
  "query": "yogurt",
  "top_k": 10,
  "taxonomy_id": "treew-skos"  // optional
}
```

### 2. embed_text
Generate embedding vector for text.

```bash
POST /tools/embed_text
{
  "text": "yogur griego natural"
}
```

### 3. get_taxonomy_concept
Get detailed information about a specific concept.

```bash
POST /tools/get_taxonomy_concept
{
  "concept_id": "111206",  // notation or URI
  "taxonomy_id": "treew-skos"  // optional
}
```

### 4. list_taxonomies
List available taxonomies in the system.

```bash
POST /tools/list_taxonomies
{
  "active_only": true
}
```

### 5. get_taxonomy_metadata
Get metadata for a specific taxonomy.

```bash
POST /tools/get_taxonomy_metadata
{
  "taxonomy_id": "treew-skos"
}
```

### 6. classify_text
Classify text into taxonomy concepts using AI.

```bash
POST /tools/classify_text
{
  "text": "yogur griego natural 0% grasa",
  "lang": "es",
  "taxonomy_id": "treew-skos"  // optional
}
```

---

## 📚 MCP Resources (4)

### 1. taxonomy://schema
Get SKOS taxonomy schema information.

```bash
GET /resources/taxonomy_schema
```

Returns: Official SKOS schema structure, concept types, hierarchy levels.

### 2. taxonomy://active
Get list of active taxonomies.

```bash
GET /resources/active_taxonomies
```

Returns: Active taxonomies with metadata, default taxonomy.

### 3. taxonomy://classification-policy
Get classification rules and policies.

```bash
GET /resources/classification_policy
```

Returns: Confidence thresholds, classification rules, model configuration.

### 4. taxonomy://project
Get project overview and capabilities.

```bash
GET /resources/project_overview
```

Returns: System capabilities, usage guide, best practices.

---

## 🎯 Use Cases for LLM Agents

### 1. Explore Available Categories

```
Agent: "What product categories are available?"

1. Call: list_taxonomies()
2. Call: get_taxonomy_metadata("treew-skos")
3. Get resource: taxonomy://schema
```

### 2. Find Relevant Category for Product

```
Agent: "Find category for 'organic greek yogurt'"

1. Call: search_taxonomy_concepts(query="yogurt")
2. Review results and select best match
3. Call: get_taxonomy_concept(concept_id="111206")
```

### 3. Classify Product Description

```
Agent: "Classify this product: 'yogur griego natural 0% grasa'"

1. Call: classify_text(text="yogur griego natural 0% grasa")
2. Get classification with confidence
3. Optionally: get_taxonomy_concept() for more details
```

### 4. Understand System Rules

```
Agent: "What are the confidence thresholds?"

1. Get resource: taxonomy://classification-policy
2. Review thresholds: high (0.8), medium (0.6), low (0.4)
```

---

## 🔒 Security & Encapsulation

### ✅ What is Exposed

- High-level business capabilities (tools)
- Static knowledge (resources)
- Domain models and concepts
- Semantic operations

### ❌ What is NOT Exposed

- SQLite database access
- SQL queries
- OpenAI API keys
- Internal table structures
- Infrastructure details

This ensures agents cannot:
- Access databases directly
- Execute arbitrary SQL
- Leak sensitive information
- Hallucinate with infrastructure details

---

## 📊 Comparison with Legacy Server

| Feature | Old Server | New Server v2.0 |
|---------|------------|-----------------|
| Architecture | Monolithic | Hexagonal + DDD |
| Tools | 3 (wrong names) | 6 (correct) |
| Resources | 0 | 4 |
| DB Exposure | Direct | Encapsulated |
| Testability | Hard | Easy |
| Agent-Friendly | No | Yes ✅ |

---

## 🧪 Testing

### Health Check

```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "architecture": "hexagonal + DDD",
  "active_taxonomies": 1,
  "tools_count": 6,
  "resources_count": 4
}
```

### Test Search

```bash
curl -X POST http://localhost:8080/tools/search_taxonomy_concepts \
  -H "Content-Type: application/json" \
  -d '{"query": "yogurt", "top_k": 5}'
```

### Test Resources

```bash
curl http://localhost:8080/resources/project_overview
```

---

## 📝 Documentation Files

All design and implementation documentation is in `.copilot/`:

1. **mcp-instructions.md** - Agent guidelines
2. **mcp-current-state.md** - Current state analysis
3. **mcp-refactored-design.md** - Architecture design
4. **mcp-final-summary.md** - Implementation summary

---

## 🚀 Next Steps

1. ✅ Start MCP server
2. ✅ Review documentation at `/docs`
3. ✅ Test tools with sample requests
4. ✅ Explore resources for static knowledge
5. ✅ Integrate with LLM agents

---

## 🤝 Integration with Main API

The MCP server (port 8080) works alongside the main REST API (port 8000):

- **Port 8000:** General REST API for applications
- **Port 8080:** MCP server for LLM agents

Both share the same domain layer and adapters, but expose different interfaces.

---

**Version:** 2.0.0  
**Architecture:** Hexagonal + Domain-Driven Design  
**Purpose:** Agent-oriented interface for SKOS taxonomy operations
