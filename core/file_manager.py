#!/usr/bin/env python3
"""
📁 FILE MANAGER - Gestión Centralizada de Archivos
================================================
Maneja todos los archivos del sistema de forma unificada:
- Entrada: SKOS, CSV, Excel, JSON
- Salida: Exportaciones, reportes, logs
- Almacenamiento organizado por tipo y fecha
- Limpieza automática de archivos temporales
"""

import os
import json
import shutil
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum
import logging
import tempfile
import pandas as pd
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class FileType(str, Enum):
    """Tipos de archivo manejados por el sistema"""
    # Entrada
    SKOS_TAXONOMY = "skos_taxonomy"
    CSV_INPUT = "csv_input"
    EXCEL_INPUT = "excel_input"
    JSON_INPUT = "json_input"
    
    # Salida
    CLASSIFICATION_EXPORT = "classification_export"
    BATCH_EXPORT = "batch_export"
    REPORT = "report"
    METRICS = "metrics"
    
    # Sistema
    CONFIG = "config"
    LOG = "log"
    TEMP = "temp"
    BACKUP = "backup"

class FileFormat(str, Enum):
    """Formatos de archivo soportados"""
    JSON = "json"
    JSONLD = "jsonld"
    CSV = "csv"
    XLSX = "xlsx" 
    XLS = "xls"
    PDF = "pdf"
    XML = "xml"
    TXT = "txt"
    ZIP = "zip"

class FileStatus(str, Enum):
    """Estados de archivos"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    EXPORTED = "exported"
    ARCHIVED = "archived"
    ERROR = "error"
    DELETED = "deleted"

class FileMetadata(BaseModel):
    """Metadatos de archivo"""
    file_id: str = Field(..., description="ID único del archivo")
    original_name: str = Field(..., description="Nombre original del archivo")
    file_type: FileType = Field(..., description="Tipo de archivo")
    file_format: FileFormat = Field(..., description="Formato del archivo")
    size_bytes: int = Field(..., description="Tamaño en bytes")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    status: FileStatus = Field(FileStatus.UPLOADED, description="Estado del archivo")
    
    # Ubicación
    storage_path: str = Field(..., description="Ruta de almacenamiento")
    relative_path: str = Field(..., description="Ruta relativa desde base")
    
    # Información adicional
    checksum: Optional[str] = Field(None, description="Checksum del archivo")
    mime_type: Optional[str] = Field(None, description="Tipo MIME")
    tags: List[str] = Field(default_factory=list, description="Etiquetas del archivo")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos adicionales")
    
    # Limpieza automática
    expires_at: Optional[datetime] = Field(None, description="Fecha de expiración")
    auto_delete: bool = Field(False, description="Eliminar automáticamente")

class FileOperation(BaseModel):
    """Operación sobre archivo"""
    operation_id: str = Field(..., description="ID de la operación")
    file_id: str = Field(..., description="ID del archivo")
    operation_type: str = Field(..., description="Tipo de operación")
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(None)
    success: bool = Field(False, description="Si la operación fue exitosa")
    result: Dict[str, Any] = Field(default_factory=dict, description="Resultado de la operación")
    errors: List[str] = Field(default_factory=list, description="Errores ocurridos")

class FileProcessor(ABC):
    """Clase base para procesadores de archivos"""
    
    @abstractmethod
    def can_handle(self, file_format: FileFormat, file_type: FileType) -> bool:
        """Verificar si puede procesar el archivo"""
        pass
    
    @abstractmethod
    async def process(self, file_path: Path, metadata: FileMetadata) -> Dict[str, Any]:
        """Procesar el archivo"""
        pass

class JSONProcessor(FileProcessor):
    """Procesador de archivos JSON"""
    
    def can_handle(self, file_format: FileFormat, file_type: FileType) -> bool:
        return file_format in [FileFormat.JSON, FileFormat.JSONLD]
    
    async def process(self, file_path: Path, metadata: FileMetadata) -> Dict[str, Any]:
        """Procesar archivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                'success': True,
                'data': data,
                'records_count': len(data) if isinstance(data, list) else 1,
                'file_size_mb': file_path.stat().st_size / (1024 * 1024)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

