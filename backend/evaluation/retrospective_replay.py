from typing import List, Dict, Any, Optional
import json
import dataclasses

from multimodal_ingestion.case_study_ingestion import CaseStudyIngestor, TimePhase, TimeSlice
from retrieval.similarity_engine import SimilarityEngine
from prediction.timeline_projection import TimelineProjector
from reasoning.intervention_reasoner import InterventionReasoner
from uncertainty.confidence_propagation import ConfidenceIntegrator
from output.response_formatter import ResponseFormatter, SystemResponse

from memory.experience_unit import ExperienceUnit
from canonical_state.earthquake_state import Outcomes

class RetrospectiveReplayEvaluator:
    """
    Evaluates the system by replaying historical cases phase-by-phase.
    Compares system outputs (predictions/interventions) against actual historical ground truth.
    Focuses on decision quality, timeliness, and caution.
    """

    def __init__(self):
        # Initialize pipeline components
        self.ingestor = CaseStudyIngestor()
        self.similarity_engine = SimilarityEngine()
        self.timeline_projector = TimelineProjector()
        self.intervention_reasoner = InterventionReasoner()
        self.confidence_integrator = ConfidenceIntegrator()
        self.response_formatter = ResponseFormatter()

    def replay_case(self, case_study_raw: Dict[str, Any], historical_memory: List[ExperienceUnit]) -> List[Dict[str, Any]]:
        """
        Replays a single case study through all its available phases.
        
        Args:
            case_study_raw: Dictionary containing the full case study data.
            historical_memory: List of ExperienceUnits representing the system's knowledge base 
                             (should EXCLUDE the case being replayed to prevent leakage/cheating).
                             
        Returns:
            List of structured log entries (one per phase).
        """
        # 1. Slice the case into phases
        slices = self.ingestor.ingest_case_study(case_study_raw)
        
        # 2. Identify Ground Truth (Final Outcomes)
        # We look for the latest phase (usually T3) to serve as the "actual outcome" reference.
        final_outcomes = None
        for s in reversed(slices):
            if s.situation.outcomes and (
                s.situation.outcomes.casualties is not None or 
                s.situation.outcomes.economic_loss is not None
            ):
                final_outcomes = s.situation.outcomes
                break
        
        logs = []

        # 3. Simulate Phase-by-Phase
        for i, current_slice in enumerate(slices):
            phase_log = self._process_phase(
                current_slice, 
                historical_memory, 
                slices[i+1:], # Future slices (for "actual actions taken later")
                final_outcomes
            )
            logs.append(phase_log)
            
        return logs

    def _process_phase(
        self, 
        current_slice: TimeSlice, 
        memory: List[ExperienceUnit], 
        future_slices: List[TimeSlice],
        final_outcomes: Optional[Outcomes]
    ) -> Dict[str, Any]:
        
        # A. Run Pipeline
        
        # 1. Similarity Retrieval
        # We assume the memory has already been vector-searched or we do brute-force for evaluation efficiency.
        # Since Step 4 defined Qdrant interface but Step 5 engine takes List[ExperienceUnit], 
        # we'll assume 'memory' is the candidate list (simplification for pure logic replay).
        # In a real full integ test, we'd call Qdrant here. For Step 10 logic:
        cohort_results = self.similarity_engine.rank_candidates(current_slice.situation, memory)
        
        # Take top K (e.g. 5)
        top_cohort = cohort_results[:5]
        
        # 2. Timeline Projection (Step 6)
        raw_projections = self.timeline_projector.project_timeline(current_slice.phase, top_cohort)
        
        # 3. Intervention Reasoning (Step 7)
        raw_interventions = self.intervention_reasoner.recommend_interventions(current_slice.phase, top_cohort)
        
        # 4. Confidence Integration (Step 8)
        # Calibrate projections
        calibrated_projections = self.confidence_integrator.calibrate_projections(raw_projections)
        
        # Calibrate interventions (requiring baseline conf)
        calibrated_interventions = self.confidence_integrator.calibrate_interventions(raw_interventions, calibrated_projections)
        
        # 5. Output Formatting (Step 9)
        cohort_meta = {
            "cohort_size": len(top_cohort),
            "patterns": "Evaluation Replay Mode" 
        }
        
        system_response = self.response_formatter.format_response(
            situation=current_slice.situation,
            projections=raw_projections,
            projection_conf=calibrated_projections,
            interventions=calibrated_interventions,
            cohort_meta=cohort_meta
        )

        # B. Gather Validation Data
        
        # Actual Actions Taken Later
        future_actions = []
        for f_slice in future_slices:
            acts = f_slice.situation.actions_taken
            if acts.rescue_operations and acts.rescue_operations.value: 
                future_actions.append(f"{f_slice.phase.value}: Rescue={acts.rescue_operations.value}")
            if acts.evacuation_status and acts.evacuation_status.value: 
                future_actions.append(f"{f_slice.phase.value}: Evac={acts.evacuation_status.value}")
            if acts.medical_deployment and acts.medical_deployment.value: 
                future_actions.append(f"{f_slice.phase.value}: Med={acts.medical_deployment.value}")
                
        # Format Final Outcomes
        outcome_summary = "Unknown"
        if final_outcomes:
            cas = final_outcomes.casualties.value if final_outcomes.casualties else "?"
            loss = final_outcomes.economic_loss.value if final_outcomes.economic_loss else "?"
            outcome_summary = f"Casualties: {cas}, Loss: {loss}"
            
        # C. Construct Log
        return {
            "case_id": system_response.situation_summary.event_id,
            "phase": current_slice.phase.value,
            "system_output": system_response.to_dict(),
            "validation": {
                "actual_subsequent_actions": future_actions,
                "actual_final_outcomes": outcome_summary
            },
            "evaluation_notes": {
                "timeliness_check": "Compare 'system_output.intervention_options' vs 'actual_subsequent_actions'",
                "accuracy_check": "Compare 'system_output.baseline_projections' vs 'actual_final_outcomes'"
            }
        }
