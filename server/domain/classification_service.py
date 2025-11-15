"""
Classification Service - Domain service for text classification
Pure business logic without infrastructure dependencies
"""
import sys
import os
from typing import Optional

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from server.domain.models import ClassificationResult, TaxonomyConcept, ConfidenceLevel
from client.classify_standard_api import classify as base_classify


class ClassificationService:
    """Service for classification operations - encapsulates business logic"""
    
    def __init__(self):
        pass
    
    def classify(
        self, 
        text: str, 
        lang: str = "es",
        taxonomy_id: Optional[str] = None
    ) -> ClassificationResult:
        """
        Classify text into taxonomy concepts
        
        Args:
            text: Text to classify
            lang: Language code (default: es)
            taxonomy_id: Optional taxonomy ID (uses default if None)
            
        Returns:
            ClassificationResult object
            
        Raises:
            ValueError: If classification fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Call existing classification function (from client/classify_standard_api.py)
        # This integrates with OpenAI GPT-4o-mini
        result = base_classify(
            text=text.strip(),
            product_id=None,  # Not needed for MCP
            taxonomy_id=taxonomy_id
        )
        
        # Check for errors
        if 'error' in result:
            raise ValueError(f"Classification failed: {result['error']}")
        
        # Extract concept information
        concept = TaxonomyConcept(
            uri=result.get('concept_uri', ''),
            pref_label=result.get('prefLabel', ''),
            notation=result.get('notation', ''),
            level=result.get('level')
        )
        
        # Get confidence
        confidence = result.get('confidence', 0.0)
        
        # Determine confidence level
        confidence_level = self._determine_confidence_level(confidence)
        
        # Get taxonomy ID from result
        taxonomy_used = result.get('taxonomy_id', taxonomy_id or 'unknown')
        
        return ClassificationResult(
            text=text.strip(),
            concept=concept,
            confidence=confidence,
            confidence_level=confidence_level,
            taxonomy_id=taxonomy_used
        )
    
    def _determine_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """
        Determine confidence level from confidence score
        
        Args:
            confidence: Confidence score (0.0 to 1.0)
            
        Returns:
            ConfidenceLevel enum
        """
        if confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.UNCERTAIN


# Global instance
classification_service = ClassificationService()
