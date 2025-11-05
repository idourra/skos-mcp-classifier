#!/bin/bash
# Stop script for LangGraph Multi-Agent SKOS Classifier

set -e

echo "=========================================="
echo "Stopping LangGraph Multi-Agent Classifier"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Stop services
echo -e "${YELLOW}🛑 Stopping services...${NC}"
docker-compose -f docker-compose.langgraph.yml down

echo ""
echo -e "${GREEN}✅ All services stopped${NC}"
echo ""
echo "To remove volumes: docker-compose -f docker-compose.langgraph.yml down -v"
echo ""
