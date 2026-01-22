from typing import List, Dict, Any, Optional
import json
import uuid
from dataclasses import asdict

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct, VectorParams, Distance
except ImportError:
    # Fallback for environments without qdrant_client installed (Mocking for structural correctness)
    # Fallback for environments without qdrant_client installed (Mocking for structural correctness)
    class QdrantClient:
        def __init__(self, location=None, **kwargs): 
            self.collections = {}
        def recreate_collection(self, collection_name, **kwargs): 
            self.collections[collection_name] = []
        def upsert(self, collection_name, points, **kwargs):
            if collection_name not in self.collections:
                self.collections[collection_name] = []
            self.collections[collection_name].extend(points)
        def search(self, collection_name, query_vector, limit=5, **kwargs):
            # purely mock return of what was stored, no actual vector search in mock
            # return the LAST N items (most recent) to simulate finding the 'current' relevant thing in sequential tests
            items = self.collections.get(collection_name, [])
            return [
                type('ScoredPoint', (object,), {"payload": p.payload, "score": 1.0})() 
                for p in items[::-1][:limit]
            ]
    class PointStruct:
        def __init__(self, id, vector, payload, **kwargs):
            self.id = id
            self.vector = vector
            self.payload = payload
    class VectorParams:
        def __init__(self, **kwargs): pass
    class Distance:
        COSINE = "Cosine"

from memory.experience_unit import ExperienceUnit
from multimodal_ingestion.case_study_ingestion import TimePhase, TimeSlice
from canonical_state.earthquake_state import (
    EarthquakeSituation, EventIdentity, SpatialContext, HumanExposure, 
    BuiltEnvironment, DamageIndicators, ActionsTaken, Outcomes, UncertainProperty
)

