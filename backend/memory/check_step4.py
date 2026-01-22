import sys
import os
import random

# Adjust path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from memory.experience_unit import ExperienceUnit
from multimodal_ingestion.case_study_ingestion import TimePhase, TimeSlice
from canonical_state.earthquake_state import EarthquakeSituation, Outcomes, UncertainProperty, EventIdentity
from memory.qdrant_interface import QdrantMemory

def test_qdrant_integration():
    print("Test 1: Initialize Qdrant Memory")
    # use :memory: for testing
    memory = QdrantMemory(location=":memory:") 
    print("Success: QdrantMemory initialized.")

    print("\nTest 2: Store an Experience")
    # Create valid ExperienceUnit
    sit = EarthquakeSituation(
        event_identity=EventIdentity(
            event_id="test_case_A",
            magnitude=UncertainProperty(value=6.5, source="USGS"),
            phase="immediate_impact"
        )
    )
    slice = TimeSlice(phase=TimePhase.T0_IMPACT, situation=sit)
    unit = ExperienceUnit.from_timeslice(slice, source_case_id="case_A")
    
    # Mock Vector (random)
    mock_vector = [random.random() for _ in range(384)]
    
    memory.store_experience(unit, mock_vector)
    print("Success: Experience stored.")

    print("\nTest 3: Retrieve and Reconstruct")
    # Retrieve using the same vector (should match perfectly in exact search/small data)
    results = memory.retrieve_candidates(mock_vector, limit=1)
    
    if not results:
        print("FAILURE: No results found.")
        return

    retrieved_unit = results[0]
    print(f"Retrieved Unit Phase: {retrieved_unit.phase}")
    print(f"Retrieved Unit Source Case: {retrieved_unit.source_case_id}")
    print(f"Retrieved Magnitude: {retrieved_unit.situation.event_identity.magnitude.value}")

    assert retrieved_unit.source_case_id == "case_A"
    assert retrieved_unit.phase == TimePhase.T0_IMPACT
    assert retrieved_unit.situation.event_identity.magnitude.value == 6.5
    
    print("\nTest 4: Verify Full Reconstruction (Outcomes)")
    # Store another one with outcomes
    sit2 = EarthquakeSituation(event_identity=EventIdentity(event_id="test_case_B"))
    out2 = Outcomes(casualties=UncertainProperty(value=50))
    slice2 = TimeSlice(phase=TimePhase.T3_OUTCOME, situation=sit2)
    unit2 = ExperienceUnit.from_timeslice(slice2, source_case_id="case_B", outcomes=out2)
    mock_vector_2 = [0.1] * 384
    
    memory.store_experience(unit2, mock_vector_2)
    results2 = memory.retrieve_candidates(mock_vector_2, limit=1)
    retrieved_unit_2 = results2[0]
    
    print(f"Retrieved 2 outcome casualties: {retrieved_unit_2.subsequent_outcomes.casualties.value}")
    assert retrieved_unit_2.subsequent_outcomes.casualties.value == 50
    
    print("\nAll Tests Passed: Storage, Retrieval, and Reconstruction working.")

if __name__ == "__main__":
    test_qdrant_integration()
