from qdrant_client import QdrantClient
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def reset_db():
    qdrant_url = os.environ.get("QDRANT_URL")
    qdrant_api_key = os.environ.get("QDRANT_API_KEY")
    
    try:
        if qdrant_url:
            print(f"Connecting to Qdrant Cloud at {qdrant_url}...")
            client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            host = os.environ.get("QDRANT_HOST", "localhost")
            port = int(os.environ.get("QDRANT_PORT", 6333))
            print(f"Connecting to Local Qdrant at {host}:{port}...")
            client = QdrantClient(host=host, port=port)
        collection_name = "decision_snapshots"
        
        if client.collection_exists(collection_name):
            print(f"Deleting existing collection '{collection_name}'...")
            client.delete_collection(collection_name)
            print("Deleted.")
        else:
            print(f"Collection '{collection_name}' does not exist.")
            
        print("Reset complete. The application will recreate it on next startup with correct dimensions.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reset_db()