class QdrantMemory:
    """
    Long-term memory layer using Qdrant.
    Responsible for storage and raw retrieval of ExperienceUnits.
    Does NOT perform ranking or reasoning.
    """

    def __init__(self, collection_name: str = "earthquake_experiences", location: str = ":memory:"):
        """
        Initialize Qdrant client. Defaults to in-memory for development/testing.
        """
        self.client = QdrantClient(location=location)
        self.collection_name = collection_name
        self._ensure_collection()

    def _ensure_collection(self, vector_size: int = 384): # Defaulting to a common size, but should be dynamic
        """
        Ensures the collection exists. 
        Note: In a real system, vector_size should match the encoder. 
        Here we assume a fixed size or handle it dynamically if recreating.
        """
        # For this step, we just ensure it exists or recreate it safe for testing.
        # In prod, we wouldn't recreate on every init.
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

    def store_experience(self, unit: ExperienceUnit, vector: List[float]):
        """
        Stores an ExperienceUnit with its associated vector embedding.
        The vector represents the 'situation' at time T.
        """
        # Serialize payloads
        payload = unit.to_dict()
        
        # Determine ID (using UUID based on source_case_id + phase to be deterministic or random)
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{unit.source_case_id}_{unit.phase.value}"))

        point = PointStruct(
            id=point_id,
            vector=vector,
            payload=payload
        )

        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

    def retrieve_candidates(self, vector: List[float], limit: int = 5) -> List[ExperienceUnit]:
        """
        Performs raw KNN search to find similar experiences.
        Returns reconstructed ExperienceUnits.
        """
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit
        )

        results = []
        for hit in search_result:
            if hit.payload:
                restored_unit = self._reconstruct_experience_unit(hit.payload)
                results.append(restored_unit)
        
        return results

    def _reconstruct_experience_unit(self, payload: Dict[str, Any]) -> ExperienceUnit:
        """
        Reconstructs an ExperienceUnit from the dictionary payload.
        Manual reconstruction required since Step 1 classes might not have robust from_dict methods.
        """
        sit_dict = payload.get("situation", {})
        situation = self._reconstruct_situation(sit_dict)
        
        outcomes_dict = payload.get("subsequent_outcomes")
        outcomes = self._reconstruct_outcomes(outcomes_dict) if outcomes_dict else None
        
        return ExperienceUnit(
            situation=situation,
            phase=TimePhase(payload["phase"]),
            source_case_id=payload["source_case_id"],
            subsequent_outcomes=outcomes
        )

    # --- Reconstruction Helpers ---
    # Because Step 1 classes strictly use Optional[UncertainProperty[T]], we need to match that.

    def _uprop(self, data: Optional[Dict], type_func=lambda x: x) -> Optional[UncertainProperty]:
        if not data:
            return None
        return UncertainProperty(
            value=type_func(data["value"]) if data.get("value") is not None else None,
            source=data.get("source", "unknown"),
            confidence=data.get("confidence", "unknown")
        )

    def _uprop_list(self, data_list: List[Dict], type_func=lambda x: x) -> List[UncertainProperty]:
        if not data_list:
            return []
        return [self._uprop(item, type_func) for item in data_list if item] # type: ignore

    def _reconstruct_situation(self, data: Dict[str, Any]) -> EarthquakeSituation:
        sit = EarthquakeSituation()
        
        eid = data.get("event_identity", {})
        sit.event_identity = EventIdentity(
            event_id=eid.get("event_id"),
            event_type=eid.get("event_type", "earthquake"),
            magnitude=self._uprop(eid.get("magnitude"), float),
            intensity=self._uprop(eid.get("intensity"), str),
            phase=eid.get("phase"),
            # timestamp handling omitted for brevity/safety unless needed
            time_since_event_hours=eid.get("time_since_event_hours")
        )

        sp = data.get("spatial_context", {})
        sit.spatial_context = SpatialContext(
            region_type=self._uprop(sp.get("region_type")),
            terrain=self._uprop(sp.get("terrain")),
            secondary_hazards=self._uprop_list(sp.get("secondary_hazards", [])),
            location_description=sp.get("location_description")
        )

        he = data.get("human_exposure", {})
        sit.human_exposure = HumanExposure(
            population_density=self._uprop(he.get("population_density")),
            vulnerable_groups=self._uprop_list(he.get("vulnerable_groups", [])),
            time_of_day_context=he.get("time_of_day_context")
        )

        be = data.get("built_environment", {})
        sit.built_environment = BuiltEnvironment(
            dominant_building_types=self._uprop_list(be.get("dominant_building_types", [])),
            construction_quality=self._uprop(be.get("construction_quality")),
            critical_infrastructure_status={
                k: self._uprop(v) for k, v in be.get("critical_infrastructure_status", {}).items() # type: ignore
            }
        )

        di = data.get("damage_indicators", {})
        sit.damage_indicators = DamageIndicators(
            building_collapse_severity=self._uprop(di.get("building_collapse_severity")),
            access_disruption=self._uprop(di.get("access_disruption")),
            utility_failures=self._uprop_list(di.get("utility_failures", [])),
            visible_hazards=self._uprop_list(di.get("visible_hazards", []))
        )

        at = data.get("actions_taken", {})
        sit.actions_taken = ActionsTaken(
            rescue_operations=self._uprop(at.get("rescue_operations")),
            evacuation_status=self._uprop(at.get("evacuation_status")),
            medical_deployment=self._uprop(at.get("medical_deployment")),
            logistics_coordination=self._uprop(at.get("logistics_coordination"))
        )
        
        # Outcomes inside situation (if any, though structurally rarely used in situation itself vs subsequent)
        out = data.get("outcomes", {})
        sit.outcomes = self._reconstruct_outcomes(out) if out else Outcomes()

        return sit

    def _reconstruct_outcomes(self, data: Dict[str, Any]) -> Outcomes:
        return Outcomes(
            casualties=self._uprop(data.get("casualties"), int),
            injuries=self._uprop(data.get("injuries"), int),
            displacement=self._uprop(data.get("displacement"), int),
            economic_loss=self._uprop(data.get("economic_loss"))
        )
