"""
Search Service - Domain service for taxonomy search operations
Pure business logic without infrastructure dependencies
"""
from typing import List, Optional
from server.domain.models import SearchResult, TextEmbedding
from server.adapters.taxonomy_repository import taxonomy_repository
from server.adapters.embedding_client import embedding_client


class SearchService:
    """Service for search operations - encapsulates business logic"""
    
    def __init__(self):
        self.repository = taxonomy_repository
        self.embedding_client = embedding_client
    
    def search_concepts(
        self, 
        query: str, 
        top_k: int = 10, 
        taxonomy_id: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Search for concepts in taxonomy
        
        Args:
            query: Search query text
            top_k: Maximum number of results
            taxonomy_id: Optional taxonomy ID (uses default if None)
            
        Returns:
            List of SearchResult objects
        """
        if not query or not query.strip():
            return []
        
        # Validate top_k
        if top_k < 1:
            top_k = 1
        if top_k > 100:
            top_k = 100
        
        # Perform search using repository
        results = self.repository.search_concepts(
            query=query.strip(),
            top_k=top_k,
            taxonomy_id=taxonomy_id
        )
        
        return results
    
    def embed_text(self, text: str) -> TextEmbedding:
        """
        Generate embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            TextEmbedding object
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        return self.embedding_client.embed_text(text.strip())


# Global instance
search_service = SearchService()
