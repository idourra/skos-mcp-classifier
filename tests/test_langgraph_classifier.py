#!/usr/bin/env python3
"""
Unit tests for LangGraph Multi-Agent SKOS Classifier
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.langgraph_classifier import (
    MultiAgentClassifier,
    ClassifierConfig,
    ClassifierState,
    Candidate,
    EmbeddingService,
    LanguageDetector
)


@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client"""
    with patch('core.langgraph_classifier.QdrantClient') as mock:
        client = MagicMock()
        mock.return_value = client
        
        # Mock search results
        mock_point = MagicMock()
        mock_point.score = 0.85
        mock_point.payload = {
            'uri': 'https://test.io/concept/1',
            'scheme': 'https://test.io/',
            'lang': 'es',
            'prefLabel': 'Test Concept',
            'breadcrumb': ['Root', 'Level1', 'Test Concept'],
            'ancestors': ['https://test.io/concept/root'],
            'broader': 'https://test.io/concept/parent',
            'related': [],
            'centroids': {}
        }
        
        client.search.return_value = [mock_point]
        client.get_collections.return_value = {'collections': []}
        
        yield client


@pytest.fixture
def classifier_config():
    """Default classifier configuration"""
    return ClassifierConfig(
        qdrant_url="http://localhost:6333",
        collection_name="test_concepts",
        tau_low=0.55,
        epsilon_tie=0.03,
        retrieval_limit=50,
        top_k_output=5,
        embedding_dim=768
    )


@pytest.fixture
def classifier(mock_qdrant_client, classifier_config):
    """Create classifier instance with mocked dependencies"""
    with patch('core.langgraph_classifier.QdrantClient', return_value=mock_qdrant_client):
        clf = MultiAgentClassifier(classifier_config)
        return clf


class TestEmbeddingService:
    """Test embedding service"""
    
    def test_initialization(self):
        """Test embedding service initialization"""
        service = EmbeddingService(dim=768)
        assert service.dim == 768
        assert service.model_name is not None
    
    def test_encode_methods(self):
        """Test all encoding methods return correct dimensions"""
        service = EmbeddingService(dim=768)
        
        text = "test text"
        
        assert len(service.encode_lexical(text)) == 768
        assert len(service.encode_desc(text)) == 768
        assert len(service.encode_path(text)) == 768
        assert len(service.encode_comp(text)) == 768


class TestLanguageDetector:
    """Test language detector"""
    
    def test_initialization(self):
        """Test language detector initialization"""
        detector = LanguageDetector()
        assert detector is not None
    
    def test_detect_default(self):
        """Test default language detection"""
        detector = LanguageDetector()
        lang = detector.detect("some text")
        assert lang in ["es", "en", "pt", "fr"]


