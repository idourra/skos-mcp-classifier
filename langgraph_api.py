#!/usr/bin/env python3
"""
FastAPI wrapper for LangGraph Multi-Agent SKOS Classifier
Provides REST API endpoints for the multi-agent classification system
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
from contextlib import asynccontextmanager

from core.langgraph_classifier import MultiAgentClassifier, ClassifierConfig, Candidate
from core.langgraph_config import load_config, LangGraphClassifierConfig

# Global classifier instance
classifier: Optional[MultiAgentClassifier] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    global classifier
    
    # Startup: Initialize classifier
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        config = load_config(config_path="langgraph_config.yaml", use_env=True)
        
        # Convert to ClassifierConfig
        classifier_config = ClassifierConfig(
            qdrant_url=config.qdrant.url,
            collection_name=config.qdrant.collection_name,
            cross_encoder_enabled=config.features.cross_encoder_enabled,
            tau_low=config.thresholds.tau_low,
            epsilon_tie=config.thresholds.epsilon_tie,
            retrieval_limit=config.retrieval.retrieval_limit,
            top_k_output=config.retrieval.top_k_output,
            top_m_rerank=config.retrieval.top_m_rerank,
            embedding_dim=config.embedding.embedding_dim,
            weight_comp=config.retrieval.weight_comp,
            weight_lex=config.retrieval.weight_lex,
            weight_path=config.retrieval.weight_path,
            weight_graph=config.retrieval.weight_graph,
        )
        
        classifier = MultiAgentClassifier(classifier_config)
        logger.info("✅ LangGraph Multi-Agent Classifier initialized")
    except Exception as e:
        logger.warning(f"⚠️  Warning: Could not initialize classifier: {e}")
        logger.info("   Using fallback mode")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down classifier")


app = FastAPI(
    title="LangGraph Multi-Agent SKOS Classifier API",
    description="Advanced multi-agent architecture for SKOS taxonomy classification with Qdrant vector search",
    version="1.0.0",
    lifespan=lifespan
)


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class ClassificationRequest(BaseModel):
    """Request for single text classification"""
    text: str = Field(..., description="Text to classify")
    scheme_uri: str = Field(..., description="URI of SKOS taxonomy scheme")
    hint_type: Optional[str] = Field(None, description="Type hint: product, intent, etc.")
    lang: Optional[str] = Field(None, description="Language code (auto-detect if not provided)")
    ancestor_filter: Optional[str] = Field(None, description="Filter by ancestor concept URI")


class BatchClassificationRequest(BaseModel):
    """Request for batch classification"""
    items: List[ClassificationRequest] = Field(..., description="List of items to classify")
    parallel: bool = Field(True, description="Process in parallel")


class ClassificationResponse(BaseModel):
    """Response for classification"""
    trace_id: str
    classification: Optional[Dict[str, Any]]
    top_k: List[Dict[str, Any]]
    confidence: float
    validated: bool
    abstain_reason: Optional[str]
    explanation: List[str]
    metrics: Dict[str, Any]
    detected_lang: Optional[str]
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    classifier_initialized: bool
    qdrant_connected: bool
    timestamp: str


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "LangGraph Multi-Agent SKOS Classifier",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    classifier_ready = classifier is not None
    qdrant_ready = False
    
    if classifier_ready:
        try:
            # Try to ping Qdrant
            collections = classifier.qdrant.get_collections()
            qdrant_ready = True
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Qdrant health check failed: {e}")
            qdrant_ready = False
    
    return HealthResponse(
        status="healthy" if (classifier_ready and qdrant_ready) else "degraded",
        classifier_initialized=classifier_ready,
        qdrant_connected=qdrant_ready,
        timestamp=datetime.utcnow().isoformat()
    )


@app.post("/classify", response_model=ClassificationResponse)
async def classify_text(request: ClassificationRequest):
    """
    Classify a single text against a SKOS taxonomy
    
    This endpoint uses the multi-agent LangGraph pipeline with:
    - Text normalization and language detection
    - Multivector embedding generation
    - ANN search in Qdrant with multiple vector views
    - SKOS hierarchy-aware re-ranking
    - Confidence calibration and validation
    """
    if classifier is None:
        raise HTTPException(
            status_code=503,
            detail="Classifier not initialized. Check Qdrant connection."
        )
    
    try:
        result = classifier.classify(
            text=request.text,
            scheme_uri=request.scheme_uri,
            hint_type=request.hint_type,
            lang=request.lang,
            ancestor_filter=request.ancestor_filter
        )
        
        return ClassificationResponse(
            trace_id=result["trace_id"],
            classification=result["classification"],
            top_k=result["top_k"],
            confidence=result["confidence"],
            validated=result["validated"],
            abstain_reason=result["abstain_reason"],
            explanation=result["explanation"],
            metrics=result["metrics"],
            detected_lang=result["detected_lang"],
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Classification error: {str(e)}"
        )


@app.post("/classify/batch", response_model=List[ClassificationResponse])
async def classify_batch(request: BatchClassificationRequest):
    """
    Classify multiple texts in batch
    
    Supports parallel processing for improved throughput.
    """
    if classifier is None:
        raise HTTPException(
            status_code=503,
            detail="Classifier not initialized. Check Qdrant connection."
        )
    
    try:
        if request.parallel:
            # Process in parallel
            tasks = [
                asyncio.to_thread(
                    classifier.classify,
                    text=item.text,
                    scheme_uri=item.scheme_uri,
                    hint_type=item.hint_type,
                    lang=item.lang,
                    ancestor_filter=item.ancestor_filter
                )
                for item in request.items
            ]
            results = await asyncio.gather(*tasks)
        else:
            # Process sequentially
            results = []
            for item in request.items:
                result = classifier.classify(
                    text=item.text,
                    scheme_uri=item.scheme_uri,
                    hint_type=item.hint_type,
                    lang=item.lang,
                    ancestor_filter=item.ancestor_filter
                )
                results.append(result)
        
        # Convert to response models
        responses = []
        for result in results:
            responses.append(ClassificationResponse(
                trace_id=result["trace_id"],
                classification=result["classification"],
                top_k=result["top_k"],
                confidence=result["confidence"],
                validated=result["validated"],
                abstain_reason=result["abstain_reason"],
                explanation=result["explanation"],
                metrics=result["metrics"],
                detected_lang=result["detected_lang"],
                timestamp=datetime.utcnow().isoformat()
            ))
        
        return responses
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch classification error: {str(e)}"
        )


@app.get("/metrics", response_model=Dict[str, Any])
async def get_metrics():
    """
    Get aggregated metrics about classifier performance
    
    Returns statistics about:
    - Request counts
    - Latency percentiles
    - Confidence distribution
    - Abstain rates
    """
    # TODO: Implement metrics collection
    return {
        "status": "not_implemented",
        "message": "Metrics collection coming soon"
    }


@app.get("/config", response_model=Dict[str, Any])
async def get_config():
    """Get current classifier configuration"""
    if classifier is None:
        raise HTTPException(
            status_code=503,
            detail="Classifier not initialized"
        )
    
    return {
        "qdrant_url": classifier.config.qdrant_url,
        "collection_name": classifier.config.collection_name,
        "cross_encoder_enabled": classifier.config.cross_encoder_enabled,
        "tau_low": classifier.config.tau_low,
        "epsilon_tie": classifier.config.epsilon_tie,
        "retrieval_limit": classifier.config.retrieval_limit,
        "top_k_output": classifier.config.top_k_output,
        "weights": {
            "comp": classifier.config.weight_comp,
            "lex": classifier.config.weight_lex,
            "path": classifier.config.weight_path,
            "graph": classifier.config.weight_graph,
        }
    }


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
