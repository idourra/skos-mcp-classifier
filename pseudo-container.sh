#!/bin/bash
# 📦 Pseudo-Containerización sin Docker
# Simula un entorno containerizado usando venv y systemd

echo "📦 PSEUDO-CONTAINER SETUP - SKOS MCP Classifier"
echo "=============================================="

# Crear entorno aislado
create_isolated_env() {
    echo "🏗️ Creando entorno pseudo-containerizado..."
    
    # Crear directorio aislado
    mkdir -p ~/.local/containers/skos-classifier
    cd ~/.local/containers/skos-classifier
    
    # Copiar archivos necesarios
    cp -r /home/urra/projects/skos-mcp-classifier/* .
    
    # Crear entorno virtual aislado
    python3 -m venv container-env
    source container-env/bin/activate
    
    # Instalar dependencias
    pip install -r server/requirements.txt
    
    # Configurar variables
    cp .env.example .env 2>/dev/null || true
    echo "OPENAI_API_KEY=${OPENAI_API_KEY}" > .env
    echo "PORT=8000" >> .env
    
    # Inicializar base de datos
    python server/skos_loader.py
    cp skos.sqlite server/
    
    echo "✅ Entorno pseudo-containerizado creado"
}

# Ejecutar como servicio
run_as_service() {
    echo "🚀 Iniciando servicio pseudo-containerizado..."
    
    cd ~/.local/containers/skos-classifier
    source container-env/bin/activate
    
    # Ejecutar en background con logging
    nohup python server/main.py > service.log 2>&1 &
    echo $! > service.pid
    
    echo "✅ Servicio iniciado (PID: $(cat service.pid))"
    echo "🌐 API: http://localhost:8000"
    echo "📄 Logs: ~/.local/containers/skos-classifier/service.log"
}

# Detener servicio
stop_service() {
    if [ -f ~/.local/containers/skos-classifier/service.pid ]; then
        PID=$(cat ~/.local/containers/skos-classifier/service.pid)
        kill $PID 2>/dev/null && echo "✅ Servicio detenido" || echo "❌ Servicio ya detenido"
        rm -f ~/.local/containers/skos-classifier/service.pid
    fi
}

# Estado del servicio
service_status() {
    if [ -f ~/.local/containers/skos-classifier/service.pid ]; then
        PID=$(cat ~/.local/containers/skos-classifier/service.pid)
        if ps -p $PID > /dev/null 2>&1; then
            echo "✅ Servicio ejecutándose (PID: $PID)"
            echo "📊 Uso de recursos:"
            ps -p $PID -o pid,%cpu,%mem,rss,comm --no-headers
            echo "📋 Últimos logs:"
            tail -5 ~/.local/containers/skos-classifier/service.log
        else
            echo "❌ Servicio no está ejecutándose"
        fi
    else
        echo "❌ Servicio no iniciado"
    fi
}

case ${1:-help} in
    "create")
        create_isolated_env
        ;;
    "start")
        run_as_service
        ;;
    "stop")
        stop_service
        ;;
    "status")
        service_status
        ;;
    "restart")
        stop_service
        sleep 2
        run_as_service
        ;;
    *)
        echo "Uso: $0 {create|start|stop|status|restart}"
        echo ""
        echo "  create  - Crear entorno pseudo-containerizado"
        echo "  start   - Iniciar servicio"
        echo "  stop    - Detener servicio"
        echo "  status  - Ver estado del servicio"
        echo "  restart - Reiniciar servicio"
        ;;
esac