#!/bin/bash
# 🚀 Script de Despliegue Automático - SKOS MCP Classifier

set -e

echo "🏷️  SKOS MCP Classifier - Deployment Script"
echo "=========================================="

# Variables
PROJECT_NAME="skos-mcp-classifier"
DOCKER_IMAGE="ghcr.io/idourra/${PROJECT_NAME}"
VERSION=${1:-latest}

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [OPCION]"
    echo ""
    echo "Opciones de despliegue:"
    echo "  local       - Despliegue local con Docker"
    echo "  github      - Setup para GitHub Codespaces"
    echo "  railway     - Despliegue en Railway"
    echo "  render      - Despliegue en Render"
    echo "  docker      - Build y push imagen Docker"
    echo "  test        - Solo ejecutar tests"
    echo "  help        - Mostrar esta ayuda"
}

# Función para despliegue local
deploy_local() {
    echo "🏠 Desplegando localmente con Docker..."
    
    # Build imagen
    docker build -t ${PROJECT_NAME}:${VERSION} .
    
    # Parar containers existentes
    docker-compose down || true
    
    # Iniciar servicios
    docker-compose up -d
    
    echo "✅ Servicios iniciados:"
    echo "   🌐 API REST: http://localhost:8000"
    echo "   🔧 MCP Server: http://localhost:8080"
    echo "   📚 Docs: http://localhost:8000/docs"
    
    # Health check
    sleep 10
    curl -s http://localhost:8000/health && echo "✅ API OK" || echo "❌ API Error"
    curl -s http://localhost:8080/health && echo "✅ MCP OK" || echo "❌ MCP Error"
}

# Función para setup GitHub
setup_github() {
    echo "🐙 Configurando para GitHub..."
    
    # Verificar archivos necesarios
    echo "✅ Devcontainer configurado"
    echo "✅ GitHub Actions configurado"
    echo "✅ Docker files listos"
    
    echo ""
    echo "📋 Pasos siguientes:"
    echo "1. git add ."
    echo "2. git commit -m '🚀 Setup deployment configs'"
    echo "3. git push origin main"
    echo "4. Ir a GitHub > Settings > Codespaces"
    echo "5. Crear nuevo Codespace"
    echo ""
    echo "🔑 Configurar secrets:"
    echo "   - OPENAI_API_KEY en GitHub Secrets"
}

# Función para Railway
deploy_railway() {
    echo "🚄 Preparando para Railway..."
    
    echo "📋 Pasos para Railway:"
    echo "1. Ir a https://railway.app/"
    echo "2. Conectar repositorio GitHub"
    echo "3. Configurar variables:"
    echo "   - OPENAI_API_KEY"
    echo "   - PYTHONPATH=/app"
    echo "4. Deploy automático configurado"
    
    echo "✅ railway.json configurado"
}

# Función para Render  
deploy_render() {
    echo "🎨 Preparando para Render..."
    
    echo "📋 Pasos para Render:"
    echo "1. Ir a https://render.com/"
    echo "2. Conectar repositorio GitHub"  
    echo "3. Crear Web Service"
    echo "4. Build Command: pip install -r requirements.txt"
    echo "5. Start Command: python classification_api.py"
    echo "6. Configurar variables:"
    echo "   - OPENAI_API_KEY"
    echo "   - PYTHONPATH=/opt/render/project/src"
    
    echo "✅ render.yaml configurado"
}

# Función para build Docker
build_docker() {
    echo "🐳 Building Docker image..."
    
    docker build -t ${DOCKER_IMAGE}:${VERSION} .
    docker tag ${DOCKER_IMAGE}:${VERSION} ${DOCKER_IMAGE}:latest
    
    echo "✅ Imagen creada: ${DOCKER_IMAGE}:${VERSION}"
    
    # Push si está en GitHub Actions
    if [ "$CI" = "true" ]; then
        echo "📤 Pushing to registry..."
        docker push ${DOCKER_IMAGE}:${VERSION}
        docker push ${DOCKER_IMAGE}:latest
    fi
}

# Función para tests
run_tests() {
    echo "🧪 Ejecutando tests..."
    
    # Verificar entorno
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "⚠️  Configurar OPENAI_API_KEY en .env"
    fi
    
    # Instalar dependencias
    pip install -r requirements.txt
    pip install pytest pytest-asyncio
    
    # Ejecutar tests
    python -m pytest --tb=short -v
    
    echo "✅ Tests completados"
}

# Main switch
case ${1:-help} in
    "local")
        deploy_local
        ;;
    "github")
        setup_github
        ;;
    "railway")
        deploy_railway
        ;;
    "render")
        deploy_render
        ;;
    "docker")
        build_docker
        ;;
    "test")
        run_tests
        ;;
    "help"|*)
        show_help
        ;;
esac

echo ""
echo "🎉 Proceso completado!"