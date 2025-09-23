#!/usr/bin/env python3
# csv_exporter.py - Exportador standalone para CSV
import csv
import sys
import argparse
from datetime import datetime
from client.classify_standard_api import classify

def export_products_to_csv(products_data, output_file=None, include_headers=True):
    """
    Exporta productos clasificados a CSV
    
    Args:
        products_data: Lista de productos (str o dict con 'text'/'product' e 'id'/'sku')
        output_file: Archivo de salida (opcional, se genera automático)
        include_headers: Si incluir cabeceras en el CSV
    
    Returns:
        tuple: (filename, results_list)
    """
    
    # Generar nombre de archivo si no se proporciona
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"productos_clasificados_{timestamp}.csv"
    
    results = []
    
    print(f"📊 Clasificando {len(products_data)} productos para CSV...")
    
    # Abrir archivo CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'product_id',
            'product_description', 
            'skos_category',
            'skos_notation',
            'skos_uri',
            'confidence_score',
            'classification_timestamp',
            'status'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Escribir headers si se solicita
        if include_headers:
            writer.writeheader()
        
        # Procesar cada producto
        for idx, product in enumerate(products_data, 1):
            # Extraer datos del producto
            if isinstance(product, dict):
                product_text = product.get('text', product.get('product', ''))
                product_id = product.get('id', product.get('sku', f'PROD-{idx:03d}'))
            else:
                product_text = str(product)
                product_id = f'PROD-{idx:03d}'
            
            print(f"  [{idx}/{len(products_data)}] {product_text}")
            
            try:
                # Clasificar producto
                result = classify(product_text, product_id)
                
                # Preparar fila CSV
                csv_row = {
                    'product_id': product_id,
                    'product_description': product_text,
                    'skos_category': result.get('prefLabel', ''),
                    'skos_notation': result.get('notation', ''),
                    'skos_uri': result.get('concept_uri', ''),
                    'confidence_score': result.get('confidence', 0),
                    'classification_timestamp': datetime.now().isoformat(),
                    'status': 'success' if 'error' not in result else 'error'
                }
                
                writer.writerow(csv_row)
                
                results.append({
                    'product_id': product_id,
                    'product_text': product_text,
                    'classification': result,
                    'success': True
                })
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                
                # Escribir fila de error
                error_row = {
                    'product_id': product_id,
                    'product_description': product_text,
                    'skos_category': f'ERROR: {str(e)}',
                    'skos_notation': '',
                    'skos_uri': '',
                    'confidence_score': 0,
                    'classification_timestamp': datetime.now().isoformat(),
                    'status': 'error'
                }
                
                writer.writerow(error_row)
                
                results.append({
                    'product_id': product_id,
                    'product_text': product_text,
                    'error': str(e),
                    'success': False
                })
    
    # Stats
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"\n✅ CSV generado exitosamente:")
    print(f"   📁 Archivo: {output_file}")
    print(f"   📊 Total procesados: {len(results)}")
    print(f"   ✅ Exitosos: {successful}")
    if failed > 0:
        print(f"   ❌ Errores: {failed}")
    
    return output_file, results

def load_products_from_file(input_file):
    """Cargar productos desde archivo (CSV, TXT, JSON)"""
    products = []
    
    try:
        if input_file.endswith('.csv'):
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Buscar columnas de texto e ID
                    text_col = None
                    id_col = None
                    
                    for key in row.keys():
                        key_lower = key.lower()
                        if any(term in key_lower for term in ['product', 'text', 'description', 'nombre']):
                            text_col = key
                        elif any(term in key_lower for term in ['id', 'sku', 'code', 'codigo']):
                            id_col = key
                    
                    if text_col:
                        product = {'text': row[text_col]}
                        if id_col and row[id_col]:
                            product['id'] = row[id_col]
                        products.append(product)
        
        elif input_file.endswith('.txt'):
            with open(input_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:  # Ignorar líneas vacías
                        # Formato: "texto" o "id|texto"
                        if '|' in line:
                            parts = line.split('|', 1)
                            products.append({'id': parts[0].strip(), 'text': parts[1].strip()})
                        else:
                            products.append({'text': line, 'id': f'LINE-{line_num:03d}'})
        
        elif input_file.endswith('.json'):
            import json
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    products = data
                else:
                    print("❌ El JSON debe contener una lista de productos")
                    return []
        
        else:
            print("❌ Formato de archivo no soportado. Use .csv, .txt o .json")
            return []
            
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return []
    
    return products

def main():
    """Script principal con argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description='Exportador CSV para clasificación SKOS')
    
    parser.add_argument('--input', '-i', 
                       help='Archivo de entrada (CSV, TXT, JSON) con productos')
    parser.add_argument('--output', '-o', 
                       help='Archivo CSV de salida (opcional)')
    parser.add_argument('--products', '-p', nargs='+',
                       help='Productos a clasificar (lista separada por espacios)')
    parser.add_argument('--no-headers', action='store_true',
                       help='No incluir cabeceras en el CSV')
    
    args = parser.parse_args()
    
    # Determinar productos a procesar
    products_data = []
    
    if args.input:
        print(f"📂 Cargando productos desde: {args.input}")
        products_data = load_products_from_file(args.input)
        if not products_data:
            print("❌ No se pudieron cargar productos del archivo")
            sys.exit(1)
            
    elif args.products:
        products_data = args.products
        
    else:
        # Productos de ejemplo si no se especifica nada
        print("ℹ️  No se especificaron productos. Usando ejemplos:")
        products_data = [
            {"text": "yogur natural griego 0%", "id": "YOG-001"},
            {"text": "pan integral centeno", "id": "PAN-002"}, 
            {"text": "aceite oliva virgen extra", "id": "ACE-003"},
            {"text": "queso manchego curado", "id": "QUE-004"},
            {"text": "cerveza artesanal IPA", "id": "BEB-005"}
        ]
    
    # Exportar a CSV
    print(f"\n🚀 Iniciando exportación CSV de {len(products_data)} productos")
    print("=" * 60)
    
    filename, results = export_products_to_csv(
        products_data, 
        args.output,
        not args.no_headers
    )
    
    print(f"\n🎉 Exportación completada!")
    print(f"📁 Archivo generado: {filename}")

if __name__ == "__main__":
    main()