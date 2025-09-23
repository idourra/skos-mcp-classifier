#!/usr/bin/env python3
"""
Multi-Taxonomy MCP Server
Servidor MCP actualizado para manejar múltiples taxonomías SKOS
"""
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional
import sqlite3
import logging

from utils.taxonomy_manager import taxonomy_manager

logger = logging.getLogger(__name__)

app = FastAPI(title="Multi-Taxonomy SKOS MCP Server")

# Modelos Pydantic existentes con extensiones
class SearchQuery(BaseModel):
    query: str
    lang: str = "es"
    k: int = 10
    taxonomy_id: Optional[str] = None  # Nuevo: taxonomía específica

class ConceptHit(BaseModel):
    concept_uri: str
    prefLabel: Dict[str, str]
    altLabel: Dict[str, List[str]]
    notation: Optional[str]
    ancestors: List[str]
    descendants: List[str]
    score: float
    taxonomy_id: str  # Nuevo: ID de taxonomía de origen

class SearchResponse(BaseModel):
    hits: List[ConceptHit]
    taxonomy_used: str  # Nuevo: qué taxonomía se usó
    total_taxonomies_available: int  # Nuevo: cuántas taxonomías hay

class GetContextQuery(BaseModel):
    concept_uri: str
    taxonomy_id: Optional[str] = None  # Nuevo: taxonomía específica

class ConceptContext(BaseModel):
    concept_uri: str
    prefLabel: Dict[str, str]
    altLabel: Dict[str, List[str]]
    definition: Dict[str, str]
    scopeNote: Dict[str, str]
    notation: Optional[str]
    broader: List[str]
    narrower: List[str]
    related: List[str]
    taxonomy_id: str  # Nuevo: ID de taxonomía de origen

class ValidateNotationQuery(BaseModel):
    notation: str
    taxonomy_id: Optional[str] = None  # Nuevo: taxonomía específica

class ValidateNotationResponse(BaseModel):
    exists: bool
    concept_uri: Optional[str] = None
    prefLabel: Optional[Dict[str, str]] = None
    level: Optional[int] = None
    taxonomy_id: str  # Nuevo: ID de taxonomía donde se encontró

# Funciones auxiliares
def get_taxonomy_id_or_default(taxonomy_id: Optional[str] = None) -> str:
    """Obtener ID de taxonomía válido o default"""
    if taxonomy_id:
        # Validar que la taxonomía existe y está activa
        metadata = taxonomy_manager.get_taxonomy_metadata(taxonomy_id)
        if not metadata:
            raise HTTPException(status_code=404, detail=f"Taxonomía '{taxonomy_id}' no encontrada")
        if not metadata.get("is_active", False):
            raise HTTPException(status_code=400, detail=f"Taxonomía '{taxonomy_id}' no está activa")
        return taxonomy_id
    else:
        try:
            return taxonomy_manager.get_default_taxonomy_id()
        except ValueError as e:
            raise HTTPException(status_code=503, detail=f"No hay taxonomías disponibles: {str(e)}")

# Endpoints MCP actualizados
@app.post("/tools/search_concepts", response_model=SearchResponse)
async def search_concepts(query: SearchQuery):
    """
    Buscar conceptos en taxonomía específica o default
    """
    try:
        taxonomy_id = get_taxonomy_id_or_default(query.taxonomy_id)
        
        with taxonomy_manager.get_db_connection(taxonomy_id) as conn:
            cursor = conn.cursor()
            
            # Búsqueda básica en prefLabel (mejorar con FTS si es necesario)
            search_query = f"%{query.query.lower()}%"
            sql = """
                SELECT uri, prefLabel, notation, level
                FROM concepts 
                WHERE LOWER(prefLabel) LIKE ? 
                ORDER BY 
                    CASE WHEN LOWER(prefLabel) = LOWER(?) THEN 1 ELSE 2 END,
                    LENGTH(prefLabel)
                LIMIT ?
            """
            
            results = cursor.execute(sql, (search_query, query.query, query.k)).fetchall()
            
            hits = []
            for uri, prefLabel, notation, level in results:
                # Calcular score básico (mejorar con algoritmo más sofisticado)
                score = 1.0 if prefLabel.lower() == query.query.lower() else 0.5
                
                hit = ConceptHit(
                    concept_uri=uri,
                    prefLabel={query.lang: prefLabel},
                    altLabel={},  # TODO: implementar altLabel
                    notation=notation,
                    ancestors=[],  # TODO: implementar ancestors
                    descendants=[],  # TODO: implementar descendants
                    score=score,
                    taxonomy_id=taxonomy_id
                )
                hits.append(hit)
        
        # Contar taxonomías disponibles
        active_taxonomies = taxonomy_manager.get_active_taxonomies()
        
        return SearchResponse(
            hits=hits,
            taxonomy_used=taxonomy_id,
            total_taxonomies_available=len(active_taxonomies)
        )
        
    except Exception as e:
        logger.error(f"Error en búsqueda de conceptos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}")

