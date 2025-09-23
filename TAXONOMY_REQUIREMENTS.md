# 📋 Requisitos del Sistema Multi-Taxonomía SKOS

## Descripción General

El sistema SKOS MCP Classifier implementa **gestión rigurosa de múltiples taxonomías** con validaciones estrictas para garantizar calidad en la clasificación de productos.

### Principios Fundamentales

1. **Taxonomía por Defecto Activa**: El sistema siempre debe tener al menos una taxonomía activa como default
2. **Validación SKOS Estricta**: Solo se aceptan taxonomías que cumplan estándares mínimos de calidad
3. **Selección Explícita**: Se especifica qué taxonomía se usa en cada clasificación para transparencia
4. **Persistencia Garantizada**: Las taxonomías se almacenan permanentemente con versionado
5. **Identificación Única**: Cada taxonomía tiene ID y versión únicos en el sistema

## 🔒 Requisitos Mínimos OBLIGATORIOS

Para que una taxonomía sea aceptada en el sistema, debe cumplir:

### 1. Compliance SKOS Básico
- ✅ **Conceptos SKOS**: Mínimo 20 conceptos con `skos:Concept`
- ✅ **Esquema**: Al menos un `skos:ConceptScheme` 
- ✅ **Jerarquía**: Relaciones `skos:broader`/`skos:narrower` o `skos:hasTopConcept`

### 2. Etiquetado Obligatorio
- ✅ **Etiquetas principales**: 95%+ conceptos con `skos:prefLabel`
- ✅ **Sin huérfanos**: <10% conceptos sin conexión al esquema
- ✅ **Idioma consistente**: Etiquetas en idioma declarado

### 3. Estructura Coherente
- ✅ **Conceptos raíz**: Al menos un concepto sin `skos:broader` 
- ✅ **Sin ciclos**: Jerarquía acíclica válida
- ✅ **Profundidad mínima**: Al menos 2 niveles jerárquicos

### 4. Calidad Mínima para Clasificación
- ✅ **Puntuación**: Mínimo 60% en escala de calidad
- ✅ **Usabilidad**: Apta para clasificación automática de productos

## 🌟 Características Recomendadas para ALTA CALIDAD

### Enriquecimiento Semántico
- 💎 **Definiciones**: >60% conceptos con `skos:definition`
- 🏷️ **Etiquetas alternativas**: >40% conceptos con `skos:altLabel` 
- 🔢 **Notaciones**: Códigos únicos con `skos:notation`
- 🔗 **Relaciones semánticas**: Enlaces `skos:related` entre conceptos

### Estructura Avanzada
- 📊 **Jerarquía profunda**: 3-5 niveles para granularidad
- 🌐 **Mappings externos**: Enlaces `skos:exactMatch`/`skos:closeMatch`
- 🌍 **Multiidioma**: Etiquetas en múltiples idiomas
- 📚 **Documentación**: Metadatos descriptivos completos

## 🏗️ Arquitectura del Sistema

### Gestión de Taxonomías
```
taxonomies/
├── treew-skos/              # Taxonomía por defecto
│   ├── original.jsonld      # Archivo SKOS original
│   ├── taxonomy.sqlite      # Base de datos procesada
│   └── metadata.json        # Metadatos y validación
├── google-shopping/         # Taxonomía adicional
│   ├── original.jsonld
│   ├── taxonomy.sqlite
│   └── metadata.json
└── metadata_global.json     # Índice global de taxonomías
```

### Estados de Taxonomía
- **active**: Disponible para clasificación
- **inactive**: Almacenada pero no usable
- **default**: Taxonomía usada por defecto
- **validated**: Pasó validación estricta

## 🔧 Operaciones del Sistema

### 1. Validación Previa
```bash
# Validar archivo antes de subir
curl -X POST "http://localhost:8080/taxonomies/validate" \
  -F "file=@nueva_taxonomia.jsonld"
```

**Respuesta de validación:**
```json
{
  "valid": true,
  "quality_score": 0.85,
  "compliance_level": "very_good",
  "requirements_met": {
    "skos_compliant": true,
    "has_hierarchy": true, 
    "has_labels": true,
    "quality_threshold": true
  },
  "statistics": {
    "total_concepts": 156,
    "concepts_with_definitions": 124,
    "max_hierarchy_depth": 4
  },
  "enrichment_features": [
    "✨ Definiciones: 79.5% de conceptos",
    "🏷️ Etiquetas alternativas: 45.5% de conceptos"
  ]
}
```

