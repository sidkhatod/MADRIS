from qdrant_client import QdrantClient
import os

host = os.environ.get("QDRANT_HOST", "localhost")
port = int(os.environ.get("QDRANT_PORT", 6333))

client = QdrantClient(host=host, port=port)

print("Client type:", type(client))
print("Methods:")
for method in dir(client):
    if "search" in method or "query" in method:
        print(f" - {method}")