@app.post("/tools/get_concept_context", response_model=ConceptContext)
async def get_concept_context(query: GetContextQuery):
    """
    Obtener contexto completo de un concepto
    """
    try:
        taxonomy_id = get_taxonomy_id_or_default(query.taxonomy_id)
        
        with taxonomy_manager.get_db_connection(taxonomy_id) as conn:
            cursor = conn.cursor()
            
            # Obtener concepto principal
            concept_sql = "SELECT uri, prefLabel, notation FROM concepts WHERE uri = ?"
            concept_result = cursor.execute(concept_sql, (query.concept_uri,)).fetchone()
            
            if not concept_result:
                raise HTTPException(status_code=404, detail=f"Concepto '{query.concept_uri}' no encontrado")
            
            uri, prefLabel, notation = concept_result
            
            # TODO: Implementar obtención de relaciones (broader, narrower, related)
            # Por ahora, devolver estructura básica
            
            return ConceptContext(
                concept_uri=uri,
                prefLabel={"es": prefLabel},
                altLabel={},
                definition={},
                scopeNote={},
                notation=notation,
                broader=[],
                narrower=[],
                related=[],
                taxonomy_id=taxonomy_id
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo contexto: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo contexto: {str(e)}")

@app.post("/tools/validate_notation", response_model=ValidateNotationResponse)
async def validate_notation(query: ValidateNotationQuery):
    """
    Validar si una notación existe en la taxonomía
    """
    try:
        taxonomy_id = get_taxonomy_id_or_default(query.taxonomy_id)
        
        with taxonomy_manager.get_db_connection(taxonomy_id) as conn:
            cursor = conn.cursor()
            
            sql = "SELECT uri, prefLabel, level FROM concepts WHERE notation = ?"
            result = cursor.execute(sql, (query.notation,)).fetchone()
            
            if result:
                uri, prefLabel, level = result
                return ValidateNotationResponse(
                    exists=True,
                    concept_uri=uri,
                    prefLabel={"es": prefLabel},
                    level=level,
                    taxonomy_id=taxonomy_id
                )
            else:
                return ValidateNotationResponse(
                    exists=False,
                    taxonomy_id=taxonomy_id
                )
                
    except Exception as e:
        logger.error(f"Error validando notación: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error validando notación: {str(e)}")

# Nuevos endpoints específicos para multi-taxonomía
@app.get("/taxonomies/available")
async def get_available_taxonomies():
    """
    Obtener lista de taxonomías disponibles para MCP
    """
    try:
        active_taxonomies = taxonomy_manager.get_active_taxonomies()
        default_taxonomy = taxonomy_manager.get_default_taxonomy_id()
        
        return {
            "taxonomies": [
                {
                    "id": tax_id,
                    "name": metadata["name"],
                    "description": metadata["description"],
                    "language": metadata["language"],
                    "domain": metadata["domain"],
                    "concepts_count": metadata["concepts_count"],
                    "is_default": tax_id == default_taxonomy
                }
                for tax_id, metadata in active_taxonomies.items()
            ],
            "default_taxonomy": default_taxonomy,
            "total_active": len(active_taxonomies)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo taxonomías disponibles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo taxonomías: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Verificar estado del servidor MCP y taxonomías
    """
    try:
        active_taxonomies = taxonomy_manager.get_active_taxonomies()
        default_taxonomy = None
        
        try:
            default_taxonomy = taxonomy_manager.get_default_taxonomy_id()
        except ValueError:
            pass
        
        # Verificar conexión a taxonomía default
        db_status = "disconnected"
        if default_taxonomy:
            try:
                with taxonomy_manager.get_db_connection(default_taxonomy) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM concepts")
                    db_status = "connected"
            except Exception:
                db_status = "error"
        
        return {
            "status": "healthy" if db_status == "connected" else "degraded",
            "timestamp": "2025-09-23T12:00:00Z",
            "database_status": db_status,
            "taxonomies": {
                "total_active": len(active_taxonomies),
                "default_taxonomy": default_taxonomy,
                "available_ids": list(active_taxonomies.keys())
            },
            "version": "2.0.0-multi-taxonomy"
        }
        
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return {
            "status": "error",
            "timestamp": "2025-09-23T12:00:00Z",
            "error": str(e),
            "version": "2.0.0-multi-taxonomy"
        }

# Endpoint de compatibilidad hacia atrás
@app.post("/search_concepts")
async def search_concepts_legacy(query: SearchQuery):
    """
    Endpoint legacy para compatibilidad
    """
    return await search_concepts(query)

@app.post("/get_concept_context") 
async def get_concept_context_legacy(query: GetContextQuery):
    """
    Endpoint legacy para compatibilidad
    """
    return await get_concept_context(query)

@app.post("/validate_notation")
async def validate_notation_legacy(query: ValidateNotationQuery):
    """
    Endpoint legacy para compatibilidad
    """
    return await validate_notation(query)

if __name__ == "__main__":
    import uvicorn
    
    # Inicializar manager de taxonomías
    logger.info("Inicializando Multi-Taxonomy MCP Server...")
    
    try:
        active_count = len(taxonomy_manager.get_active_taxonomies())
        default_taxonomy = taxonomy_manager.get_default_taxonomy_id()
        logger.info(f"Servidor listo - {active_count} taxonomías activas, default: {default_taxonomy}")
    except Exception as e:
        logger.warning(f"Advertencia en inicialización: {e}")
    
    uvicorn.run(app, host="0.0.0.0", port=8080)