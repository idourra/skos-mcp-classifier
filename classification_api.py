#!/usr/bin/env python3
# classification_api.py - API REST completa para clasificación SKOS
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import uuid
from datetime import datetime
from client.classify_standard_api import classify

app = FastAPI(
    title="SKOS Product Classifier API",
    description="API REST para clasificar productos usando taxonomía SKOS",
    version="1.0.0"
)

# Modelos Pydantic
class ProductRequest(BaseModel):
    text: str = Field(..., description="Descripción del producto a clasificar")
    product_id: Optional[str] = Field(None, description="ID/SKU opcional del producto")

class BatchProductRequest(BaseModel):
    products: List[ProductRequest] = Field(..., description="Lista de productos a clasificar")
    
class ClassificationResponse(BaseModel):
    product_id: Optional[str]
    search_text: str
    concept_uri: str
    prefLabel: str
    notation: str
    level: Optional[int]
    confidence: float
    timestamp: str
    
class BatchClassificationResponse(BaseModel):
    total: int
    successful: int 
    failed: int
    results: List[Dict[str, Any]]
    batch_id: str
    
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: str

# Store para trabajos en background (en producción usar Redis/DB)
background_jobs = {}

@app.get("/")
def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "SKOS Product Classifier API",
        "version": "1.0.0",
        "endpoints": {
            "classify": "/classify",
            "batch": "/classify/batch", 
            "async_batch": "/classify/batch/async",
            "job_status": "/jobs/{job_id}",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Prueba rápida de clasificación
        test_result = classify("test product")
        return {
            "status": "healthy",
            "mcp_server": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/classify", response_model=ClassificationResponse)
def classify_single_product(request: ProductRequest):
    """Clasificar un producto individual"""
    try:
        result = classify(request.text, request.product_id)
        
        # Verificar que el resultado tenga los campos necesarios
        if 'error' in result:
            raise HTTPException(
                status_code=422,
                detail=f"Error en clasificación: {result.get('error', 'Error desconocido')}"
            )
        
        return ClassificationResponse(
            product_id=result.get('product_id'),
            search_text=result.get('search_text', request.text),
            concept_uri=result.get('concept_uri', ''),
            prefLabel=result.get('prefLabel', ''),
            notation=result.get('notation', ''),
            level=result.get('level'),
            confidence=result.get('confidence', 0.0),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/classify/batch", response_model=BatchClassificationResponse)
def classify_batch_products(request: BatchProductRequest):
    """Clasificar múltiples productos en lote (síncrono)"""
    batch_id = str(uuid.uuid4())
    results = []
    successful = 0
    failed = 0
    
    for idx, product in enumerate(request.products):
        try:
            result = classify(product.text, product.product_id)
            
            if 'error' not in result:
                results.append({
                    "index": idx,
                    "product_id": product.product_id,
                    "search_text": product.text,
                    "classification": result,
                    "status": "success",
                    "timestamp": datetime.now().isoformat()
                })
                successful += 1
            else:
                results.append({
                    "index": idx,
                    "product_id": product.product_id,
                    "search_text": product.text,
                    "error": result['error'],
                    "status": "failed",
                    "timestamp": datetime.now().isoformat()
                })
                failed += 1
                
        except Exception as e:
            results.append({
                "index": idx,
                "product_id": product.product_id,
                "search_text": product.text,
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            })
            failed += 1
    
    return BatchClassificationResponse(
        total=len(request.products),
        successful=successful,
        failed=failed,
        results=results,
        batch_id=batch_id
    )

def process_batch_async(products: List[ProductRequest], job_id: str):
    """Procesar lote de productos en background"""
    background_jobs[job_id]["status"] = "processing"
    background_jobs[job_id]["started_at"] = datetime.now().isoformat()
    
    results = []
    successful = 0
    failed = 0
    
    for idx, product in enumerate(products):
        try:
            # Actualizar progreso
            background_jobs[job_id]["progress"] = {
                "current": idx + 1,
                "total": len(products),
                "percentage": ((idx + 1) / len(products)) * 100
            }
            
            result = classify(product.text, product.product_id)
            
            if 'error' not in result:
                results.append({
                    "index": idx,
                    "product_id": product.product_id,
                    "search_text": product.text,
                    "classification": result,
                    "status": "success",
                    "timestamp": datetime.now().isoformat()
                })
                successful += 1
            else:
                results.append({
                    "index": idx,
                    "product_id": product.product_id,
                    "search_text": product.text,
                    "error": result['error'],
                    "status": "failed", 
                    "timestamp": datetime.now().isoformat()
                })
                failed += 1
                
        except Exception as e:
            results.append({
                "index": idx,
                "product_id": product.product_id,
                "search_text": product.text,
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            })
            failed += 1
    
    # Completar job
    background_jobs[job_id].update({
        "status": "completed",
        "completed_at": datetime.now().isoformat(),
        "results": {
            "total": len(products),
            "successful": successful,
            "failed": failed,
            "data": results
        }
    })

@app.post("/classify/batch/async")
def classify_batch_async(request: BatchProductRequest, background_tasks: BackgroundTasks):
    """Clasificar múltiples productos en lote (asíncrono)"""
    job_id = str(uuid.uuid4())
    
    # Inicializar job
    background_jobs[job_id] = {
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "total_products": len(request.products),
        "progress": {"current": 0, "total": len(request.products), "percentage": 0}
    }
    
    # Agregar tarea en background
    background_tasks.add_task(process_batch_async, request.products, job_id)
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Procesamiento iniciado en background",
        "total_products": len(request.products),
        "check_status_url": f"/jobs/{job_id}"
    }

@app.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    """Obtener estado de un trabajo en background"""
    if job_id not in background_jobs:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    
    return background_jobs[job_id]

# Endpoints adicionales de utilidad
@app.get("/stats")
def get_api_stats():
    """Estadísticas de uso de la API"""
    total_jobs = len(background_jobs)
    completed = sum(1 for job in background_jobs.values() if job.get("status") == "completed")
    processing = sum(1 for job in background_jobs.values() if job.get("status") == "processing")
    
    return {
        "total_background_jobs": total_jobs,
        "completed_jobs": completed,
        "processing_jobs": processing,
        "api_uptime": "N/A",  # En producción calcular uptime real
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando SKOS Classification API...")
    print("📖 Documentación: http://localhost:8000/docs")
    print("🔗 API: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)