# SKOS MCP Classifier (Treew)

Repo de ejemplo para exponer una taxonomía **SKOS** como **servidor MCP** y conectarla a **OpenAI** (Responses API / Agents SDK) para clasificación de productos.

## Estructura
```
skos-mcp-classifier/
├─ server/                     # servidor MCP (FastAPI)
├─ client/                     # clientes (Python y TS)
└─ data/taxonomy.jsonld        # tu SKOS JSON-LD (copiado)
```

## Pasos rápidos
1) Crea la DB a partir de tu SKOS:
```
make load
```
2) Levanta el servidor MCP:
```
make run
```
3) Prueba la clasificación con Responses API:
```
export OPENAI_API_KEY=...
export MCP_SERVER_URL=http://localhost:8080
make classify
```

## Docker
```
docker build -t skos-mcp-server ./server
docker run -p 8080:8080 --rm skos-mcp-server
```

## Notas
- `server/skos_loader.py` detecta automáticamente JSON-LD (`.jsonld`) y TTL/RDF.
- Endpoints MCP expuestos:
  - `POST /tools/search_concepts`
  - `POST /tools/get_context`
  - `POST /tools/validate_notation`
- El archivo `server/mcp_tools.json` declara las herramientas MCP.

> La taxonomía incluida es la que nos compartiste, en formato JSON-LD dentro de `data/taxonomy.jsonld`.
