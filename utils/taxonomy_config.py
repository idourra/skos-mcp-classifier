#!/usr/bin/env python3
# utils/taxonomy_config.py - Configuración y gestión de taxonomías
import os
import json
from typing import Optional, Dict, Any
from pathlib import Path

def get_default_taxonomy() -> str:
    """
    Obtiene la taxonomía por defecto desde variables de entorno o metadata.
    
    Returns:
        str: ID de la taxonomía por defecto
    """
    # Primero verificar variable de entorno
    default_taxonomy = os.getenv("DEFAULT_TAXONOMY")
    
    if default_taxonomy:
        return default_taxonomy
    
    # Si no hay variable de entorno, buscar en metadata.json
    try:
        metadata_path = Path(__file__).parent.parent / "taxonomies" / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                
            # Buscar taxonomía marcada como default
            for taxonomy_id, taxonomy_data in metadata.get("taxonomies", {}).items():
                if taxonomy_data.get("is_default", False):
                    return taxonomy_id
    except Exception as e:
        print(f"Warning: Error reading taxonomy metadata: {e}")
    
    # Fallback por defecto
    return "treew-skos"

def get_available_taxonomies() -> Dict[str, Dict[str, Any]]:
    """
    Obtiene lista de taxonomías disponibles desde metadata.json
    
    Returns:
        Dict[str, Dict[str, Any]]: Diccionario con información de taxonomías
    """
    try:
        metadata_path = Path(__file__).parent.parent / "taxonomies" / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            return metadata.get("taxonomies", {})
    except Exception as e:
        print(f"Warning: Error reading taxonomy metadata: {e}")
    
    return {}

def validate_taxonomy_id(taxonomy_id: Optional[str]) -> str:
    """
    Valida si un ID de taxonomía existe y está activo.
    Si no se proporciona o no es válido, retorna la taxonomía por defecto.
    
    Args:
        taxonomy_id (Optional[str]): ID de taxonomía a validar
        
    Returns:
        str: ID de taxonomía validado (o por defecto si no es válido)
    """
    if not taxonomy_id:
        return get_default_taxonomy()
    
    available_taxonomies = get_available_taxonomies()
    
    # Verificar si existe y está activa
    if taxonomy_id in available_taxonomies:
        taxonomy_data = available_taxonomies[taxonomy_id]
        if taxonomy_data.get("is_active", False):
            return taxonomy_id
    
    # Si no es válida, usar por defecto
    print(f"Warning: Taxonomy '{taxonomy_id}' not found or inactive. Using default.")
    return get_default_taxonomy()

def get_taxonomy_info(taxonomy_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Obtiene información completa de una taxonomía específica.
    
    Args:
        taxonomy_id (Optional[str]): ID de taxonomía. Si es None, usa la por defecto.
        
    Returns:
        Dict[str, Any]: Información completa de la taxonomía
    """
    validated_id = validate_taxonomy_id(taxonomy_id)
    available_taxonomies = get_available_taxonomies()
    
    return available_taxonomies.get(validated_id, {
        "id": validated_id,
        "name": "Default Taxonomy",
        "description": "Taxonomía por defecto del sistema",
        "is_active": True,
        "is_default": True
    })