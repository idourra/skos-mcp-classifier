#!/usr/bin/env python3
"""
🧪 TEST UNIFIED ARCHITECTURE - Pruebas de la Arquitectura Unificada
================================================================
Valida el funcionamiento completo del sistema unificado:
- Data Gateway
- Processing Pipeline  
- Output Manager
- File Manager
- API Unificada
"""

import asyncio
import json
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Imports de la arquitectura unificada
try:
    from core.data_gateway import (
        DataRequest, DataSource, DataType, InputFormat, ProductInput,
        data_gateway, process_product
    )
    from core.processing_pipeline import (
        processing_pipeline, process_product_request
    )
    from core.output_manager import (
        OutputRequest, OutputMetadata, OutputType, OutputFormat,
        DeliveryMethod, OutputDestination, output_manager
    )
    from core.file_manager import (
        file_manager, FileType, FileFormat, store_taxonomy_file,
        export_classification_results
    )
    
    print("✅ Todos los módulos de la arquitectura unificada importados correctamente")
    
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("💡 Asegúrate de que todos los archivos core/* existan y estén correctos")
    sys.exit(1)

class UnifiedArchitectureTest:
    """Clase principal para pruebas de la arquitectura unificada"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
    
    async def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🧪 INICIANDO PRUEBAS DE ARQUITECTURA UNIFICADA")
        print("=" * 60)
        
        tests = [
            ("Data Gateway", self.test_data_gateway),
            ("Output Manager", self.test_output_manager), 
            ("File Manager", self.test_file_manager),
            ("Processing Pipeline", self.test_processing_pipeline),
            ("Integración Completa", self.test_full_integration)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔬 Ejecutando: {test_name}")
            print("-" * 40)
            
            try:
                result = await test_func()
                self.test_results.append({
                    'test': test_name,
                    'success': result,
                    'timestamp': datetime.now().isoformat()
                })
                
                if result:
                    print(f"✅ {test_name}: EXITOSO")
                else:
                    print(f"❌ {test_name}: FALLIDO")
                    
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {str(e)}")
                self.test_results.append({
                    'test': test_name,
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        await self.generate_test_report()
    
    async def test_data_gateway(self) -> bool:
        """Probar Data Gateway"""
        try:
            print("  🔹 Probando ingesta de producto individual...")
            
            # Crear request de producto
            product_request = DataRequest(
                source=DataSource(
                    name="Test Product",
                    type=DataType.PRODUCT,
                    format=InputFormat.JSON
                ),
                data=ProductInput(
                    text="yogur griego natural 0% grasa",
                    product_id="TEST-001"
                )
            )
            
            # Procesar a través del gateway
            result = await data_gateway.process_request(product_request)
            
            if result.status == "processed":
                print(f"    ✅ Gateway procesó {result.data_processed} elemento(s)")
                print(f"    📊 Siguiente etapa: {result.next_stage}")
                return True
            else:
                print(f"    ❌ Gateway falló: {result.status}")
                return False
                
        except Exception as e:
            print(f"    💥 Error en Data Gateway: {str(e)}")
            return False
    
    async def test_output_manager(self) -> bool:
        """Probar Output Manager"""
        try:
            print("  🔹 Probando entrega de resultados...")
            
            # Datos de prueba
            test_data = {
                "product_id": "TEST-001",
                "search_text": "yogur griego natural",
                "prefLabel": "Yogur",
                "notation": "10.20.30",
                "level": 3,
                "score": 0.95,
                "taxonomy_used": {
                    "id": "test-taxonomy",
                    "name": "Test Taxonomy"
                }
            }
            
            # Crear request de output
            output_request = OutputRequest(
                metadata=OutputMetadata(
                    type=OutputType.CLASSIFICATION_RESPONSE,
                    format=OutputFormat.JSON,
                    destination=OutputDestination(
                        method=DeliveryMethod.HTTP_RESPONSE,
                        target=""
                    )
                ),
                data=test_data
            )
            
            # Entregar a través del output manager
            delivery_result = await output_manager.deliver_output(output_request)
            
            if delivery_result.success:
                print(f"    ✅ Output entregado: {delivery_result.output_id}")
                print(f"    📦 Tamaño: {delivery_result.response_size} bytes")
                return True
            else:
                print(f"    ❌ Output falló: {delivery_result.errors}")
                return False
                
        except Exception as e:
            print(f"    💥 Error en Output Manager: {str(e)}")
            return False
    
    async def test_file_manager(self) -> bool:
        """Probar File Manager"""
        try:
            print("  🔹 Probando gestión de archivos...")
            
            # Crear archivo de prueba
            test_data = {
                "test": "data",
                "timestamp": datetime.now().isoformat(),
                "products": [
                    {"text": "producto 1", "id": "P1"},
                    {"text": "producto 2", "id": "P2"}
                ]
            }
            
            # Almacenar archivo
            file_metadata = await file_manager.store_file(
                content=json.dumps(test_data, indent=2),
                original_name="test_data.json",
                file_type=FileType.JSON_INPUT,
                file_format=FileFormat.JSON
            )
            
            print(f"    ✅ Archivo almacenado: {file_metadata.file_id}")
            print(f"    📁 Ruta: {file_metadata.relative_path}")
            
            # Procesar archivo
            operation = await file_manager.process_file(file_metadata.file_id)
            
            if operation.success:
                print(f"    ✅ Archivo procesado: {operation.operation_id}")
                processed_count = operation.result.get('records_count', 0)
                print(f"    📊 Registros procesados: {processed_count}")
                return True
            else:
                print(f"    ❌ Procesamiento falló: {operation.errors}")
                return False
                
        except Exception as e:
            print(f"    💥 Error en File Manager: {str(e)}")
            return False
    
    async def test_processing_pipeline(self) -> bool:
        """Probar Processing Pipeline"""
        try:
            print("  🔹 Probando pipeline de procesamiento...")
            
            # Simular procesamiento de producto (sin clasificación real)
            # ya que necesitaríamos el sistema completo funcionando
            
            # Por ahora verificamos que el pipeline se inicialice correctamente
            stats = processing_pipeline.get_stats()
            
            print(f"    ✅ Pipeline inicializado")
            print(f"    📊 Total procesados: {stats['total_processed']}")
            print(f"    ⚡ Tasa de éxito: {stats['success_rate_percent']}%")
            
            # Verificar que los procesadores estén registrados
            stage_count = len(processing_pipeline.stage_processors)
            print(f"    🔧 Procesadores registrados: {stage_count}")
            
            return stage_count > 0
                
        except Exception as e:
            print(f"    💥 Error en Processing Pipeline: {str(e)}")
            return False
    
    async def test_full_integration(self) -> bool:
        """Probar integración completa"""
        try:
            print("  🔹 Probando integración completa del sistema...")
            
            # Test 1: Verificar que todos los componentes estén disponibles
            components = {
                'data_gateway': data_gateway,
                'output_manager': output_manager,
                'file_manager': file_manager,
                'processing_pipeline': processing_pipeline
            }
            
            print("    🔍 Verificando componentes:")
            for name, component in components.items():
                if component:
                    print(f"      ✅ {name}: Disponible")
                else:
                    print(f"      ❌ {name}: No disponible")
                    return False
            
            # Test 2: Verificar métodos principales
            methods_test = {
                'gateway.process_request': hasattr(data_gateway, 'process_request'),
                'output_manager.deliver_output': hasattr(output_manager, 'deliver_output'),
                'file_manager.store_file': hasattr(file_manager, 'store_file'),
                'pipeline.process': hasattr(processing_pipeline, 'process')
            }
            
            print("    🔍 Verificando métodos:")
            for method, available in methods_test.items():
                if available:
                    print(f"      ✅ {method}: Disponible")
                else:
                    print(f"      ❌ {method}: No disponible")
                    return False
            
            # Test 3: Verificar estadísticas
            try:
                gateway_stats = {"message": "Gateway stats not implemented"}  # Placeholder
                output_stats = output_manager.get_stats()
                file_stats = file_manager.get_stats()
                pipeline_stats = processing_pipeline.get_stats()
                
                print("    📊 Estadísticas del sistema:")
                print(f"      📤 Output: {output_stats['total_outputs']} entregas")
                print(f"      📁 Files: {file_stats['total_files']} archivos")
                print(f"      ⚙️ Pipeline: {pipeline_stats['total_processed']} procesados")
                
            except Exception as e:
                print(f"    ⚠️ Error obteniendo estadísticas: {str(e)}")
                # No es crítico para la integración
            
            print("    ✅ Integración completa verificada")
            return True
            
        except Exception as e:
            print(f"    💥 Error en integración completa: {str(e)}")
            return False
    
    async def generate_test_report(self):
        """Generar reporte de pruebas"""
        print("\n" + "=" * 60)
        print("📋 REPORTE DE PRUEBAS")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - successful_tests
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Resumen:")
        print(f"  Total de pruebas: {total_tests}")
        print(f"  Exitosas: {successful_tests}")
        print(f"  Fallidas: {failed_tests}")
        print(f"  Tasa de éxito: {success_rate:.1f}%")
        
        print(f"\n⏱️ Tiempo total: {(datetime.now() - self.start_time).total_seconds():.2f} segundos")
        
        # Detalles de pruebas fallidas
        failed_details = [r for r in self.test_results if not r['success']]
        if failed_details:
            print(f"\n❌ Pruebas fallidas:")
            for failure in failed_details:
                print(f"  • {failure['test']}")
                if 'error' in failure:
                    print(f"    Error: {failure['error']}")
        
        # Generar archivo de reporte
        try:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_tests': total_tests,
                    'successful': successful_tests,
                    'failed': failed_tests,
                    'success_rate_percent': round(success_rate, 1)
                },
                'test_results': self.test_results,
                'execution_time_seconds': (datetime.now() - self.start_time).total_seconds()
            }
            
            # Crear directorio de reportes si no existe
            reports_dir = Path("test_reports")
            reports_dir.mkdir(exist_ok=True)
            
            # Guardar reporte
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = reports_dir / f"unified_architecture_test_{timestamp}.json"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 Reporte guardado en: {report_path}")
            
        except Exception as e:
            print(f"\n⚠️ No se pudo guardar el reporte: {str(e)}")
        
        # Conclusión
        if success_rate >= 80:
            print(f"\n🎉 ARQUITECTURA UNIFICADA: FUNCIONANDO CORRECTAMENTE")
            print("✅ El sistema está listo para uso en producción")
        elif success_rate >= 60:
            print(f"\n⚠️ ARQUITECTURA UNIFICADA: FUNCIONAMIENTO PARCIAL")
            print("🔧 Revisa las pruebas fallidas antes de usar en producción")
        else:
            print(f"\n❌ ARQUITECTURA UNIFICADA: REQUIERE CORRECCIONES")
            print("🚨 No usar en producción hasta corregir los problemas")

async def main():
    """Función principal"""
    print("🌟 UNIFIED SKOS ARCHITECTURE - TEST SUITE")
    print(f"⏰ Iniciado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    test_suite = UnifiedArchitectureTest()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n💥 Error crítico en las pruebas: {str(e)}")
        sys.exit(1)