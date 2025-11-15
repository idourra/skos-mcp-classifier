"""
MCP Tools implementation
Exposes domain services as MCP tools for LLM agents
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import HTTPException
from typing import Union

from server.mcp.schemas import (
    SearchConceptsRequest, SearchConceptsResponse, SearchResultResponse,
    EmbedTextRequest, EmbedTextResponse,
    GetConceptRequest, ConceptResponse,
    ListTaxonomiesRequest, ListTaxonomiesResponse, TaxonomyMetadataResponse,
    GetTaxonomyMetadataRequest,
    ClassifyTextRequest, ClassifyTextResponse,
    ErrorResponse
)

from server.domain.search_service import search_service
from server.domain.taxonomy_service import taxonomy_service
from server.domain.classification_service import classification_service


class MCPTools:
    """MCP Tools - Entry point for LLM agents"""
    
    def __init__(self):
        self.search_service = search_service
        self.taxonomy_service = taxonomy_service
        self.classification_service = classification_service
    
    async def search_taxonomy_concepts(
        self, 
        request: SearchConceptsRequest
    ) -> Union[SearchConceptsResponse, ErrorResponse]:
        """
        Search for SKOS concepts by text query
        
        Tool: search_taxonomy_concepts
        Purpose: Find relevant taxonomy concepts matching a search query
        """
        try:
            results = self.search_service.search_concepts(
                query=request.query,
                top_k=request.top_k,
                taxonomy_id=request.taxonomy_id
            )
            
            # Convert domain models to response models
            result_responses = [
                SearchResultResponse(**result.to_dict())
                for result in results
            ]
            
            # Get taxonomy ID used
            taxonomy_id = request.taxonomy_id or self.taxonomy_service.get_default_taxonomy_id()
            
            return SearchConceptsResponse(
                results=result_responses,
                total_found=len(result_responses),
                taxonomy_id=taxonomy_id,
                query=request.query
            )
            
        except Exception as e:
            return ErrorResponse(
                error=str(e),
                error_code="SEARCH_ERROR"
            )
    
    async def embed_text(
        self, 
        request: EmbedTextRequest
    ) -> Union[EmbedTextResponse, ErrorResponse]:
        """
        Generate embedding vector for text
        
        Tool: embed_text
        Purpose: Convert text into vector representation for semantic search
        """
        try:
            embedding = self.search_service.embed_text(request.text)
            
            return EmbedTextResponse(
                embedding=embedding.embedding,
                dimension=embedding.dimension(),
                model=embedding.model,
                text_length=len(request.text)
            )
            
        except Exception as e:
            return ErrorResponse(
                error=str(e),
                error_code="EMBEDDING_ERROR"
            )
    
    async def get_taxonomy_concept(
        self, 
        request: GetConceptRequest
    ) -> Union[ConceptResponse, ErrorResponse]:
        """
        Get detailed information about a specific concept
        
        Tool: get_taxonomy_concept
        Purpose: Retrieve full details of a concept by URI or notation
        """
        try:
            concept = self.taxonomy_service.get_concept(
                concept_id=request.concept_id,
                taxonomy_id=request.taxonomy_id
            )
            
            if not concept:
                return ErrorResponse(
                    error=f"Concept '{request.concept_id}' not found",
                    error_code="CONCEPT_NOT_FOUND"
                )
            
            return ConceptResponse(
                uri=concept.uri,
                pref_label=concept.pref_label,
                notation=concept.notation,
                level=concept.level,
                broader=concept.broader,
                narrower=concept.narrower
            )
            
        except Exception as e:
            return ErrorResponse(
                error=str(e),
                error_code="CONCEPT_ERROR"
            )
    
    async def list_taxonomies(
        self, 
        request: ListTaxonomiesRequest
    ) -> Union[ListTaxonomiesResponse, ErrorResponse]:
        """
        List available taxonomies
        
        Tool: list_taxonomies
        Purpose: Get list of available SKOS taxonomies in the system
        """
        try:
            taxonomies = self.taxonomy_service.list_taxonomies(
                active_only=request.active_only
            )
            
            taxonomy_responses = [
                TaxonomyMetadataResponse(**metadata.to_dict())
                for metadata in taxonomies.values()
            ]
            
            # Find default taxonomy
            default_taxonomy = None
            for metadata in taxonomies.values():
                if metadata.is_default:
                    default_taxonomy = metadata.id
                    break
            
            return ListTaxonomiesResponse(
                taxonomies=taxonomy_responses,
                total_count=len(taxonomy_responses),
                default_taxonomy=default_taxonomy
            )
            
        except Exception as e:
            return ErrorResponse(
                error=str(e),
                error_code="LIST_ERROR"
            )
    
    async def get_taxonomy_metadata(
        self, 
        request: GetTaxonomyMetadataRequest
    ) -> Union[TaxonomyMetadataResponse, ErrorResponse]:
        """
        Get metadata for a specific taxonomy
        
        Tool: get_taxonomy_metadata
        Purpose: Retrieve detailed information about a taxonomy
        """
        try:
            metadata = self.taxonomy_service.get_metadata(request.taxonomy_id)
            
            if not metadata:
                return ErrorResponse(
                    error=f"Taxonomy '{request.taxonomy_id}' not found",
                    error_code="TAXONOMY_NOT_FOUND"
                )
            
            return TaxonomyMetadataResponse(**metadata.to_dict())
            
        except Exception as e:
            return ErrorResponse(
                error=str(e),
                error_code="METADATA_ERROR"
            )
    
    async def classify_text(
        self, 
        request: ClassifyTextRequest
    ) -> Union[ClassifyTextResponse, ErrorResponse]:
        """
        Classify text into taxonomy concepts
        
        Tool: classify_text
        Purpose: Automatically classify product descriptions into taxonomy
        """
        try:
            result = self.classification_service.classify(
                text=request.text,
                lang=request.lang,
                taxonomy_id=request.taxonomy_id
            )
            
            return ClassifyTextResponse(
                text=result.text,
                concept_uri=result.concept.uri,
                pref_label=result.concept.pref_label,
                notation=result.concept.notation,
                confidence=result.confidence,
                confidence_level=result.confidence_level.value,
                taxonomy_id=result.taxonomy_id,
                level=result.concept.level
            )
            
        except Exception as e:
            return ErrorResponse(
                error=str(e),
                error_code="CLASSIFICATION_ERROR"
            )


# Global instance
mcp_tools = MCPTools()
