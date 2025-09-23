# 📁 Sistema de Gestión de Exportaciones

## Overview

El clasificador SKOS ahora incluye un sistema robusto de gestión de archivos exportados que:

- 🗂️ **Organiza automáticamente** los archivos en carpetas por fecha
- 🧹 **Limpia automáticamente** archivos antiguos
- 📊 **Soporta múltiples formatos** (CSV, Excel, JSON)
- 🚫 **Mantiene el repo limpio** excluyendo archivos temporales

## Estructura de Directorios

```
exports/
├── csv/              # Archivos CSV
│   └── 2025-09-23/   # Organizados por fecha
├── excel/            # Archivos Excel (.xlsx)
│   └── 2025-09-23/
├── json/             # Resultados en JSON
│   └── 2025-09-23/
└── temp/             # Archivos temporales y logs
    └── 2025-09-23/
```

## Configuración

Agrega a tu `.env`:

```bash
# Configuración de exportaciones
EXPORT_RETENTION_DAYS=7          # Días que se conservan los archivos
EXPORT_MAX_FILE_SIZE_MB=100      # Tamaño máximo por archivo (MB)
EXPORT_AUTO_CLEANUP=true         # Limpieza automática activada
```

## Uso Programático

### Exportador CSV

```python
from csv_exporter import export_products_to_csv

# Los archivos se guardan automáticamente en exports/csv/YYYY-MM-DD/
products = ["yogur natural", "pan integral"]
filename, results = export_products_to_csv(products)
print(f"Guardado en: {filename}")
```

### Exportador Excel

```python
from excel_exporter import export_to_excel

# Los archivos se guardan automáticamente en exports/excel/YYYY-MM-DD/
products = [{"text": "queso", "id": "Q001"}]
filename, results = export_to_excel(products)
print(f"Guardado en: {filename}")
```

### Configuración Personalizada

```python
from utils.export_config import get_full_export_path

# Generar ruta personalizada
custom_path = get_full_export_path(
    "mi_catalogo", 
    "csv",
    include_timestamp=False,
    custom_suffix="v2"
)
# Resultado: exports/csv/2025-09-23/mi_catalogo_v2.csv
```

## Comandos Make

```bash
# Exportar productos de ejemplo
make export-csv         # Exporta CSV con productos ejemplo
make export-excel       # Exporta Excel con productos ejemplo
make export             # Ambos formatos

# Limpieza de archivos
make clean-exports-dry  # Ver qué archivos se eliminarían
make clean-exports      # Limpiar archivos antiguos
make clean              # Limpieza completa (exports + cache)
```

## Utilidad de Limpieza

### Uso Básico

```bash
# Ver qué archivos se eliminarían (sin eliminar)
python utils/clean_exports.py

# Ejecutar limpieza real
python utils/clean_exports.py --execute

# Solo listar archivos
python utils/clean_exports.py --list-only
```

### Configuración Avanzada

```bash
# Retención personalizada (30 días)
python utils/clean_exports.py --execute --retention-days 30

# Límite de tamaño personalizado (50MB)
python utils/clean_exports.py --execute --max-size-mb 50

# Modo silencioso
python utils/clean_exports.py --execute --quiet
```

## Integración con Git

El sistema está completamente integrado con Git:

- ✅ `exports/` está excluido del control de versiones
- ✅ Estructura básica se conserva (README.md, .gitignore)
- ✅ Archivos temporales nunca contaminarán el repo

## Migración desde Sistema Anterior

Si tienes archivos de exportación en el directorio raíz:

```bash
# 1. Mover archivos existentes
mkdir -p exports/csv/$(date +%Y-%m-%d)
mv *.csv exports/csv/$(date +%Y-%m-%d)/ 2>/dev/null || true

mkdir -p exports/excel/$(date +%Y-%m-%d)  
mv *.xlsx exports/excel/$(date +%Y-%m-%d)/ 2>/dev/null || true

# 2. Limpiar archivos del directorio raíz
rm -f products_classified*.csv products_classified*.xlsx
```

## API de Configuración

### `utils/export_config.py`

#### Funciones Principales

```python
# Obtener ruta de directorio
get_export_path(export_type='csv', create_dirs=True, use_date_subdir=True)

# Generar nombre de archivo
generate_filename(base_name, export_type='csv', include_timestamp=True)

# Ruta completa (directorio + archivo)
get_full_export_path(base_name, export_type='csv', **kwargs)

# Crear estructura de directorios
ensure_export_structure()

# Configuración de limpieza
get_cleanup_config()
```

#### Tipos de Export Soportados

- `'csv'` → `.csv` files en `exports/csv/`
- `'excel'` → `.xlsx` files en `exports/excel/`
- `'json'` → `.json` files en `exports/json/`
- `'temp'` → `.tmp` files en `exports/temp/`

## Monitoreo y Estadísticas

```python
from utils.clean_exports import scan_export_files

# Obtener estadísticas de archivos
files_info = scan_export_files()
total_size = sum(f['size_mb'] for f in files_info)
print(f"Total exports: {len(files_info)} archivos, {total_size:.1f} MB")
```

## Mejores Prácticas

### 📋 Desarrollo
- Usa `make clean-exports-dry` antes de commits para verificar limpieza
- Configura `EXPORT_RETENTION_DAYS` apropiado para tu flujo de trabajo
- Usa nombres descriptivos en `get_full_export_path()`

### 🚀 Producción  
- Activa `EXPORT_AUTO_CLEANUP=true`
- Configura cron job para `make clean-exports` si es necesario
- Monitorea el tamaño de `exports/` periódicamente

### 🔧 Personalización
- Extiende `SUBDIRS` en `export_config.py` para nuevos tipos
- Modifica `extensions` en `clean_exports.py` para nuevos formatos
- Ajusta `RETENTION_DAYS` según políticas de la organización

---

*Sistema implementado en la rama `feature/export-management`*