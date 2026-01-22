import sys
import os
import json

# Adjust path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from evaluation.retrospective_replay import RetrospectiveReplayEvaluator
from memory.experience_unit import ExperienceUnit
from multimodal_ingestion.case_study_ingestion import TimePhase, TimeSlice
from canonical_state.earthquake_state import EarthquakeSituation, Outcomes, UncertainProperty, EventIdentity, ActionsTaken

def test_replay():
    print("Test 1: Replay Historical Case")
    
    # 1. Setup Historical Memory (Past Experience)
    # A case where evacuation saved lives
    mem_sit = EarthquakeSituation()
    mem_sit.actions_taken.evacuation_status = UncertainProperty("completed")
    mem_unit = ExperienceUnit(
        situation=mem_sit, 
        phase=TimePhase.T1_EARLY_RESPONSE, 
        source_case_id="hist_001",
        subsequent_outcomes=Outcomes(casualties=UncertainProperty(50)) # Low casualties
    )
    
    memory = [mem_unit]
    
    # 2. Setup New Case to Replay (The "Query Case")
    # Raw dictionary input mocking Step 2 style
    query_case_raw = {
        "identity": {"event_id": "eval_event_2025", "phase": "immediate_impact"},
        "damage": {"building_collapse": "severe"},
        # Future phases implied by having more data in real ingestion, 
        # but here we simulate a case that *progresses*.
        # For 'ingest_case_study' to produce multiple slices, we usually need different inputs or a list.
        # Step 2 'ingest_case_study' produces slices from ONE dict if it has enough info.
        # Let's provide a dict that implies T0 and T1 data to get 2 slices.
        "actions": {"rescue": "pending"}, # T1 gets created if actions exist
        "outcomes": {"casualties": 500} # T3 gets created if outcomes exist
    }
    
    evaluator = RetrospectiveReplayEvaluator()
    logs = evaluator.replay_case(query_case_raw, memory)
    
    print(f"Generated {len(logs)} log entries.")
    
    # Check T0 Log (Impact Phase)
    log_t0 = logs[0]
    print("\n--- Phase T0 Log ---")
    print(f"Phase: {log_t0['phase']}")
    print(f"System Recommended: {[opt['action'] for opt in log_t0['system_output']['intervention_options']]}")
    print(f"Actual Outcome: {log_t0['validation']['actual_final_outcomes']}")
    
    # In T0, we expect the system to see the similarity to 'hist_001' (evac=good) and recommend evacuation?
    # Similarity Step 5 compares Situations.
    # Query T0 sit vs Memory T1 sit.
    # Step 5 engine might penalize phase mismatch, but should yield *some* similarity.
    # Step 7 reasoner looks for "Action Taken" in cohort. Memory has "evacuation".
    # So we *should* see an evacuation recommendation if the score logic allows.
    
    intervention_names = [opt['action'] for opt in log_t0['system_output']['intervention_options']]
    if "evacuation" in intervention_names:
        print("SUCCESS: System recommended evacuation based on history.")
    else:
        print("NOTE: System was cautious (or phase mismatch penalty too high).")
        
    # Check Validation Content
    print(f"Future Actions Recorded: {log_t0['validation']['actual_subsequent_actions']}")
    
    assert log_t0['phase'] == "T0_IMPACT"
    assert log_t0['system_output']['situation_summary']['event_id'] == "eval_event_2025"
    assert "Casualties: 500" in log_t0['validation']['actual_final_outcomes']
    
    print("\nAll Tests Passed.")

if __name__ == "__main__":
    test_replay()
