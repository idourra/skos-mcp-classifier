#!/bin/bash

# 🛑 Script para detener el Sistema SKOS Classifier
# ===============================================

echo "🛑 DETENIENDO SISTEMA SKOS CLASSIFIER"
echo "===================================="

# Leer PIDs si existen
if [ -f ".mcp_pid" ] && [ -f ".api_pid" ]; then
    MCP_PID=$(cat .mcp_pid)
    API_PID=$(cat .api_pid)
    
    echo "📋 Deteniendo procesos guardados..."
    echo "   - MCP Server PID: $MCP_PID"
    echo "   - API REST PID:   $API_PID"
    
    # Detener procesos
    kill $MCP_PID 2>/dev/null && echo "✅ MCP Server detenido" || echo "⚠️ MCP Server ya estaba detenido"
    kill $API_PID 2>/dev/null && echo "✅ API REST detenido" || echo "⚠️ API REST ya estaba detenido"
    
    # Limpiar archivos de PID
    rm -f .mcp_pid .api_pid
else
    echo "📋 No se encontraron PIDs guardados. Buscando procesos..."
fi

# Limpiar cualquier proceso restante
echo "🧹 Limpiando procesos restantes..."
pkill -f "uvicorn.*server.main" 2>/dev/null && echo "✅ Procesos MCP Server limpiados"
pkill -f "classification_api.py" 2>/dev/null && echo "✅ Procesos API REST limpiados"

# Verificar que los puertos están libres
sleep 2
if ! lsof -i:8080 > /dev/null 2>&1; then
    echo "✅ Puerto 8080 (MCP Server) liberado"
else
    echo "⚠️ Puerto 8080 aún ocupado"
fi

if ! lsof -i:8000 > /dev/null 2>&1; then
    echo "✅ Puerto 8000 (API REST) liberado"
else
    echo "⚠️ Puerto 8000 aún ocupado"
fi

echo ""
echo "🎯 SISTEMA DETENIDO COMPLETAMENTE"
echo "==============================="
echo "Para reactivar el sistema ejecute: ./start_system.sh"
echo ""