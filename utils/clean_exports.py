#!/usr/bin/env python3
"""
clean_exports.py - Utilidad para limpiar archivos de exportación antiguos
"""
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Agregar el directorio padre al PATH para importar utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.export_config import get_cleanup_config, EXPORTS_BASE_DIR

def get_file_age_days(file_path):
    """
    Calcula la edad de un archivo en días
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        int: Edad en días
    """
    try:
        file_stat = file_path.stat()
        file_time = datetime.fromtimestamp(file_stat.st_mtime)
        age = datetime.now() - file_time
        return age.days
    except Exception:
        return 0

def get_file_size_mb(file_path):
    """
    Obtiene el tamaño de un archivo en MB
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        float: Tamaño en MB
    """
    try:
        size_bytes = file_path.stat().st_size
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0

def scan_export_files(base_dir=None, extensions=None):
    """
    Escanea archivos de exportación
    
    Args:
        base_dir: Directorio base (por defecto exports/)
        extensions: Lista de extensiones a buscar
        
    Returns:
        list: Lista de diccionarios con info de archivos
    """
    if base_dir is None:
        base_dir = EXPORTS_BASE_DIR
        
    if extensions is None:
        extensions = ['.csv', '.xlsx', '.json', '.tmp', '.log']
    
    files_info = []
    
    if not base_dir.exists():
        return files_info
    
    for file_path in base_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            # Saltar archivos especiales
            if file_path.name in ['.gitignore', 'README.md']:
                continue
                
            files_info.append({
                'path': file_path,
                'name': file_path.name,
                'relative_path': file_path.relative_to(base_dir),
                'size_mb': get_file_size_mb(file_path),
                'age_days': get_file_age_days(file_path),
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
            })
    
    return sorted(files_info, key=lambda x: x['modified'], reverse=True)

