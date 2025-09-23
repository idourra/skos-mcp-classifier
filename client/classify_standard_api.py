# client/classify_standard_api.py
import os
import requests
import json
from dotenv import load_dotenv
from openai import OpenAI
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.openai_cost_calculator import calculate_openai_cost, format_cost_info

# Load environment variables from .env file
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8080")

def search_concepts(query: str, lang: str = "es", k: int = 10):
    """Search for SKOS concepts using the MCP server"""
    response = requests.post(
        f"{SERVER_URL}/tools/search_concepts",
        headers={"Content-Type": "application/json"},
        json={"query": query, "lang": lang, "k": k}
    )
    response.raise_for_status()
    return response.json()

def get_context(concept_uri: str):
    """Get detailed context for a SKOS concept"""
    response = requests.post(
        f"{SERVER_URL}/tools/get_context",
        headers={"Content-Type": "application/json"},
        json={"concept_uri": concept_uri}
    )
    response.raise_for_status()
    return response.json()

def classify(text: str, product_id: str = None):
    """Classify a product using OpenAI with function calling to access SKOS taxonomy
    
    Args:
        text (str): Product description to classify
        product_id (str, optional): Optional ID/SKU to include in the result
        
    Returns:
        dict: Classification result including product_id and OpenAI cost information
    """

    # Variables for cost tracking
    total_prompt_tokens = 0
    total_completion_tokens = 0
    model_used = "gpt-4o-mini"
    api_calls_count = 0

    # Define the functions that OpenAI can call
    functions = [
        {
            "name": "search_concepts",
            "description": "Search for SKOS concepts in the taxonomy",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for finding relevant concepts"
                    },
                    "lang": {
                        "type": "string",
                        "description": "Language code (es for Spanish)",
                        "default": "es"
                    },
                    "k": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "get_context",
            "description": "Get detailed context for a specific SKOS concept",
            "parameters": {
                "type": "object",
                "properties": {
                    "concept_uri": {
                        "type": "string",
                        "description": "URI of the concept to get context for"
                    }
                },
                "required": ["concept_uri"]
            }
        }
    ]
    
    # Start the conversation
    messages = [
        {
            "role": "system",
            "content": (
                "Eres un clasificador experto de productos que usa una taxonomía SKOS. "
                "Tu tarea es clasificar productos alimentarios usando las funciones disponibles. "
                "Primero busca conceptos relevantes, luego obtén el contexto del mejor concepto, "
                "y finalmente devuelve un JSON con: search_text, concept_uri, prefLabel, notation, level, confidence (0-1). "
                "Si se proporciona un ID de producto, inclúyelo como 'product_id' en la respuesta."
            )
        },
        {
            "role": "user",
            "content": f"Clasifica el producto: {text}" + (f" [ID: {product_id}]" if product_id else "")
        }
    ]
    
    # First API call
    response = client.chat.completions.create(
        model=model_used,
        messages=messages,
        functions=functions,
        function_call="auto"
    )
    
    # Track tokens from first call (using real OpenAI response data)
    api_calls_count += 1
    if hasattr(response, 'usage') and response.usage:
        total_prompt_tokens += response.usage.prompt_tokens
        total_completion_tokens += response.usage.completion_tokens
        # Update model_used with exact model from response
        if hasattr(response, 'model'):
            model_used = response.model
    
    # Process function calls
    while response.choices[0].message.function_call:
        function_call = response.choices[0].message.function_call
        function_name = function_call.name
        function_args = json.loads(function_call.arguments)
        
        # Execute the function
        if function_name == "search_concepts":
            function_result = search_concepts(**function_args)
        elif function_name == "get_context":
            function_result = get_context(**function_args)
        else:
            function_result = {"error": f"Unknown function: {function_name}"}
        
        # Add the function call and result to the conversation
        messages.append({
            "role": "assistant",
            "content": None,
            "function_call": {
                "name": function_name,
                "arguments": function_call.arguments
            }
        })
        messages.append({
            "role": "function",
            "name": function_name,
            "content": json.dumps(function_result)
        })
        
        # Continue the conversation
        response = client.chat.completions.create(
            model=model_used,
            messages=messages,
            functions=functions,
            function_call="auto"
        )
        
        # Track tokens from continuation calls (using real OpenAI response data)
        api_calls_count += 1
        if hasattr(response, 'usage') and response.usage:
            total_prompt_tokens += response.usage.prompt_tokens
            total_completion_tokens += response.usage.completion_tokens
    
    # Parse the final response
    final_content = response.choices[0].message.content
    
    # Calculate total cost using real token usage from OpenAI
    cost_info = None
    if total_prompt_tokens > 0 or total_completion_tokens > 0:
        try:
            # Use the exact model name returned by OpenAI for accurate pricing
            cost_info = calculate_openai_cost(model_used, total_prompt_tokens, total_completion_tokens)
        except Exception as e:
            print(f"Warning: Could not calculate cost: {e}")
    
    # Try to extract JSON from the response
    try:
        # Find JSON in the response
        start_idx = final_content.find('{')
        end_idx = final_content.rfind('}') + 1
        if start_idx != -1 and end_idx != -1:
            json_str = final_content[start_idx:end_idx]
            result = json.loads(json_str)
            
            # Add product_id to result if provided
            if product_id:
                result['product_id'] = product_id
                
            # Add cost information if available (using real OpenAI usage data)
            if cost_info:
                result['openai_cost'] = format_cost_info(cost_info)
                result['openai_cost']['api_calls'] = api_calls_count  # Track number of API calls
                
            return result
        else:
            result = {"error": "No JSON found in response", "raw_response": final_content}
            if product_id:
                result['product_id'] = product_id
            if cost_info:
                result['openai_cost'] = format_cost_info(cost_info)
                result['openai_cost']['api_calls'] = api_calls_count
            return result
    except json.JSONDecodeError:
        result = {"error": "Invalid JSON in response", "raw_response": final_content}
        if product_id:
            result['product_id'] = product_id
        if cost_info:
            result['openai_cost'] = format_cost_info(cost_info)
            result['openai_cost']['api_calls'] = api_calls_count
        return result

if __name__ == "__main__":
    result = classify("yogur natural 125g sin azúcar")
    print(json.dumps(result, indent=2, ensure_ascii=False))