class TestMultiAgentClassifier:
    """Test multi-agent classifier"""
    
    def test_initialization(self, classifier):
        """Test classifier initialization"""
        assert classifier is not None
        assert classifier.config is not None
        assert classifier.graph is not None
        assert classifier.app is not None
    
    def test_n0_ingest(self, classifier):
        """Test N0: Ingest & Normalize node"""
        state: ClassifierState = {
            "text": "  Test Product  ",
            "scheme_uri": "https://test.io/",
        }
        
        result = classifier.n0_ingest(state)
        
        assert "text_norm" in result
        assert "detected_lang" in result
        assert "trace_id" in result
        assert "metrics" in result
        assert "n0_ms" in result["metrics"]
        assert result["text_norm"] == "test product"
    
    def test_n0_ingest_empty_text(self, classifier):
        """Test N0 with empty text raises error"""
        state: ClassifierState = {
            "text": "",
            "scheme_uri": "https://test.io/",
        }
        
        with pytest.raises(ValueError):
            classifier.n0_ingest(state)
    
    def test_n1_build_query_vecs(self, classifier):
        """Test N1: Query Embeddings Builder node"""
        state: ClassifierState = {
            "text_norm": "test product",
            "metrics": {}
        }
        
        result = classifier.n1_build_query_vecs(state)
        
        assert "qvec_lexical" in result
        assert "qvec_desc" in result
        assert "qvec_path" in result
        assert "qvec_comp" in result
        assert len(result["qvec_comp"]) == classifier.config.embedding_dim
        assert "n1_ms" in result["metrics"]
    
    def test_n2_retrieval(self, classifier):
        """Test N2: Vector Retrieval node"""
        state: ClassifierState = {
            "text_norm": "test product",
            "scheme_uri": "https://test.io/",
            "detected_lang": "es",
            "qvec_comp": [0.1] * 768,
            "qvec_path": [0.2] * 768,
            "metrics": {}
        }
        
        result = classifier.n2_retrieval(state)
        
        assert "hits_comp" in result
        assert "hits_path" in result
        assert isinstance(result["hits_comp"], list)
        assert "n2_ms" in result["metrics"]
    
    def test_n3_lexical_boost(self, classifier):
        """Test N3: Lexical Booster node"""
        state: ClassifierState = {
            "text_norm": "test",
            "scheme_uri": "https://test.io/",
            "detected_lang": "es",
            "qvec_lexical": [0.1] * 768,
            "metrics": {}
        }
        
        result = classifier.n3_lexical_boost(state)
        
        assert "hits_lex" in result
        assert isinstance(result["hits_lex"], list)
        assert "n3_ms" in result["metrics"]
    
    def test_n4_merge(self, classifier):
        """Test N4: Hybrid Merger node"""
        candidate1: Candidate = {
            "uri": "https://test.io/concept/1",
            "scheme": "https://test.io/",
            "lang": "es",
            "prefLabel": "Test 1",
            "breadcrumb": [],
            "ancestors": [],
            "broader": None,
            "related": [],
            "scores": {"comp_vec": 0.9},
            "centroids": {},
            "explanation": []
        }
        
        candidate2: Candidate = {
            "uri": "https://test.io/concept/2",
            "scheme": "https://test.io/",
            "lang": "es",
            "prefLabel": "Test 2",
            "breadcrumb": [],
            "ancestors": [],
            "broader": None,
            "related": [],
            "scores": {"lexical_vec": 0.8},
            "centroids": {},
            "explanation": []
        }
        
        state: ClassifierState = {
            "hits_comp": [candidate1],
            "hits_lex": [candidate2],
            "hits_path": [],
            "metrics": {}
        }
        
        result = classifier.n4_merge(state)
        
        assert "candidates_merged" in result
        assert len(result["candidates_merged"]) == 2
        assert "merge" in result["candidates_merged"][0]["scores"]
        assert "n4_ms" in result["metrics"]
    
    def test_n5_graph_reasoner(self, classifier):
        """Test N5: SKOS Graph Reasoner node"""
        candidate: Candidate = {
            "uri": "https://test.io/concept/1",
            "scheme": "https://test.io/",
            "lang": "es",
            "prefLabel": "Test",
            "breadcrumb": [],
            "ancestors": [],
            "broader": "https://test.io/concept/parent",
            "related": [],
            "scores": {"merge": 0.85},
            "centroids": {},
            "explanation": []
        }
        
        state: ClassifierState = {
            "candidates_merged": [candidate],
            "metrics": {}
        }
        
        result = classifier.n5_graph_reasoner(state)
        
        assert "candidates_graph" in result
        assert "graph" in result["candidates_graph"][0]["scores"]
        assert "n5_ms" in result["metrics"]
    
    def test_n7_decide(self, classifier):
        """Test N7: Decision & Calibration node"""
        candidate: Candidate = {
            "uri": "https://test.io/concept/1",
            "scheme": "https://test.io/",
            "lang": "es",
            "prefLabel": "Test",
            "breadcrumb": [],
            "ancestors": [],
            "broader": None,
            "related": [],
            "scores": {"merge": 0.85, "graph": 0.02},
            "centroids": {},
            "explanation": []
        }
        
        state: ClassifierState = {
            "candidates_graph": [candidate],
            "metrics": {}
        }
        
        result = classifier.n7_decide(state)
        
        assert "classification" in result
        assert "top_k" in result
        assert "confidence" in result
        assert result["classification"]["uri"] == candidate["uri"]
        assert 0 <= result["confidence"] <= 1
        assert "n7_ms" in result["metrics"]
    
    def test_n8_validate_success(self, classifier):
        """Test N8: Validation with valid classification"""
        state: ClassifierState = {
            "classification": {"uri": "test", "prefLabel": "Test"},
            "confidence": 0.8,
            "metrics": {}
        }
        
        result = classifier.n8_validate(state)
        
        assert result["validated"] is True
        assert result["abstain_reason"] is None
    
    def test_n8_validate_low_confidence(self, classifier):
        """Test N8: Validation with low confidence"""
        state: ClassifierState = {
            "classification": {"uri": "test", "prefLabel": "Test"},
            "confidence": 0.3,
            "metrics": {}
        }
        
        result = classifier.n8_validate(state)
        
        assert result["validated"] is False
        assert result["abstain_reason"] == "low_confidence"
    
    def test_n8_validate_no_classification(self, classifier):
        """Test N8: Validation with no classification"""
        state: ClassifierState = {
            "classification": None,
            "confidence": 0.0,
            "metrics": {}
        }
        
        result = classifier.n8_validate(state)
        
        assert result["validated"] is False
        assert result["abstain_reason"] == "no_candidates"
    
    def test_n9_persist(self, classifier):
        """Test N9: Persist & Telemetry node"""
        state: ClassifierState = {
            "metrics": {
                "n0_ms": 10,
                "n1_ms": 20,
                "n2_ms": 30
            }
        }
        
        result = classifier.n9_persist(state)
        
        assert "total_ms" in result["metrics"]
        assert result["metrics"]["total_ms"] == 60
    
    def test_n10_error(self, classifier):
        """Test N10: Error Handler node"""
        state: ClassifierState = {
            "text": "test"
        }
        
        result = classifier.n10_error(state)
        
        assert result["validated"] is False
        assert result["classification"] is None
        assert result["abstain_reason"] is not None
    
    def test_need_lexical_boost_short_query(self, classifier):
        """Test conditional edge for short query"""
        state: ClassifierState = {
            "text_norm": "yogur"
        }
        
        result = classifier.need_lexical_boost(state)
        assert result == "N3_LEXBOOST"
    
    def test_need_lexical_boost_normal_query(self, classifier):
        """Test conditional edge for normal query"""
        state: ClassifierState = {
            "text_norm": "yogur natural sin azúcar"
        }
        
        result = classifier.need_lexical_boost(state)
        assert result == "N4_MERGE"
    
    def test_need_lexical_boost_sku(self, classifier):
        """Test conditional edge for SKU pattern"""
        state: ClassifierState = {
            "text_norm": "SKU-12345"
        }
        
        result = classifier.need_lexical_boost(state)
        assert result == "N3_LEXBOOST"
    
    def test_use_cross_encoder_disabled(self, classifier):
        """Test conditional edge when cross-encoder disabled"""
        classifier.config.cross_encoder_enabled = False
        state: ClassifierState = {
            "metrics": {}
        }
        
        result = classifier.use_cross_encoder(state)
        assert result == "N7_DECIDE"
    
    def test_normalize_text(self, classifier):
        """Test text normalization"""
        text = "  Test   Product   "
        normalized = classifier._normalize_text(text)
        
        assert normalized == "test product"
        assert normalized.islower()
        assert "  " not in normalized
    
    def test_calculate_confidence(self, classifier):
        """Test confidence calculation"""
        candidate: Candidate = {
            "uri": "test",
            "scheme": "test",
            "lang": "es",
            "prefLabel": "Test",
            "breadcrumb": [],
            "ancestors": [],
            "broader": None,
            "related": [],
            "scores": {"merge": 0.85},
            "centroids": {},
            "explanation": []
        }
        
        confidence = classifier._calculate_confidence(candidate, [candidate])
        
        assert 0 <= confidence <= 1
        assert confidence > 0


