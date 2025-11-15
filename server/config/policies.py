"""
Classification policies and rules
Static configuration that can be exposed as MCP resource
"""

# Classification confidence thresholds
CONFIDENCE_THRESHOLDS = {
    "high": 0.8,
    "medium": 0.6,
    "low": 0.4,
    "uncertain": 0.0
}

# Classification rules
CLASSIFICATION_RULES = {
    "prefer_specific_concepts": True,
    "max_alternatives": 3,
    "require_minimum_confidence": 0.4,
    "use_semantic_search": True
}

# OpenAI configuration
OPENAI_CONFIG = {
    "model": "gpt-4o-mini",
    "max_retries": 3,
    "temperature": 0.0
}

# Search configuration
SEARCH_CONFIG = {
    "default_top_k": 10,
    "max_top_k": 100,
    "min_top_k": 1
}

# Embedding configuration
EMBEDDING_CONFIG = {
    "model": "text-embedding-3-small",
    "max_batch_size": 100
}


def get_classification_policy() -> dict:
    """
    Get the complete classification policy as a dictionary
    This can be exposed as MCP resource
    """
    return {
        "confidence_thresholds": CONFIDENCE_THRESHOLDS,
        "classification_rules": CLASSIFICATION_RULES,
        "openai_model": OPENAI_CONFIG["model"],
        "max_retries": OPENAI_CONFIG["max_retries"],
        "search_top_k": SEARCH_CONFIG["default_top_k"]
    }
