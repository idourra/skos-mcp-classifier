#!/usr/bin/env python3
# classification_api.py - API REST completa para clasificación SKOS
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import uuid
import os
import tempfile
import csv
from pathlib import Path
from datetime import datetime
from client.classify_standard_api import classify
from utils.export_config import get_full_export_path, ensure_export_structure, EXPORTS_BASE_DIR

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

# Modelos para el endpoint unificado
class UnifiedProductRequest(BaseModel):
    products: List[ProductRequest] = Field(..., description="Lista de productos a clasificar (1 o más)", min_items=1)
    
class UnifiedClassificationResponse(BaseModel):
    total: int = Field(..., description="Total de productos procesados")
    successful: int = Field(..., description="Productos clasificados exitosamente") 
    failed: int = Field(..., description="Productos que fallaron")
    results: List[Dict[str, Any]] = Field(..., description="Array con resultados de clasificación")
    processing_time_seconds: Optional[float] = Field(None, description="Tiempo de procesamiento en segundos")
    timestamp: str = Field(..., description="Timestamp del procesamiento")

class ExportRequest(BaseModel):
    products: List[ProductRequest] = Field(..., description="Lista de productos para exportar")
    format: str = Field(..., description="Formato de exportación: 'csv' o 'excel'")
    filename: Optional[str] = Field(None, description="Nombre del archivo (opcional)")
    
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

