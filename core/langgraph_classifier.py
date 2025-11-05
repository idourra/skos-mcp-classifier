#!/usr/bin/env python3
"""
Multi-Agent SKOS Classifier with LangGraph
Optimized architecture for classifying texts against SKOS taxonomies in Qdrant
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
import numpy as np
import time
import uuid
import re
from dataclasses import dataclass


# =============================================================================
# STATE DEFINITIONS
# =============================================================================

class Candidate(TypedDict):
    """Candidate concept from SKOS taxonomy"""
    uri: str
    scheme: str
    lang: str
    prefLabel: str
    breadcrumb: List[str]
    ancestors: List[str]
    broader: Optional[str]
    related: List[str]
    scores: Dict[str, float]  # {"comp":..., "lex":..., "path":..., "graph":..., "ce":...}
    centroids: Dict[str, List[float]]  # {"descendants": [...], "neighborhood": [...]}
    explanation: List[str]


class ClassifierState(TypedDict, total=False):
    """Shared state between LangGraph nodes"""
    # Input parameters
    text: str
    hint_type: Optional[str]
    scheme_uri: str
    ancestor_filter: Optional[str]
    lang: Optional[str]
    
    # Normalized/query processing
    text_norm: str
    detected_lang: str
    qvec_lexical: List[float]
    qvec_desc: List[float]
    qvec_path: List[float]
    qvec_comp: List[float]
    
    # Retrieval results
    hits_comp: List[Candidate]
    hits_lex: List[Candidate]
    hits_path: List[Candidate]
    hits_lexical_extra: List[Candidate]
    
    # Merged & ranked candidates
    candidates_merged: List[Candidate]
    candidates_graph: List[Candidate]
    candidates_ce: List[Candidate]
    
    # Decision outputs
    classification: Optional[Candidate]
    top_k: List[Candidate]
    confidence: float
    explanation: List[str]
    
    # Policy & telemetry
    validated: bool
    abstain_reason: Optional[str]
    metrics: Dict[str, Any]
    trace_id: str


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class ClassifierConfig:
    """Configuration for the multi-agent classifier"""
    qdrant_url: str = "http://qdrant:6333"
    collection_name: str = "concepts"
    cross_encoder_enabled: bool = False
    tau_low: float = 0.55
    epsilon_tie: float = 0.03
    retrieval_limit: int = 50
    top_k_output: int = 5
    top_m_rerank: int = 20
    embedding_dim: int = 768
    
    # Fusion weights
    weight_comp: float = 1.0
    weight_lex: float = 0.3
    weight_path: float = 0.2
    weight_graph: float = 0.02


# =============================================================================
# HELPER CLASSES
# =============================================================================

class EmbeddingService:
    """Service for generating embeddings (placeholder for actual implementation)"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", dim: int = 768):
        self.model_name = model_name
        self.dim = dim
        # TODO: Initialize actual model
        # from sentence_transformers import SentenceTransformer
        # self.model = SentenceTransformer(model_name)
    
    def encode_lexical(self, text: str) -> List[float]:
        """Generate lexical embedding focusing on exact terms"""
        # TODO: Implement actual encoding
        return list(np.random.rand(self.dim).astype(float))
    
    def encode_desc(self, text: str) -> List[float]:
        """Generate description embedding for semantic matching"""
        # TODO: Implement actual encoding
        return list(np.random.rand(self.dim).astype(float))
    
    def encode_path(self, text: str) -> List[float]:
        """Generate path/hierarchy-aware embedding"""
        # TODO: Implement actual encoding
        return list(np.random.rand(self.dim).astype(float))
    
    def encode_comp(self, text: str) -> List[float]:
        """Generate composite embedding combining multiple views"""
        # TODO: Implement actual encoding
        return list(np.random.rand(self.dim).astype(float))


