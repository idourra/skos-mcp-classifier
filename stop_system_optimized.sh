#!/bin/bash
# ================================================================
# 🛑 SKOS MCP Classifier - Script de Parada Optimizado v3.0
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
PID_DIR="$PROJECT_ROOT/.pids"
LOG_DIR="$PROJECT_ROOT/logs"

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

# Función para mostrar banner de parada
show_stop_banner() {
    echo -e "${RED}"
    echo "  ╔══════════════════════════════════════════════════════════════════╗"
    echo "  ║                                                                  ║"
    echo "  ║           🛑 DETENIENDO SKOS MCP CLASSIFIER v3.0 🛑              ║"
    echo "  ║                                                                  ║"
    echo "  ╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Función para detener un servicio por PID
stop_service() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            log_status "INFO" "Deteniendo $service_name (PID: $pid)..."
            kill $pid
            
            # Esperar hasta 10 segundos para que el proceso termine
            local count=0
            while ps -p $pid > /dev/null 2>&1 && [ $count -lt 10 ]; do
                sleep 1
                ((count++))
            done
            
            if ps -p $pid > /dev/null 2>&1; then
                log_status "WARN" "Forzando detención de $service_name..."
                kill -9 $pid
                sleep 2
            fi
            
            if ! ps -p $pid > /dev/null 2>&1; then
                log_status "SUCCESS" "$service_name detenido correctamente"
                rm -f "$pid_file"
            else
                log_status "ERROR" "No se pudo detener $service_name"
            fi
        else
            log_status "WARN" "$service_name no estaba ejecutándose (PID inválido)"
            rm -f "$pid_file"
        fi
    else
        log_status "INFO" "No se encontró archivo PID para $service_name"
    fi
}

# Función para detener procesos por nombre
stop_by_name() {
    local process_pattern=$1
    local service_name=$2
    
    local pids=$(pgrep -f "$process_pattern")
    if [ ! -z "$pids" ]; then
        log_status "INFO" "Deteniendo procesos $service_name encontrados..."
        echo "$pids" | while read pid; do
            if ps -p $pid > /dev/null 2>&1; then
                log_status "INFO" "Deteniendo proceso $service_name (PID: $pid)..."
                kill $pid
            fi
        done
        sleep 3
        
        # Verificar si aún hay procesos
        local remaining_pids=$(pgrep -f "$process_pattern")
        if [ ! -z "$remaining_pids" ]; then
            log_status "WARN" "Forzando detención de procesos $service_name restantes..."
            echo "$remaining_pids" | while read pid; do
                kill -9 $pid
            done
        fi
        
        log_status "SUCCESS" "Procesos $service_name detenidos"
    else
        log_status "INFO" "No se encontraron procesos $service_name ejecutándose"
    fi
}

# Función para limpiar recursos
cleanup_resources() {
    log_status "STEP" "Limpiando recursos del sistema..."
    
    # Limpiar archivos PID obsoletos
    if [ -d "$PID_DIR" ]; then
        for pid_file in "$PID_DIR"/*.pid; do
            if [ -f "$pid_file" ]; then
                local pid=$(cat "$pid_file" 2>/dev/null)
                if [ ! -z "$pid" ] && ! ps -p $pid > /dev/null 2>&1; then
                    log_status "INFO" "Eliminando archivo PID obsoleto: $(basename "$pid_file")"
                    rm -f "$pid_file"
                fi
            fi
        done
    fi
    
    # Limpiar archivos temporales
    if [ -d "$PROJECT_ROOT/files/temp" ]; then
        find "$PROJECT_ROOT/files/temp" -type f -mtime +1 -delete 2>/dev/null
        log_status "INFO" "Archivos temporales antiguos eliminados"
    fi
    
    log_status "SUCCESS" "Limpieza de recursos completada"
}

# Función para mostrar estado final
show_final_status() {
    echo -e "\n${WHITE}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}                        📊 ESTADO FINAL DEL SISTEMA${NC}"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════════════${NC}"
    
    # Verificar que no hay procesos ejecutándose
    local api_processes=$(pgrep -f "uvicorn.*unified_api" | wc -l)
    local mcp_processes=$(pgrep -f "python.*server/main.py" | wc -l)
    
    if [ $api_processes -eq 0 ] && [ $mcp_processes -eq 0 ]; then
        echo -e "${GREEN}✅ Todos los servicios han sido detenidos correctamente${NC}"
    else
        echo -e "${RED}⚠️  Algunos servicios pueden seguir ejecutándose:${NC}"
        [ $api_processes -gt 0 ] && echo -e "${YELLOW}   • API Principal: $api_processes procesos${NC}"
        [ $mcp_processes -gt 0 ] && echo -e "${YELLOW}   • MCP Server: $mcp_processes procesos${NC}"
    fi
    
    echo -e "\n${CYAN}📝 Logs disponibles en:${NC} $LOG_DIR"
    echo -e "${CYAN}🔄 Para reiniciar:${NC} ./start_system_optimized.sh"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════════════${NC}\n"
}

# Función principal
main() {
    show_stop_banner
    
    cd "$PROJECT_ROOT"
    
    log_status "STEP" "Iniciando proceso de detención del sistema..."
    
    # Detener servicios por archivos PID
    stop_service "API Principal" "$PID_DIR/main-api.pid"
    stop_service "MCP Server" "$PID_DIR/mcp-server.pid"
    
    # Detener cualquier proceso restante por nombre
    stop_by_name "uvicorn.*unified_api" "API Principal"
    stop_by_name "uvicorn.*classification_api" "API Clasificación"
    stop_by_name "python.*server/main.py" "MCP Server"
    
    # Limpiar recursos
    cleanup_resources
    
    # Mostrar estado final
    show_final_status
    
    log_status "SUCCESS" "🏁 Sistema SKOS MCP Classifier detenido correctamente"
}

# Ejecutar función principal
main "$@"