import sys
import os
import json

# Adjust path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from output.response_formatter import ResponseFormatter, SystemResponse
from canonical_state.earthquake_state import EarthquakeSituation, EventIdentity, UncertainProperty
from prediction.timeline_projection import ProjectionResult
from reasoning.intervention_reasoner import InterventionRecommendation
from uncertainty.confidence_propagation import ConfidenceAssessment

def test_formatter():
    print("Test 1: Full System Response Formatting")
    
    # Mock Inputs
    sit = EarthquakeSituation(event_identity=EventIdentity(event_id="evt_test", magnitude=UncertainProperty(7.2), phase="immediate_impact"))
    
    # Mock Projections & Confidence
    projs = {
        "0-12h": ProjectionResult("0-12h", casualty_trend="stable", casualty_range="10-50", confidence_score=0.8, supporting_experience_count=5),
        "12-24h": ProjectionResult("12-24h", casualty_trend="increasing", casualty_range="50-100", confidence_score=0.6, supporting_experience_count=4)
    }
    
    proj_conf = {
        "0-12h": ConfidenceAssessment(0.8, "High", "Good data", []),
        "12-24h": ConfidenceAssessment(0.6, "Medium", "Variance", ["Variance detected"])
    }
    
    # Mock Interventions
    rec1 = InterventionRecommendation("deploy_search_rescue", "0-12h", "Associated with better outcomes", 0.7, 3)
    conf1 = ConfidenceAssessment(0.7, "Medium", "Limited data", ["Sparse data"])
    interventions = [(rec1, conf1)]
    
    cohort_meta = {"cohort_size": 5, "patterns": "Urban clustering"}
    
    formatter = ResponseFormatter()
    response = formatter.format_response(sit, projs, proj_conf, interventions, cohort_meta)
    
    # Verify Structure
    data = response.to_dict()
    print("Serialized Response Snippet:")
    print(json.dumps(data, indent=2)[:500] + "...")
    
    assert data["situation_summary"]["event_id"] == "evt_test"
    assert len(data["baseline_projections"]) == 2
    assert data["baseline_projections"][0]["confidence_label"] == "High"
    assert len(data["intervention_options"]) == 1
    assert data["intervention_options"][0]["action"] == "deploy_search_rescue"
    assert data["confidence_overview"]["overall_level"] == "Medium" # Min of 0.8 and 0.6 is 0.6 -> Medium
    assert "Variance detected" in data["confidence_overview"]["drivers"]
    
    print("\nTest 2: Assertions Passed")

if __name__ == "__main__":
    test_formatter()
