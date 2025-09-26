# 🎯 Enhanced Classifier Response Format - Specification v3.1

## 📊 **FORMATO MEJORADO DE RESPUESTA**

### **🌟 Nuevo Formato Enriquecido**

```json
{
  "classification": {
    "primary": {
      "concept_uri": "https://treew.io/taxonomy/concept/111206",
      "prefLabel": "Yogur y sustitutos",
      "notation": "111206",
      "level": 1,
      "confidence": {
        "overall": 0.95,
        "breakdown": {
          "semantic_match": 0.92,
          "context_relevance": 0.98,
          "taxonomy_fit": 0.95,
          "term_precision": 0.94
        },
        "factors": {
          "positive": [
            "Coincidencia exacta con término 'yogur'",
            "Contexto alimentario claro",
            "Atributo 'natural' consistente"
          ],
          "concerns": [
            "Leve ambigüedad en subcategoría específica"
          ]
        }
      },
      "reasoning": {
        "decision_process": "Identificado como producto lácteo fermentado. La presencia de 'yogur' como término principal, junto con 'natural' como calificador, indica claramente pertenencia a la categoría 111206.",
        "key_indicators": [
          "Término principal: 'yogur'",
          "Calificador: 'natural'", 
          "Contexto: producto alimentario"
        ],
        "taxonomy_path": [
          "Alimentos",
          "Productos lácteos",
          "Lácteos fermentados",
          "Yogur y sustitutos"
        ]
      }
    },
    "alternatives": [
      {
        "concept_uri": "https://treew.io/taxonomy/concept/111204",
        "prefLabel": "Leche y productos lácteos líquidos",
        "confidence": 0.73,
        "reason": "Alternativa por contexto lácteo general, pero menos específica"
      },
      {
        "concept_uri": "https://treew.io/taxonomy/concept/111208", 
        "prefLabel": "Productos lácteos probióticos",
        "confidence": 0.68,
        "reason": "Posible si se enfoca en beneficios probióticos del yogur"
      }
    ],
    "related_concepts": [
      {
        "concept_uri": "https://treew.io/taxonomy/concept/111299",
        "prefLabel": "Ingredientes lácteos",
        "relationship": "broader",
        "relevance": 0.85
      }
    ]
  },
  "product": {
    "original_text": "yogur griego natural orgánico 125g",
    "normalized_text": "yogur griego natural orgánico", 
    "product_id": "YOGUR-001",
    "detected_attributes": {
      "type": ["yogur"],
      "variety": ["griego"],
      "characteristics": ["natural", "orgánico"],
      "packaging": ["125g"]
    },
    "quality_indicators": {
      "text_clarity": 0.98,
      "information_completeness": 0.92,
      "ambiguity_level": 0.08
    }
  },
  "processing": {
    "pipeline": {
      "id": "pipeline_20250115_103045_abc123",
      "version": "3.1.0",
      "steps_completed": [
        {
          "step": "text_normalization",
          "duration_ms": 12,
          "status": "success"
        },
        {
          "step": "concept_search",
          "duration_ms": 234,
          "status": "success",
          "details": {
            "concepts_found": 15,
            "top_matches": 3
          }
        },
        {
          "step": "context_analysis", 
          "duration_ms": 189,
          "status": "success"
        },
        {
          "step": "confidence_calculation",
          "duration_ms": 45,
          "status": "success"
        }
      ],
      "total_duration_ms": 480
    },
    "ai_interaction": {
      "model_used": "gpt-4o-mini-2024-07-18",
      "function_calls": [
        {
          "function": "search_concepts",
          "parameters": {"query": "yogur griego natural", "k": 10},
          "duration_ms": 234
        },
        {
          "function": "get_concept_context",
          "parameters": {"concept_uri": "111206"},
          "duration_ms": 189
        }
      ],
      "cost_info": {
        "total_usd": 0.000487,
        "breakdown": {
          "prompt_tokens": 1245,
          "completion_tokens": 158,
          "total_tokens": 1403
        },
        "cost_per_token": {
          "input": 0.00000015,
          "output": 0.0000006
        }
      }
    }
  },
  "taxonomy": {
    "id": "treew-skos",
    "name": "TreeW SKOS Food Taxonomy",
    "version": "2.1",
    "is_default": true,
    "total_concepts": 282,
    "hierarchy_levels": 4
  },
  "metadata": {
    "api_version": "3.1.0",
    "timestamp": "2025-01-15T10:30:45.123Z",
    "request_id": "req_20250115_103045_xyz789",
    "session_id": "sess_abc123def456",
    "processing_node": "classifier-node-01",
    "quality_score": {
      "overall": 0.94,
      "components": {
        "input_quality": 0.95,
        "processing_reliability": 0.96,
        "output_consistency": 0.91
      }
    },
    "recommendations": {
      "confidence_level": "high",
      "suggested_actions": [
        "Resultado confiable, usar sin revisión adicional"
      ],
      "review_needed": false
    }
  }
}
```