def cleanup_old_files(dry_run=True, retention_days=None, max_size_mb=None, verbose=True):
    """
    Limpia archivos antiguos de exportación
    
    Args:
        dry_run: Si solo mostrar qué se haría sin eliminar
        retention_days: Días de retención (usa config si es None)
        max_size_mb: Tamaño máximo por archivo en MB
        verbose: Si mostrar información detallada
        
    Returns:
        dict: Estadísticas de la limpieza
    """
    config = get_cleanup_config()
    
    if retention_days is None:
        retention_days = config['retention_days']
    if max_size_mb is None:
        max_size_mb = config['max_file_size_mb']
    
    files_info = scan_export_files()
    
    # Clasificar archivos para eliminar
    to_delete = []
    reasons = []
    
    for file_info in files_info:
        delete_reasons = []
        
        # Archivos demasiado antiguos
        if file_info['age_days'] > retention_days:
            delete_reasons.append(f"antiguo ({file_info['age_days']} días)")
        
        # Archivos demasiado grandes
        if file_info['size_mb'] > max_size_mb:
            delete_reasons.append(f"grande ({file_info['size_mb']:.1f} MB)")
        
        if delete_reasons:
            to_delete.append(file_info)
            reasons.append(", ".join(delete_reasons))
    
    # Estadísticas
    stats = {
        'total_files': len(files_info),
        'files_to_delete': len(to_delete),
        'total_size_mb': sum(f['size_mb'] for f in files_info),
        'delete_size_mb': sum(f['size_mb'] for f in to_delete),
        'retention_days': retention_days,
        'max_size_mb': max_size_mb,
        'dry_run': dry_run
    }
    
    if verbose:
        print(f"🔍 Escaneando exportaciones en: {EXPORTS_BASE_DIR}")
        print(f"📊 Archivos encontrados: {stats['total_files']}")
        print(f"💾 Tamaño total: {stats['total_size_mb']:.1f} MB")
        print(f"⏰ Retención: {retention_days} días")
        print(f"📏 Tamaño máximo: {max_size_mb} MB")
        print()
    
    if not to_delete:
        if verbose:
            print("✨ No hay archivos para eliminar")
        return stats
    
    if verbose:
        print(f"🗑️  Archivos para {'eliminar' if not dry_run else 'eliminar (simulación)'}:")
        for file_info, reason in zip(to_delete, reasons):
            print(f"   📄 {file_info['relative_path']}")
            print(f"      💾 {file_info['size_mb']:.1f} MB | 📅 {file_info['modified'].strftime('%Y-%m-%d %H:%M')}")
            print(f"      🔍 Razón: {reason}")
            print()
    
    # Eliminar archivos (si no es dry_run)
    deleted_count = 0
    deleted_size = 0
    
    if not dry_run:
        for file_info in to_delete:
            try:
                file_info['path'].unlink()
                deleted_count += 1
                deleted_size += file_info['size_mb']
                if verbose:
                    print(f"✅ Eliminado: {file_info['relative_path']}")
            except Exception as e:
                if verbose:
                    print(f"❌ Error eliminando {file_info['relative_path']}: {e}")
    
    # Limpiar directorios vacíos
    if not dry_run:
        for root, dirs, files in os.walk(EXPORTS_BASE_DIR, topdown=False):
            for dirname in dirs:
                dir_path = Path(root) / dirname
                try:
                    if not any(dir_path.iterdir()):  # Directorio vacío
                        dir_path.rmdir()
                        if verbose:
                            print(f"📁 Directorio vacío eliminado: {dir_path.relative_to(EXPORTS_BASE_DIR)}")
                except Exception:
                    pass  # Ignorar errores en directorios no vacíos
    
    # Actualizar estadísticas
    stats.update({
        'deleted_count': deleted_count,
        'deleted_size_mb': deleted_size
    })
    
    if verbose:
        print(f"\n{'🧹' if not dry_run else '👀'} Resumen:")
        if dry_run:
            print(f"   📄 Se eliminarían: {len(to_delete)} archivos")
            print(f"   💾 Se liberarían: {stats['delete_size_mb']:.1f} MB")
        else:
            print(f"   📄 Eliminados: {deleted_count}/{len(to_delete)} archivos")
            print(f"   💾 Liberados: {deleted_size:.1f} MB")
    
    return stats

def main():
    """Script principal con argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description='Limpieza de archivos de exportación')
    
    parser.add_argument('--execute', action='store_true',
                       help='Ejecutar limpieza real (por defecto es simulación)')
    parser.add_argument('--retention-days', type=int,
                       help='Días de retención de archivos')
    parser.add_argument('--max-size-mb', type=float,
                       help='Tamaño máximo por archivo en MB')
    parser.add_argument('--quiet', action='store_true',
                       help='Ejecutar en modo silencioso')
    parser.add_argument('--list-only', action='store_true',
                       help='Solo listar archivos sin analizar para eliminar')
    
    args = parser.parse_args()
    
    if args.list_only:
        files_info = scan_export_files()
        if not files_info:
            print("📂 No hay archivos de exportación")
            return
        
        print(f"📂 Archivos de exportación en {EXPORTS_BASE_DIR}:")
        print("=" * 80)
        
        total_size = 0
        for file_info in files_info:
            print(f"📄 {file_info['relative_path']}")
            print(f"   💾 {file_info['size_mb']:.1f} MB | "
                  f"📅 {file_info['modified'].strftime('%Y-%m-%d %H:%M')} | "
                  f"⏰ {file_info['age_days']} días")
            total_size += file_info['size_mb']
        
        print("=" * 80)
        print(f"📊 Total: {len(files_info)} archivos, {total_size:.1f} MB")
        return
    
    # Ejecutar limpieza
    cleanup_old_files(
        dry_run=not args.execute,
        retention_days=args.retention_days,
        max_size_mb=args.max_size_mb,
        verbose=not args.quiet
    )
    
    if args.execute and not args.quiet:
        print("\n🎉 Limpieza completada!")

if __name__ == "__main__":
    main()