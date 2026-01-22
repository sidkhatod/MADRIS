import os
import sys
from typing import List, Dict, Any, Optional
import uuid
from core.domain import DecisionSnapshot

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct, VectorParams, Distance
except ImportError:
    # We must have qdrant_client installed for this step as per requirements
    raise RuntimeError("qdrant_client library not installed. Please install it.")

class MemoryService:
    def __init__(self, collection_name: str = "decision_snapshots"):
        self.collection_name = collection_name
        
        # Load config from env
        qdrant_url = os.environ.get("QDRANT_URL")
        qdrant_api_key = os.environ.get("QDRANT_API_KEY")
        
        try:
            if qdrant_url:
                print(f"Connecting to Qdrant Cloud at {qdrant_url}...")
                self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
            else:
                host = os.environ.get("QDRANT_HOST", "localhost")
                port = int(os.environ.get("QDRANT_PORT", 6333))
                print(f"Connecting to Local Qdrant at {host}:{port}...")
                self.client = QdrantClient(host=host, port=port)

            self._ensure_collection()
            print("Qdrant connection successful.")
        except Exception as e:
            print(f"Failed to connect to Qdrant or ensure collection: {e}", file=sys.stderr)
            raise e

    def _ensure_collection(self):
        # Check if collection exists
        if not self.client.collection_exists(self.collection_name):
            print(f"Collection '{self.collection_name}' not found. Creating...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
        else:
             print(f"Collection '{self.collection_name}' exists.")
             # Optionally verify vector size matches if we were being very strict

    def store_snapshots(self, snapshots: List[DecisionSnapshot], embeddings: List[List[float]]):
        if not snapshots:
            print("Warning: No snapshots to store.")
            return

        points = []
        for snap, vector in zip(snapshots, embeddings):
            # Minimal payload as requested
            payload = {
                "snapshot_id": snap.snapshot_id,
                "case_study_id": snap.case_study_id,
                "inferred_time_window": snap.inferred_time_window,
                "source_pdf": snap.source_pdf,
                "full_narrative_dump": snap.to_dict() # Storing full data for retrieval reconstruction
            }
            
            points.append(PointStruct(
                id=str(uuid.uuid4()), # Unique vector ID
                vector=vector,
                payload=payload
            ))
            
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def retrieve_relevant(self, query_vector: List[float], limit: int = 5) -> List[tuple[DecisionSnapshot, float]]:
        # Using query_points as search() appears unavailable in this version
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True
        )
        
        results = []
        for hit in response.points:
            if hit.payload:
                data = hit.payload.get("full_narrative_dump", {})
                snap = DecisionSnapshot(
                    snapshot_id=data.get("snapshot_id"),
                    case_study_id=data.get("case_study_id"),
                    source_pdf=data.get("source_pdf"),
                    inferred_time_window=data.get("inferred_time_window"),
                    location_context=data.get("location_context"),
                    decision_context=data.get("decision_context"),
                    uncertainties=data.get("uncertainties"),
                    risks_perceived=data.get("risks_perceived"),
                    actions_considered=data.get("actions_considered"),
                    action_taken_narrative=data.get("action_taken_narrative")
                )
                results.append((snap, hit.score))
        return results
