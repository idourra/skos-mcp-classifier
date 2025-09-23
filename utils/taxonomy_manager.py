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
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any
import rdflib
from rdflib import Graph, Namespace, RDF, SKOS
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
        """
        Registrar una nueva taxonomía en el sistema con validación estricta
        
        Args:
            taxonomy_id: Identificador único de la taxonomía
            file_path: Ruta al archivo SKOS
            metadata: Metadatos básicos de la taxonomía
            
        Returns:
            Dict con metadatos completos de la taxonomía registrada
            
        Raises:
            ValueError: Si la taxonomía no cumple los requisitos mínimos
        """
        logger.info(f"Iniciando registro de taxonomía: {taxonomy_id}")
        
        # Validar ID único
        if taxonomy_id in self.taxonomies:
            raise ValueError(f"Taxonomía '{taxonomy_id}' ya existe")
        
        # VALIDACIÓN SKOS ESTRICTA (OBLIGATORIA)
        logger.info("Validando archivo SKOS...")
        validation_result = self.validate_skos_file(str(file_path))
        
        if not validation_result["valid"]:
            error_msg = "La taxonomía no cumple los requisitos mínimos:\n"
            for error in validation_result["errors"]:
                error_msg += f"  • {error}\n"
            
            if validation_result["warnings"]:
                error_msg += "\nAdvertencias:\n"
                for warning in validation_result["warnings"]:
                    error_msg += f"  • {warning}\n"
            
            raise ValueError(error_msg)
        
        # Mostrar resultados de validación
        logger.info(f"✅ Validación exitosa - Calidad: {validation_result['quality_score']:.1%}")
        logger.info(f"📊 Compliance Level: {validation_result['compliance_level']}")
        logger.info(f"🏗️ Conceptos: {validation_result['statistics']['total_concepts']}")
        
        if validation_result["enrichment_features"]:
            logger.info("🌟 Características de enriquecimiento detectadas:")
            for feature in validation_result["enrichment_features"]:
                logger.info(f"  • {feature}")
        
        # Crear directorio para la taxonomía
        taxonomy_dir = self.taxonomies_dir / taxonomy_id
        taxonomy_dir.mkdir(exist_ok=True)
        
        # Copiar archivo original
        original_file = taxonomy_dir / "original.jsonld"
        shutil.copy2(file_path, original_file)
        
        # Procesar y crear base de datos SQLite
        logger.info("Procesando taxonomía a base de datos...")
        db_path = taxonomy_dir / "taxonomy.sqlite"
        processing_stats = self._process_taxonomy_to_sqlite(original_file, db_path)
        
        # Completar metadatos incluyendo información de validación
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
            
            # Información de validación y calidad
            "validation": {
                "quality_score": validation_result["quality_score"],
                "compliance_level": validation_result["compliance_level"],
                "validated_at": datetime.now().isoformat(),
                "requirements_met": validation_result["requirements_met"],
                "enrichment_features": validation_result["enrichment_features"]
            },
            
            # Estadísticas de la taxonomía
            "skos_statistics": validation_result["statistics"],
            
            **processing_stats
        }
        
        # Si hay recomendaciones, incluirlas
        if validation_result.get("recommendations"):
            full_metadata["validation"]["recommendations"] = validation_result["recommendations"]
        
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
    
    def validate_skos_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validar que un archivo SKOS sea válido, compliant y de alta calidad
        Requisitos mínimos para aceptar una taxonomía:
        1. SKOS compliant (conceptos, esquemas, jerarquías)
        2. Etiquetas obligatorias (prefLabel)
        3. Estructura jerárquica coherente
        4. Calidad mínima para clasificación efectiva
        
        Args:
            file_path: Ruta al archivo SKOS
            
        Returns:
            Dict con resultado de validación detallada
        """
        validation_result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "statistics": {},
            "quality_score": 0.0,
            "compliance_level": "none",
            "enrichment_features": [],
            "requirements_met": {
                "skos_compliant": False,
                "has_hierarchy": False,
                "has_labels": False,
                "quality_threshold": False
            }
        }
        
        try:
            # Parse el archivo según su formato
            g = Graph()
            
            if file_path.endswith('.jsonld'):
                g.parse(file_path, format='json-ld')
            elif file_path.endswith('.rdf') or file_path.endswith('.xml'):
                g.parse(file_path, format='xml')
            elif file_path.endswith('.ttl'):
                g.parse(file_path, format='turtle')
            else:
                validation_result["errors"].append("❌ Formato de archivo no soportado. Use .jsonld, .rdf, .xml, o .ttl")
                return validation_result
            
            logger.info(f"Validando archivo SKOS: {file_path}")
            
            # 1. VALIDACIONES SKOS BÁSICAS (OBLIGATORIAS)
            skos_concepts = list(g.subjects(RDF.type, SKOS.Concept))
            concept_schemes = list(g.subjects(RDF.type, SKOS.ConceptScheme))
            
            if not skos_concepts:
                validation_result["errors"].append("❌ CRÍTICO: No se encontraron conceptos SKOS (skos:Concept)")
                return validation_result
            
            if len(skos_concepts) < 20:
                validation_result["errors"].append("❌ CRÍTICO: Taxonomía muy pequeña (<20 conceptos). Mínimo requerido: 20")
                return validation_result
            
            if not concept_schemes:
                validation_result["errors"].append("❌ CRÍTICO: No se encontró esquema de conceptos (skos:ConceptScheme)")
                return validation_result
            
            validation_result["requirements_met"]["skos_compliant"] = True
            
            # 2. VALIDACIONES DE ESTRUCTURA JERÁRQUICA (OBLIGATORIA)
            broader_relations = list(g.subject_objects(SKOS.broader))
            narrower_relations = list(g.subject_objects(SKOS.narrower))
            top_concepts = list(g.objects(None, SKOS.hasTopConcept))
            
            if not broader_relations and not narrower_relations and not top_concepts:
                validation_result["errors"].append("❌ CRÍTICO: No se encontraron relaciones jerárquicas (skos:broader/narrower/hasTopConcept)")
                return validation_result
            
            # Verificar que hay conceptos de nivel superior
            root_concepts = set()
            for concept in skos_concepts:
                has_broader = bool(list(g.objects(concept, SKOS.broader)))
                if not has_broader:
                    root_concepts.add(concept)
            
            if not root_concepts and not top_concepts:
                validation_result["errors"].append("❌ CRÍTICO: No se encontraron conceptos raíz (sin skos:broader)")
                return validation_result
            
            validation_result["requirements_met"]["has_hierarchy"] = True
            
            # 3. VALIDACIONES DE ETIQUETAS (OBLIGATORIAS)
            concepts_without_preflabel = []
            concepts_with_multilang = 0
            total_preflabels = 0
            
            for concept in skos_concepts:
                pref_labels = list(g.objects(concept, SKOS.prefLabel))
                if not pref_labels:
                    concepts_without_preflabel.append(str(concept))
                else:
                    total_preflabels += len(pref_labels)
                    if len(pref_labels) > 1:
                        concepts_with_multilang += 1
            
            if concepts_without_preflabel:
                if len(concepts_without_preflabel) > len(skos_concepts) * 0.05:  # >5% sin etiqueta es crítico
                    validation_result["errors"].append(f"❌ CRÍTICO: {len(concepts_without_preflabel)} conceptos sin skos:prefLabel ({len(concepts_without_preflabel)/len(skos_concepts)*100:.1f}%)")
                    return validation_result
                else:
                    validation_result["warnings"].append(f"⚠️ {len(concepts_without_preflabel)} conceptos sin skos:prefLabel")
            
            validation_result["requirements_met"]["has_labels"] = True
            
            # 4. VALIDACIONES DE ENRIQUECIMIENTO (CALIDAD)
            quality_features = []
            quality_score = 0.0
            
            # Base score por cumplir requisitos básicos
            quality_score = 0.4
            
            # Definiciones (skos:definition) - CRÍTICO para clasificación
            concepts_with_definition = len([c for c in skos_concepts if list(g.objects(c, SKOS.definition))])
            if concepts_with_definition > 0:
                definition_ratio = concepts_with_definition / len(skos_concepts)
                quality_features.append(f"✨ Definiciones: {definition_ratio:.1%} de conceptos")
                quality_score += 0.3 * definition_ratio
                
                if definition_ratio < 0.3:  # <30% con definiciones es problemático
                    validation_result["warnings"].append("⚠️ Pocas definiciones (<30%). Recomendado para mejor clasificación: >60%")
            else:
                validation_result["warnings"].append("⚠️ ADVERTENCIA: Sin definiciones (skos:definition). Afectará calidad de clasificación")
            
            # Etiquetas alternativas (skos:altLabel) - Importante para búsqueda
            concepts_with_altlabel = len([c for c in skos_concepts if list(g.objects(c, SKOS.altLabel))])
            if concepts_with_altlabel > 0:
                altlabel_ratio = concepts_with_altlabel / len(skos_concepts)
                quality_features.append(f"🏷️ Etiquetas alternativas: {altlabel_ratio:.1%} de conceptos")
                quality_score += 0.15 * altlabel_ratio
            
            # Notaciones (skos:notation) - Útil para códigos de producto
            concepts_with_notation = len([c for c in skos_concepts if list(g.objects(c, SKOS.notation))])
            if concepts_with_notation > 0:
                notation_ratio = concepts_with_notation / len(skos_concepts)
                quality_features.append(f"🔢 Notaciones: {notation_ratio:.1%} de conceptos")
                quality_score += 0.1 * notation_ratio
            
            # Relaciones semánticas (skos:related)
            related_relations = list(g.subject_objects(SKOS.related))
            if related_relations:
                quality_features.append(f"🔗 Relaciones semánticas: {len(related_relations)} enlaces")
                quality_score += 0.05
            
            # Mapeo a otros vocabularios (skos:exactMatch, skos:closeMatch)
            exact_matches = list(g.subject_objects(SKOS.exactMatch))
            close_matches = list(g.subject_objects(SKOS.closeMatch))
            if exact_matches or close_matches:
                quality_features.append(f"🌐 Mappings externos: {len(exact_matches + close_matches)} enlaces")
                quality_score += 0.05
            
            # Verificar profundidad jerárquica
            max_depth = self._calculate_hierarchy_depth(g, skos_concepts)
            if max_depth >= 3:
                quality_features.append(f"📊 Jerarquía profunda: {max_depth} niveles")
                quality_score += 0.05
            elif max_depth < 2:
                validation_result["warnings"].append("⚠️ Jerarquía muy plana (<2 niveles). Recomendado: 3-5 niveles")
            
            # 5. VERIFICAR UMBRAL DE CALIDAD MÍNIMA
            QUALITY_THRESHOLD = 0.6  # 60% mínimo
            if quality_score >= QUALITY_THRESHOLD:
                validation_result["requirements_met"]["quality_threshold"] = True
            else:
                validation_result["errors"].append(f"❌ CRÍTICO: Calidad insuficiente ({quality_score:.1%}). Mínimo requerido: {QUALITY_THRESHOLD:.0%}")
                return validation_result
            
            # 6. VALIDACIONES DE CONSISTENCIA
            consistency_issues = []
            
            # Verificar que no hay conceptos huérfanos (sin conexión al esquema)
            orphaned_concepts = []
            for concept in skos_concepts:
                connected = False
                for scheme in concept_schemes:
                    if (concept, SKOS.inScheme, scheme) in g or (scheme, SKOS.hasTopConcept, concept) in g:
                        connected = True
                        break
                if not connected and not list(g.objects(concept, SKOS.topConceptOf)):
                    orphaned_concepts.append(concept)
            
            if orphaned_concepts:
                if len(orphaned_concepts) > len(skos_concepts) * 0.1:  # >10% huérfanos es crítico
                    validation_result["errors"].append(f"❌ CRÍTICO: {len(orphaned_concepts)} conceptos huérfanos (sin conexión al esquema)")
                    return validation_result
                else:
                    consistency_issues.append(f"⚠️ {len(orphaned_concepts)} conceptos huérfanos")
            
            # 7. CÁLCULO FINAL DE COMPLIANCE LEVEL
            if quality_score >= 0.9:
                compliance_level = "excellent"
            elif quality_score >= 0.8:
                compliance_level = "very_good"
            elif quality_score >= 0.7:
                compliance_level = "good"
            elif quality_score >= QUALITY_THRESHOLD:
                compliance_level = "acceptable"
            else:
                compliance_level = "insufficient"
            
            # 8. ESTADÍSTICAS DETALLADAS
            validation_result["statistics"] = {
                "total_concepts": len(skos_concepts),
                "total_schemes": len(concept_schemes),
                "total_triples": len(g),
                "hierarchical_relations": len(broader_relations) + len(narrower_relations),
                "semantic_relations": len(related_relations),
                "concepts_with_definitions": concepts_with_definition,
                "concepts_with_altlabels": concepts_with_altlabel,
                "concepts_with_notations": concepts_with_notation,
                "multilingual_concepts": concepts_with_multilang,
                "external_mappings": len(exact_matches) + len(close_matches),
                "max_hierarchy_depth": max_depth,
                "root_concepts": len(root_concepts),
                "orphaned_concepts": len(orphaned_concepts) if 'orphaned_concepts' in locals() else 0
            }
            
            # Éxito: la taxonomía cumple todos los requisitos
            validation_result.update({
                "valid": True,
                "quality_score": min(quality_score, 1.0),
                "compliance_level": compliance_level,
                "enrichment_features": quality_features
            })
            
            if consistency_issues:
                validation_result["warnings"].extend(consistency_issues)
            
            # Recomendaciones para mejorar
            recommendations = []
            if concepts_with_definition < len(skos_concepts) * 0.6:
                recommendations.append("💡 Agregar más definiciones (skos:definition) para mejor clasificación")
            if concepts_with_altlabel < len(skos_concepts) * 0.4:
                recommendations.append("💡 Agregar etiquetas alternativas (skos:altLabel) para mejorar búsqueda")
            if not related_relations:
                recommendations.append("💡 Agregar relaciones semánticas (skos:related) entre conceptos relacionados")
            if max_depth < 3:
                recommendations.append("💡 Considerar mayor profundidad jerárquica para clasificación más precisa")
            
            validation_result["recommendations"] = recommendations
            
            logger.info(f"Validación completada - Calidad: {quality_score:.1%}, Nivel: {compliance_level}")
            
        except Exception as e:
            logger.error(f"Error validando archivo SKOS: {str(e)}")
            validation_result["errors"].append(f"❌ Error parseando archivo: {str(e)}")
        
        return validation_result
    
    def _calculate_hierarchy_depth(self, graph: Graph, concepts) -> int:
        """Calcular la profundidad máxima de la jerarquía"""
        try:
            max_depth = 0
            
            # Encontrar conceptos raíz (sin broader)
            root_concepts = []
            for concept in concepts:
                if not list(graph.objects(concept, SKOS.broader)):
                    root_concepts.append(concept)
            
            # Calcular profundidad desde cada raíz
            for root in root_concepts:
                depth = self._get_concept_depth(graph, root, 0, set())
                max_depth = max(max_depth, depth)
            
            return max_depth
        except Exception:
            return 1  # Valor por defecto en caso de error
    
    def _get_concept_depth(self, graph: Graph, concept, current_depth: int, visited) -> int:
        """Calcular profundidad recursiva de un concepto"""
        if concept in visited:
            return current_depth  # Evitar ciclos
        
        visited.add(concept)
        max_child_depth = current_depth
        
        # Buscar conceptos más específicos (narrower)
        for narrower in graph.objects(concept, SKOS.narrower):
            child_depth = self._get_concept_depth(graph, narrower, current_depth + 1, visited.copy())
            max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth


# Instancia global del manager
taxonomy_manager = TaxonomyManager()