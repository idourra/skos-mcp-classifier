#!/bin/bash
# ================================================================
# 🚀 SKOS MCP Classifier - Script de Inicio Optimizado v3.0
# ================================================================

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # Sin color

# Configuración
PROJECT_ROOT="/workspaces/skos-mcp-classifier"
VENV_PATH="$PROJECT_ROOT/venv"
CONFIG_FILE="$PROJECT_ROOT/config.yaml"
PID_DIR="$PROJECT_ROOT/.pids"
LOG_DIR="$PROJECT_ROOT/logs"

# Crear directorios necesarios
mkdir -p "$PID_DIR" "$LOG_DIR"

# Función para mostrar el banner
show_banner() {
    echo -e "${CYAN}"
    echo "  ╔══════════════════════════════════════════════════════════════════╗"
    echo "  ║                                                                  ║"
    echo "  ║        🌟 SKOS MCP CLASSIFIER - SISTEMA UNIFICADO v3.0 🌟        ║"
    echo "  ║                                                                  ║"
    echo "  ║    🔄 Arquitectura Unificada  │  🚀 API v2.x + v3.0             ║"
    echo "  ║    📊 Taxonomías SKOS        │  🤖 OpenAI GPT-4o-mini          ║"
    echo "  ║    🔗 MCP Integration        │  📁 Gestión de Archivos          ║"
    echo "  ║                                                                  ║"
    echo "  ╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Función para mostrar estado
log_status() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")  echo -e "${BLUE}[INFO]${NC}  ${timestamp} - $message" ;;
        "WARN")  echo -e "${YELLOW}[WARN]${NC}  ${timestamp} - $message" ;;
        "ERROR") echo -e "${RED}[ERROR]${NC} ${timestamp} - $message" ;;
        "SUCCESS") echo -e "${GREEN}[OK]${NC}    ${timestamp} - $message" ;;
        "STEP")  echo -e "${PURPLE}[STEP]${NC}  ${timestamp} - $message" ;;
    esac
}

# Función para verificar dependencias
check_dependencies() {
    log_status "STEP" "Verificando dependencias del sistema..."
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        log_status "ERROR" "Python3 no está instalado"
        exit 1
    fi
    
    # Verificar entorno virtual
    if [ ! -d "$VENV_PATH" ]; then
        log_status "WARN" "Entorno virtual no encontrado, creando..."
        python3 -m venv "$VENV_PATH"
    fi
    
    # Activar entorno virtual
    source "$VENV_PATH/bin/activate"
    log_status "SUCCESS" "Entorno virtual activado"
    
    # Verificar e instalar dependencias
    log_status "INFO" "Instalando/actualizando dependencias..."
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt 2>/dev/null || {
        log_status "WARN" "requirements.txt no encontrado, instalando dependencias básicas"
        pip install --quiet fastapi uvicorn openai pydantic sqlite3 rdflib python-dotenv pytest
    }
    
    log_status "SUCCESS" "Dependencias verificadas y actualizadas"
}

# Función para verificar base de datos
check_database() {
    log_status "STEP" "Verificando base de datos..."
    
    if [ ! -f "$PROJECT_ROOT/skos.sqlite" ]; then
        log_status "WARN" "Base de datos no encontrada, será creada automáticamente"
    else
        log_status "SUCCESS" "Base de datos encontrada"
    fi
}

# Función para iniciar servicios
start_services() {
    log_status "STEP" "Iniciando servicios del sistema..."
    
    # Configurar PYTHONPATH
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
    
    # Iniciar MCP Server
    log_status "INFO" "Iniciando MCP Server..."
    cd "$PROJECT_ROOT/server"
    nohup python main.py > "$LOG_DIR/mcp-server.log" 2>&1 &
    MCP_PID=$!
    echo $MCP_PID > "$PID_DIR/mcp-server.pid"
    log_status "SUCCESS" "MCP Server iniciado (PID: $MCP_PID) en puerto 8080"
    
    # Esperar un momento para que el MCP Server se inicie
    sleep 3
    
    # Iniciar API Principal
    log_status "INFO" "Iniciando API Principal..."
    cd "$PROJECT_ROOT"
    nohup python -m uvicorn unified_api:app --host 0.0.0.0 --port 8000 > "$LOG_DIR/main-api.log" 2>&1 &
    API_PID=$!
    echo $API_PID > "$PID_DIR/main-api.pid"
    log_status "SUCCESS" "API Principal iniciada (PID: $API_PID) en puerto 8000"
    
    # Esperar un momento más
    sleep 2
}