### **🔧 Componentes del Formato Mejorado**

#### **1. 🎯 Classification Section**
- **Primary**: Clasificación principal con confianza detallada
- **Alternatives**: Opciones secundarias con explicación
- **Related Concepts**: Conceptos relacionados en la taxonomía

#### **2. 📦 Product Section** 
- **Original/Normalized Text**: Texto original y procesado
- **Detected Attributes**: Atributos extraídos automáticamente
- **Quality Indicators**: Métricas de calidad del input

#### **3. ⚙️ Processing Section**
- **Pipeline**: Pasos detallados del procesamiento
- **AI Interaction**: Información de interacciones con OpenAI
- **Performance Metrics**: Tiempos y costos detallados

#### **4. 📚 Taxonomy Section**
- **Metadata**: Información completa de la taxonomía usada
- **Context**: Estadísticas de uso y cobertura

#### **5. 🏷️ Metadata Section**
- **System Info**: Versión, timestamps, IDs únicos
- **Quality Assessment**: Métricas de calidad global
- **Recommendations**: Sugerencias para uso del resultado

### **📋 Beneficios del Nuevo Formato**

1. **🔍 Transparencia Total**: Proceso completo visible
2. **🎯 Confianza Granular**: Desglose detallado de certeza
3. **🔄 Alternativas Útiles**: Opciones secundarias con contexto
4. **📊 Métricas Avanzadas**: Información completa de rendimiento
5. **🛠️ Debugging Facilit**: Información para troubleshooting
6. **📈 Analytics Ready**: Datos estructurados para análisis

### **🔄 Compatibilidad**

- **Backward Compatible**: El formato anterior se mantiene en campo `legacy_format`
- **Progressive Enhancement**: Clientes pueden usar nivel básico o avanzado
- **Configurable**: Niveles de detalle ajustables por endpoint

### **📐 Niveles de Detalle**

1. **Basic** (`detail_level=basic`): Solo clasificación principal
2. **Standard** (`detail_level=standard`): Incluye alternativas y reasoning
3. **Full** (`detail_level=full`): Formato completo mostrado arriba
4. **Debug** (`detail_level=debug`): Incluye información técnica adicional

---

## 🎨 **IMPLEMENTACIÓN GRADUAL**

### **Fase 1: Modelos Base**
- Definir nuevos modelos Pydantic
- Mantener compatibilidad con formato actual

### **Fase 2: Lógica Mejorada**
- Implementar cálculo de confianza granular
- Agregar sistema de alternativas

### **Fase 3: Integración**
- Actualizar endpoints existentes
- Agregar configuración de nivel de detalle

### **Fase 4: Optimización**
- Performance tuning
- Caching inteligente de componentes

---

**🎯 Este formato enriquecido proporcionará una experiencia mucho más rica y útil para los usuarios del clasificador, manteniendo la compatibilidad existente.**