class CSVProcessor(FileProcessor):
    """Procesador de archivos CSV"""
    
    def can_handle(self, file_format: FileFormat, file_type: FileType) -> bool:
        return file_format == FileFormat.CSV
    
    async def process(self, file_path: Path, metadata: FileMetadata) -> Dict[str, Any]:
        """Procesar archivo CSV"""
        try:
            df = pd.read_csv(file_path)
            
            return {
                'success': True,
                'data': df.to_dict('records'),
                'rows': len(df),
                'columns': list(df.columns),
                'file_size_mb': file_path.stat().st_size / (1024 * 1024)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

class ExcelProcessor(FileProcessor):
    """Procesador de archivos Excel"""
    
    def can_handle(self, file_format: FileFormat, file_type: FileType) -> bool:
        return file_format in [FileFormat.XLSX, FileFormat.XLS]
    
    async def process(self, file_path: Path, metadata: FileMetadata) -> Dict[str, Any]:
        """Procesar archivo Excel"""
        try:
            df = pd.read_excel(file_path)
            
            return {
                'success': True,
                'data': df.to_dict('records'),
                'rows': len(df),
                'columns': list(df.columns),
                'file_size_mb': file_path.stat().st_size / (1024 * 1024)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

class FileManager:
    """
    📁 Manager centralizado para todos los archivos del sistema
    
    Responsabilidades:
    - Organizar archivos por tipo y fecha
    - Procesar archivos de entrada
    - Generar archivos de salida
    - Limpieza automática
    - Backup y recuperación
    """
    
    def __init__(self, base_path: str = "files"):
        self.base_path = Path(base_path)
        self.logger = logging.getLogger(f"{__name__}.FileManager")
        
        # Crear estructura de directorios
        self._setup_directory_structure()
        
        # Registrar procesadores
        self.processors = [
            JSONProcessor(),
            CSVProcessor(), 
            ExcelProcessor()
        ]
        
        # Base de datos en memoria para metadatos (en producción usar DB real)
        self.file_metadata: Dict[str, FileMetadata] = {}
        self.file_operations: Dict[str, FileOperation] = {}
        
        # Configuración
        self.max_file_size_mb = 100
        self.temp_retention_days = 7
        self.auto_cleanup_enabled = True
    
    def _setup_directory_structure(self):
        """Crear estructura de directorios organizada"""
        directories = [
            "input/skos_taxonomies",
            "input/csv_files", 
            "input/excel_files",
            "input/json_files",
            "output/classifications",
            "output/reports",
            "output/exports",
            "temp",
            "backups",
            "logs",
            "config"
        ]
        
        for directory in directories:
            dir_path = self.base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"📁 Estructura de directorios creada en {self.base_path}")
    
    async def store_file(
        self,
        content: Union[bytes, str],
        original_name: str,
        file_type: FileType,
        file_format: FileFormat,
        metadata: Optional[Dict[str, Any]] = None,
        auto_delete_after: Optional[timedelta] = None
    ) -> FileMetadata:
        """
        Almacenar archivo en el sistema
        
        Args:
            content: Contenido del archivo
            original_name: Nombre original
            file_type: Tipo de archivo
            file_format: Formato del archivo
            metadata: Metadatos adicionales
            auto_delete_after: Tiempo de retención
            
        Returns:
            FileMetadata: Metadatos del archivo almacenado
        """
        import uuid
        import hashlib
        
        file_id = str(uuid.uuid4())
        self.logger.info(f"📁 Almacenando archivo {file_id}: {original_name}")
        
        try:
            # Determinar directorio según tipo
            type_directory = self._get_directory_for_type(file_type)
            
            # Crear nombre único preservando extensión
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = Path(original_name).suffix
            unique_name = f"{timestamp}_{file_id[:8]}{file_extension}"
            
            # Crear ruta completa
            storage_path = self.base_path / type_directory / unique_name
            storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Escribir archivo
            if isinstance(content, bytes):
                with open(storage_path, 'wb') as f:
                    f.write(content)
                checksum = hashlib.sha256(content).hexdigest()
            else:
                with open(storage_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()
            
            # Crear metadatos
            file_metadata = FileMetadata(
                file_id=file_id,
                original_name=original_name,
                file_type=file_type,
                file_format=file_format,
                size_bytes=storage_path.stat().st_size,
                storage_path=str(storage_path),
                relative_path=str(storage_path.relative_to(self.base_path)),
                checksum=checksum,
                metadata=metadata or {},
                auto_delete=auto_delete_after is not None,
                expires_at=datetime.now() + auto_delete_after if auto_delete_after else None
            )
            
            # Guardar en registro
            self.file_metadata[file_id] = file_metadata
            
            self.logger.info(f"✅ Archivo {file_id} almacenado en {storage_path}")
            return file_metadata
            
        except Exception as e:
            self.logger.error(f"❌ Error almacenando archivo {file_id}: {str(e)}")
            raise
    
    async def process_file(self, file_id: str) -> FileOperation:
        """
        Procesar archivo usando el procesador adecuado
        
        Args:
            file_id: ID del archivo a procesar
            
        Returns:
            FileOperation: Resultado del procesamiento
        """
        import uuid
        
        operation_id = str(uuid.uuid4())
        self.logger.info(f"⚙️ Procesando archivo {file_id}")
        
        # Verificar que el archivo existe
        if file_id not in self.file_metadata:
            raise ValueError(f"Archivo {file_id} no encontrado")
        
        metadata = self.file_metadata[file_id]
        
        # Crear operación
        operation = FileOperation(
            operation_id=operation_id,
            file_id=file_id,
            operation_type="process_file"
        )
        
        try:
            # Buscar procesador adecuado
            processor = None
            for p in self.processors:
                if p.can_handle(metadata.file_format, metadata.file_type):
                    processor = p
                    break
            
            if not processor:
                raise ValueError(f"No hay procesador para {metadata.file_format}")
            
            # Procesar archivo
            file_path = Path(metadata.storage_path)
            result = await processor.process(file_path, metadata)
            
            # Actualizar operación
            operation.success = result.get('success', False)
            operation.result = result
            operation.completed_at = datetime.now()
            
            # Actualizar estado del archivo
            metadata.status = FileStatus.PROCESSED if operation.success else FileStatus.ERROR
            metadata.updated_at = datetime.now()
            
            self.file_operations[operation_id] = operation
            
            if operation.success:
                self.logger.info(f"✅ Archivo {file_id} procesado exitosamente")
            else:
                self.logger.error(f"❌ Error procesando archivo {file_id}: {result.get('error')}")
            
            return operation
            
        except Exception as e:
            operation.success = False
            operation.errors = [str(e)]
            operation.completed_at = datetime.now()
            
            metadata.status = FileStatus.ERROR
            metadata.updated_at = datetime.now()
            
            self.file_operations[operation_id] = operation
            
            self.logger.error(f"❌ Error crítico procesando archivo {file_id}: {str(e)}")
            return operation
    
    async def export_data(
        self,
        data: Any,
        filename: str,
        file_format: FileFormat,
        destination: Optional[str] = None
    ) -> FileMetadata:
        """
        Exportar datos a archivo
        
        Args:
            data: Datos a exportar
            filename: Nombre del archivo
            file_format: Formato de exportación
            destination: Directorio destino (opcional)
            
        Returns:
            FileMetadata: Metadatos del archivo exportado
        """
        self.logger.info(f"📤 Exportando datos a {filename}")
        
        try:
            # Determinar directorio de salida
            if destination:
                output_dir = self.base_path / destination
            else:
                output_dir = self.base_path / "output" / "exports"
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Crear nombre único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = Path(filename).stem
            extension = self._get_extension_for_format(file_format)
            unique_filename = f"{base_name}_{timestamp}.{extension}"
            
            file_path = output_dir / unique_filename
            
            # Exportar según formato
            if file_format == FileFormat.JSON:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            
            elif file_format == FileFormat.CSV:
                if isinstance(data, dict) and 'results' in data:
                    # Formato de resultados de clasificación
                    df = pd.DataFrame([
                        {
                            'product_id': r.get('product_id', ''),
                            'search_text': r.get('search_text', ''),
                            'prefLabel': r.get('prefLabel', ''),
                            'notation': r.get('notation', ''),
                            'level': r.get('level', 0),
                            'score': r.get('score', 0.0),
                            'taxonomy': r.get('taxonomy_used', {}).get('name', '')
                        }
                        for r in data.get('results', [])
                    ])
                else:
                    df = pd.DataFrame([data] if isinstance(data, dict) else data)
                
                df.to_csv(file_path, index=False, encoding='utf-8')
            
            elif file_format == FileFormat.XLSX:
                if isinstance(data, dict) and 'results' in data:
                    df = pd.DataFrame([
                        {
                            'Product ID': r.get('product_id', ''),
                            'Search Text': r.get('search_text', ''),
                            'Category': r.get('prefLabel', ''),
                            'Notation': r.get('notation', ''),
                            'Level': r.get('level', 0),
                            'Confidence': r.get('score', 0.0),
                            'Taxonomy': r.get('taxonomy_used', {}).get('name', ''),
                            'Timestamp': datetime.now().isoformat()
                        }
                        for r in data.get('results', [])
                    ])
                else:
                    df = pd.DataFrame([data] if isinstance(data, dict) else data)
                
                df.to_excel(file_path, index=False)
            
            # Crear metadatos
            file_metadata = await self.store_file(
                content=file_path.read_bytes(),
                original_name=unique_filename,
                file_type=FileType.CLASSIFICATION_EXPORT,
                file_format=file_format,
                metadata={'exported_at': datetime.now().isoformat()}
            )
            
            self.logger.info(f"✅ Datos exportados a {file_path}")
            return file_metadata
            
        except Exception as e:
            self.logger.error(f"❌ Error exportando datos: {str(e)}")
            raise
    
    def _get_directory_for_type(self, file_type: FileType) -> str:
        """Obtener directorio para tipo de archivo"""
        type_directories = {
            FileType.SKOS_TAXONOMY: "input/skos_taxonomies",
            FileType.CSV_INPUT: "input/csv_files",
            FileType.EXCEL_INPUT: "input/excel_files", 
            FileType.JSON_INPUT: "input/json_files",
            FileType.CLASSIFICATION_EXPORT: "output/classifications",
            FileType.BATCH_EXPORT: "output/exports",
            FileType.REPORT: "output/reports",
            FileType.TEMP: "temp",
            FileType.CONFIG: "config",
            FileType.LOG: "logs"
        }
        return type_directories.get(file_type, "temp")
    
    def _get_extension_for_format(self, file_format: FileFormat) -> str:
        """Obtener extensión para formato"""
        extensions = {
            FileFormat.JSON: "json",
            FileFormat.JSONLD: "jsonld",
            FileFormat.CSV: "csv",
            FileFormat.XLSX: "xlsx",
            FileFormat.XLS: "xls",
            FileFormat.PDF: "pdf",
            FileFormat.XML: "xml",
            FileFormat.TXT: "txt",
            FileFormat.ZIP: "zip"
        }
        return extensions.get(file_format, "dat")
    
    async def cleanup_expired_files(self):
        """Limpiar archivos expirados"""
        if not self.auto_cleanup_enabled:
            return
        
        self.logger.info("🧹 Iniciando limpieza de archivos expirados")
        
        cleaned_count = 0
        now = datetime.now()
        
        for file_id, metadata in list(self.file_metadata.items()):
            if metadata.auto_delete and metadata.expires_at and metadata.expires_at < now:
                try:
                    # Eliminar archivo físico
                    file_path = Path(metadata.storage_path)
                    if file_path.exists():
                        file_path.unlink()
                    
                    # Eliminar metadatos
                    del self.file_metadata[file_id]
                    cleaned_count += 1
                    
                    self.logger.info(f"🗑️ Archivo expirado eliminado: {file_id}")
                    
                except Exception as e:
                    self.logger.error(f"❌ Error eliminando archivo {file_id}: {str(e)}")
        
        self.logger.info(f"✅ Limpieza completada. {cleaned_count} archivos eliminados")
    
    def get_file_info(self, file_id: str) -> Optional[FileMetadata]:
        """Obtener información de archivo"""
        return self.file_metadata.get(file_id)
    
    def list_files(
        self,
        file_type: Optional[FileType] = None,
        status: Optional[FileStatus] = None
    ) -> List[FileMetadata]:
        """Listar archivos con filtros opcionales"""
        files = list(self.file_metadata.values())
        
        if file_type:
            files = [f for f in files if f.file_type == file_type]
        
        if status:
            files = [f for f in files if f.status == status]
        
        return sorted(files, key=lambda f: f.created_at, reverse=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del file manager"""
        total_files = len(self.file_metadata)
        total_size = sum(f.size_bytes for f in self.file_metadata.values())
        
        # Estadísticas por tipo
        by_type = {}
        for metadata in self.file_metadata.values():
            file_type = metadata.file_type.value
            if file_type not in by_type:
                by_type[file_type] = {'count': 0, 'size_mb': 0}
            by_type[file_type]['count'] += 1
            by_type[file_type]['size_mb'] += metadata.size_bytes / (1024 * 1024)
        
        # Estadísticas por estado
        by_status = {}
        for metadata in self.file_metadata.values():
            status = metadata.status.value
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'by_type': by_type,
            'by_status': by_status,
            'operations_completed': len(self.file_operations)
        }

# Instancia global del file manager
file_manager = FileManager()

# Funciones de conveniencia
async def store_taxonomy_file(content: Union[bytes, str], filename: str) -> FileMetadata:
    """Almacenar archivo de taxonomía SKOS"""
    file_format = FileFormat.JSONLD if filename.endswith('.jsonld') else FileFormat.JSON
    
    return await file_manager.store_file(
        content=content,
        original_name=filename,
        file_type=FileType.SKOS_TAXONOMY,
        file_format=file_format,
        auto_delete_after=timedelta(days=30)  # Limpieza automática después de 30 días
    )

async def export_classification_results(data: Any, format: str = "json") -> FileMetadata:
    """Exportar resultados de clasificación"""
    file_format = FileFormat(format.lower())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"classification_results_{timestamp}"
    
    return await file_manager.export_data(
        data=data,
        filename=filename,
        file_format=file_format
    )

async def process_uploaded_file(file_id: str) -> FileOperation:
    """Procesar archivo subido"""
    return await file_manager.process_file(file_id)