## Instrucciones para Copilot – Servidor MCP en nuestro proyecto

### Objetivo del servidor MCP

El servidor MCP NO es el backend general.  
Su única misión es:

> **Exponer tools (capacidades) y resources (conocimiento estructural) para que un agente LLM pueda operar con nuestro proyecto sin alucinar.**

---

## 1. Tools que el MCP debe exponer

Tools mínimas y esenciales:

### A. Búsqueda semántica
- `search_taxonomy_concepts(query: string, top_k: int)`
- `embed_text(text: string)`

### B. Consulta de taxonomías SKOS
- `get_taxonomy_concept(concept_id: string)`
- `list_taxonomies()`
- `get_taxonomy_metadata(taxonomy_id: string)`

### C. Clasificación inteligente
- `classify_text(text: string, lang?: string)`

**Todas las tools deben encapsular el dominio.  
Nunca exponer infraestructura directamente.**

---

## 2. Resources que el MCP debe exponer

El MCP debe dar acceso sólo a contexto estable:

- `resource:taxonomy_schema`  
  Estructura SKOS oficial del proyecto.

- `resource:active_taxonomies`  
  Lista y metadatos de taxonomías cargadas.

- `resource:classification_policy`  
  Reglas del sistema (umbrales, criterios).

- `resource:project_overview`  
  Qué hace nuestro proyecto y cómo debe usarse.

---

## 3. Lo que NO debe hacer el MCP

- ❌ No exponer SQLite, PostgreSQL, etc.  
- ❌ No exponer la base vectorial directamente.  
- ❌ No exponer modelos o entidades internas.  
- ❌ No mezclar API general con MCP.  

El MCP debe ser **simple, seguro y orientado al agente**.

---

## 4. Tareas que debe ejecutar Copilot

### 1. Localizar el servidor MCP actual
- Identificar dónde se define.
- Enumerar tools existentes.
- Enumerar resources existentes.

### 2. Comparar "actual vs ideal"
Para cada tool:
- ¿Existe?  
- ¿Tiene la firma correcta?  
- ¿Exposición innecesaria?  
- ¿Es útil para un agente?

Para cada resource:
- ¿Existe?
- ¿Es estable y útil?
- ¿Debe crearse o corregirse?

### 3. Refactor necesario
- Ajustar nombres y firmas de tools.
- Crear tools faltantes.
- Crear resources faltantes.
- Eliminar herramientas que expongan infraestructura.
- Reorganizar el servidor MCP siguiendo:
  - Arquitectura hexagonal  
  - DDD  
  - Adaptadores limpios

### 4. Validación final
- Generar un resumen claro del MCP final.
- Listar tools expuestas.
- Listar resources expuestos.
- Confirmar que un agente LLM puede:
  - Consultar taxonomías.
  - Buscar semánticamente.
  - Clasificar textos.
  - Comprender reglas del sistema.

---

## 5. Estilo de trabajo esperado

- Explicar siempre lo que se está haciendo.  
- Resumir estado actual antes de cambiar.  
- Resumir estado final después de cambiar.  
- Mantener consistencia con hexagonal + DDD.  
- Asegurar claridad y encapsulación del MCP.