class TestFullPipeline:
    """Integration tests for full classification pipeline"""
    
    def test_classify_success(self, classifier):
        """Test successful classification"""
        result = classifier.classify(
            text="test product",
            scheme_uri="https://test.io/",
            lang="es"
        )
        
        assert "trace_id" in result
        assert "classification" in result
        assert "confidence" in result
        assert "validated" in result
        assert "metrics" in result
    
    def test_classify_with_hint(self, classifier):
        """Test classification with type hint"""
        result = classifier.classify(
            text="test product",
            scheme_uri="https://test.io/",
            hint_type="product",
            lang="es"
        )
        
        assert result is not None
        assert "trace_id" in result
    
    def test_classify_with_ancestor_filter(self, classifier):
        """Test classification with ancestor filter"""
        result = classifier.classify(
            text="test product",
            scheme_uri="https://test.io/",
            lang="es",
            ancestor_filter="https://test.io/concept/parent"
        )
        
        assert result is not None
    
    def test_classify_error_handling(self, classifier):
        """Test error handling in classification"""
        # Mock a failure in one of the nodes
        with patch.object(classifier, 'n1_build_query_vecs', side_effect=Exception("Test error")):
            result = classifier.classify(
                text="test product",
                scheme_uri="https://test.io/",
                lang="es"
            )
            
            assert result["validated"] is False
            assert result["classification"] is None
            assert "Error" in result["explanation"][0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
