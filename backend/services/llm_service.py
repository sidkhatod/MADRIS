import os
import sys
import random
import requests
from typing import List, Optional

# Optional imports for specific providers to avoid hard crashes if not installed
try:
    from groq import Groq, GroqError
except ImportError:
    Groq = None
    GroqError = Exception

try:
    from openai import OpenAI, OpenAIError
except ImportError:
    OpenAI = None
    OpenAIError = Exception

class LLMClient:
    """
    Abstraction for LLM interactions.
    """
    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError

    def embed_text(self, text: str) -> List[float]:
        raise NotImplementedError

# --- Text Generation Providers ---

class GroqLLMClient(LLMClient):
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        # Updated to currently supported model (Jan 2026)
        self.model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        if not self.api_key:
            print("WARNING: GROQ_API_KEY not found in environment.")
        
        if Groq is None:
            raise RuntimeError("groq library not installed. pip install groq")
            
        self.client = Groq(api_key=self.api_key)

    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
            )
            return chat_completion.choices[0].message.content.strip()
        except GroqError as e:
            print(f"Groq API Error: {e}", file=sys.stderr)
            raise e
        except Exception as e:
            print(f"Unexpected Groq Error: {e}", file=sys.stderr)
            raise e

    def embed_text(self, text: str) -> List[float]:
        raise NotImplementedError("Groq does not support embeddings in this client.")

class OpenAITextClient(LLMClient):
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key: print("WARNING: OPENAI_API_KEY missing.")
        if OpenAI is None: raise RuntimeError("openai lib missing")
        self.client = OpenAI(api_key=self.api_key)

    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
        
    def embed_text(self, text: str) -> List[float]:
         raise NotImplementedError("Use OpenAIEmbeddingClient")

# --- Embedding Providers ---

class HuggingFaceEmbeddingClient(LLMClient):
    def __init__(self):
        self.api_token = os.environ.get("HF_API_TOKEN")
        # Switched to BAAI/bge-small-en-v1.5 (384 dim)
        # Updated URL to new router endpoint as api-inference.huggingface.co is deprecated (410 Gone)
        self.api_url = "https://router.huggingface.co/hf-inference/models/BAAI/bge-small-en-v1.5"
        
        if not self.api_token:
            print("CRITICAL: HF_API_TOKEN not found via environment variable.")
            # We don't raise here to allow instantiation, but methods will fail.
            # However, the factory is where we typically want to fail fast if this is the chosen provider.

    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError("This client is for embeddings only.")

    def embed_text(self, text: str) -> List[float]:
        if not self.api_token:
            raise RuntimeError("HF_API_TOKEN required for embeddings.")
            
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        payload = {"inputs": text}
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Prompt requirement: embedding = response[0]
            # We assume the API returns [ [embedding_values] ] for a single string input
            # or sometimes just [embedding_values] depending on exact pipeline quirks.
            # But the prompt explicitly said: Parse the response as: embedding = response[0]
            
            if isinstance(data, list) and len(data) > 0:
                # Security check to ensure we are getting the vector
                embedding = data
                if isinstance(data[0], list):
                    embedding = data[0]
                elif isinstance(data[0], float):
                    # In case it returns the flat vector directly (unlikely for this pipeline endpoint but possible)
                    embedding = data
                
                # Verify dimension if we can, but primarily return it
                return embedding
            
            raise ValueError(f"Unexpected HF response format: {data}")
            
        except Exception as e:
            print(f"HF Embedding Error: {e}", file=sys.stderr)
            raise e

class OpenAIEmbeddingClient(LLMClient):
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if OpenAI is None: raise RuntimeError("openai lib missing")
        self.client = OpenAI(api_key=self.api_key)

    def generate_text(self, p: str, s: str = "") -> str: raise NotImplementedError
    
    def embed_text(self, text: str) -> List[float]:
        resp = self.client.embeddings.create(input=text, model="text-embedding-3-small")
        return resp.data[0].embedding

# --- Composite Client ---

class CompositeLLMClient(LLMClient):
    """
    Routes requests to specific providers.
    """
    def __init__(self, text_provider: LLMClient, embedding_provider: LLMClient):
        self.text_provider = text_provider
        self.embedding_provider = embedding_provider

    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        return self.text_provider.generate_text(prompt, system_prompt)

    def embed_text(self, text: str) -> List[float]:
        return self.embedding_provider.embed_text(text)

class MockLLMClient(LLMClient):
    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        if "snapshot" in prompt.lower(): return self._mock_snapshot_json()
        return "Mock response based on Groq/HF structure."
    def embed_text(self, text: str) -> List[float]:
        return [random.random() for _ in range(384)] # Match HF dim
    def _mock_snapshot_json(self) -> str:
        import json
        return json.dumps([{
            "inferred_time_window": "mock time",
            "decision_context": "mock context",
            "uncertainties": [], "risks_perceived": [], "actions_considered": [], "action_taken_narrative": "mock action"
        }])

# --- Factory ---

def create_llm_client() -> LLMClient:
    """
    Factory to assemble the client based on env vars.
    TEXT_LLM_PROVIDER: groq | openai | mock
    EMBEDDING_PROVIDER: huggingface | openai | mock
    """
    text_mode = os.environ.get("TEXT_LLM_PROVIDER", "groq").lower()
    embed_mode = os.environ.get("EMBEDDING_PROVIDER", "huggingface").lower()
    
    if os.environ.get("MOCK_MODE") == "true": 
        return MockLLMClient()

    # Init Text Provider
    if text_mode == "groq":
        text_client = GroqLLMClient()
    elif text_mode == "openai":
        text_client = OpenAITextClient()
    elif text_mode == "mock":
        return MockLLMClient() # Short curcuit
    else:
        raise ValueError(f"Unknown TEXT_LLM_PROVIDER: {text_mode}")

    # Init Embedding Provider
    if embed_mode == "huggingface":
        embed_client = HuggingFaceEmbeddingClient()
    elif embed_mode == "openai":
        embed_client = OpenAIEmbeddingClient()
    else:
        raise ValueError(f"Unknown EMBEDDING_PROVIDER: {embed_mode}")

    return CompositeLLMClient(text_provider=text_client, embedding_provider=embed_client)
