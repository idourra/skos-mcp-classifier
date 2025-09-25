# 📋 Requisitos del Sistema - SKOS MCP Classifier

## 🎯 **Para Dar Servicios en Producción**

### **🖥️ Requisitos Mínimos de Hardware**

#### **Servidor Local/VPS:**
- **CPU:** 1 core, 2.0 GHz mínimo
- **RAM:** 512 MB mínimo, 1GB recomendado
- **Disco:** 2GB espacio libre
- **Red:** Conexión estable a Internet

#### **Servicios Cloud (Recomendado):**
- **GitHub Codespaces:** 2 cores, 4GB RAM (gratuito)
- **Railway:** 512MB RAM, 1GB disco (plan gratuito)
- **Render:** 512MB RAM, 1GB disco (plan gratuito)

---

### **🐍 Requisitos de Software**

#### **Runtime Environment:**
```bash
✅ Python 3.8+ (recomendado 3.9+)
✅ pip package manager
✅ Virtual environment support
```

#### **Dependencias Core:**
```bash
✅ FastAPI 0.100+        # Web framework
✅ Uvicorn 0.20+         # ASGI server
✅ Pydantic 2.0+         # Data validation
✅ RDFlib 7.0+           # SKOS/RDF processing
✅ SQLite3               # Database (incluido en Python)
```

#### **Sistema Operativo:**
```bash
✅ Linux (Ubuntu/Debian) - Recomendado
✅ macOS 10.15+          - Compatible  
✅ Windows 10+           - Compatible con WSL
```

---

### **🔑 Configuración Requerida**

#### **Variables de Entorno Esenciales:**
```bash
# OBLIGATORIO
OPENAI_API_KEY=sk-proj-xxx...    # API key de OpenAI

# OPCIONALES (con defaults)
PORT=8000                        # Puerto del servidor
MCP_SERVER_URL=http://localhost:8080
DEBUG=false                      # Para producción
LOG_LEVEL=INFO
```

#### **Archivos de Configuración:**
```bash
✅ .env                 # Variables de entorno
✅ server/skos.sqlite   # Base de datos SKOS
✅ server/requirements.txt # Dependencias Python
```

---

### **🌐 Requisitos de Red**

#### **Puertos Necesarios:**
```bash
✅ Puerto 8000/8001/8002  # API REST server
✅ Puerto 8080            # MCP server (opcional)
✅ Puerto 443/80          # HTTPS/HTTP (producción)
```

#### **Conectividad Externa:**
```bash
✅ Internet access       # Para OpenAI API
✅ HTTPS support         # Para webhooks/callbacks
✅ DNS resolution        # Para dominios externos
```

---

### **📊 Requisitos por Tipo de Despliegue**

#### **1. GitHub Codespaces** 🌐
```bash
Requisitos mínimos:
✅ Cuenta GitHub (gratuita)
✅ Navegador web moderno
✅ Conexión a Internet
✅ OPENAI_API_KEY en GitHub Secrets

Incluye automáticamente:
- Python 3.8+ preinstalado
- VS Code en navegador
- Port forwarding automático
- SSL certificates
```

#### **2. Docker Local** 🐳
```bash
Requisitos adicionales:
✅ Docker 20.0+ instalado
✅ Docker Compose 2.0+
✅ 2GB RAM disponible
✅ 4GB espacio en disco

Ventajas:
- Entorno aislado
- Fácil escalamiento
- Rollback automático
```

#### **3. Railway** 🚄
```bash
Requisitos mínimos:
✅ Cuenta Railway (plan gratuito)
✅ Repositorio GitHub
✅ OPENAI_API_KEY configurada

Incluye automáticamente:
- Escalado automático
- PostgreSQL database
- SSL certificates
- Monitoring y logs
```

#### **4. Render** 🎨
```bash
Requisitos mínimos:
✅ Cuenta Render (plan gratuito)
✅ Repositorio GitHub  
✅ OPENAI_API_KEY configurada

Limitaciones plan gratuito:
- Sleep después de 15min inactividad
- 750 horas/mes
- 512MB RAM
```

---

### **🔐 Requisitos de Seguridad**

#### **Para Producción:**
```bash
✅ HTTPS obligatorio      # SSL/TLS certificates
✅ API rate limiting      # Prevenir abuse
✅ Environment variables  # No hardcode secrets
✅ Input validation       # Pydantic schemas
✅ Error handling         # No info disclosure
```

#### **Secrets Management:**
```bash
✅ GitHub Secrets         # Para Codespaces/Actions
✅ Railway Variables      # Para Railway deploy
✅ Render Environment     # Para Render deploy  
✅ .env local            # Para desarrollo
```

---

### **📈 Requisitos de Monitoreo**

#### **Logs Necesarios:**
```bash
✅ Application logs       # Uvicorn access logs
✅ Error tracking        # Exception handling
✅ Performance metrics   # Response times
✅ API usage stats       # Request counts
```

#### **Health Checks:**
```bash
✅ /health endpoint      # Basic health check
✅ Database connectivity # SQLite file access
✅ External API status   # OpenAI API access
```

---

### **🎯 Resumen por Escenario de Uso**

#### **Para Desarrollo/Testing:**
```bash
Mínimo absoluto:
- Python 3.8+ + pip
- 512MB RAM
- OPENAI_API_KEY
- Conexión a Internet

Tiempo setup: 5 minutos
```

#### **Para Producción Personal:**
```bash
Recomendado:
- GitHub Codespaces (gratuito)
- 2GB RAM, 2 cores
- Domain name (opcional)
- Monitoring básico

Tiempo setup: 10 minutos
```

#### **Para Producción Empresarial:**
```bash
Profesional:
- Railway/Render Pro plans
- Load balancing
- Database backups
- 99.9% uptime SLA
- Custom domain + SSL

Tiempo setup: 30 minutos
```

---

### **✅ Checklist de Preparación**

Antes de desplegar, verifica:

```bash
□ Python 3.8+ instalado
□ OPENAI_API_KEY válida y configurada
□ Base de datos SKOS inicializada
□ Dependencias instaladas (requirements.txt)
□ Puerto disponible (8000/8001/8002)
□ Conexión a Internet estable
□ Backup de configuración (.env)
□ Health checks funcionando
□ Logs configurados
□ SSL/HTTPS para producción
```

---

**🎉 Con estos requisitos cubiertos, tu SKOS MCP Classifier estará listo para dar servicios robustos y escalables en cualquier entorno.**