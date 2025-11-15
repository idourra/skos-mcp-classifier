"""
MCP Resources implementation
Exposes static knowledge and configuration as MCP resources
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from server.mcp.schemas import ResourceResponse
from server.config.schema import get_taxonomy_schema
from server.config.policies import get_classification_policy
from server.domain.taxonomy_service import taxonomy_service


class MCPResources:
    """MCP Resources - Static knowledge for LLM agents"""
    
    def __init__(self):
        self.taxonomy_service = taxonomy_service
    
    async def get_taxonomy_schema(self) -> ResourceResponse:
        """
        Get SKOS taxonomy schema information
        
        Resource: taxonomy://schema
        Purpose: Provide agents with understanding of SKOS structure
        """
        schema = get_taxonomy_schema()
        
        return ResourceResponse(
            uri="taxonomy://schema",
            name="SKOS Taxonomy Schema",
            description="Official SKOS schema structure used in this project",
            mimeType="application/json",
            content=schema
        )
    
    async def get_active_taxonomies(self) -> ResourceResponse:
        """
        Get list of active taxonomies
        
        Resource: taxonomy://active
        Purpose: Inform agents about available taxonomies
        """
        taxonomies = self.taxonomy_service.list_taxonomies(active_only=True)
        
        # Convert to simple dict format
        taxonomies_list = []
        default_taxonomy = None
        
        for tax_id, metadata in taxonomies.items():
            tax_dict = metadata.to_dict()
            taxonomies_list.append(tax_dict)
            if metadata.is_default:
                default_taxonomy = tax_id
        
        content = {
            "taxonomies": taxonomies_list,
            "total_active": len(taxonomies_list),
            "default_taxonomy": default_taxonomy
        }
        
        return ResourceResponse(
            uri="taxonomy://active",
            name="Active Taxonomies",
            description="List of currently active SKOS taxonomies in the system",
            mimeType="application/json",
            content=content
        )
    
    async def get_classification_policy(self) -> ResourceResponse:
        """
        Get classification rules and policies
        
        Resource: taxonomy://classification-policy
        Purpose: Inform agents about classification thresholds and rules
        """
        policy = get_classification_policy()
        
        return ResourceResponse(
            uri="taxonomy://classification-policy",
            name="Classification Policy",
            description="System rules, thresholds, and policies for classification",
            mimeType="application/json",
            content=policy
        )
    
    async def get_project_overview(self) -> ResourceResponse:
        """
        Get project overview and capabilities
        
        Resource: taxonomy://project
        Purpose: Help agents understand the system and how to use it
        """
        overview = {
            "name": "SKOS MCP Classifier",
            "version": "2.0",
            "description": "Intelligent product classification system using SKOS taxonomies and AI",
            "capabilities": [
                "Semantic search in SKOS taxonomies",
                "Intelligent text classification with AI",
                "Multi-taxonomy support",
                "Text embedding generation",
                "Concept hierarchy navigation"
            ],
            "usage_guide": {
                "search_concepts": {
                    "tool": "search_taxonomy_concepts",
                    "purpose": "Find relevant taxonomy concepts by text query",
                    "example": "search for 'yogurt' to find related concepts"
                },
                "classify_products": {
                    "tool": "classify_text",
                    "purpose": "Automatically classify product descriptions",
                    "example": "classify 'yogur griego natural' to get taxonomy category"
                },
                "get_concept_details": {
                    "tool": "get_taxonomy_concept",
                    "purpose": "Get full information about a specific concept",
                    "example": "get details for concept URI or notation code"
                },
                "list_available_taxonomies": {
                    "tool": "list_taxonomies",
                    "purpose": "See what taxonomies are available",
                    "example": "list all active taxonomies in the system"
                },
                "generate_embeddings": {
                    "tool": "embed_text",
                    "purpose": "Convert text to vector representation",
                    "example": "embed text for semantic similarity comparison"
                }
            },
            "best_practices": [
                "Use classify_text for end-to-end product classification",
                "Use search_taxonomy_concepts to explore available categories",
                "Check active_taxonomies resource to see available taxonomies",
                "Review classification_policy resource to understand confidence thresholds",
                "Use get_taxonomy_concept to navigate concept hierarchies"
            ],
            "architecture": {
                "design": "Hexagonal Architecture + Domain-Driven Design",
                "layers": {
                    "mcp": "Entry point for LLM agents (this interface)",
                    "domain": "Business logic and services",
                    "adapters": "Infrastructure and external integrations"
                },
                "principle": "No infrastructure exposure - only high-level capabilities"
            }
        }
        
        return ResourceResponse(
            uri="taxonomy://project",
            name="Project Overview",
            description="System overview, capabilities, and usage guide",
            mimeType="application/json",
            content=overview
        )


# Global instance
mcp_resources = MCPResources()
