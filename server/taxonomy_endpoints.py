#!/usr/bin/env python3
"""
Endpoints para gestión de múltiples taxonomías SKOS
Permite upload, activación, selección y gestión de taxonomías
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import tempfile
import json
from pathlib import Path
import logging

from utils.taxonomy_manager import taxonomy_manager

logger = logging.getLogger(__name__)

# Router para endpoints de taxonomías
taxonomy_router = APIRouter(prefix="/taxonomies", tags=["taxonomies"])

# Modelos Pydantic
class TaxonomyMetadata(BaseModel):
    """Metadatos para upload de taxonomía"""
    id: str = Field(..., description="ID único de la taxonomía")
    name: str = Field(..., description="Nombre descriptivo")
    description: str = Field("", description="Descripción de la taxonomía")
    provider: str = Field("Unknown", description="Proveedor de la taxonomía")
    language: str = Field("en", description="Código de idioma (ISO 639-1)")
    domain: str = Field("general", description="Dominio de aplicación")
    version: str = Field("1.0.0", description="Versión de la taxonomía")

class TaxonomyResponse(BaseModel):
    """Respuesta con información de taxonomía"""
    id: str
    name: str
    description: str
    provider: str
    language: str
    domain: str
    version: str
    concepts_count: int
    is_active: bool
    is_default: bool
    created_at: str
    updated_at: str
    file_size_mb: float

class TaxonomyListResponse(BaseModel):
    """Respuesta con lista de taxonomías"""
    taxonomies: List[TaxonomyResponse]
    total_count: int
    active_count: int
    default_taxonomy: Optional[str]

class TaxonomyValidationResponse(BaseModel):
    """Respuesta de validación de taxonomía"""
    valid: bool
    quality_score: float
    compliance_level: str
    requirements_met: Dict[str, bool]
    statistics: Dict[str, Any]
    enrichment_features: List[str]
    recommendations: List[str]
    warnings: List[str]
    errors: List[str]

class TaxonomyUploadResponse(BaseModel):
    """Respuesta de upload de taxonomía"""
    success: bool
    taxonomy_id: str
    message: str
    stats: Dict[str, Any]
    validation: Dict[str, Any] = {"skos_valid": True, "warnings": [], "errors": []}

@taxonomy_router.post("/validate", response_model=TaxonomyValidationResponse)
async def validate_taxonomy_file(
    file: UploadFile = File(..., description="Archivo SKOS para validar")
):
    """
    Validar un archivo SKOS sin subirlo al sistema
    
    Permite verificar si una taxonomía cumple los requisitos mínimos:
    • SKOS compliant (conceptos, esquemas, jerarquías)  
    • Mínimo 20 conceptos con etiquetas
    • Estructura jerárquica coherente
    • Calidad mínima 60% para clasificación efectiva
    
    Útil para verificar archivos antes del upload definitivo.
    """
    try:
        # Validar archivo según extensión
        allowed_extensions = ('.jsonld', '.json', '.rdf', '.xml', '.ttl')
        if not file.filename.endswith(allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"Formato no soportado. Use: {', '.join(allowed_extensions)}"
            )
        
        # Validar tamaño del archivo
        content = await file.read()
        if len(content) > 100 * 1024 * 1024:  # 100MB máximo
            raise HTTPException(status_code=413, detail="Archivo muy grande (máximo 100MB)")
        
        # Guardar archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            temp_file.write(content)
            temp_file_path = Path(temp_file.name)
        
        try:
            # VALIDACIÓN SKOS ESTRICTA
            logger.info(f"Validando archivo: {file.filename}")
            validation_result = taxonomy_manager.validate_skos_file(str(temp_file_path))
            
            return TaxonomyValidationResponse(
                valid=validation_result["valid"],
                quality_score=validation_result.get("quality_score", 0.0),
                compliance_level=validation_result.get("compliance_level", "none"),
                requirements_met=validation_result.get("requirements_met", {}),
                statistics=validation_result.get("statistics", {}),
                enrichment_features=validation_result.get("enrichment_features", []),
                recommendations=validation_result.get("recommendations", []),
                warnings=validation_result.get("warnings", []),
                errors=validation_result.get("errors", [])
            )
            
        finally:
            # Limpiar archivo temporal
            temp_file_path.unlink(missing_ok=True)
            
    except Exception as e:
        logger.error(f"Error validando archivo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error validando archivo: {str(e)}")

@taxonomy_router.post("/upload", response_model=TaxonomyUploadResponse)
async def upload_taxonomy(
    file: UploadFile = File(..., description="Archivo SKOS en formato JSON-LD"),
    metadata: str = Query(..., description="Metadatos de la taxonomía en JSON")
):
    """
    Subir nueva taxonomía SKOS al sistema con validación estricta
    
    REQUISITOS MÍNIMOS para aceptar la taxonomía:
    • SKOS compliant (conceptos, esquemas, jerarquías)
    • Mínimo 20 conceptos con etiquetas
    • Estructura jerárquica coherente  
    • Calidad mínima 60% para clasificación efectiva
    
    - **file**: Archivo SKOS (.jsonld, .rdf, .xml, .ttl)
    - **metadata**: JSON con metadatos (id, name, description, etc.)
    """
    try:
        # Parsear metadatos
        try:
            metadata_dict = json.loads(metadata)
            taxonomy_metadata = TaxonomyMetadata(**metadata_dict)
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(status_code=400, detail=f"Metadatos inválidos: {str(e)}")
        
        # Validar archivo según extensión
        allowed_extensions = ('.jsonld', '.json', '.rdf', '.xml', '.ttl')
        if not file.filename.endswith(allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"Formato no soportado. Use: {', '.join(allowed_extensions)}"
            )
        
        # Validar que no exista la taxonomía
        if taxonomy_manager.get_taxonomy_metadata(taxonomy_metadata.id):
            raise HTTPException(status_code=409, detail=f"Taxonomía '{taxonomy_metadata.id}' ya existe")
        
        # Validar tamaño del archivo
        content = await file.read()
        if len(content) > 100 * 1024 * 1024:  # 100MB máximo
            raise HTTPException(status_code=413, detail="Archivo muy grande (máximo 100MB)")
        
        # Guardar archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            temp_file.write(content)
            temp_file_path = Path(temp_file.name)
        
        try:
            # VALIDACIÓN SKOS ESTRICTA
            logger.info(f"Validando taxonomía '{taxonomy_metadata.id}'...")
            
            # Registrar la taxonomía (incluye validación automática)
            result_metadata = taxonomy_manager.register_taxonomy(
                taxonomy_metadata.id,
                temp_file_path,
                taxonomy_metadata.dict()
            )
            
            # Extraer información de validación
            validation_info = result_metadata.get("validation", {})
            skos_stats = result_metadata.get("skos_statistics", {})
            
            logger.info(f"✅ Taxonomía '{taxonomy_metadata.id}' registrada exitosamente")
            
            return TaxonomyUploadResponse(
                success=True,
                taxonomy_id=taxonomy_metadata.id,
                message=f"Taxonomía registrada exitosamente. Calidad: {validation_info.get('quality_score', 0):.1%}",
                stats={
                    "concepts_processed": result_metadata.get("concepts_processed", 0),
                    "concepts_imported": result_metadata.get("concepts_imported", 0),
                    "processing_time_seconds": result_metadata.get("processing_time_seconds", 0),
                    "total_concepts": skos_stats.get("total_concepts", 0),
                    "hierarchical_relations": skos_stats.get("hierarchical_relations", 0),
                    "concepts_with_definitions": skos_stats.get("concepts_with_definitions", 0)
                },
                validation={
                    "skos_valid": True,
                    "quality_score": validation_info.get("quality_score", 0),
                    "compliance_level": validation_info.get("compliance_level", "unknown"),
                    "enrichment_features": validation_info.get("enrichment_features", []),
                    "recommendations": validation_info.get("recommendations", []),
                    "warnings": [],
                    "errors": []
                }
            )
            
        except ValueError as ve:
            # Error de validación SKOS
            logger.warning(f"Taxonomía '{taxonomy_metadata.id}' rechazada: {str(ve)}")
            return TaxonomyUploadResponse(
                success=False,
                taxonomy_id=taxonomy_metadata.id,
                message="Taxonomía no cumple los requisitos mínimos",
                stats={},
                validation={
                    "skos_valid": False,
                    "quality_score": 0,
                    "compliance_level": "insufficient",
                    "enrichment_features": [],
                    "recommendations": [],
                    "warnings": [],
                    "errors": [str(ve)]
                }
            )
            
        finally:
            # Limpiar archivo temporal
            temp_file_path.unlink(missing_ok=True)
            
    except Exception as e:
        logger.error(f"Error en upload de taxonomía: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando taxonomía: {str(e)}")

@taxonomy_router.get("/", response_model=TaxonomyListResponse)
async def list_taxonomies(
    active_only: bool = Query(False, description="Mostrar solo taxonomías activas")
):
    """
    Listar todas las taxonomías disponibles
    
    - **active_only**: Si es True, solo muestra taxonomías activas
    """
    try:
        taxonomies_data = taxonomy_manager.list_taxonomies()
        
        if active_only:
            taxonomies_data = taxonomy_manager.get_active_taxonomies()
        
        # Convertir a formato de respuesta
        taxonomies = [
            TaxonomyResponse(**metadata) 
            for metadata in taxonomies_data.values()
        ]
        
        # Encontrar taxonomía default
        default_taxonomy = None
        for tax_id, metadata in taxonomies_data.items():
            if metadata.get("is_default", False):
                default_taxonomy = tax_id
                break
        
        active_count = sum(1 for meta in taxonomies_data.values() if meta.get("is_active", False))
        
        return TaxonomyListResponse(
            taxonomies=taxonomies,
            total_count=len(taxonomies),
            active_count=active_count,
            default_taxonomy=default_taxonomy
        )
        
    except Exception as e:
        logger.error(f"Error listando taxonomías: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo taxonomías: {str(e)}")

@taxonomy_router.get("/{taxonomy_id}", response_model=TaxonomyResponse)
async def get_taxonomy(taxonomy_id: str):
    """
    Obtener detalles de una taxonomía específica
    
    - **taxonomy_id**: ID de la taxonomía
    """
    metadata = taxonomy_manager.get_taxonomy_metadata(taxonomy_id)
    
    if not metadata:
        raise HTTPException(status_code=404, detail=f"Taxonomía '{taxonomy_id}' no encontrada")
    
    return TaxonomyResponse(**metadata)

@taxonomy_router.put("/{taxonomy_id}/activate")
async def activate_taxonomy(taxonomy_id: str, active: bool = Query(True, description="Estado activo")):
    """
    Activar o desactivar una taxonomía
    
    - **taxonomy_id**: ID de la taxonomía
    - **active**: True para activar, False para desactivar
    """
    try:
        taxonomy_manager.activate_taxonomy(taxonomy_id, active)
        action = "activada" if active else "desactivada"
        
        return JSONResponse(
            content={
                "success": True,
                "message": f"Taxonomía '{taxonomy_id}' {action} exitosamente",
                "taxonomy_id": taxonomy_id,
                "is_active": active
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error activando taxonomía: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error activando taxonomía: {str(e)}")

@taxonomy_router.put("/{taxonomy_id}/default")
async def set_default_taxonomy(taxonomy_id: str):
    """
    Establecer una taxonomía como default del sistema
    
    - **taxonomy_id**: ID de la taxonomía a establecer como default
    """
    try:
        taxonomy_manager.set_default_taxonomy(taxonomy_id)
        
        return JSONResponse(
            content={
                "success": True,
                "message": f"Taxonomía '{taxonomy_id}' establecida como default",
                "taxonomy_id": taxonomy_id,
                "is_default": True
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error estableciendo taxonomía default: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error estableciendo default: {str(e)}")

@taxonomy_router.delete("/{taxonomy_id}")
async def delete_taxonomy(taxonomy_id: str):
    """
    Eliminar una taxonomía del sistema
    
    - **taxonomy_id**: ID de la taxonomía a eliminar
    
    ⚠️ **Advertencia**: Esta acción es irreversible
    """
    try:
        taxonomy_manager.delete_taxonomy(taxonomy_id)
        
        return JSONResponse(
            content={
                "success": True,
                "message": f"Taxonomía '{taxonomy_id}' eliminada exitosamente",
                "taxonomy_id": taxonomy_id
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error eliminando taxonomía: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error eliminando taxonomía: {str(e)}")

@taxonomy_router.get("/{taxonomy_id}/stats")
async def get_taxonomy_stats(taxonomy_id: str):
    """
    Obtener estadísticas detalladas de una taxonomía
    
    - **taxonomy_id**: ID de la taxonomía
    """
    metadata = taxonomy_manager.get_taxonomy_metadata(taxonomy_id)
    
    if not metadata:
        raise HTTPException(status_code=404, detail=f"Taxonomía '{taxonomy_id}' no encontrada")
    
    try:
        # Obtener estadísticas adicionales de la base de datos
        with taxonomy_manager.get_db_connection(taxonomy_id) as conn:
            cursor = conn.cursor()
            
            # Contar conceptos por nivel
            levels_query = "SELECT level, COUNT(*) FROM concepts GROUP BY level ORDER BY level"
            levels_data = cursor.execute(levels_query).fetchall()
            concepts_by_level = {str(level): count for level, count in levels_data}
            
            # Obtener algunos conceptos de ejemplo
            sample_concepts_query = "SELECT uri, prefLabel, level FROM concepts LIMIT 10"
            sample_concepts = [
                {"uri": uri, "prefLabel": label, "level": level}
                for uri, label, level in cursor.execute(sample_concepts_query).fetchall()
            ]
        
        return {
            "taxonomy_id": taxonomy_id,
            "basic_info": metadata,
            "concepts_by_level": concepts_by_level,
            "sample_concepts": sample_concepts,
            "database_path": taxonomy_manager.get_db_path(taxonomy_id),
            "is_operational": taxonomy_manager.get_db_path(taxonomy_id) is not None
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")

def _validate_skos_file(file_path: Path) -> Dict[str, Any]:
    """
    Validar formato básico de archivo SKOS
    TODO: Implementar validación completa de SKOS
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Validación básica de JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            return {
                "skos_valid": False,
                "errors": [f"JSON inválido: {str(e)}"],
                "warnings": []
            }
        
        # Validaciones básicas de estructura SKOS
        warnings = []
        errors = []
        
        # Verificar que es un array o tiene @graph
        if not isinstance(data, list) and "@graph" not in data:
            warnings.append("El archivo no parece tener estructura SKOS estándar")
        
        # TODO: Agregar validaciones más específicas de SKOS
        # - Verificar conceptos con skos:prefLabel
        # - Validar relaciones jerárquicas
        # - Verificar URIs válidas
        # - Validar idiomas
        
        return {
            "skos_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
        
    except Exception as e:
        return {
            "skos_valid": False,
            "errors": [f"Error leyendo archivo: {str(e)}"],
            "warnings": []
        }