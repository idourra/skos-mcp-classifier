"""
Taxonomy Repository - Adapter for SKOS taxonomy data access
Encapsulates all database access for taxonomies
"""
import sqlite3
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
from pathlib import Path
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.taxonomy_manager import taxonomy_manager
from server.domain.models import TaxonomyConcept, TaxonomyMetadata, SearchResult


class TaxonomyRepository:
    """Repository for accessing taxonomy data - Adapter pattern"""
    
    def __init__(self):
        self.taxonomy_manager = taxonomy_manager
    
    @contextmanager
    def _get_connection(self, taxonomy_id: str):
        """Get database connection for a taxonomy"""
        with self.taxonomy_manager.get_db_connection(taxonomy_id) as conn:
            yield conn
    
    def get_concept_by_uri(self, concept_uri: str, taxonomy_id: Optional[str] = None) -> Optional[TaxonomyConcept]:
        """Retrieve a concept by its URI"""
        taxonomy_id = taxonomy_id or self._get_default_taxonomy_id()
        
        with self._get_connection(taxonomy_id) as conn:
            cursor = conn.cursor()
            
            # Get main concept data
            query = """
                SELECT uri, prefLabel, notation, level
                FROM concepts 
                WHERE uri = ?
            """
            row = cursor.execute(query, (concept_uri,)).fetchone()
            
            if not row:
                return None
            
            uri, pref_label, notation, level = row
            
            # Get relationships (if tables exist)
            broader = self._get_related_concepts(cursor, concept_uri, "broader")
            narrower = self._get_related_concepts(cursor, concept_uri, "narrower")
            
            return TaxonomyConcept(
                uri=uri,
                pref_label=pref_label,
                notation=notation,
                level=level,
                broader=broader,
                narrower=narrower
            )
    
    def get_concept_by_notation(self, notation: str, taxonomy_id: Optional[str] = None) -> Optional[TaxonomyConcept]:
        """Retrieve a concept by its notation"""
        taxonomy_id = taxonomy_id or self._get_default_taxonomy_id()
        
        with self._get_connection(taxonomy_id) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT uri, prefLabel, notation, level
                FROM concepts 
                WHERE notation = ?
            """
            row = cursor.execute(query, (notation,)).fetchone()
            
            if not row:
                return None
            
            uri, pref_label, notation, level = row
            
            return TaxonomyConcept(
                uri=uri,
                pref_label=pref_label,
                notation=notation,
                level=level
            )
    
    def search_concepts(self, query: str, top_k: int = 10, taxonomy_id: Optional[str] = None) -> List[SearchResult]:
        """Search for concepts matching the query"""
        taxonomy_id = taxonomy_id or self._get_default_taxonomy_id()
        
        with self._get_connection(taxonomy_id) as conn:
            cursor = conn.cursor()
            
            # Simple text search (can be enhanced with FTS or embeddings)
            search_query = f"%{query.lower()}%"
            sql = """
                SELECT uri, prefLabel, notation, level
                FROM concepts 
                WHERE LOWER(prefLabel) LIKE ? 
                   OR LOWER(notation) LIKE ?
                ORDER BY 
                    CASE WHEN LOWER(prefLabel) = LOWER(?) THEN 1 ELSE 2 END,
                    LENGTH(prefLabel)
                LIMIT ?
            """
            
            results = cursor.execute(sql, (search_query, search_query, query, top_k)).fetchall()
            
            search_results = []
            for uri, pref_label, notation, level in results:
                # Calculate simple score
                score = 1.0 if pref_label.lower() == query.lower() else 0.5
                
                concept = TaxonomyConcept(
                    uri=uri,
                    pref_label=pref_label,
                    notation=notation,
                    level=level
                )
                
                search_results.append(SearchResult(
                    concept=concept,
                    score=score,
                    taxonomy_id=taxonomy_id
                ))
            
            return search_results
    
    def list_taxonomies(self, active_only: bool = False) -> Dict[str, TaxonomyMetadata]:
        """List all taxonomies"""
        if active_only:
            taxonomies = self.taxonomy_manager.get_active_taxonomies()
        else:
            taxonomies = self.taxonomy_manager.list_taxonomies()
        
        result = {}
        for tax_id, metadata in taxonomies.items():
            result[tax_id] = TaxonomyMetadata(
                id=metadata.get("id", tax_id),
                name=metadata.get("name", ""),
                description=metadata.get("description", ""),
                language=metadata.get("language", "en"),
                domain=metadata.get("domain", "general"),
                version=metadata.get("version", "1.0.0"),
                concepts_count=metadata.get("concepts_count", 0),
                is_active=metadata.get("is_active", False),
                is_default=metadata.get("is_default", False)
            )
        
        return result
    
    def get_taxonomy_metadata(self, taxonomy_id: str) -> Optional[TaxonomyMetadata]:
        """Get metadata for a specific taxonomy"""
        metadata = self.taxonomy_manager.get_taxonomy_metadata(taxonomy_id)
        
        if not metadata:
            return None
        
        return TaxonomyMetadata(
            id=metadata.get("id", taxonomy_id),
            name=metadata.get("name", ""),
            description=metadata.get("description", ""),
            language=metadata.get("language", "en"),
            domain=metadata.get("domain", "general"),
            version=metadata.get("version", "1.0.0"),
            concepts_count=metadata.get("concepts_count", 0),
            is_active=metadata.get("is_active", False),
            is_default=metadata.get("is_default", False)
        )
    
    def _get_default_taxonomy_id(self) -> str:
        """Get the default taxonomy ID"""
        try:
            return self.taxonomy_manager.get_default_taxonomy_id()
        except ValueError:
            raise ValueError("No default taxonomy configured")
    
    def _get_related_concepts(self, cursor, concept_uri: str, relation_type: str) -> List[str]:
        """Helper to get related concepts (broader, narrower, etc.)"""
        # Check if the relation table exists
        table_check = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (relation_type,)
        ).fetchone()
        
        if not table_check:
            return []
        
        try:
            query = f"SELECT {relation_type} FROM {relation_type} WHERE concept_uri = ?"
            results = cursor.execute(query, (concept_uri,)).fetchall()
            return [row[0] for row in results]
        except sqlite3.OperationalError:
            # Table might not have the expected structure
            return []


# Global instance
taxonomy_repository = TaxonomyRepository()