class ExportResponse(BaseModel):
    status: str
    filename: str
    download_url: str
    total_products: int
    successful: int
    failed: int
    file_size_bytes: Optional[int] = None
    timestamp: str
    
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
        "version": "2.0.0",
        "description": "API REST para clasificación de productos usando taxonomía SKOS",
        "endpoints": {
            "classification": {
                "classify_products": {
                    "url": "/classify/products",
                    "method": "POST",
                    "description": "Clasifica 1 o N productos en una sola llamada",
                    "example_single": {
                        "products": [
                            {"text": "leche descremada", "product_id": "SKU001"}
                        ]
                    },
                    "example_multiple": {
                        "products": [
                            {"text": "arroz blanco", "product_id": "SKU001"},
                            {"text": "pollo congelado", "product_id": "SKU002"},
                            {"text": "yogurt natural", "product_id": "SKU003"}
                        ]
                    }
                }
            },
            "export": {
                "export_csv": {
                    "url": "/export/csv",
                    "method": "POST", 
                    "description": "Exportar productos clasificados a CSV"
                },
                "export_excel": {
                    "url": "/export/excel",
                    "method": "POST",
                    "description": "Exportar productos clasificados a Excel"
                },
                "download": {
                    "url": "/download/{filename}",
                    "method": "GET",
                    "description": "Descargar archivo exportado"
                }
            },
            "system": {
                "health": {
                    "url": "/health",
                    "method": "GET",
                    "description": "Verificar estado del sistema"
                },
                "stats": {
                    "url": "/stats", 
                    "method": "GET",
                    "description": "Estadísticas de uso de la API"
                }
            }
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Prueba rápida de clasificación
        classify("test product")
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

@app.post("/classify", response_model=ClassificationResponse, deprecated=True)
def classify_single_product(request: ProductRequest):
    """
    [DEPRECATED] Clasificar un producto individual
    
    ⚠️ Este endpoint está deprecado. Use /classify/products en su lugar.
    
    Mantenido por compatibilidad hacia atrás.
    """
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

@app.post("/classify/products", response_model=UnifiedClassificationResponse)
def classify_products_unified(request: UnifiedProductRequest):
    """
    Endpoint unificado para clasificar productos.
    
    Acepta un array de productos (1 o más) y devuelve un array con los resultados.
    - Para clasificar 1 producto: envía array con 1 elemento
    - Para clasificar N productos: envía array con N elementos
    
    Respuesta siempre en formato array con todos los resultados de clasificación.
    """
    import time
    start_time = time.time()
    
    # Validar que el array no esté vacío
    if not request.products:
        raise HTTPException(
            status_code=422,
            detail="Array de productos no puede estar vacío. Debe contener al menos 1 producto."
        )
    
    results = []
    successful = 0
    failed = 0
    
    for idx, product in enumerate(request.products):
        try:
            result = classify(product.text, product.product_id)
            
            if 'error' not in result:
                # Formato unificado de respuesta exitosa
                classification_result = {
                    "index": idx,
                    "product_id": product.product_id,
                    "search_text": product.text,
                    "concept_uri": result.get('concept_uri', ''),
                    "prefLabel": result.get('prefLabel', ''),
                    "notation": result.get('notation', ''),
                    "level": result.get('level'),
                    "confidence": result.get('confidence', 0.0),
                    "status": "success",
                    "timestamp": datetime.now().isoformat()
                }
                results.append(classification_result)
                successful += 1
            else:
                # Formato unificado de respuesta con error
                error_result = {
                    "index": idx,
                    "product_id": product.product_id,
                    "search_text": product.text,
                    "error": result['error'],
                    "status": "error",
                    "timestamp": datetime.now().isoformat()
                }
                results.append(error_result)
                failed += 1
                
        except Exception as e:
            # Formato unificado para excepciones
            exception_result = {
                "index": idx,
                "product_id": product.product_id,
                "search_text": product.text,
                "error": str(e),
                "status": "exception",
                "timestamp": datetime.now().isoformat()
            }
            results.append(exception_result)
            failed += 1
    
    processing_time = time.time() - start_time
    
    return UnifiedClassificationResponse(
        total=len(request.products),
        successful=successful,
        failed=failed,
        results=results,
        processing_time_seconds=round(processing_time, 3),
        timestamp=datetime.now().isoformat()
    )
@app.post("/classify/batch", response_model=BatchClassificationResponse, deprecated=True)
def classify_batch_products(request: BatchProductRequest):
    """
    [DEPRECATED] Clasificar múltiples productos en lote (síncrono)
    
    ⚠️ Este endpoint está deprecado. Use /classify/products en su lugar.
    
    Mantenido por compatibilidad hacia atrás.
    """
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

@app.post("/classify/batch/async", deprecated=True)
def classify_batch_async(request: BatchProductRequest, background_tasks: BackgroundTasks):
    """
    [DEPRECATED] Clasificar múltiples productos en lote (asíncrono)
    
    ⚠️ Este endpoint está deprecado. Use /classify/products para clasificación síncrona.
    
    Mantenido por compatibilidad hacia atrás.
    """
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

# Funciones de exportación
def create_csv_export(results_data: List[Dict], filename: str = None) -> str:
    """
    Crea un archivo CSV con los resultados de clasificación
    
    Args:
        results_data: Lista con resultados de clasificación
        filename: Nombre del archivo (opcional)
        
    Returns:
        str: Ruta completa del archivo creado
    """
    ensure_export_structure()
    
    if not filename:
        output_path = get_full_export_path("api_export", "csv")
    else:
        output_path = get_full_export_path(filename.replace('.csv', ''), "csv")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'product_id',
            'product_description', 
            'skos_category',
            'skos_notation',
            'skos_uri',
            'confidence_score',
            'classification_timestamp',
            'status'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in results_data:
            if item.get('status') == 'success' and 'classification' in item:
                classification = item['classification']
                
                # Manejar prefLabel que puede ser un diccionario
                pref_label = classification.get('prefLabel', '')
                if isinstance(pref_label, dict):
                    pref_label = pref_label.get('es', pref_label.get('en', str(pref_label)))
                
                row = {
                    'product_id': item.get('product_id', ''),
                    'product_description': item.get('search_text', ''),
                    'skos_category': pref_label,
                    'skos_notation': classification.get('notation', ''),
                    'skos_uri': classification.get('concept_uri', ''),
                    'confidence_score': classification.get('confidence', 0),
                    'classification_timestamp': item.get('timestamp', ''),
                    'status': 'success'
                }
            else:
                row = {
                    'product_id': item.get('product_id', ''),
                    'product_description': item.get('search_text', ''),
                    'skos_category': f"ERROR: {item.get('error', 'Unknown error')}",
                    'skos_notation': '',
                    'skos_uri': '',
                    'confidence_score': 0,
                    'classification_timestamp': item.get('timestamp', ''),
                    'status': 'error'
                }
            writer.writerow(row)
    
    return str(output_path)

def create_excel_export(results_data: List[Dict], filename: str = None) -> str:
    """
    Crea un archivo Excel con los resultados de clasificación
    
    Args:
        results_data: Lista con resultados de clasificación
        filename: Nombre del archivo (opcional)
        
    Returns:
        str: Ruta completa del archivo creado
    """
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
    except ImportError:
        raise HTTPException(
            status_code=500, 
            detail="openpyxl no está instalado. Ejecute: pip install openpyxl"
        )
    
    ensure_export_structure()
    
    if not filename:
        output_path = get_full_export_path("api_export", "excel")
    else:
        output_path = get_full_export_path(filename.replace('.xlsx', ''), "excel")
    
    # Crear workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Productos Clasificados"
    
    # Estilos
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'), 
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Headers
    headers = [
        "ID Producto",
        "Descripción del Producto", 
        "Categoría SKOS",
        "Notación SKOS",
        "URI Concepto",
        "Nivel de Confianza",
        "Timestamp Clasificación",
        "Estado"
    ]
    
    # Escribir headers
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = border
    
    # Escribir datos
    for row_idx, item in enumerate(results_data, 2):
        if item.get('status') == 'success' and 'classification' in item:
            classification = item['classification']
            
            # Manejar prefLabel que puede ser un diccionario
            pref_label = classification.get('prefLabel', '')
            if isinstance(pref_label, dict):
                pref_label = pref_label.get('es', pref_label.get('en', str(pref_label)))
            
            data = [
                item.get('product_id', ''),
                item.get('search_text', ''),
                pref_label,
                classification.get('notation', ''),
                classification.get('concept_uri', ''),
                classification.get('confidence', 0),
                item.get('timestamp', ''),
                'success'
            ]
        else:
            data = [
                item.get('product_id', ''),
                item.get('search_text', ''),
                f"ERROR: {item.get('error', 'Unknown error')}",
                '',
                '',
                0,
                item.get('timestamp', ''),
                'error'
            ]
        
        for col, value in enumerate(data, 1):
            cell = ws.cell(row=row_idx, column=col, value=value)
            cell.border = border
    
    # Ajustar ancho de columnas
    column_widths = [15, 40, 25, 15, 50, 15, 20, 10]
    for col, width in enumerate(column_widths, 1):
        ws.column_dimensions[get_column_letter(col)].width = width
    
    # Guardar archivo
    wb.save(output_path)
    
    return str(output_path)

# Endpoints de exportación
@app.post("/export/csv", response_model=ExportResponse)
def export_to_csv_endpoint(request: ExportRequest):
    """Exportar productos clasificados a CSV y generar URL de descarga"""
    try:
        # Clasificar productos
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
        
        # Crear archivo CSV
        file_path = create_csv_export(results, request.filename)
        filename = Path(file_path).name
        
        # Obtener tamaño del archivo
        file_size = Path(file_path).stat().st_size
        
        return ExportResponse(
            status="success",
            filename=filename,
            download_url=f"/download/{filename}",
            total_products=len(request.products),
            successful=successful,
            failed=failed,
            file_size_bytes=file_size,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export/excel", response_model=ExportResponse)
def export_to_excel_endpoint(request: ExportRequest):
    """Exportar productos clasificados a Excel y generar URL de descarga"""
    try:
        # Clasificar productos
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
        
        # Crear archivo Excel
        file_path = create_excel_export(results, request.filename)
        filename = Path(file_path).name
        
        # Obtener tamaño del archivo
        file_size = Path(file_path).stat().st_size
        
        return ExportResponse(
            status="success",
            filename=filename,
            download_url=f"/download/{filename}",
            total_products=len(request.products),
            successful=successful,
            failed=failed,
            file_size_bytes=file_size,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
def download_file(filename: str):
    """Descargar archivo exportado"""
    # Buscar archivo en las subcarpetas de exports
    file_found = None
    
    # Buscar en todas las subcarpetas de exports
    for root, dirs, files in os.walk(EXPORTS_BASE_DIR):
        if filename in files:
            file_found = Path(root) / filename
            break
    
    if not file_found or not file_found.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    # Determinar content type
    content_type = "application/octet-stream"
    if filename.endswith('.csv'):
        content_type = "text/csv"
    elif filename.endswith('.xlsx'):
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif filename.endswith('.json'):
        content_type = "application/json"
    
    return FileResponse(
        path=str(file_found),
        filename=filename,
        media_type=content_type
    )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando SKOS Classification API...")
    print("📖 Documentación: http://localhost:8000/docs")
    print("🔗 API: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)