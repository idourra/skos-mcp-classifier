#!/usr/bin/env python3
"""
TaxonomyManager - Gestor de múltiples taxonomías SKOS
Permite cargar, gestionar y servir múltiples taxonomías para clasificación
"""
import os
import json
import sqlite3
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class TaxonomyManager:
    """Gestor centralizado de múltiples taxonomías SKOS"""
    
    def __init__(self, taxonomies_dir: str = "taxonomies"):
        self.taxonomies_dir = Path(taxonomies_dir)
        self.taxonomies_dir.mkdir(exist_ok=True)
        self.metadata_file = self.taxonomies_dir / "metadata.json"
        self.taxonomies: Dict[str, Dict[str, Any]] = {}
        self.connections: Dict[str, str] = {}  # taxonomy_id -> db_path
        self.load_taxonomies_metadata()
    
    def load_taxonomies_metadata(self):
        """Cargar metadatos de todas las taxonomías registradas"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.taxonomies = data.get('taxonomies', {})
        else:
            # Inicializar con taxonomía actual si existe
            self._migrate_current_taxonomy()
    
    def _migrate_current_taxonomy(self):
        """Migrar la taxonomía actual a la nueva estructura"""
        current_db = Path("skos.sqlite")
        current_jsonld = Path("data/taxonomy.jsonld")
        
        if current_db.exists() and current_jsonld.exists():
            logger.info("Migrando taxonomía actual a nueva estructura...")
            
            # Crear directorio para taxonomía TreeW
            treew_dir = self.taxonomies_dir / "treew-skos"
            treew_dir.mkdir(exist_ok=True)
            
            # Copiar archivos
            shutil.copy2(current_db, treew_dir / "taxonomy.sqlite")
            shutil.copy2(current_jsonld, treew_dir / "original.jsonld")
            
            # Crear metadatos
            metadata = {
                "id": "treew-skos",
                "name": "TreeW SKOS Food Taxonomy",
                "description": "Taxonomía SKOS para productos alimentarios - TreeW",
                "version": "1.0.0",
                "provider": "TreeW",
                "language": "es",
                "domain": "food",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_active": True,
                "is_default": True,
                "file_hash": self._calculate_file_hash(current_jsonld),
                "file_size_mb": round(current_jsonld.stat().st_size / (1024*1024), 2),
                "schema_version": "1.0"
            }
            
            # Contar conceptos
            metadata["concepts_count"] = self._count_concepts("treew-skos")
            
            # Guardar metadatos específicos
            with open(treew_dir / "metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Registrar en metadatos globales
            self.taxonomies["treew-skos"] = metadata
            self.save_metadata()
            
            logger.info("Migración completada exitosamente")
    
    def register_taxonomy(self, taxonomy_id: str, file_path: Path, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Registrar una nueva taxonomía en el sistema"""
        
        # Validar ID único
        if taxonomy_id in self.taxonomies:
            raise ValueError(f"Taxonomía '{taxonomy_id}' ya existe")
        
        # Crear directorio para la taxonomía
        taxonomy_dir = self.taxonomies_dir / taxonomy_id
        taxonomy_dir.mkdir(exist_ok=True)
        
        # Copiar archivo original
        original_file = taxonomy_dir / "original.jsonld"
        shutil.copy2(file_path, original_file)
        
        # Procesar y crear base de datos SQLite
        db_path = taxonomy_dir / "taxonomy.sqlite"
        processing_stats = self._process_taxonomy_to_sqlite(original_file, db_path)
        
        # Completar metadatos
        full_metadata = {
            "id": taxonomy_id,
            "name": metadata.get("name", taxonomy_id),
            "description": metadata.get("description", ""),
            "version": metadata.get("version", "1.0.0"),
            "provider": metadata.get("provider", "Unknown"),
            "language": metadata.get("language", "en"),
            "domain": metadata.get("domain", "general"),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "is_active": True,
            "is_default": False,  # Nueva taxonomía no es default por defecto
            "file_hash": self._calculate_file_hash(original_file),
            "file_size_mb": round(original_file.stat().st_size / (1024*1024), 2),
            "schema_version": "1.0",
            **processing_stats
        }
        
        # Guardar metadatos específicos
        with open(taxonomy_dir / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(full_metadata, f, indent=2, ensure_ascii=False)
        
        # Registrar en metadatos globales
        self.taxonomies[taxonomy_id] = full_metadata
        self.save_metadata()
        
        logger.info(f"Taxonomía '{taxonomy_id}' registrada exitosamente")
        return full_metadata
    
    def _process_taxonomy_to_sqlite(self, jsonld_file: Path, db_path: Path) -> Dict[str, Any]:
        """Procesar archivo JSONLD y crear base de datos SQLite"""
        # TODO: Implementar procesamiento completo de JSONLD a SQLite
        # Por ahora, crear estructura básica
        
        start_time = datetime.now()
        
        # Crear estructura de base de datos básica
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            
            # Crear tablas básicas (similar a la estructura actual)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS concepts (
                    uri TEXT PRIMARY KEY,
                    prefLabel TEXT,
                    definition TEXT,
                    notation TEXT,
                    level INTEGER
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS relationships (
                    subject TEXT,
                    predicate TEXT,
                    object TEXT
                )
            ''')
            
            # TODO: Parsear JSONLD y poblar tablas
            # Por ahora, insertar datos de ejemplo
            sample_concepts = [
                ('http://example.com/concept/1', 'Concepto de Ejemplo', 'Definición de ejemplo', '001', 1),
            ]
            
            cursor.executemany(
                'INSERT OR REPLACE INTO concepts (uri, prefLabel, definition, notation, level) VALUES (?, ?, ?, ?, ?)',
                sample_concepts
            )
            
            concepts_count = cursor.execute('SELECT COUNT(*) FROM concepts').fetchone()[0]
            
            conn.commit()
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "concepts_count": concepts_count,
            "processing_time_seconds": round(processing_time, 2),
            "concepts_processed": concepts_count,
            "concepts_imported": concepts_count
        }
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calcular hash SHA256 de un archivo"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return f"sha256:{hash_sha256.hexdigest()}"
    
    def _count_concepts(self, taxonomy_id: str) -> int:
        """Contar conceptos en una taxonomía"""
        db_path = self.get_db_path(taxonomy_id)
        if not db_path or not Path(db_path).exists():
            return 0
        
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                result = cursor.execute('SELECT COUNT(*) FROM concepts').fetchone()
                return result[0] if result else 0
        except sqlite3.Error:
            return 0
    
    def get_db_path(self, taxonomy_id: str) -> Optional[str]:
        """Obtener ruta de base de datos para una taxonomía"""
        if taxonomy_id not in self.taxonomies:
            return None
        
        db_path = self.taxonomies_dir / taxonomy_id / "taxonomy.sqlite"
        return str(db_path) if db_path.exists() else None
    
    @contextmanager
    def get_db_connection(self, taxonomy_id: Optional[str] = None):
        """Obtener conexión a base de datos de taxonomía específica o default"""
        if not taxonomy_id:
            taxonomy_id = self.get_default_taxonomy_id()
        
        db_path = self.get_db_path(taxonomy_id)
        if not db_path:
            raise ValueError(f"Taxonomía '{taxonomy_id}' no encontrada o sin base de datos")
        
        conn = sqlite3.connect(db_path, check_same_thread=False)
        try:
            yield conn
        finally:
            conn.close()
    
    def get_default_taxonomy_id(self) -> str:
        """Obtener ID de taxonomía por defecto"""
        for tax_id, metadata in self.taxonomies.items():
            if metadata.get("is_default", False):
                return tax_id
        
        # Si no hay default, retornar la primera disponible
        if self.taxonomies:
            return list(self.taxonomies.keys())[0]
        
        raise ValueError("No hay taxonomías disponibles")
    
    def set_default_taxonomy(self, taxonomy_id: str):
        """Establecer taxonomía como default"""
        if taxonomy_id not in self.taxonomies:
            raise ValueError(f"Taxonomía '{taxonomy_id}' no existe")
        
        # Remover default de otras taxonomías
        for tax_id in self.taxonomies:
            self.taxonomies[tax_id]["is_default"] = False
        
        # Establecer nueva default
        self.taxonomies[taxonomy_id]["is_default"] = True
        self.taxonomies[taxonomy_id]["updated_at"] = datetime.now().isoformat()
        
        self.save_metadata()
        logger.info(f"Taxonomía '{taxonomy_id}' establecida como default")
    
    def activate_taxonomy(self, taxonomy_id: str, active: bool = True):
        """Activar o desactivar una taxonomía"""
        if taxonomy_id not in self.taxonomies:
            raise ValueError(f"Taxonomía '{taxonomy_id}' no existe")
        
        self.taxonomies[taxonomy_id]["is_active"] = active
        self.taxonomies[taxonomy_id]["updated_at"] = datetime.now().isoformat()
        
        self.save_metadata()
        action = "activada" if active else "desactivada"
        logger.info(f"Taxonomía '{taxonomy_id}' {action}")
    
    def get_active_taxonomies(self) -> Dict[str, Dict[str, Any]]:
        """Obtener todas las taxonomías activas"""
        return {
            tax_id: metadata 
            for tax_id, metadata in self.taxonomies.items() 
            if metadata.get("is_active", False)
        }
    
    def get_taxonomy_metadata(self, taxonomy_id: str) -> Optional[Dict[str, Any]]:
        """Obtener metadatos de una taxonomía específica"""
        return self.taxonomies.get(taxonomy_id)
    
    def list_taxonomies(self) -> Dict[str, Dict[str, Any]]:
        """Listar todas las taxonomías registradas"""
        return self.taxonomies.copy()
    
    def delete_taxonomy(self, taxonomy_id: str):
        """Eliminar una taxonomía del sistema"""
        if taxonomy_id not in self.taxonomies:
            raise ValueError(f"Taxonomía '{taxonomy_id}' no existe")
        
        # No permitir eliminar taxonomía default si es la única
        if (self.taxonomies[taxonomy_id].get("is_default", False) and 
            len(self.taxonomies) == 1):
            raise ValueError("No se puede eliminar la única taxonomía disponible")
        
        # Eliminar directorio
        taxonomy_dir = self.taxonomies_dir / taxonomy_id
        if taxonomy_dir.exists():
            shutil.rmtree(taxonomy_dir)
        
        # Remover de metadatos
        del self.taxonomies[taxonomy_id]
        
        # Si era default, establecer otra como default
        if not any(meta.get("is_default", False) for meta in self.taxonomies.values()):
            if self.taxonomies:
                first_tax_id = list(self.taxonomies.keys())[0]
                self.set_default_taxonomy(first_tax_id)
        
        self.save_metadata()
        logger.info(f"Taxonomía '{taxonomy_id}' eliminada exitosamente")
    
    def save_metadata(self):
        """Guardar metadatos globales de taxonomías"""
        metadata = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "taxonomies_count": len(self.taxonomies),
            "taxonomies": self.taxonomies
        }
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)


# Instancia global del manager
taxonomy_manager = TaxonomyManager()