class LanguageDetector:
    """Language detection service"""
    
    def __init__(self):
        # TODO: Initialize actual language detector
        # import fasttext
        pass
    
    def detect(self, text: str, default: str = "es") -> str:
        """Detect language of text"""
        # TODO: Implement actual detection
        # For now, return default
        return default


# =============================================================================
# MULTI-AGENT NODES
# =============================================================================

class MultiAgentClassifier:
    """LangGraph-based multi-agent classifier for SKOS taxonomies"""
    
    def __init__(self, config: ClassifierConfig):
        self.config = config
        self.qdrant = QdrantClient(url=config.qdrant_url)
        self.embedding_service = EmbeddingService(dim=config.embedding_dim)
        self.lang_detector = LanguageDetector()
        self.graph = self._build_graph()
        self.app = self.graph.compile()
    
    # =========================================================================
    # NODE IMPLEMENTATIONS
    # =========================================================================
    
    def n0_ingest(self, state: ClassifierState) -> ClassifierState:
        """N0: Ingest & Normalize - Clean text, detect language, tokenize"""
        t0 = time.time()
        
        text = state["text"].strip()
        if not text:
            raise ValueError("Empty text input")
        
        # Text normalization
        text_norm = self._normalize_text(text)
        state["text_norm"] = text_norm
        
        # Language detection
        detected_lang = state.get("lang") or self.lang_detector.detect(text_norm)
        state["detected_lang"] = detected_lang
        
        # Initialize metrics
        state.setdefault("metrics", {})
        state["metrics"]["n0_ms"] = int((time.time() - t0) * 1000)
        
        # Generate trace ID
        state["trace_id"] = state.get("trace_id") or str(uuid.uuid4())
        
        return state
    
    def n1_build_query_vecs(self, state: ClassifierState) -> ClassifierState:
        """N1: Query Embeddings Builder - Generate multivector embeddings"""
        t0 = time.time()
        
        txt = state["text_norm"]
        
        # Generate embeddings for different views
        state["qvec_lexical"] = self.embedding_service.encode_lexical(txt)
        state["qvec_desc"] = self.embedding_service.encode_desc(txt)
        state["qvec_path"] = self.embedding_service.encode_path(txt)
        state["qvec_comp"] = self.embedding_service.encode_comp(txt)
        
        state["metrics"]["n1_ms"] = int((time.time() - t0) * 1000)
        return state
    
    def n2_retrieval(self, state: ClassifierState) -> ClassifierState:
        """N2: Vector Retrieval - ANN search with Qdrant multivector"""
        t0 = time.time()
        
        scheme = state["scheme_uri"]
        lang = state["detected_lang"]
        ancestor = state.get("ancestor_filter")
        
        # Main composite vector search
        state["hits_comp"] = self._qdrant_search(
            state["qvec_comp"], 
            "comp_vec", 
            scheme, 
            lang, 
            ancestor
        )
        
        # Path/hierarchy context search
        state["hits_path"] = self._qdrant_search(
            state["qvec_path"],
            "path_vec",
            scheme,
            lang,
            ancestor
        )
        
        # Initialize empty lexical hits (will be filled by N3 if needed)
        state["hits_lex"] = []
        state["hits_lexical_extra"] = []
        
        state["metrics"]["n2_ms"] = int((time.time() - t0) * 1000)
        return state
    
    def n3_lexical_boost(self, state: ClassifierState) -> ClassifierState:
        """N3: Lexical Booster - Enhanced lexical matching for short queries"""
        t0 = time.time()
        
        scheme = state["scheme_uri"]
        lang = state["detected_lang"]
        ancestor = state.get("ancestor_filter")
        
        # Lexical vector search
        state["hits_lex"] = self._qdrant_search(
            state["qvec_lexical"],
            "lexical_vec",
            scheme,
            lang,
            ancestor
        )
        
        state["metrics"]["n3_ms"] = int((time.time() - t0) * 1000)
        return state
    
    def n4_merge(self, state: ClassifierState) -> ClassifierState:
        """N4: Hybrid Merger - Fuse candidates from multiple retrievals"""
        t0 = time.time()
        
        by_uri: Dict[str, Candidate] = {}
        
        # Merge candidates from different searches
        sources = [
            (state.get("hits_comp", []), "comp_vec"),
            (state.get("hits_path", []), "path_vec"),
            (state.get("hits_lex", []), "lexical_vec"),
            (state.get("hits_lexical_extra", []), "lexical_extra")
        ]
        
        for candidates, vector_name in sources:
            for c in candidates:
                uri = c["uri"]
                if uri not in by_uri:
                    by_uri[uri] = c
                else:
                    # Merge scores
                    by_uri[uri]["scores"].update(c["scores"])
        
        # Calculate fusion scores
        merged = []
        for c in by_uri.values():
            scores = c["scores"]
            fusion_score = (
                self.config.weight_comp * scores.get("comp_vec", 0.0) +
                self.config.weight_lex * scores.get("lexical_vec", 0.0) +
                self.config.weight_path * scores.get("path_vec", 0.0)
            )
            c["scores"]["merge"] = fusion_score
            merged.append(c)
        
        # Sort by fusion score and keep top K
        merged.sort(key=lambda x: x["scores"]["merge"], reverse=True)
        state["candidates_merged"] = merged[:self.config.retrieval_limit]
        
        state["metrics"]["n4_ms"] = int((time.time() - t0) * 1000)
        return state
    
    def n5_graph_reasoner(self, state: ClassifierState) -> ClassifierState:
        """N5: SKOS Graph Reasoner - Adjust scores using SKOS hierarchy"""
        t0 = time.time()
        
        cands = state["candidates_merged"]
        
        # Get top candidates for broader analysis
        top_n = min(10, len(cands))
        top_candidates = cands[:top_n]
        
        # Collect broader concepts from top candidates
        broader_concepts = set()
        for c in top_candidates:
            if c.get("broader"):
                broader_concepts.add(c["broader"])
        
        # Apply graph-based adjustments
        for c in cands:
            graph_boost = 0.0
            
            # Boost if shares broader with top candidates
            if c.get("broader") in broader_concepts:
                graph_boost += self.config.weight_graph
                c["explanation"].append("Shares broader concept with top candidates")
            
            # Boost if is broader of other top candidates
            if c["uri"] in broader_concepts:
                graph_boost += self.config.weight_graph * 1.5
                c["explanation"].append("Is broader concept of top candidates")
            
            c["scores"]["graph"] = graph_boost
        
        # Re-sort with graph scores
        def total_score(c: Candidate):
            return c["scores"].get("merge", 0.0) + c["scores"].get("graph", 0.0)
        
        cands.sort(key=total_score, reverse=True)
        state["candidates_graph"] = cands
        
        state["metrics"]["n5_ms"] = int((time.time() - t0) * 1000)
        return state
    
    def n6_cross_encoder_rerank(self, state: ClassifierState) -> ClassifierState:
        """N6: Cross-Encoder Re-rank - LLM-based reranking (optional)"""
        t0 = time.time()
        
        # Get top M candidates for reranking
        ranked = state["candidates_graph"]
        top_m = ranked[:self.config.top_m_rerank]
        
        # TODO: Implement actual cross-encoder reranking
        # For now, just pass through with CE score = merge + graph
        for c in top_m:
            c["scores"]["ce"] = (
                c["scores"].get("merge", 0.0) + 
                c["scores"].get("graph", 0.0)
            )
        
        state["candidates_ce"] = top_m
        
        state["metrics"]["n6_ms"] = int((time.time() - t0) * 1000)
        return state
    
    def n7_decide(self, state: ClassifierState) -> ClassifierState:
        """N7: Decision & Calibration - Select final classification"""
        t0 = time.time()
        
        # Get ranked candidates (from CE if available, else from graph)
        ranked = state.get("candidates_ce") or state.get("candidates_graph", [])
        
        if not ranked:
            state["classification"] = None
            state["top_k"] = []
            state["confidence"] = 0.0
            state["explanation"] = ["No candidates found"]
            state["metrics"]["n7_ms"] = int((time.time() - t0) * 1000)
            return state
        
        # Get top K
        topk = ranked[:self.config.top_k_output]
        top1 = topk[0]
        
        # Calculate confidence (TODO: implement calibration)
        conf = self._calculate_confidence(top1, topk)
        
        # Check for ties - if multiple candidates are very close, prefer broader
        if len(topk) >= 2:
            score_diff = top1["scores"].get("ce", top1["scores"].get("merge", 0.0)) - \
                        topk[1]["scores"].get("ce", topk[1]["scores"].get("merge", 0.0))
            
            if score_diff < self.config.epsilon_tie:
                # Check if they share broader - if so, return broader
                if top1.get("broader") == topk[1].get("broader") and top1.get("broader"):
                    state["explanation"].append(
                        f"Tie detected (Δ={score_diff:.3f}), returning shared broader concept"
                    )
                    # TODO: Fetch broader concept
        
        state["classification"] = top1
        state["top_k"] = topk
        state["confidence"] = conf
        state["explanation"] = state.get("explanation", []) + [
            "Multivector fusion + SKOS hierarchy adjustment"
        ]
        
        state["metrics"]["n7_ms"] = int((time.time() - t0) * 1000)
        return state
    
    def n8_validate(self, state: ClassifierState) -> ClassifierState:
        """N8: Policy & Constraints Validator - Validate classification"""
        t0 = time.time()
        
        cls = state.get("classification")
        
        # No classification found
        if not cls:
            state["validated"] = False
            state["abstain_reason"] = "no_candidates"
            state["metrics"]["n8_ms"] = int((time.time() - t0) * 1000)
            return state
        
        # Low confidence
        if state["confidence"] < self.config.tau_low:
            state["validated"] = False
            state["abstain_reason"] = "low_confidence"
            state["metrics"]["n8_ms"] = int((time.time() - t0) * 1000)
            return state
        
        # Language validation (already filtered in Qdrant)
        # Scheme validation (already filtered in Qdrant)
        
        # All validations passed
        state["validated"] = True
        state["abstain_reason"] = None
        
        state["metrics"]["n8_ms"] = int((time.time() - t0) * 1000)
        return state
    
    def n9_persist(self, state: ClassifierState) -> ClassifierState:
        """N9: Persist & Telemetry - Log results and metrics"""
        t0 = time.time()
        
        # TODO: Send to observability platform
        # For now, just record that we persisted
        state["metrics"]["n9_ms"] = int((time.time() - t0) * 1000)
        state["metrics"]["total_ms"] = sum(
            v for k, v in state["metrics"].items() if k.endswith("_ms")
        )
        
        return state
    
    def n10_error(self, state: ClassifierState) -> ClassifierState:
        """N10: Error Handler - Handle exceptions"""
        state["validated"] = False
        state["abstain_reason"] = state.get("abstain_reason") or "exception"
        state["classification"] = None
        state["top_k"] = []
        state["confidence"] = 0.0
        return state
    
    # =========================================================================
    # CONDITIONAL EDGES
    # =========================================================================
    
    def need_lexical_boost(self, state: ClassifierState) -> str:
        """Decide if lexical boost is needed for short queries"""
        text_norm = state["text_norm"]
        
        # Trigger lexical boost for short queries
        if len(text_norm.split()) <= 2:
            return "N3_LEXBOOST"
        
        # Also trigger for queries that look like SKU/GTIN
        if re.match(r'^[A-Z0-9\-]+$', text_norm):
            return "N3_LEXBOOST"
        
        return "N4_MERGE"
    
    def use_cross_encoder(self, state: ClassifierState) -> str:
        """Decide if cross-encoder reranking should be used"""
        if self.config.cross_encoder_enabled:
            # Check latency budget
            elapsed = state.get("metrics", {}).get("total_ms", 0)
            if elapsed < 5000:  # Less than 5 seconds so far
                return "N6_RERANK"
        
        return "N7_DECIDE"
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _normalize_text(self, text: str) -> str:
        """Normalize input text"""
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Convert to lowercase for consistency
        text = text.lower()
        
        # TODO: Add more normalization (remove accents, etc.)
        
        return text
    
    def _qdrant_search(
        self, 
        vec: List[float], 
        vector_name: str,
        scheme: str,
        lang: str,
        ancestor: Optional[str] = None,
        limit: int = None
    ) -> List[Candidate]:
        """Execute vector search in Qdrant"""
        if limit is None:
            limit = self.config.retrieval_limit
        
        # Build filter
        must_conditions = [
            FieldCondition(key="scheme", match=MatchValue(value=scheme)),
            FieldCondition(key="lang", match=MatchValue(value=lang))
        ]
        
        if ancestor:
            must_conditions.append(
                FieldCondition(key="ancestors", match=MatchValue(value=ancestor))
            )
        
        flt = Filter(must=must_conditions)
        
        try:
            # Execute search
            results = self.qdrant.search(
                collection_name=self.config.collection_name,
                query_vector=(vector_name, vec),
                limit=limit,
                query_filter=flt
            )
            
            # Map results to Candidate objects
            candidates = []
            for point in results:
                pl = point.payload
                candidate: Candidate = {
                    "uri": pl["uri"],
                    "scheme": pl["scheme"],
                    "lang": pl["lang"],
                    "prefLabel": pl.get("prefLabel", ""),
                    "breadcrumb": pl.get("breadcrumb", []),
                    "ancestors": pl.get("ancestors", []),
                    "broader": pl.get("broader"),
                    "related": pl.get("related", []),
                    "scores": {vector_name: float(point.score)},
                    "centroids": pl.get("centroids", {}),
                    "explanation": []
                }
                candidates.append(candidate)
            
            return candidates
        
        except Exception as e:
            # Log error and return empty list
            print(f"Qdrant search error: {e}")
            return []
    
    def _calculate_confidence(
        self, 
        top1: Candidate, 
        topk: List[Candidate]
    ) -> float:
        """Calculate calibrated confidence score"""
        # TODO: Implement proper calibration (Platt scaling or isotonic regression)
        
        # For now, use simple heuristic based on score and gap
        score = top1["scores"].get("ce", top1["scores"].get("merge", 0.0))
        
        if len(topk) >= 2:
            second_score = topk[1]["scores"].get("ce", topk[1]["scores"].get("merge", 0.0))
            gap = score - second_score
            
            # Higher confidence with bigger gap
            confidence = min(1.0, score * (1 + gap))
        else:
            confidence = score
        
        # Clip to [0, 1]
        return max(0.0, min(1.0, confidence))
    
    # =========================================================================
    # GRAPH CONSTRUCTION
    # =========================================================================
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph multi-agent pipeline"""
        graph = StateGraph(ClassifierState)
        
        # Add all nodes
        graph.add_node("N0_INGEST", self.n0_ingest)
        graph.add_node("N1_QUERYVECS", self.n1_build_query_vecs)
        graph.add_node("N2_RETR", self.n2_retrieval)
        graph.add_node("N3_LEXBOOST", self.n3_lexical_boost)
        graph.add_node("N4_MERGE", self.n4_merge)
        graph.add_node("N5_GRAPH", self.n5_graph_reasoner)
        graph.add_node("N6_RERANK", self.n6_cross_encoder_rerank)
        graph.add_node("N7_DECIDE", self.n7_decide)
        graph.add_node("N8_VALIDATE", self.n8_validate)
        graph.add_node("N9_PERSIST", self.n9_persist)
        graph.add_node("N10_ERROR", self.n10_error)
        
        # Set entry point
        graph.set_entry_point("N0_INGEST")
        
        # Add edges
        graph.add_edge("N0_INGEST", "N1_QUERYVECS")
        graph.add_edge("N1_QUERYVECS", "N2_RETR")
        
        # Conditional edge for lexical boost
        graph.add_conditional_edges(
            "N2_RETR",
            self.need_lexical_boost,
            {
                "N3_LEXBOOST": "N3_LEXBOOST",
                "N4_MERGE": "N4_MERGE"
            }
        )
        
        graph.add_edge("N3_LEXBOOST", "N4_MERGE")
        graph.add_edge("N4_MERGE", "N5_GRAPH")
        
        # Conditional edge for cross-encoder
        graph.add_conditional_edges(
            "N5_GRAPH",
            self.use_cross_encoder,
            {
                "N6_RERANK": "N6_RERANK",
                "N7_DECIDE": "N7_DECIDE"
            }
        )
        
        graph.add_edge("N6_RERANK", "N7_DECIDE")
        graph.add_edge("N7_DECIDE", "N8_VALIDATE")
        graph.add_edge("N8_VALIDATE", "N9_PERSIST")
        graph.add_edge("N9_PERSIST", END)
        
        # Error handling
        graph.add_edge("N10_ERROR", END)
        
        return graph
    
    # =========================================================================
    # PUBLIC API
    # =========================================================================
    
    def classify(
        self,
        text: str,
        scheme_uri: str,
        hint_type: Optional[str] = None,
        lang: Optional[str] = None,
        ancestor_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Classify a text against a SKOS taxonomy
        
        Args:
            text: Text to classify
            scheme_uri: URI of the SKOS taxonomy scheme
            hint_type: Optional hint about text type (product, intent, etc.)
            lang: Optional language code
            ancestor_filter: Optional URI to filter by ancestor concept
        
        Returns:
            Dictionary with classification results
        """
        # Prepare initial state
        initial_state: ClassifierState = {
            "text": text,
            "scheme_uri": scheme_uri,
            "hint_type": hint_type,
            "lang": lang,
            "ancestor_filter": ancestor_filter
        }
        
        try:
            # Execute the graph
            final_state = self.app.invoke(initial_state)
            
            # Format output
            result = {
                "trace_id": final_state.get("trace_id"),
                "classification": final_state.get("classification"),
                "top_k": final_state.get("top_k", []),
                "confidence": final_state.get("confidence", 0.0),
                "validated": final_state.get("validated", False),
                "abstain_reason": final_state.get("abstain_reason"),
                "explanation": final_state.get("explanation", []),
                "metrics": final_state.get("metrics", {}),
                "detected_lang": final_state.get("detected_lang"),
            }
            
            return result
        
        except Exception as e:
            # Handle errors through error node
            error_state = initial_state.copy()
            error_state["abstain_reason"] = str(e)
            final_state = self.n10_error(error_state)
            
            return {
                "trace_id": final_state.get("trace_id"),
                "classification": None,
                "top_k": [],
                "confidence": 0.0,
                "validated": False,
                "abstain_reason": final_state.get("abstain_reason"),
                "explanation": [f"Error: {str(e)}"],
                "metrics": {},
                "detected_lang": None
            }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_classifier(
    qdrant_url: str = "http://localhost:6333",
    collection_name: str = "concepts",
    **kwargs
) -> MultiAgentClassifier:
    """
    Factory function to create a configured multi-agent classifier
    
    Args:
        qdrant_url: URL of Qdrant instance
        collection_name: Name of the Qdrant collection
        **kwargs: Additional configuration parameters
    
    Returns:
        Configured MultiAgentClassifier instance
    """
    config = ClassifierConfig(
        qdrant_url=qdrant_url,
        collection_name=collection_name,
        **kwargs
    )
    
    return MultiAgentClassifier(config)
