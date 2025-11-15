"""
SKOS Schema information
Static configuration that can be exposed as MCP resource
"""

SKOS_SCHEMA = {
    "name": "SKOS Core Schema",
    "version": "1.0",
    "namespace": "http://www.w3.org/2004/02/skos/core#",
    "concepts": {
        "skos:Concept": {
            "description": "A SKOS concept - the fundamental unit of knowledge",
            "example": "A product category or classification term"
        },
        "skos:prefLabel": {
            "description": "The preferred lexical label for a concept",
            "example": "Yogur y sustitutos"
        },
        "skos:altLabel": {
            "description": "Alternative lexical labels for a concept",
            "example": ["yoghurt", "yogurt"]
        },
        "skos:notation": {
            "description": "A unique code or identifier for a concept",
            "example": "111206"
        },
        "skos:broader": {
            "description": "A more general concept (parent in hierarchy)",
            "example": "Dairy Products -> Yogurt"
        },
        "skos:narrower": {
            "description": "A more specific concept (child in hierarchy)",
            "example": "Yogurt -> Greek Yogurt"
        },
        "skos:related": {
            "description": "A semantically related concept (not hierarchical)",
            "example": "Yogurt <-> Cheese"
        },
        "skos:definition": {
            "description": "A complete explanation of the concept",
            "example": "Fermented milk product with specific bacteria cultures"
        }
    },
    "hierarchy_levels": {
        "0": {
            "name": "Root",
            "description": "Top-level scheme or conceptual root"
        },
        "1": {
            "name": "Main Category",
            "description": "Primary product categories"
        },
        "2": {
            "name": "Subcategory",
            "description": "Refined categorizations"
        },
        "3+": {
            "name": "Specific Concepts",
            "description": "Detailed product classifications"
        }
    },
    "usage_guidelines": {
        "classification": "Use prefLabel and altLabel for matching product descriptions",
        "hierarchy": "Follow broader/narrower relations to navigate the taxonomy tree",
        "notation": "Use notation codes for precise concept identification"
    }
}


def get_taxonomy_schema() -> dict:
    """
    Get the SKOS schema information
    This can be exposed as MCP resource
    """
    return SKOS_SCHEMA
