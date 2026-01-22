import sys
import os
from dataclasses import FrozenInstanceError

# Adjust path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from memory.experience_unit import ExperienceUnit
from multimodal_ingestion.case_study_ingestion import TimePhase, TimeSlice
from canonical_state.earthquake_state import EarthquakeSituation, Outcomes, UncertainProperty

def test_experience_unit():
    print("Test 1: Creation from TimeSlice")
    
    # Mock Data
    sit = EarthquakeSituation()
    sit.event_identity.event_id = "test_event_001"
    slice = TimeSlice(phase=TimePhase.T1_EARLY_RESPONSE, situation=sit, relative_time_label="12h")
    
    # Mock Outcomes (that happened AFTER)
    outcomes = Outcomes(casualties=UncertainProperty(value=100, source="final_report", confidence="high"))
    
    unit = ExperienceUnit.from_timeslice(slice, source_case_id="case_001", outcomes=outcomes)
    
    print(f"Success: Created unit for case {unit.source_case_id}, phase {unit.phase.value}")
    assert unit.situation.event_identity.event_id == "test_event_001"
    assert unit.subsequent_outcomes.casualties.value == 100
    
    print("\nTest 2: Immutability Check")
    try:
        unit.source_case_id = "hacked_id"
        print("ERROR: Mutation allowed!")
    except FrozenInstanceError:
        print("Success: Mutation prevented (FrozenInstanceError raised).")
    except Exception as e:
        print(f"Success: Mutation prevented ({type(e).__name__}).")

    print("\nTest 3: Serialization")
    data = unit.to_dict()
    print("Serialized snippet:", str(data)[:100] + "...")
    assert data["phase"] == "T1_EARLY_RESPONSE"
    assert data["subsequent_outcomes"]["casualties"]["value"] == 100
    
    print("\nTest 4: Assertions Passed")

if __name__ == "__main__":
    test_experience_unit()
