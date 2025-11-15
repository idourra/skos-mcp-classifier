"""
Taxonomy Service - Domain service for taxonomy operations
Pure business logic without infrastructure dependencies
"""
from typing import List, Optional, Dict
from server.domain.models import TaxonomyConcept, TaxonomyMetadata
from server.adapters.taxonomy_repository import taxonomy_repository


class TaxonomyService:
    """Service for taxonomy operations - encapsulates business logic"""
    
    def __init__(self):
        self.repository = taxonomy_repository
    
    def get_concept(self, concept_id: str, taxonomy_id: Optional[str] = None) -> Optional[TaxonomyConcept]:
        """
        Get a concept by ID (URI or notation)
        
        Args:
            concept_id: Concept URI or notation
            taxonomy_id: Optional taxonomy ID
            
        Returns:
            TaxonomyConcept if found, None otherwise
        """
        # Try as URI first
        concept = self.repository.get_concept_by_uri(concept_id, taxonomy_id)
        
        # If not found, try as notation
        if not concept:
            concept = self.repository.get_concept_by_notation(concept_id, taxonomy_id)
        
        return concept
    
    def list_taxonomies(self, active_only: bool = True) -> Dict[str, TaxonomyMetadata]:
        """
        List available taxonomies
        
        Args:
            active_only: If True, only return active taxonomies
            
        Returns:
            Dictionary of taxonomy_id -> TaxonomyMetadata
        """
        return self.repository.list_taxonomies(active_only=active_only)
    
    def get_metadata(self, taxonomy_id: str) -> Optional[TaxonomyMetadata]:
        """
        Get metadata for a specific taxonomy
        
        Args:
            taxonomy_id: Taxonomy identifier
            
        Returns:
            TaxonomyMetadata if found, None otherwise
        """
        return self.repository.get_taxonomy_metadata(taxonomy_id)
    
    def get_default_taxonomy_id(self) -> str:
        """
        Get the ID of the default taxonomy
        
        Returns:
            Default taxonomy ID
            
        Raises:
            ValueError: If no default taxonomy is configured
        """
        return self.repository._get_default_taxonomy_id()
    
    def validate_taxonomy_exists(self, taxonomy_id: str) -> bool:
        """
        Check if a taxonomy exists and is active
        
        Args:
            taxonomy_id: Taxonomy identifier
            
        Returns:
            True if taxonomy exists and is active
        """
        metadata = self.get_metadata(taxonomy_id)
        return metadata is not None and metadata.is_active


# Global instance
taxonomy_service = TaxonomyService()
