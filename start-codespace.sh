#!/bin/bash
# 🚀 Codespace Startup Script - SKOS MCP Classifier

echo "🌐 Starting SKOS MCP Classifier in GitHub Codespaces..."
echo "======================================================"

# Activar entorno virtual
echo "🐍 Activating Python virtual environment..."
source .venv/bin/activate

# Verificar que las dependencias están instaladas
echo "📦 Checking dependencies..."
if [ ! -f ".venv/bin/uvicorn" ]; then
    echo "Installing dependencies..."
    pip install -r server/requirements.txt
fi

# Verificar que la base de datos existe
echo "🗄️  Checking database..."
if [ ! -f "server/skos.sqlite" ]; then
    echo "Initializing database..."
    python server/skos_loader.py
    cp skos.sqlite server/
fi

# Configurar variables de entorno si no existen
if [ ! -f ".env" ]; then
    echo "⚙️  Setting up environment..."
    echo "OPENAI_API_KEY=${OPENAI_API_KEY}" > .env
    echo "MCP_SERVER_URL=http://localhost:8080" >> .env
    echo "PORT=8000" >> .env
fi

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the server, run:"
echo "   cd server && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "📚 Or use the deployment script:"
echo "   ./deploy.sh local"
echo ""
echo "🌐 Your app will be available at:"
echo "   - API: https://[codespace-url]:8000"
echo "   - Docs: https://[codespace-url]:8000/docs"