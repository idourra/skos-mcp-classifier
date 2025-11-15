"""
Pydantic schemas for MCP tools and resources
Request/Response models for the MCP interface
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# ===== TOOL REQUEST SCHEMAS =====

class SearchConceptsRequest(BaseModel):
    """Request for search_taxonomy_concepts tool"""
    query: str = Field(..., description="Text to search for in taxonomy concepts")
    top_k: int = Field(10, ge=1, le=100, description="Maximum number of results to return")
    taxonomy_id: Optional[str] = Field(None, description="ID of specific taxonomy to search (optional, uses default if not provided)")


class EmbedTextRequest(BaseModel):
    """Request for embed_text tool"""
    text: str = Field(..., description="Text to convert into embedding vector")


class GetConceptRequest(BaseModel):
    """Request for get_taxonomy_concept tool"""
    concept_id: str = Field(..., description="Concept URI or notation code")
    taxonomy_id: Optional[str] = Field(None, description="ID of specific taxonomy (optional)")


class ListTaxonomiesRequest(BaseModel):
    """Request for list_taxonomies tool"""
    active_only: bool = Field(True, description="If true, only return active taxonomies")


class GetTaxonomyMetadataRequest(BaseModel):
    """Request for get_taxonomy_metadata tool"""
    taxonomy_id: str = Field(..., description="ID of the taxonomy")


class ClassifyTextRequest(BaseModel):
    """Request for classify_text tool"""
    text: str = Field(..., description="Text to classify into taxonomy concepts")
    lang: str = Field("es", description="Language code (ISO 639-1)")
    taxonomy_id: Optional[str] = Field(None, description="ID of specific taxonomy (optional)")


# ===== TOOL RESPONSE SCHEMAS =====

class ConceptResponse(BaseModel):
    """Response for a single concept"""
    uri: str
    pref_label: str
    notation: Optional[str] = None
    level: Optional[int] = None
    broader: List[str] = Field(default_factory=list)
    narrower: List[str] = Field(default_factory=list)


class SearchResultResponse(BaseModel):
    """Response for a single search result"""
    concept_uri: str
    pref_label: str
    notation: Optional[str] = None
    score: float
    taxonomy_id: str
    level: Optional[int] = None


class SearchConceptsResponse(BaseModel):
    """Response for search_taxonomy_concepts tool"""
    results: List[SearchResultResponse]
    total_found: int
    taxonomy_id: str
    query: str


class EmbedTextResponse(BaseModel):
    """Response for embed_text tool"""
    embedding: List[float]
    dimension: int
    model: str
    text_length: int


class TaxonomyMetadataResponse(BaseModel):
    """Response for taxonomy metadata"""
    id: str
    name: str
    description: str
    language: str
    domain: str
    version: str
    concepts_count: int
    is_active: bool
    is_default: bool


class ListTaxonomiesResponse(BaseModel):
    """Response for list_taxonomies tool"""
    taxonomies: List[TaxonomyMetadataResponse]
    total_count: int
    default_taxonomy: Optional[str] = None


class ClassifyTextResponse(BaseModel):
    """Response for classify_text tool"""
    text: str
    concept_uri: str
    pref_label: str
    notation: Optional[str] = None
    confidence: float
    confidence_level: str
    taxonomy_id: str
    level: Optional[int] = None


# ===== RESOURCE SCHEMAS =====

class ResourceResponse(BaseModel):
    """Generic response for MCP resources"""
    uri: str
    name: str
    description: str
    mimeType: str = "application/json"
    content: Dict[str, Any]


# ===== ERROR RESPONSE =====

class ErrorResponse(BaseModel):
    """Error response for MCP operations"""
    error: str
    details: Optional[str] = None
    error_code: Optional[str] = None
