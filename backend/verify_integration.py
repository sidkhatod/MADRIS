import os
import sys

def verify_env():
    print("1. Checking Environment Variables...")
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        print(f"   [OK] OPENAI_API_KEY found ({api_key[:5]}...)")
    else:
        print("   [FAIL] OPENAI_API_KEY not found!")

    print("\n2. Checking Libraries...")
    try:
        import openai
        print(f"   [OK] openai library found (v{openai.__version__})")
    except ImportError:
        print("   [FAIL] openai library NOT found")

    try:
        import qdrant_client
        print(f"   [OK] qdrant_client library found (v{qdrant_client.__version__})")
    except ImportError:
        print("   [FAIL] qdrant_client library NOT found")

    print("\n3. Checking Qdrant Connection (localhost:6333)...")
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(host="localhost", port=6333)
        cols = client.get_collections()
        print(f"   [OK] Connected to Qdrant. Collections: {[c.name for c in cols.collections]}")
    except Exception as e:
        print(f"   [FAIL] Could not connect to Qdrant: {e}")

if __name__ == "__main__":
    verify_env()
