import sys
import os

# Adjust path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from uncertainty.confidence_propagation import ConfidenceIntegrator
from prediction.timeline_projection import ProjectionResult
from reasoning.intervention_reasoner import InterventionRecommendation

def test_confidence_propagation():
    print("Test 1: Project Calibration (Low Data)")
    
    # Raw result from Step 6 (High score but low count - simulated anomaly or single strong match)
    proj = ProjectionResult(
        horizon_label="0-12h",
        casualty_range="100-100", # exact match from 1 case
        confidence_score=0.9, 
        supporting_experience_count=1
    )
    
    integrator = ConfidenceIntegrator()
    projections = {"0-12h": proj}
    
    ass = integrator.calibrate_projections(projections)["0-12h"]
    
    print(f"Original Score: {proj.confidence_score}")
    print(f"Calibrated Score: {ass.score}")
    print(f"Label: {ass.label}")
    print(f"Explanation: {ass.explanation}")
    
    # Check penalty was applied for single data point
    assert ass.score < 0.9, "Score should be penalized for count=1"
    assert "Sparse data" in ass.drivers or "Single data point" in str(ass.drivers)
    
    print("\nTest 2: Intervention Cap (Monotonicity)")
    
    # Intervention with originally HIGH confidence
    rec = InterventionRecommendation(
        action_name="evacuation",
        suggested_time_window="0-12h",
        comparative_effect="good",
        confidence_score=0.95,
        supporting_experience_count=10
    )
    
    # Baseline with LOW confidence (e.g. 0.3)
    # The intervention confidence generally shouldn't exceed the foundational understanding of the situation
    base_ass = {"0-12h": integrator._assess_projection(ProjectionResult(horizon_label="0-12h", confidence_score=0.3, supporting_experience_count=5))}
    # Note: Using helper meant for internal but accessible for setup
    
    results = integrator.calibrate_interventions([rec], base_ass)
    rec_out, assess_out = results[0]
    
    print(f"Baseline Ceiling: 0.3 (approx)")
    print(f"Intervention Raw: 0.95")
    print(f"Intervention Final: {assess_out.score}")
    print(f"Drivers: {assess_out.drivers}")
    
    assert assess_out.score <= 0.35, "Intervention confidence should be capped by baseline (allowing small floating point margin)"
    assert "Capped by baseline" in str(assess_out.drivers)
    
    print("\nAll Tests Passed.")

if __name__ == "__main__":
    test_confidence_propagation()
