"""
Domain models for SKOS taxonomy system
Pure domain models without infrastructure dependencies
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ConfidenceLevel(Enum):
    """Classification confidence levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


@dataclass
class TaxonomyConcept:
    """Domain model for a SKOS concept"""
    uri: str
    pref_label: str
    notation: Optional[str] = None
    alt_labels: List[str] = None
    definition: Optional[str] = None
    broader: List[str] = None
    narrower: List[str] = None
    related: List[str] = None
    level: Optional[int] = None
    
    def __post_init__(self):
        if self.alt_labels is None:
            self.alt_labels = []
        if self.broader is None:
            self.broader = []
        if self.narrower is None:
            self.narrower = []
        if self.related is None:
            self.related = []


@dataclass
class SearchResult:
    """Domain model for search results"""
    concept: TaxonomyConcept
    score: float
    taxonomy_id: str
    
    def to_dict(self) -> dict:
        return {
            "concept_uri": self.concept.uri,
            "pref_label": self.concept.pref_label,
            "notation": self.concept.notation,
            "score": self.score,
            "taxonomy_id": self.taxonomy_id,
            "level": self.concept.level
        }


@dataclass
class TaxonomyMetadata:
    """Domain model for taxonomy metadata"""
    id: str
    name: str
    description: str
    language: str
    domain: str
    version: str
    concepts_count: int
    is_active: bool
    is_default: bool
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "language": self.language,
            "domain": self.domain,
            "version": self.version,
            "concepts_count": self.concepts_count,
            "is_active": self.is_active,
            "is_default": self.is_default
        }


@dataclass
class ClassificationResult:
    """Domain model for classification result"""
    text: str
    concept: TaxonomyConcept
    confidence: float
    confidence_level: ConfidenceLevel
    taxonomy_id: str
    alternatives: List[TaxonomyConcept] = None
    
    def __post_init__(self):
        if self.alternatives is None:
            self.alternatives = []
    
    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "concept_uri": self.concept.uri,
            "pref_label": self.concept.pref_label,
            "notation": self.concept.notation,
            "confidence": self.confidence,
            "confidence_level": self.confidence_level.value,
            "taxonomy_id": self.taxonomy_id,
            "level": self.concept.level
        }


@dataclass
class TextEmbedding:
    """Domain model for text embedding"""
    text: str
    embedding: List[float]
    model: str
    
    def dimension(self) -> int:
        return len(self.embedding)
