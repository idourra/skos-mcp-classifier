# client/classify_responses_api.py
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8080")

def classify(text: str):
    payload = {
      "model": "o4-mini",
      "input": f"Clasifica el producto: {text}",
      "tools": [
        {
          "type": "mcp",
          "server_label": "skos-taxonomy",
          "server_url": SERVER_URL,
          "require_approval": "never"
        }
      ],
      "instructions": (
        "Usa las herramientas MCP 'search_concepts' y 'get_context' "
        "para seleccionar el mejor concepto SKOS (Treew). Devuelve JSON con: "
        "search_text, concept_uri, prefLabel, notation, level, confidence (0-1)."
      )
    }
    r = requests.post("https://api.openai.com/v1/responses",
                      headers={"Authorization": f"Bearer {OPENAI_API_KEY}",
                               "Content-Type": "application/json"},
                      data=json.dumps(payload))
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    print(json.dumps(classify("yogur natural 125g sin azúcar"), indent=2, ensure_ascii=False))
