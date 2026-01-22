import sys
import os

# Adjust path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from prediction.timeline_projection import TimelineProjector
from retrieval.similarity_engine import SimilarityResult
from memory.experience_unit import ExperienceUnit
from canonical_state.earthquake_state import EarthquakeSituation, Outcomes, UncertainProperty, DamageIndicators
from multimodal_ingestion.case_study_ingestion import TimePhase

def test_projection():
    print("Test 1: Project with mixed cohort")
    
    # Mock Candidates
    # Unit 1: T1 (Early Response) -> Fits 12-24h for T0 query
    sit1 = EarthquakeSituation(damage_indicators=DamageIndicators(building_collapse_severity=UncertainProperty("severe")))
    unit1 = ExperienceUnit(situation=sit1, phase=TimePhase.T1_EARLY_RESPONSE, source_case_id="c1", 
                           subsequent_outcomes=Outcomes(casualties=UncertainProperty(100)))
    res1 = SimilarityResult(experience_unit=unit1, score=0.9, dimension_scores={}, penalties=[])
    
    # Unit 2: T2 (Stabilization) -> Fits 24-48h for T0 query
    sit2 = EarthquakeSituation(damage_indicators=DamageIndicators(building_collapse_severity=UncertainProperty("moderate")))
    unit2 = ExperienceUnit(situation=sit2, phase=TimePhase.T2_STABILIZATION, source_case_id="c2",
                           subsequent_outcomes=Outcomes(casualties=UncertainProperty(500)))
    res2 = SimilarityResult(experience_unit=unit2, score=0.8, dimension_scores={}, penalties=[])
    
    projector = TimelineProjector()
    
    # Query: T0
    projections = projector.project_timeline(TimePhase.T0_IMPACT, [res1, res2])
    
    # Check 12-24h (Should get data from Unit 1)
    p1 = projections["12-24h"]
    print(f"12-24h Confidence: {p1.confidence_score}, Count: {p1.supporting_experience_count}")
    print(f"12-24h Collapse: {p1.collapse_progression}")
    
    assert p1.supporting_experience_count == 1
    assert p1.collapse_progression == "severe"
    
    # Check 24-48h (Should get data from Unit 2)
    p2 = projections["24-48h"]
    print(f"24-48h Casualties: {p2.casualty_range}")
    
    assert p2.supporting_experience_count == 1
    assert p2.casualty_range == "500 - 500"
    
    print("\nTest 2: Empty Cohort")
    empty_proj = projector.project_timeline(TimePhase.T0_IMPACT, [])
    assert empty_proj["0-12h"].confidence_score == 0.0
    print("Success: Handles empty cohort.")
    
    print("\nAll Tests Passed.")

if __name__ == "__main__":
    test_projection()