# Función para verificar estado de servicios
check_services() {
    log_status "STEP" "Verificando estado de servicios..."
    
    # Verificar MCP Server
    if [ -f "$PID_DIR/mcp-server.pid" ]; then
        MCP_PID=$(cat "$PID_DIR/mcp-server.pid")
        if ps -p $MCP_PID > /dev/null 2>&1; then
            log_status "SUCCESS" "MCP Server ejecutándose (PID: $MCP_PID)"
        else
            log_status "ERROR" "MCP Server no está ejecutándose"
        fi
    fi
    
    # Verificar API Principal
    if [ -f "$PID_DIR/main-api.pid" ]; then
        API_PID=$(cat "$PID_DIR/main-api.pid")
        if ps -p $API_PID > /dev/null 2>&1; then
            log_status "SUCCESS" "API Principal ejecutándose (PID: $API_PID)"
        else
            log_status "ERROR" "API Principal no está ejecutándose"
        fi
    fi
    
    # Verificar conectividad
    sleep 5
    log_status "INFO" "Probando conectividad de servicios..."
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        log_status "SUCCESS" "API Principal responde correctamente"
    else
        log_status "WARN" "API Principal no responde en /health"
    fi
}

# Función para mostrar información del sistema
show_system_info() {
    echo -e "\n${WHITE}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}                        🖥️  INFORMACIÓN DEL SISTEMA${NC}"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}📂 Directorio de trabajo:${NC} $PROJECT_ROOT"
    echo -e "${CYAN}🐍 Entorno virtual:${NC}     $VENV_PATH"
    echo -e "${CYAN}📄 Archivo de config:${NC}   $CONFIG_FILE"
    echo -e "${CYAN}📝 Directorio de logs:${NC}  $LOG_DIR"
    echo -e "${CYAN}🆔 Directorio de PIDs:${NC}  $PID_DIR"
    echo ""
    echo -e "${WHITE}🌐 ENDPOINTS DISPONIBLES:${NC}"
    echo -e "${GREEN}   • API Principal:${NC}      http://localhost:8000"
    echo -e "${GREEN}   • Documentación:${NC}     http://localhost:8000/docs"
    echo -e "${GREEN}   • Health Check:${NC}      http://localhost:8000/health"
    echo -e "${GREEN}   • MCP Server:${NC}        http://localhost:8080"
    echo ""
    echo -e "${WHITE}🔧 COMANDOS ÚTILES:${NC}"
    echo -e "${YELLOW}   • Parar sistema:${NC}     ./stop_system.sh"
    echo -e "${YELLOW}   • Ver logs API:${NC}      tail -f logs/main-api.log"
    echo -e "${YELLOW}   • Ver logs MCP:${NC}      tail -f logs/mcp-server.log"
    echo -e "${YELLOW}   • Reiniciar:${NC}         ./start_system.sh"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════════════${NC}\n"
}

# Función principal
main() {
    show_banner
    
    # Cambiar al directorio del proyecto
    cd "$PROJECT_ROOT"
    
    # Verificar si ya hay servicios ejecutándose
    if pgrep -f "uvicorn.*unified_api" > /dev/null 2>&1; then
        log_status "WARN" "Sistema ya está ejecutándose. Use stop_system.sh para detenerlo primero."
        exit 1
    fi
    
    # Ejecutar pasos de inicialización
    check_dependencies
    check_database
    start_services
    check_services
    show_system_info
    
    log_status "SUCCESS" "🎉 Sistema SKOS MCP Classifier iniciado correctamente"
    log_status "INFO" "El sistema está listo para recibir solicitudes de clasificación"
}

# Capturar señales para limpieza
trap 'log_status "INFO" "Señal de interrupción recibida, use stop_system.sh para detener correctamente"' INT TERM

# Ejecutar función principal
main "$@"