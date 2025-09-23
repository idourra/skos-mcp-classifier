# 📁 Carpeta de Exportaciones

Esta carpeta contiene todos los archivos generados por las herramientas de exportación del clasificador SKOS.

## Estructura

```
exports/
├── csv/              # Archivos CSV exportados
├── excel/            # Archivos Excel exportados  
├── json/             # Archivos JSON de resultados
└── temp/             # Archivos temporales y logs
```

## Organización por Fecha

Los archivos se organizan automáticamente por fecha:

```
exports/csv/2025-09-23/productos_clasificados_20250923_143022.csv
exports/excel/2025-09-23/productos_clasificados_20250923_143025.xlsx
```

## Limpieza Automática

- Los archivos de más de 7 días se eliminan automáticamente
- Configurable vía `EXPORT_RETENTION_DAYS` en `.env`
- Manual: `python utils/clean_exports.py`

## Configuración

Las rutas se configuran en `utils/export_config.py`:

- `EXPORTS_BASE_DIR`: Directorio base de exports
- `RETENTION_DAYS`: Días de retención de archivos  
- `MAX_FILE_SIZE`: Tamaño máximo de archivos individuales
- `AUTO_CLEANUP`: Activar limpieza automática

---
*Nota: Esta carpeta está excluida del control de versiones Git.*