### 2. Upload de Taxonomía
```bash
# Subir taxonomía validada
curl -X POST "http://localhost:8080/taxonomies/upload" \
  -F "file=@nueva_taxonomia.jsonld" \
  -F 'metadata={"id":"mi-taxonomia","name":"Mi Taxonomía Personalizada"}'
```

### 3. Selección para Clasificación
```python
# Clasificación con taxonomía específica
from client.multi_taxonomy_classify import classify

result = classify(
    text="yogur natural griego 150g",
    taxonomy_id="google-shopping"  # Selección explícita
)

# La respuesta incluye qué taxonomía se usó
print(f"Taxonomía usada: {result['taxonomy_used']}")
```

### 4. Gestión de Estado
```bash
# Listar taxonomías disponibles
curl "http://localhost:8080/taxonomies/available"

# Activar taxonomía
curl -X POST "http://localhost:8080/taxonomies/mi-taxonomia/activate"

# Establecer como default
curl -X POST "http://localhost:8080/taxonomies/mi-taxonomia/set-default"
```

## 📊 Niveles de Compliance

| Nivel | Puntuación | Requisitos | Uso Recomendado |
|-------|------------|------------|------------------|
| **insufficient** | <60% | No cumple mínimos | ❌ Rechazada |
| **acceptable** | 60-69% | Básico compliant | ⚠️ Uso limitado |
| **good** | 70-79% | Bien estructurada | ✅ Producción |
| **very_good** | 80-89% | Rica en metadatos | 🌟 Recomendada |
| **excellent** | 90%+ | Como TreeW actual | 💎 Óptima |

## 🔍 Proceso de Validación

### 1. Parsing y Formato
- Verificar formato SKOS válido (.jsonld, .rdf, .xml, .ttl)
- Parsear con rdflib sin errores
- Verificar tamaño <100MB

### 2. Validación Estructural
- Contar conceptos, esquemas, relaciones
- Verificar jerarquía acíclica
- Detectar conceptos huérfanos

### 3. Análisis de Calidad
- Calcular cobertura de etiquetas
- Medir enriquecimiento semántico
- Evaluar profundidad jerárquica

### 4. Puntuación Final
```
Score = Base (40%) + Calidad (50%) + Consistencia (10%)

Base: Cumplir requisitos SKOS mínimos
Calidad: Definiciones, etiquetas alt, notaciones, relaciones
Consistencia: Sin ciclos, sin huérfanos, estructura coherente
```

## 🎯 Casos de Uso

### E-commerce Multi-Regional
```python
# Diferentes taxonomías por mercado
result_us = classify("organic yogurt", taxonomy_id="google-shopping-us")
result_eu = classify("yogur orgánico", taxonomy_id="treew-skos-eu") 
result_latam = classify("yogur natural", taxonomy_id="custom-latam")
```

### Migración Controlada
```python
# Comparar clasificaciones entre taxonomías
old_result = classify(product, taxonomy_id="legacy-taxonomy")
new_result = classify(product, taxonomy_id="improved-taxonomy")

# Análisis de coherencia
consistency_score = compare_results(old_result, new_result)
```

### A/B Testing de Taxonomías
```python
# Probar rendimiento de diferentes versiones
for taxonomy in ["v1", "v2", "v3"]:
    results = classify_batch(products, taxonomy_id=f"test-{taxonomy}")
    performance[taxonomy] = evaluate_results(results)
```

## 🚀 Beneficios del Sistema

### Para Desarrolladores
- **Calidad garantizada**: Solo taxonomías válidas en producción
- **Transparencia**: Siempre se sabe qué taxonomía se usa
- **Flexibilidad**: Cambio dinámico entre taxonomías
- **Backward compatibility**: Sistema actual sigue funcionando

### Para Usuarios de Negocio
- **Clasificación precisa**: Taxonomías enriquecidas mejoran resultados
- **Especialización por dominio**: Taxonomías específicas por sector
- **Evolución controlada**: Actualizaciones sin interrupciones
- **Trazabilidad**: Historial de qué taxonomía se usó cuándo

## 🔮 Evolución Futura

### Fase 1: Validación Inteligente
- Detección automática de dominios
- Sugerencias de mejora de calidad
- Validación cruzada entre taxonomías

### Fase 2: Gestión Avanzada
- Versionado automático de taxonomías
- Rollback a versiones anteriores
- Sincronización con fuentes externas

### Fase 3: Optimización Inteligente
- Recomendación automática de taxonomía óptima
- Mapping automático entre taxonomías
- Análisis de rendimiento por taxonomía

---

**🎉 El sistema está listo para manejar taxonomías de calidad enterprise con validación rigurosa y selección explícita para cada clasificación.**