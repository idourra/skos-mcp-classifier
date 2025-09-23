#!/usr/bin/env python3
"""
export_config.py - Configuración centralizada para exportaciones
"""
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración base
PROJECT_ROOT = Path(__file__).parent.parent
EXPORTS_BASE_DIR = PROJECT_ROOT / "exports"

# Configuración de retención 
RETENTION_DAYS = int(os.getenv('EXPORT_RETENTION_DAYS', '7'))
MAX_FILE_SIZE_MB = int(os.getenv('EXPORT_MAX_FILE_SIZE_MB', '100'))
AUTO_CLEANUP = os.getenv('EXPORT_AUTO_CLEANUP', 'true').lower() == 'true'

# Subdirectorios por tipo
SUBDIRS = {
    'csv': 'csv',
    'excel': 'excel', 
    'json': 'json',
    'temp': 'temp'
}

def get_export_path(export_type='csv', create_dirs=True, use_date_subdir=True):
    """
    Obtiene la ruta completa para un archivo de exportación
    
    Args:
        export_type: Tipo de export ('csv', 'excel', 'json', 'temp')
        create_dirs: Si crear directorios automáticamente
        use_date_subdir: Si usar subdirectorio por fecha (YYYY-MM-DD)
        
    Returns:
        Path: Ruta completa del directorio
    """
    if export_type not in SUBDIRS:
        raise ValueError(f"Tipo de export inválido: {export_type}. Opciones: {list(SUBDIRS.keys())}")
    
    # Construir ruta base
    base_path = EXPORTS_BASE_DIR / SUBDIRS[export_type]
    
    # Agregar subdirectorio por fecha si se solicita
    if use_date_subdir:
        today = datetime.now().strftime("%Y-%m-%d")
        base_path = base_path / today
    
    # Crear directorios si no existen
    if create_dirs:
        base_path.mkdir(parents=True, exist_ok=True)
    
    return base_path

def generate_filename(base_name, export_type='csv', include_timestamp=True, custom_suffix=None):
    """
    Genera un nombre de archivo estándar para exportaciones
    
    Args:
        base_name: Nombre base del archivo (sin extensión)
        export_type: Tipo de export para la extensión
        include_timestamp: Si incluir timestamp en el nombre
        custom_suffix: Sufijo personalizado antes de la extensión
        
    Returns:
        str: Nombre completo del archivo
    """
    extensions = {
        'csv': '.csv',
        'excel': '.xlsx', 
        'json': '.json',
        'temp': '.tmp'
    }
    
    # Construir nombre
    filename_parts = [base_name]
    
    if custom_suffix:
        filename_parts.append(custom_suffix)
        
    if include_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_parts.append(timestamp)
    
    filename = "_".join(filename_parts) + extensions.get(export_type, '.txt')
    
    return filename

def get_full_export_path(base_name, export_type='csv', **kwargs):
    """
    Obtiene la ruta completa (directorio + archivo) para una exportación
    
    Args:
        base_name: Nombre base del archivo
        export_type: Tipo de export
        **kwargs: Argumentos adicionales para get_export_path y generate_filename
        
    Returns:
        Path: Ruta completa del archivo
    """
    # Separar argumentos para cada función
    path_kwargs = {k: v for k, v in kwargs.items() if k in ['create_dirs', 'use_date_subdir']}
    file_kwargs = {k: v for k, v in kwargs.items() if k in ['include_timestamp', 'custom_suffix']}
    
    # Obtener directorio y nombre de archivo
    export_dir = get_export_path(export_type, **path_kwargs)
    filename = generate_filename(base_name, export_type, **file_kwargs)
    
    return export_dir / filename

def get_cleanup_config():
    """
    Obtiene la configuración para limpieza de archivos
    
    Returns:
        dict: Configuración de limpieza
    """
    return {
        'retention_days': RETENTION_DAYS,
        'max_file_size_mb': MAX_FILE_SIZE_MB,
        'auto_cleanup': AUTO_CLEANUP,
        'exports_dir': EXPORTS_BASE_DIR
    }

def ensure_export_structure():
    """
    Asegura que la estructura de directorios de exports existe
    """
    EXPORTS_BASE_DIR.mkdir(exist_ok=True)
    
    for subdir in SUBDIRS.values():
        (EXPORTS_BASE_DIR / subdir).mkdir(exist_ok=True)
    
    print(f"✅ Estructura de exports creada en: {EXPORTS_BASE_DIR}")

if __name__ == "__main__":
    # Test de la configuración
    ensure_export_structure()
    
    print("\n🔧 Configuración de Exports:")
    print(f"   📁 Directorio base: {EXPORTS_BASE_DIR}")
    print(f"   📅 Retención: {RETENTION_DAYS} días")
    print(f"   📏 Tamaño máximo: {MAX_FILE_SIZE_MB} MB")
    print(f"   🧹 Auto-limpieza: {'✅' if AUTO_CLEANUP else '❌'}")
    
    print("\n📂 Ejemplo de rutas:")
    for export_type in SUBDIRS.keys():
        example_path = get_full_export_path("productos_clasificados", export_type)
        print(f"   {export_type.upper()}: {example_path}")