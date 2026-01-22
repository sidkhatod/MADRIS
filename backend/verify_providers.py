import os
import sys
from dotenv import load_dotenv
load_dotenv()

from services.llm_service import create_llm_client

def verify_providers():
    print("1. Checking Environment Variables...")
    groq_key = os.environ.get("GROQ_API_KEY")
    hf_token = os.environ.get("HF_API_TOKEN")
    
    if groq_key:
        print(f"   [OK] GROQ_API_KEY found ({groq_key[:5]}...)")
    else:
        print("   [FAIL] GROQ_API_KEY not found!")
        
    if hf_token:
        print(f"   [OK] HF_API_TOKEN found ({hf_token[:5]}...)")
    else:
        print("   [FAIL] HF_API_TOKEN not found!")

    print("\n2. Initializing LLM Client...")
    try:
        client = create_llm_client()
        print(f"   [OK] Client initialized: {type(client).__name__}")
    except Exception as e:
        print(f"   [FAIL] Client initialization failed: {e}")
        return

    print("\n3. Testing Text Generation (Groq)...")
    try:
        text = client.generate_text("Say 'Hello Antigravity' and nothing else.")
        print(f"   [OK] Generated text: '{text}'")
    except Exception as e:
        print(f"   [FAIL] Text generation failed: {e}")

    print("\n4. Testing Embedding (HuggingFace)...")
    try:
        vector = client.embed_text("Test embedding")
        print(f"   [OK] Embedding generated. Dimension: {len(vector)}")
        if len(vector) == 384:
            print("   [OK] Dimension matches expected (384).")
        else:
            print(f"   [WARN] Dimension mismatch! Expected 384, got {len(vector)}")
    except Exception as e:
        print(f"   [FAIL] Embedding failed: {e}")

if __name__ == "__main__":
    verify_providers()
