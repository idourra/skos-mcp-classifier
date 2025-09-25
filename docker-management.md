# 🐳 Docker Management Guide - SKOS MCP Classifier

## 🚀 Quick Start

### Ejecutar el contenedor:
```bash
cd /home/urra/projects/skos-mcp-classifier
sudo docker run -d \
  --name skos-classifier-$(date +%s) \
  -p 8000:8000 \
  --restart unless-stopped \
  --health-cmd="curl -f http://localhost:8000/health || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  skos-mcp-classifier:latest
```

## 📊 Monitoreo

### Ver estado del contenedor:
```bash
sudo docker ps | grep skos
```

### Logs en tiempo real:
```bash
sudo docker logs -f <CONTAINER_NAME>
```

### Health check status:
```bash
sudo docker inspect <CONTAINER_NAME> | grep -A 5 Health
```

## 🔧 Gestión Básica

### Detener contenedor:
```bash
sudo docker stop <CONTAINER_NAME>
```

### Reiniciar contenedor:
```bash
sudo docker restart <CONTAINER_NAME>
```

### Eliminar contenedor:
```bash
sudo docker rm <CONTAINER_NAME>
```

## 🌐 Endpoints Disponibles

- **Base URL:** `http://localhost:8000`
- **API Docs:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`
- **Search Concepts:** `POST http://localhost:8000/tools/search_concepts`
- **Get Context:** `POST http://localhost:8000/tools/get_context`

## 🧪 Testing de la API

### Test básico:
```bash
curl http://localhost:8000/health
```

### Test de búsqueda:
```bash
curl -X POST "http://localhost:8000/tools/search_concepts" \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"query": "beef", "limit": 5}}'
```

## 📦 Deployment en Producción

### Docker Compose (recomendado):
```bash
docker-compose up -d
```

### Con variables de entorno:
```bash
sudo docker run -d \
  --name skos-classifier \
  -p 8000:8000 \
  -e LOG_LEVEL=info \
  -e WORKERS=4 \
  --restart unless-stopped \
  skos-mcp-classifier:latest
```

## 🚨 Troubleshooting

### Puerto ocupado:
```bash
sudo fuser -k 8000/tcp
```

### Ver procesos Docker:
```bash
sudo docker ps -a
```

### Limpiar todo:
```bash
sudo docker system prune -a
```

### Rebuild imagen:
```bash
sudo docker build -t skos-mcp-classifier:latest .
```

## 💾 Backup y Distribución

### Exportar imagen:
```bash
sudo docker save skos-mcp-classifier:latest | gzip > skos-classifier.tar.gz
```

### Importar imagen:
```bash
sudo docker load < skos-classifier.tar.gz
```

## 📈 Optimización

### Ver uso de recursos:
```bash
sudo docker stats <CONTAINER_NAME>
```

### Limitar memoria:
```bash
sudo docker run -d \
  --name skos-classifier \
  --memory="512m" \
  --cpus="1.0" \
  -p 8000:8000 \
  skos-mcp-classifier:latest
```

---
**✅ Aplicación containerizada exitosamente con Docker!**