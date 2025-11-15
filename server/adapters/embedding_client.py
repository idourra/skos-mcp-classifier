"""
Embedding Client - Adapter for text embedding generation
Encapsulates OpenAI embeddings API (or other providers)
"""
import os
from typing import List, Optional
from dotenv import load_dotenv

from server.domain.models import TextEmbedding

# Load environment variables
load_dotenv()


class EmbeddingClient:
    """Client for generating text embeddings - Adapter pattern"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "text-embedding-3-small"  # Default model
        self._client = None
    
    def _get_client(self):
        """Lazy load OpenAI client"""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("OpenAI package not installed. Run: pip install openai")
        return self._client
    
    def embed_text(self, text: str) -> TextEmbedding:
        """
        Generate embedding for a text
        
        Args:
            text: Text to embed
            
        Returns:
            TextEmbedding domain model
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        client = self._get_client()
        
        # Call OpenAI embeddings API
        response = client.embeddings.create(
            model=self.model,
            input=text
        )
        
        # Extract embedding vector
        embedding_vector = response.data[0].embedding
        
        return TextEmbedding(
            text=text,
            embedding=embedding_vector,
            model=self.model
        )
    
    def embed_batch(self, texts: List[str]) -> List[TextEmbedding]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of TextEmbedding domain models
        """
        if not texts:
            return []
        
        client = self._get_client()
        
        # Call OpenAI embeddings API with batch
        response = client.embeddings.create(
            model=self.model,
            input=texts
        )
        
        # Create TextEmbedding objects
        results = []
        for i, embedding_data in enumerate(response.data):
            results.append(TextEmbedding(
                text=texts[i],
                embedding=embedding_data.embedding,
                model=self.model
            ))
        
        return results


# Global instance
embedding_client = EmbeddingClient()
