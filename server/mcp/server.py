"""
MCP Server - FastAPI application
Entry point for Model Context Protocol
Agent-oriented interface following Hexagonal + DDD architecture
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import logging

from server.mcp.schemas import (
    SearchConceptsRequest, EmbedTextRequest, GetConceptRequest,
    ListTaxonomiesRequest, GetTaxonomyMetadataRequest, ClassifyTextRequest,
    ErrorResponse
)
from server.mcp.tools import mcp_tools
from server.mcp.resources import mcp_resources

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="SKOS MCP Server",
    description="Model Context Protocol server for SKOS taxonomy operations - Agent-oriented interface",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ===== MCP TOOLS ENDPOINTS =====

@app.post("/tools/search_taxonomy_concepts", 
          summary="Search taxonomy concepts",
          description="Search for SKOS concepts by text query. Returns relevant concepts with scores.")
async def tool_search_taxonomy_concepts(request: SearchConceptsRequest):
    """
    MCP Tool: search_taxonomy_concepts
    
    Find relevant taxonomy concepts matching a search query.
    Useful for exploring available categories and finding related concepts.
    """
    result = await mcp_tools.search_taxonomy_concepts(request)
    
    if isinstance(result, ErrorResponse):
        raise HTTPException(status_code=500, detail=result.dict())
    
    return result


@app.post("/tools/embed_text",
          summary="Generate text embedding",
          description="Convert text into vector embedding for semantic search.")
async def tool_embed_text(request: EmbedTextRequest):
    """
    MCP Tool: embed_text
    
    Generate embedding vector for text.
    Useful for semantic similarity comparison and vector search.
    """
    result = await mcp_tools.embed_text(request)
    
    if isinstance(result, ErrorResponse):
        raise HTTPException(status_code=500, detail=result.dict())
    
    return result


@app.post("/tools/get_taxonomy_concept",
          summary="Get concept details",
          description="Retrieve detailed information about a specific concept by URI or notation.")
async def tool_get_taxonomy_concept(request: GetConceptRequest):
    """
    MCP Tool: get_taxonomy_concept
    
    Get full details of a taxonomy concept.
    Useful for exploring concept hierarchies and relationships.
    """
    result = await mcp_tools.get_taxonomy_concept(request)
    
    if isinstance(result, ErrorResponse):
        raise HTTPException(status_code=404, detail=result.dict())
    
    return result


@app.post("/tools/list_taxonomies",
          summary="List available taxonomies",
          description="Get list of all available SKOS taxonomies in the system.")
async def tool_list_taxonomies(request: ListTaxonomiesRequest):
    """
    MCP Tool: list_taxonomies
    
    List available taxonomies in the system.
    Useful for discovering what taxonomies can be used.
    """
    result = await mcp_tools.list_taxonomies(request)
    
    if isinstance(result, ErrorResponse):
        raise HTTPException(status_code=500, detail=result.dict())
    
    return result


@app.post("/tools/get_taxonomy_metadata",
          summary="Get taxonomy metadata",
          description="Retrieve detailed metadata about a specific taxonomy.")
async def tool_get_taxonomy_metadata(request: GetTaxonomyMetadataRequest):
    """
    MCP Tool: get_taxonomy_metadata
    
    Get metadata for a specific taxonomy.
    Useful for understanding taxonomy characteristics and statistics.
    """
    result = await mcp_tools.get_taxonomy_metadata(request)
    
    if isinstance(result, ErrorResponse):
        raise HTTPException(status_code=404, detail=result.dict())
    
    return result


@app.post("/tools/classify_text",
          summary="Classify text",
          description="Classify text into taxonomy concepts using AI.")
async def tool_classify_text(request: ClassifyTextRequest):
    """
    MCP Tool: classify_text
    
    Classify text into taxonomy concepts.
    Useful for automatic product categorization and classification.
    """
    result = await mcp_tools.classify_text(request)
    
    if isinstance(result, ErrorResponse):
        raise HTTPException(status_code=500, detail=result.dict())
    
    return result


# ===== MCP RESOURCES ENDPOINTS =====

@app.get("/resources/taxonomy_schema",
         summary="Get SKOS schema",
         description="Get the official SKOS schema structure used in this project.")
async def resource_taxonomy_schema():
    """
    MCP Resource: taxonomy://schema
    
    SKOS taxonomy schema information.
    Static knowledge about SKOS concepts and structure.
    """
    return await mcp_resources.get_taxonomy_schema()


@app.get("/resources/active_taxonomies",
         summary="Get active taxonomies",
         description="Get list of currently active taxonomies with metadata.")
async def resource_active_taxonomies():
    """
    MCP Resource: taxonomy://active
    
    List of active taxonomies.
    Dynamic resource showing current system state.
    """
    return await mcp_resources.get_active_taxonomies()


@app.get("/resources/classification_policy",
         summary="Get classification policy",
         description="Get system rules, thresholds, and policies for classification.")
async def resource_classification_policy():
    """
    MCP Resource: taxonomy://classification-policy
    
    Classification rules and policies.
    Static configuration for understanding system behavior.
    """
    return await mcp_resources.get_classification_policy()


@app.get("/resources/project_overview",
         summary="Get project overview",
         description="Get system overview, capabilities, and usage guide.")
async def resource_project_overview():
    """
    MCP Resource: taxonomy://project
    
    Project overview and capabilities.
    Static knowledge about the system and how to use it.
    """
    return await mcp_resources.get_project_overview()


# ===== HEALTH AND INFO ENDPOINTS =====

@app.get("/health",
         summary="Health check",
         description="Check if the MCP server is operational.")
async def health_check():
    """
    Health check endpoint
    Returns server status and basic information
    """
    try:
        # Test basic functionality
        from server.domain.taxonomy_service import taxonomy_service
        taxonomies = taxonomy_service.list_taxonomies(active_only=True)
        
        return {
            "status": "healthy",
            "version": "2.0.0",
            "architecture": "hexagonal + DDD",
            "active_taxonomies": len(taxonomies),
            "tools_count": 6,
            "resources_count": 4,
            "message": "MCP server is operational"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "message": "MCP server has issues"
            }
        )


@app.get("/",
         summary="Server info",
         description="Get information about the MCP server.")
async def root():
    """
    Root endpoint - Server information
    """
    return {
        "name": "SKOS MCP Server",
        "version": "2.0.0",
        "description": "Model Context Protocol server for SKOS taxonomy operations",
        "architecture": {
            "pattern": "Hexagonal Architecture + Domain-Driven Design",
            "layers": ["MCP (entry)", "Domain (business logic)", "Adapters (infrastructure)"]
        },
        "tools": [
            "search_taxonomy_concepts",
            "embed_text",
            "get_taxonomy_concept",
            "list_taxonomies",
            "get_taxonomy_metadata",
            "classify_text"
        ],
        "resources": [
            "taxonomy://schema",
            "taxonomy://active",
            "taxonomy://classification-policy",
            "taxonomy://project"
        ],
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting SKOS MCP Server v2.0.0")
    logger.info("Architecture: Hexagonal + DDD")
    logger.info("Agent-oriented interface - No infrastructure exposure")
    
    uvicorn.run(app, host="0.0.0.0", port=8080)
