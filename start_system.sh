#!/bin/bash

# 🚀 Script de activación del Sistema SKOS Classifier
# ================================================

echo "🚀 ACTIVANDO SISTEMA SKOS CLASSIFIER"
echo "====================================="

# Cambiar al directorio del proyecto
cd "$(dirname "$0")"

# 1. Verificar entorno virtual
echo "📋 PASO 1: Verificando entorno virtual..."
if [ ! -d ".venv" ]; then
    echo "❌ Entorno virtual no encontrado. Ejecute: python -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi
echo "✅ Entorno virtual encontrado"

# 2. Activar entorno virtual
echo "📋 PASO 2: Activando entorno virtual..."
source .venv/bin/activate
echo "✅ Entorno virtual activado"

# 3. Verificar variables de entorno
echo "📋 PASO 3: Verificando variables de entorno..."
if [ ! -f ".env" ]; then
    echo "⚠️ Archivo .env no encontrado. Asegúrese de tener OPENAI_API_KEY configurada"
fi

# 4. Verificar base de datos
echo "📋 PASO 4: Verificando base de datos..."
if [ ! -f "skos.sqlite" ]; then
    echo "❌ Base de datos no encontrada. Regenerando..."
    python server/skos_loader.py taxonomies/treew-skos/original.jsonld
    if [ $? -eq 0 ]; then
        echo "✅ Base de datos regenerada"
    else
        echo "❌ Error regenerando base de datos"
        exit 1
    fi
else
    echo "✅ Base de datos encontrada"
fi

# 5. Limpiar procesos anteriores
echo "📋 PASO 5: Limpiando procesos anteriores..."
pkill -f "uvicorn.*server.main" 2>/dev/null
pkill -f "classification_api.py" 2>/dev/null
sleep 2
echo "✅ Procesos limpiados"

# 6. Iniciar MCP Server
echo "📋 PASO 6: Iniciando MCP Server (puerto 8080)..."
python -m uvicorn server.main:app --host 0.0.0.0 --port 8080 &
MCP_PID=$!
sleep 3

# Verificar que el MCP Server inició
if curl -s http://localhost:8080/docs > /dev/null 2>&1; then
    echo "✅ MCP Server iniciado correctamente (PID: $MCP_PID)"
else
    echo "❌ Error iniciando MCP Server"
    kill $MCP_PID 2>/dev/null
    exit 1
fi

# 7. Iniciar API REST
echo "📋 PASO 7: Iniciando API REST (puerto 8000)..."
python classification_api.py &
API_PID=$!
sleep 3

# Verificar que el API REST inició
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API REST iniciado correctamente (PID: $API_PID)"
else
    echo "❌ Error iniciando API REST"
    kill $API_PID 2>/dev/null
    kill $MCP_PID 2>/dev/null
    exit 1
fi

# 8. Prueba de conectividad
echo "📋 PASO 8: Probando conectividad..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ Sistema completamente operativo"
else
    echo "⚠️ Sistema iniciado pero con advertencias"
fi

# 9. Información final
echo ""
echo "🎉 ¡SISTEMA SKOS CLASSIFIER ACTIVADO!"
echo "====================================="
echo "📊 MCP Server:  http://localhost:8080"
echo "   - Documentación: http://localhost:8080/docs"
echo "🔗 API REST:    http://localhost:8000"
echo "   - Documentación: http://localhost:8000/docs"
echo "   - Health Check:  http://localhost:8000/health"
echo ""
echo "📝 PIDs de procesos:"
echo "   - MCP Server: $MCP_PID"
echo "   - API REST:   $API_PID"
echo ""
echo "🛑 Para detener el sistema:"
echo "   kill $MCP_PID $API_PID"
echo "   o ejecute: ./stop_system.sh"
echo ""
echo "🧪 Prueba rápida:"
echo "curl -X POST http://localhost:8000/classify \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"text\": \"leche\", \"product_id\": \"test\"}'"
echo ""

# Guardar PIDs para script de parada
echo "$MCP_PID" > .mcp_pid
echo "$API_PID" > .api_pid

echo "✅ Sistema listo para usar!"