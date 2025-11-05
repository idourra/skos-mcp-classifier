#!/bin/bash
# Startup script for LangGraph Multi-Agent SKOS Classifier

set -e

echo "=========================================="
echo "LangGraph Multi-Agent SKOS Classifier"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose is not installed${NC}"
    echo "Please install docker-compose first"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    if [ -f .env.example ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo -e "${GREEN}✅ .env file created${NC}"
        echo -e "${YELLOW}⚠️  Please edit .env and add your configuration${NC}"
    else
        echo -e "${YELLOW}⚠️  .env.example not found, creating minimal .env${NC}"
        echo "# LangGraph Classifier Environment Variables" > .env
        echo "QDRANT_URL=http://qdrant:6333" >> .env
        echo "QDRANT_COLLECTION=concepts" >> .env
        echo -e "${GREEN}✅ Minimal .env file created${NC}"
    fi
fi

# Check if config file exists, warn if missing (non-fatal)
if [ ! -f langgraph_config.yaml ]; then
    echo -e "${YELLOW}⚠️  langgraph_config.yaml not found${NC}"
    echo "   Container will use default configuration and environment variables"
    echo "   To customize, create langgraph_config.yaml in this directory"
fi

echo -e "${GREEN}🚀 Starting services...${NC}"
echo ""

# Start services
docker-compose -f docker-compose.langgraph.yml up -d

echo ""
echo -e "${GREEN}✅ Services started!${NC}"
echo ""

# Wait for services to be healthy
echo "Waiting for services to be healthy..."
sleep 5

# Get configured ports from environment or use defaults
QDRANT_PORT="${QDRANT_PORT:-6333}"
API_PORT="${API_PORT:-8001}"

# Check Qdrant with timeout and status code validation
if curl -sf --max-time 5 "http://localhost:${QDRANT_PORT}/" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Qdrant is running${NC}"
else
    echo -e "${YELLOW}⚠️  Qdrant is not responding yet...${NC}"
fi

# Check LangGraph Classifier with timeout and health check validation
if curl -sf --max-time 5 "http://localhost:${API_PORT}/health" > /dev/null 2>&1; then
    HEALTH_STATUS=$(curl -s "http://localhost:${API_PORT}/health" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    if [ "$HEALTH_STATUS" = "healthy" ]; then
        echo -e "${GREEN}✅ LangGraph Classifier is running and healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  LangGraph Classifier status: ${HEALTH_STATUS}${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  LangGraph Classifier is starting...${NC}"
fi

echo ""
echo "=========================================="
echo "Services Available:"
echo "=========================================="
echo ""
echo -e "🔵 Qdrant Vector DB:"
echo "   URL: http://localhost:${QDRANT_PORT}"
echo "   Dashboard: http://localhost:${QDRANT_PORT}/dashboard"
echo ""
echo -e "🤖 LangGraph Classifier API:"
echo "   URL: http://localhost:${API_PORT}"
echo "   Docs: http://localhost:${API_PORT}/docs"
echo "   Health: http://localhost:${API_PORT}/health"
echo ""
echo "=========================================="
echo "Quick Test:"
echo "=========================================="
echo ""
echo "curl -X POST http://localhost:${API_PORT}/classify \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"text\": \"yogur griego natural\","
echo "    \"scheme_uri\": \"https://treew.io/taxonomy/\","
echo "    \"lang\": \"es\""
echo "  }'"
echo ""
echo "=========================================="
echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "To stop services: ./stop_langgraph.sh"
echo "To view logs: docker-compose -f docker-compose.langgraph.yml logs -f"
echo ""
