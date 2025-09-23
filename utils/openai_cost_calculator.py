"""
OpenAI Cost Calculator

Utilidad para calcular costos de llamadas a la API de OpenAI basado en:
- Tokens de entrada (prompt tokens)
- Tokens de salida (completion tokens)  
- Modelo utilizado
- Precios actuales de OpenAI (septiembre 2025)
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CostInfo:
    """Información de costos de una llamada a OpenAI"""
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    prompt_cost_usd: float
    completion_cost_usd: float
    total_cost_usd: float
    timestamp: str

# Precios de OpenAI por 1M tokens (actualizados septiembre 2025)
OPENAI_PRICING = {
    "gpt-4o-mini": {
        "prompt": 0.15,      # $0.15 por 1M tokens de entrada
        "completion": 0.60,  # $0.60 por 1M tokens de salida
    },
    "gpt-4o": {
        "prompt": 2.50,      # $2.50 por 1M tokens de entrada
        "completion": 10.00, # $10.00 por 1M tokens de salida
    },
    "gpt-4": {
        "prompt": 30.00,     # $30.00 por 1M tokens de entrada
        "completion": 60.00, # $60.00 por 1M tokens de salida
    },
    "gpt-3.5-turbo": {
        "prompt": 0.50,      # $0.50 por 1M tokens de entrada
        "completion": 1.50,  # $1.50 por 1M tokens de salida
    }
}

def calculate_openai_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int
) -> CostInfo:
    """
    Calcula el costo de una llamada a OpenAI
    
    Args:
        model (str): Modelo utilizado (ej: "gpt-4o-mini-2024-07-18")
        prompt_tokens (int): Tokens de entrada/prompt
        completion_tokens (int): Tokens de salida/completion
        
    Returns:
        CostInfo: Información detallada de costos
        
    Raises:
        ValueError: Si el modelo no está en la lista de precios
    """
    # Normalize model name to base model for pricing lookup
    base_model = model
    
    # Handle model names with dates (e.g., "gpt-4o-mini-2024-07-18" -> "gpt-4o-mini")
    for pricing_model in OPENAI_PRICING.keys():
        if model.startswith(pricing_model):
            base_model = pricing_model
            break
    
    if base_model not in OPENAI_PRICING:
        raise ValueError(f"Modelo '{model}' (base: '{base_model}') no encontrado en pricing. Modelos disponibles: {list(OPENAI_PRICING.keys())}")
    
    pricing = OPENAI_PRICING[base_model]
    
    # Calcular costos (precios por 1M tokens, convertir a costo real)
    prompt_cost = (prompt_tokens / 1_000_000) * pricing["prompt"]
    completion_cost = (completion_tokens / 1_000_000) * pricing["completion"]
    total_cost = prompt_cost + completion_cost
    total_tokens = prompt_tokens + completion_tokens
    
    return CostInfo(
        model=model,  # Keep original model name
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        prompt_cost_usd=round(prompt_cost, 6),
        completion_cost_usd=round(completion_cost, 6),
        total_cost_usd=round(total_cost, 6),
        timestamp=datetime.now().isoformat()
    )

def extract_usage_from_response(response) -> Tuple[int, int]:
    """
    Extrae información de usage de una respuesta de OpenAI
    
    Args:
        response: Respuesta de OpenAI ChatCompletion
        
    Returns:
        Tuple[int, int]: (prompt_tokens, completion_tokens)
    """
    if hasattr(response, 'usage') and response.usage:
        return (
            response.usage.prompt_tokens,
            response.usage.completion_tokens
        )
    else:
        # Fallback si no hay información de usage
        return (0, 0)

def format_cost_info(cost_info: CostInfo) -> Dict:
    """
    Formatea la información de costos para incluir en respuestas API
    
    Args:
        cost_info (CostInfo): Información de costos
        
    Returns:
        Dict: Información formateada para API
    """
    # Normalize model name for pricing lookup
    base_model = cost_info.model
    for pricing_model in OPENAI_PRICING.keys():
        if cost_info.model.startswith(pricing_model):
            base_model = pricing_model
            break
    
    return {
        "model": cost_info.model,  # Keep original model name
        "usage": {
            "prompt_tokens": cost_info.prompt_tokens,
            "completion_tokens": cost_info.completion_tokens,
            "total_tokens": cost_info.total_tokens
        },
        "cost_usd": {
            "prompt": cost_info.prompt_cost_usd,
            "completion": cost_info.completion_cost_usd,
            "total": cost_info.total_cost_usd
        },
        "cost_breakdown": {
            "base_model_for_pricing": base_model,
            "prompt_cost_per_1m_tokens": OPENAI_PRICING[base_model]["prompt"],
            "completion_cost_per_1m_tokens": OPENAI_PRICING[base_model]["completion"],
            "calculation_timestamp": cost_info.timestamp
        }
    }

def get_model_pricing(model: str) -> Optional[Dict]:
    """
    Obtiene información de precios para un modelo específico
    
    Args:
        model (str): Nombre del modelo
        
    Returns:
        Optional[Dict]: Información de precios o None si no existe
    """
    return OPENAI_PRICING.get(model)

def estimate_cost(model: str, estimated_prompt_tokens: int, estimated_completion_tokens: int) -> float:
    """
    Estima el costo de una llamada antes de realizarla
    
    Args:
        model (str): Modelo a utilizar
        estimated_prompt_tokens (int): Estimación de tokens de entrada
        estimated_completion_tokens (int): Estimación de tokens de salida
        
    Returns:
        float: Costo estimado en USD
    """
    if model not in OPENAI_PRICING:
        return 0.0
    
    pricing = OPENAI_PRICING[model]
    prompt_cost = (estimated_prompt_tokens / 1_000_000) * pricing["prompt"]
    completion_cost = (estimated_completion_tokens / 1_000_000) * pricing["completion"]
    
    return round(prompt_cost + completion_cost, 6)

# Función de utilidad para debugging/logging
def print_cost_summary(cost_info: CostInfo):
    """
    Imprime un resumen legible de los costos
    
    Args:
        cost_info (CostInfo): Información de costos
    """
    print(f"💰 COSTO OPENAI - {cost_info.model}")
    print(f"   📥 Prompt: {cost_info.prompt_tokens:,} tokens → ${cost_info.prompt_cost_usd:.6f}")
    print(f"   📤 Completion: {cost_info.completion_tokens:,} tokens → ${cost_info.completion_cost_usd:.6f}")
    print(f"   💳 TOTAL: {cost_info.total_tokens:,} tokens → ${cost_info.total_cost_usd:.6f}")

if __name__ == "__main__":
    # Ejemplo de uso
    print("🧪 Prueba de calculadora de costos OpenAI")
    print("=" * 50)
    
    # Simular una clasificación típica
    cost = calculate_openai_cost(
        model="gpt-4o-mini",
        prompt_tokens=850,      # ~850 tokens para prompt + functions + context
        completion_tokens=150   # ~150 tokens para respuesta JSON
    )
    
    print_cost_summary(cost)
    print()
    
    # Mostrar formato API
    formatted = format_cost_info(cost)
    import json
    print("📊 Formato para API:")
    print(json.dumps(formatted, indent=2))
    
    # Comparación de modelos
    print("\n📋 Comparación de costos por modelo (1000 prompt + 200 completion tokens):")
    for model in OPENAI_PRICING.keys():
        cost = calculate_openai_cost(model, 1000, 200)
        print(f"   {model:15} → ${cost.total_cost_usd:.6f}")