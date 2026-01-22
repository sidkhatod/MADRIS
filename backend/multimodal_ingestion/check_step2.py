import sys
import os

# Adjust path to find sibling modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from multimodal_ingestion.case_study_ingestion import CaseStudyIngestor, TimePhase
from canonical_state.earthquake_state import EarthquakeSituation

def test_ingestion():
    print("Test 1: Ingesting a mock case study")
    
    # Mock Data with mixing of early and late info
    mock_data = {
        "identity": {
            "event_id": "case_TOK_2011",
            "magnitude": 9.0
        },
        "spatial": {
            "region_type": "coastal_urban"
        },
        "damage": {
            "building_collapse": "severe"
        },
        "actions": {
            "rescue": "deployed",
            "medical": "stabilizing_triage" 
        },
        "outcomes": {
            "casualties": 15000,
            "economic_loss": "catastrophic"
        }
    }
    
    ingestor = CaseStudyIngestor()
    slices = ingestor.ingest_case_study(mock_data)
    
    print(f"Generated {len(slices)} slices from mock data.")
    
    # Check T0
    t0 = next(s for s in slices if s.phase == TimePhase.T0_IMPACT)
    print("\nChecking T0 (Impact):")
    print(f" - Phase: {t0.situation.event_identity.phase}")
    print(f" - Casualties (Should be None): {t0.situation.outcomes.casualties}")
    print(f" - Medical Actions (Should be None): {t0.situation.actions_taken.medical_deployment}")
    
    assert t0.situation.outcomes.casualties is None, "ERROR: Future leakage (casualties) in T0"
    assert t0.situation.actions_taken.medical_deployment is None, "ERROR: Future leakage (medical) in T0"
    
    # Check T1
    t1 = next(s for s in slices if s.phase == TimePhase.T1_EARLY_RESPONSE)
    print("\nChecking T1 (Early Response):")
    print(f" - Rescue Actions: {t1.situation.actions_taken.rescue_operations.value}")
    print(f" - Medical Actions (Should be None): {t1.situation.actions_taken.medical_deployment}")
    print(f" - Casualties (Should be None): {t1.situation.outcomes.casualties}")

    assert t1.situation.actions_taken.rescue_operations.value == "deployed", "ERROR: Rescue missing in T1"
    assert t1.situation.outcomes.casualties is None, "ERROR: Future leakage in T1"

    # Check T3
    t3 = next(s for s in slices if s.phase == TimePhase.T3_OUTCOME)
    print("\nChecking T3 (Outcome):")
    print(f" - Casualties: {t3.situation.outcomes.casualties.value}")
    
    assert t3.situation.outcomes.casualties.value == 15000, "ERROR: Outcomes missing in T3"
    
    print("\nTest 2: Assertions Passed. Logic enforces temporal separation.")

if __name__ == "__main__":
    test_ingestion()
