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
        echo -e "${RED}❌ .env.example not found${NC}"
        echo "Please create a .env file with required variables"
        exit 1
    fi
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

# Check Qdrant
if curl -s http://localhost:6333/ > /dev/null; then
    echo -e "${GREEN}✅ Qdrant is running${NC}"
else
    echo -e "${YELLOW}⚠️  Qdrant is not responding yet...${NC}"
fi

# Check LangGraph Classifier
if curl -s http://localhost:8001/health > /dev/null; then
    echo -e "${GREEN}✅ LangGraph Classifier is running${NC}"
else
    echo -e "${YELLOW}⚠️  LangGraph Classifier is starting...${NC}"
fi

echo ""
echo "=========================================="
echo "Services Available:"
echo "=========================================="
echo ""
echo -e "🔵 Qdrant Vector DB:"
echo "   URL: http://localhost:6333"
echo "   Dashboard: http://localhost:6333/dashboard"
echo ""
echo -e "🤖 LangGraph Classifier API:"
echo "   URL: http://localhost:8001"
echo "   Docs: http://localhost:8001/docs"
echo "   Health: http://localhost:8001/health"
echo ""
echo "=========================================="
echo "Quick Test:"
echo "=========================================="
echo ""
echo "curl -X POST http://localhost:8001/classify \\"
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
