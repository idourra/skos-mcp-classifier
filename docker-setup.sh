#!/bin/bash
# 🐳 Script de Instalación y Uso de Docker - SKOS MCP Classifier

echo "🐳 Docker Setup para SKOS MCP Classifier"
echo "========================================"

# Función para instalar Docker
install_docker() {
    echo "📦 Instalando Docker..."
    
    # Actualizar repositorios
    sudo apt update
    
    # Instalar Docker
    sudo apt install -y docker.io docker-compose
    
    # Agregar usuario al grupo docker
    sudo usermod -aG docker $USER
    
    # Iniciar servicio
    sudo systemctl start docker
    sudo systemctl enable docker
    
    echo "✅ Docker instalado. Reinicia la sesión para usar sin sudo"
}

# Función para construir imagen
build_image() {
    echo "🏗️ Construyendo imagen Docker..."
    
    docker build -t skos-mcp-classifier:latest .
    
    echo "✅ Imagen construida: skos-mcp-classifier:latest"
}

# Función para ejecutar con Docker
run_docker() {
    echo "🚀 Ejecutando con Docker..."
    
    # Parar contenedor existente si existe
    docker stop skos-classifier 2>/dev/null || true
    docker rm skos-classifier 2>/dev/null || true
    
    # Ejecutar nuevo contenedor
    docker run -d \
        --name skos-classifier \
        -p 8000:8000 \
        --env-file .env \
        --restart unless-stopped \
        skos-mcp-classifier:latest
    
    echo "✅ Contenedor iniciado en puerto 8000"
    echo "🌐 API: http://localhost:8000"
    echo "📚 Docs: http://localhost:8000/docs"
}

# Función para usar Docker Compose
run_compose() {
    echo "🎼 Ejecutando con Docker Compose..."
    
    # Parar servicios existentes
    docker-compose down
    
    # Construir y ejecutar
    docker-compose up -d --build
    
    echo "✅ Servicios iniciados con Docker Compose"
    echo "🌐 API: http://localhost:8000"
}

# Función para monitorear
monitor_docker() {
    echo "📊 Estado de los contenedores:"
    docker ps | grep skos
    
    echo -e "\n📈 Recursos utilizados:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep skos
    
    echo -e "\n📋 Logs recientes:"
    docker logs --tail 20 skos-classifier 2>/dev/null || echo "No logs disponibles"
}

# Función para limpiar
cleanup_docker() {
    echo "🧹 Limpiando contenedores Docker..."
    
    docker stop skos-classifier 2>/dev/null || true
    docker rm skos-classifier 2>/dev/null || true
    docker-compose down 2>/dev/null || true
    
    echo "✅ Limpieza completada"
}

# Menú principal
case ${1:-help} in
    "install")
        install_docker
        ;;
    "build")
        build_image
        ;;
    "run")
        run_docker
        ;;
    "compose")
        run_compose
        ;;
    "status")
        monitor_docker
        ;;
    "clean")
        cleanup_docker
        ;;
    "help"|*)
        echo "Uso: $0 [COMANDO]"
        echo ""
        echo "Comandos disponibles:"
        echo "  install  - Instalar Docker y Docker Compose"
        echo "  build    - Construir imagen Docker"
        echo "  run      - Ejecutar contenedor simple"
        echo "  compose  - Usar Docker Compose (recomendado)"
        echo "  status   - Ver estado y recursos"
        echo "  clean    - Limpiar contenedores"
        echo "  help     - Mostrar esta ayuda"
        echo ""
        echo "Ejemplo de uso completo:"
        echo "  ./docker-setup.sh install   # Solo la primera vez"
        echo "  ./docker-setup.sh compose   # Iniciar aplicación"
        echo "  ./docker-setup.sh status    # Ver estado"
        ;;
esac