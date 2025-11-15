# MCP Server - Estado Actual vs Ideal

## 📋 Inventario de Tools Actuales

### Tools existentes en `server/main.py`:
1. **`/tools/search_concepts`** (POST)
   - ✅ Búsqueda de conceptos SKOS
   - ❌ Expone detalles de BD directamente (score, ancestors, descendants)
   - ❌ Nombre no sigue convención ideal
   - ✅ Útil para agentes

2. **`/tools/get_context`** (POST)
   - ✅ Obtiene contexto de concepto
   - ❌ Expone estructura de BD interna
   - ❌ Nombre no sigue convención ideal
   - ✅ Útil para agentes

3. **`/tools/validate_notation`** (POST)
   - ✅ Valida código de taxonomía
   - ❌ Expone detalles internos (rowid, level)
   - ⚠️ Útil pero muy específico

### Tools existentes en `server/multi_taxonomy_main.py`:
1. **`/tools/search_concepts`** (POST)
   - ✅ Búsqueda multi-taxonomía
   - ❌ Acceso directo a BD (conn.cursor())
   - ✅ Soporte para taxonomy_id
   - ⚠️ Implementación incompleta (TODOs en el código)

2. **`/tools/get_concept_context`** (POST)
   - Similar a get_context pero con multi-taxonomía
   - ❌ Acceso directo a BD
   - ⚠️ Implementación incompleta

3. **`/tools/validate_notation`** (POST)
   - Similar al anterior con multi-taxonomía

### Endpoints adicionales (NO son tools MCP):
- `/taxonomies/available` (GET) - Lista taxonomías
- `/health` (GET) - Health check
- Legacy endpoints para compatibilidad

## ❌ Tools Faltantes (requeridas por instrucciones):

1. **`search_taxonomy_concepts`** ❌
   - NO existe con este nombre
   - Existe search_concepts pero con diferente semántica

2. **`embed_text`** ❌
   - NO existe
   - Necesaria para búsqueda semántica

3. **`get_taxonomy_concept`** ❌
   - NO existe con este nombre
   - Existe get_context pero diferente semántica

4. **`list_taxonomies`** ❌
   - NO existe como tool MCP
   - Existe como endpoint REST general

5. **`get_taxonomy_metadata`** ❌
   - NO existe como tool MCP
   - Existe en endpoints REST

6. **`classify_text`** ❌
   - NO existe en MCP server
   - Existe en classification_api.py (API separada)

## 📚 Inventario de Resources Actuales

### Resources existentes:
**NINGUNO** ❌

El servidor MCP actual NO expone resources, solo tools.

## ❌ Resources Faltantes (requeridas por instrucciones):

1. **`resource:taxonomy_schema`** ❌
   - Estructura SKOS oficial del proyecto

2. **`resource:active_taxonomies`** ❌
   - Lista y metadatos de taxonomías cargadas

3. **`resource:classification_policy`** ❌
   - Reglas del sistema (umbrales, criterios)

4. **`resource:project_overview`** ❌
   - Qué hace el proyecto y cómo usarse

## 🔴 Problemas Identificados

### 1. Exposición de Infraestructura
```python
# ❌ MALO: Acceso directo a BD en tools
cn = db(); c = cn.cursor()
c.execute("SELECT concept_uri, pref_lang, pref_label...")
```

### 2. Mezcla de Responsabilidades
- MCP server incluye endpoints REST generales
- No hay separación clara entre MCP tools y API REST

### 3. Arquitectura No Hexagonal
- Tools acceden directamente a BD
- No hay capa de dominio
- No hay adaptadores limpios
- Lógica de negocio mezclada con infraestructura

### 4. No hay Resources
- MCP debería exponer conocimiento estático
- Agentes no pueden consultar metadata sin ejecutar tools

### 5. Tools Incompletas
- Muchos TODOs en el código
- Implementaciones parciales (altLabel, ancestors, etc.)

### 6. Clasificación Fuera de MCP
- classify_text está en otra API
- Agentes no pueden clasificar vía MCP

## ✅ Puntos Positivos

1. ✅ Soporte multi-taxonomía funcional
2. ✅ FastAPI bien configurado
3. ✅ Modelos Pydantic definidos
4. ✅ Sistema de metadatos robusto
5. ✅ Health checks implementados

## 📊 Comparación Actual vs Ideal

| Componente | Estado Actual | Estado Ideal | Gap |
|------------|---------------|--------------|-----|
| **search_taxonomy_concepts** | Existe como search_concepts | ✅ | Renombrar |
| **embed_text** | ❌ No existe | ✅ Necesario | Crear |
| **get_taxonomy_concept** | Existe como get_context | ✅ | Renombrar |
| **list_taxonomies** | Solo REST | ✅ Tool MCP | Migrar |
| **get_taxonomy_metadata** | Solo REST | ✅ Tool MCP | Migrar |
| **classify_text** | API separada | ✅ Tool MCP | Integrar |
| **Resources** | 0/4 | 4/4 | Crear todas |
| **Arquitectura Hexagonal** | ❌ | ✅ | Refactorizar |
| **Encapsulación** | ❌ BD expuesta | ✅ Dominio | Crear capa |

## 🎯 Conclusión

**Cobertura actual:** ~40%
- 3/6 tools básicas (con nombres incorrectos)
- 0/4 resources
- Arquitectura no alineada con DDD+Hexagonal
- Exposición de infraestructura crítica

**Trabajo requerido:**
1. ✅ Refactorizar arquitectura completa
2. ✅ Crear capa de dominio/aplicación
3. ✅ Implementar 6 tools correctas
4. ✅ Implementar 4 resources
5. ✅ Eliminar acceso directo a BD
6. ✅ Separar MCP de REST API general
