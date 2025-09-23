#!/usr/bin/env python3
"""
Multi-Taxonomy Classification Client
Cliente actualizado para clasificación con múltiples taxonomías SKOS
"""
import os
import requests
import json
from dotenv import load_dotenv
from openai import OpenAI
import sys
from typing import Optional, Dict, Any, List
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.openai_cost_calculator import calculate_openai_cost, format_cost_info

# Load environment variables from .env file
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8080")

def get_available_taxonomies() -> Dict[str, Any]:
    """
    Obtener lista de taxonomías disponibles en el servidor MCP
    
    Returns:
        Dict con información de taxonomías disponibles
    """
    try:
        response = requests.get(f"{SERVER_URL}/taxonomies/available", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error obteniendo taxonomías disponibles: {e}")
        return {"taxonomies": [], "default_taxonomy": None, "total_active": 0}

def list_taxonomies() -> List[Dict[str, Any]]:
    """
    Listar todas las taxonomías disponibles de forma amigable
    
    Returns:
        Lista de taxonomías con información básica
    """
    taxonomies_info = get_available_taxonomies()
    
    print("\n🗂️  Taxonomías Disponibles:")
    print("=" * 50)
    
    if not taxonomies_info["taxonomies"]:
        print("❌ No hay taxonomías disponibles")
        return []
    
    for i, tax in enumerate(taxonomies_info["taxonomies"], 1):
        default_marker = " (DEFAULT)" if tax["is_default"] else ""
        print(f"{i}. {tax['name']}{default_marker}")
        print(f"   ID: {tax['id']}")
        print(f"   Idioma: {tax['language']} | Dominio: {tax['domain']}")
        print(f"   Conceptos: {tax['concepts_count']:,}")
        print(f"   Descripción: {tax['description']}")
        print()
    
    print(f"Total: {taxonomies_info['total_active']} taxonomías activas")
    print(f"Default: {taxonomies_info['default_taxonomy']}")
    
    return taxonomies_info["taxonomies"]

def classify(text: str, product_id: Optional[str] = None, taxonomy_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Clasificar un producto usando una taxonomía específica o la default
    
    Args:
        text: Descripción del producto a clasificar
        product_id: ID opcional del producto
        taxonomy_id: ID de taxonomía específica (opcional, usa default si no se especifica)
    
    Returns:
        Dict con resultado de clasificación incluyendo información de taxonomía usada
    """
    try:
        # Si se especifica taxonomía, validar que existe
        if taxonomy_id:
            available_taxonomies = get_available_taxonomies()
            taxonomy_ids = [t["id"] for t in available_taxonomies["taxonomies"]]
            
            if taxonomy_id not in taxonomy_ids:
                return {
                    "error": f"Taxonomía '{taxonomy_id}' no disponible",
                    "available_taxonomies": taxonomy_ids,
                    "text": text,
                    "product_id": product_id
                }
        
        # Función search_concepts en el MCP server
        search_function = {
            "name": "search_concepts",
            "description": "Buscar conceptos SKOS relevantes",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Texto de búsqueda"},
                    "lang": {"type": "string", "description": "Código de idioma", "default": "es"},
                    "k": {"type": "integer", "description": "Número máximo de resultados", "default": 5},
                    "taxonomy_id": {"type": "string", "description": "ID de taxonomía específica"}
                },
                "required": ["query"]
            }
        }
        
        # Función get_concept_context
        context_function = {
            "name": "get_concept_context", 
            "description": "Obtener contexto detallado de un concepto SKOS",
            "parameters": {
                "type": "object",
                "properties": {
                    "concept_uri": {"type": "string", "description": "URI del concepto SKOS"},
                    "taxonomy_id": {"type": "string", "description": "ID de taxonomía específica"}
                },
                "required": ["concept_uri"]
            }
        }
        
        # Preparar mensajes para OpenAI
        system_message = """Eres un experto en clasificación de productos usando taxonomías SKOS.

Tu trabajo es:
1. Buscar conceptos relevantes usando search_concepts
2. Obtener contexto detallado si es necesario con get_concept_context  
3. Seleccionar el concepto más apropiado
4. Responder SOLO con un JSON válido con esta estructura exacta:

{
  "search_text": "texto usado para búsqueda",
  "concept_uri": "URI del concepto seleccionado",
  "prefLabel": "etiqueta preferida del concepto",
  "notation": "notación/código del concepto",
  "level": nivel_jerárquico_número,
  "confidence": confianza_entre_0_y_1,
  "taxonomy_used": "id_de_taxonomia_utilizada"
}

IMPORTANTE: 
- Responde ÚNICAMENTE con el JSON, sin texto adicional
- Usa confidence de 1.0 para coincidencias exactas, 0.8-0.9 para muy buenas, 0.5-0.7 para moderadas
- Si tienes dudas entre conceptos, elige el más específico que aplique"""

        user_message = f"Clasifica este producto: '{text}'"
        
        # Agregar información de taxonomía si se especifica
        if taxonomy_id:
            user_message += f"\n\nUsa la taxonomía específica: {taxonomy_id}"
        
        functions = [search_function, context_function]
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Tracking de costos y calls
        total_cost_info = {
            "model": "gpt-4o-mini-2024-07-18",
            "total_tokens": 0,
            "prompt_tokens": 0, 
            "completion_tokens": 0,
            "api_calls": 0,
            "total_cost_usd": 0.0,
            "calls_detail": []
        }
        
        # Primera llamada a OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=messages,
            functions=functions,
            function_call="auto",
            temperature=0.1
        )
        
        # Actualizar costos
        cost_info = calculate_openai_cost(response)
        total_cost_info["api_calls"] += 1
        total_cost_info["total_tokens"] += cost_info["usage"]["total_tokens"]
        total_cost_info["prompt_tokens"] += cost_info["usage"]["prompt_tokens"]
        total_cost_info["completion_tokens"] += cost_info["usage"]["completion_tokens"]
        total_cost_info["total_cost_usd"] += cost_info["cost_usd"]["total"]
        total_cost_info["calls_detail"].append({
            "call": 1,
            "function": "initial_classification",
            "cost": cost_info["cost_usd"]["total"]
        })
        
        # Procesar respuesta y function calls
        while response.choices[0].message.function_call:
            function_name = response.choices[0].message.function_call.name
            function_args = json.loads(response.choices[0].message.function_call.arguments)
            
            # Agregar taxonomy_id si se especificó y no está en los argumentos
            if taxonomy_id and "taxonomy_id" not in function_args:
                function_args["taxonomy_id"] = taxonomy_id
            
            # Llamar función MCP
            if function_name == "search_concepts":
                mcp_response = requests.post(
                    f"{SERVER_URL}/tools/search_concepts", 
                    json=function_args,
                    timeout=30
                )
            elif function_name == "get_concept_context":
                mcp_response = requests.post(
                    f"{SERVER_URL}/tools/get_concept_context",
                    json=function_args, 
                    timeout=30
                )
            else:
                function_result = {"error": f"Función desconocida: {function_name}"}
                
            if 'mcp_response' in locals():
                if mcp_response.status_code == 200:
                    function_result = mcp_response.json()
                else:
                    function_result = {"error": f"Error MCP: {mcp_response.status_code}"}
            
            # Agregar mensaje de función y continuar conversación
            messages.append({
                "role": "assistant",
                "content": None,
                "function_call": {
                    "name": function_name,
                    "arguments": json.dumps(function_args)
                }
            })
            messages.append({
                "role": "function", 
                "name": function_name,
                "content": json.dumps(function_result)
            })
            
            # Nueva llamada a OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",
                messages=messages,
                functions=functions,
                function_call="auto",
                temperature=0.1
            )
            
            # Actualizar costos
            cost_info = calculate_openai_cost(response)
            total_cost_info["api_calls"] += 1
            total_cost_info["total_tokens"] += cost_info["usage"]["total_tokens"]
            total_cost_info["prompt_tokens"] += cost_info["usage"]["prompt_tokens"] 
            total_cost_info["completion_tokens"] += cost_info["usage"]["completion_tokens"]
            total_cost_info["total_cost_usd"] += cost_info["cost_usd"]["total"]
            total_cost_info["calls_detail"].append({
                "call": total_cost_info["api_calls"],
                "function": function_name,
                "cost": cost_info["cost_usd"]["total"]
            })
        
        # Procesar respuesta final
        final_content = response.choices[0].message.content
        
        try:
            result = json.loads(final_content)
            
            # Agregar información adicional
            result["product_id"] = product_id
            result["timestamp"] = "2025-09-23T12:00:00Z"
            
            # Formatear información de costos  
            formatted_cost = format_cost_info(
                "gpt-4o-mini-2024-07-18",
                {
                    "prompt_tokens": total_cost_info["prompt_tokens"],
                    "completion_tokens": total_cost_info["completion_tokens"], 
                    "total_tokens": total_cost_info["total_tokens"]
                },
                total_cost_info["api_calls"]
            )
            
            result["openai_cost"] = formatted_cost
            
            return result
            
        except json.JSONDecodeError:
            return {
                "error": "Respuesta inválida de OpenAI",
                "raw_response": final_content,
                "text": text,
                "product_id": product_id,
                "taxonomy_id": taxonomy_id,
                "openai_cost": format_cost_info(
                    "gpt-4o-mini-2024-07-18",
                    {
                        "prompt_tokens": total_cost_info["prompt_tokens"],
                        "completion_tokens": total_cost_info["completion_tokens"],
                        "total_tokens": total_cost_info["total_tokens"]
                    },
                    total_cost_info["api_calls"]
                )
            }
            
    except Exception as e:
        return {
            "error": str(e),
            "text": text,
            "product_id": product_id,
            "taxonomy_id": taxonomy_id
        }

def classify_batch(products: List[Dict[str, str]], taxonomy_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Clasificar múltiples productos usando una taxonomía específica
    
    Args:
        products: Lista de dicts con 'text' y opcionalmente 'product_id'
        taxonomy_id: ID de taxonomía específica (opcional)
    
    Returns:
        Lista con resultados de clasificación
    """
    results = []
    
    print(f"🔄 Clasificando {len(products)} productos...")
    if taxonomy_id:
        print(f"📚 Usando taxonomía: {taxonomy_id}")
    else:
        print("📚 Usando taxonomía por defecto")
    
    for i, product in enumerate(products, 1):
        print(f"[{i}/{len(products)}] Clasificando: {product['text'][:50]}...")
        
        result = classify(
            text=product["text"],
            product_id=product.get("product_id"),
            taxonomy_id=taxonomy_id
        )
        
        results.append(result)
    
    print("✅ Clasificación en lotes completada")
    return results

def interactive_classification():
    """
    Modo interactivo para clasificación con selección de taxonomía
    """
    print("\n🏷️  CLASIFICADOR MULTI-TAXONOMÍA SKOS")
    print("=" * 50)
    
    # Mostrar taxonomías disponibles
    taxonomies = list_taxonomies()
    
    if not taxonomies:
        print("❌ No hay taxonomías disponibles. Configure al menos una taxonomía.")
        return
    
    # Permitir selección de taxonomía
    print("\n🎯 Opciones de clasificación:")
    print("1. Usar taxonomía por defecto")
    print("2. Seleccionar taxonomía específica")
    
    choice = input("\nSeleccione opción (1 o 2): ").strip()
    
    taxonomy_id = None
    if choice == "2":
        print("\n📚 Taxonomías disponibles:")
        for i, tax in enumerate(taxonomies, 1):
            print(f"{i}. {tax['name']} ({tax['id']})")
        
        try:
            tax_choice = int(input(f"\nSeleccione taxonomía (1-{len(taxonomies)}): "))
            if 1 <= tax_choice <= len(taxonomies):
                taxonomy_id = taxonomies[tax_choice - 1]["id"]
                print(f"✅ Taxonomía seleccionada: {taxonomies[tax_choice - 1]['name']}")
            else:
                print("❌ Selección inválida, usando taxonomía por defecto")
        except ValueError:
            print("❌ Entrada inválida, usando taxonomía por defecto")
    
    # Loop de clasificación
    print("\n💬 Ingrese productos para clasificar (escriba 'quit' para salir):")
    
    while True:
        text = input("\n🛍️  Producto: ").strip()
        
        if text.lower() in ['quit', 'salir', 'exit']:
            break
        
        if not text:
            continue
        
        print("🔄 Clasificando...")
        result = classify(text, taxonomy_id=taxonomy_id)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print("\n✅ Resultado:")
            print(f"   Categoría: {result.get('prefLabel', 'N/A')}")
            print(f"   Código: {result.get('notation', 'N/A')}")
            print(f"   Confianza: {result.get('confidence', 0):.2f}")
            print(f"   Taxonomía: {result.get('taxonomy_used', 'N/A')}")
            
            if "openai_cost" in result:
                cost = result["openai_cost"]
                print(f"   💰 Costo: ${cost['cost_usd']['total']:.6f}")

if __name__ == "__main__":
    interactive_classification()