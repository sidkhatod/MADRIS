import sys
import os

# Adjust path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from retrieval.similarity_engine import SimilarityEngine
from canonical_state.earthquake_state import EarthquakeSituation, EventIdentity, SpatialContext, UncertainProperty, BuiltEnvironment, HumanExposure
from memory.experience_unit import ExperienceUnit
from multimodal_ingestion.case_study_ingestion import TimePhase

def test_similarity():
    print("Test 1: Identical Match (Should be near 1.0)")
    
    # Base Situation
    sit_a = EarthquakeSituation(
        event_identity=EventIdentity(magnitude=UncertainProperty(7.0), phase="immediate_impact"),
        spatial_context=SpatialContext(region_type=UncertainProperty("urban")),
        human_exposure=HumanExposure(population_density=UncertainProperty("dense")),
        built_environment=BuiltEnvironment(dominant_building_types=[UncertainProperty("concrete")])
    )
    
    # Candidate Unit (Identical)
    unit_a = ExperienceUnit(situation=sit_a, phase=TimePhase.T0_IMPACT, source_case_id="case_A")
    
    engine = SimilarityEngine()
    result = engine.compute_similarity(sit_a, unit_a)
    
    print(f"Score: {result.score}")
    print(f"Dims: {result.dimension_scores}")
    print(f"Penalties: {result.penalties}")
    
    # Score might not be perfectly 1.0 if defaults are involved for empty fields, 
    # but magnitude and region match perfectly.
    assert result.score > 0.8, "Score should be high for identical input"
    assert "scale" in result.dimension_scores
    
    print("\nTest 2: Magnitude Difference & Phase Mismatch")
    
    # Query: Mag 7.0, IMPACT
    # Cand: Mag 5.0, OUTCOME (Significant Diff + Phase Penalty)
    
    sit_b = EarthquakeSituation(
        event_identity=EventIdentity(magnitude=UncertainProperty(5.0), phase="outcome"), # Mismatch implicitly in structure?
        # Actually unit_b handles phase context
    )
    unit_b = ExperienceUnit(situation=sit_b, phase=TimePhase.T3_OUTCOME, source_case_id="case_B")
    
    # Query (still sit_a): Mag 7.0, "immediate_impact"
    
    result_b = engine.compute_similarity(sit_a, unit_b)
    
    print(f"Score B: {result_b.score}")
    print(f"Dims B: {result_b.dimension_scores}")
    print(f"Penalties B: {result_b.penalties}")
    
    # Magnitude delta 2.0 -> Score 1.0 - (2.0/3.0) = 0.33 for scale
    # Phase mismatch "immediate_impact" vs T3_OUTCOME -> Penalty applied (0.8x)
    
    expected_scale_score = max(0.0, 1.0 - (2.0 / 3.0))
    assert abs(result_b.dimension_scores["scale"] - expected_scale_score) < 0.01, f"Scale score mismatch {result_b.dimension_scores['scale']}"
    assert len(result_b.penalties) > 0, "Phase penalty should be applied"
    
    print("\nTest 3: Ranking")
    candidates = [unit_a, unit_b]
    ranked = engine.rank_candidates(sit_a, candidates)
    
    print(f"Top 1: {ranked[0].experience_unit.source_case_id} (Score: {ranked[0].score})")
    assert ranked[0].experience_unit.source_case_id == "case_A"
    
    print("\nAll Tests Passed.")

if __name__ == "__main__":
    test_similarity()
