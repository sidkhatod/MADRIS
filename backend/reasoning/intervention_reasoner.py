from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from statistics import mean

from multimodal_ingestion.case_study_ingestion import TimePhase
from retrieval.similarity_engine import SimilarityResult
from canonical_state.earthquake_state import EarthquakeSituation, ActionsTaken, Outcomes

@dataclass
class InterventionRecommendation:
    """
    Proposed intervention based on historical evidence.
    """
    action_name: str
    suggested_time_window: str # e.g. "0-12h"
    comparative_effect: str # e.g. "associated with 20% lower casualties"
    confidence_score: float
    supporting_experience_count: int
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action_name,
            "window": self.suggested_time_window,
            "effect": self.comparative_effect,
            "confidence": self.confidence_score,
            "support": self.supporting_experience_count,
            "notes": self.notes
        }

class InterventionReasoner:
    """
    Discovers potential interventions by comparing 'treated' vs 'untreated' 
    similar past experiences.
    """

    def recommend_interventions(self, query_phase: TimePhase, cohort: List[SimilarityResult]) -> List[InterventionRecommendation]:
        """
        Main reasoning method.
        """
        recommendations = []
        
        # 1. Identify all actions taken in the cohort *after* the query phase.
        #    We look at ActionsTaken in the candidate units.
        #    Strictly speaking, we should only look at actions that happened in phases LATER than query_phase,
        #    but often candidates are separate units. 
        #    We assume the candidate Unit represents a *future state* relative to current query if its phase is later.
        
        # Simplified Logic for Step 7:
        # We group candidates by "Did they take Action X?".
        
        potential_actions = set()
        
        # Collect potential actions from T1/T2 phases in cohort (if query is T0)
        # For simplicity, we scan all candidates for discrete actions in `actions_taken`.
        
        for res in cohort:
            unit = res.experience_unit
            actions = unit.situation.actions_taken
            
            # Helper to add standard actions if present
            if self._has_action(actions.rescue_operations): potential_actions.add("rescue_operations")
            if self._has_action(actions.evacuation_status): potential_actions.add("evacuation")
            if self._has_action(actions.medical_deployment): potential_actions.add("medical_deployment")
            # ... others
            
        # 2. For each action, Compare Outcomes (With vs Without)
        for action in potential_actions:
            rec = self._evaluate_action(action, cohort)
            if rec:
                recommendations.append(rec)
                
        # Sort by confidence
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        return recommendations

    def _has_action(self, prop) -> bool:
        """Returns true if property has a value indicating action was taken."""
        return prop is not None and prop.value is not None and prop.value not in ["none", "pending", "unknown"]

    def _evaluate_action(self, action_key: str, cohort: List[SimilarityResult]) -> Optional[InterventionRecommendation]:
        """
        Compares outcomes of candidates with `action_key` vs those without.
        """
        group_with = []
        group_without = []
        
        for res in cohort:
            start_unit = res.experience_unit
            # Check presence
            val_present = False
            acts = start_unit.situation.actions_taken
            
            if action_key == "rescue_operations" and self._has_action(acts.rescue_operations): val_present = True
            elif action_key == "evacuation" and self._has_action(acts.evacuation_status): val_present = True
            elif action_key == "medical_deployment" and self._has_action(acts.medical_deployment): val_present = True
            
            if val_present:
                group_with.append(res)
            else:
                group_without.append(res)
                
        if not group_with or not group_without:
            return None # Cannot compare
            
        # Compare Outcomes (Casualties primarily)
        avg_cas_with = self._get_avg_casualties(group_with)
        avg_cas_without = self._get_avg_casualties(group_without)
        
        if avg_cas_with is None or avg_cas_without is None:
            return None # Missing outcome data
            
        # Logic: If With < Without -> Good
        if avg_cas_with < avg_cas_without:
            diff = avg_cas_without - avg_cas_with
            pct = (diff / avg_cas_without) * 100 if avg_cas_without > 0 else 0
            
            # Confidence based on cohort size
            conf = min(0.9, (len(group_with) + len(group_without)) / 10.0) 
            
            return InterventionRecommendation(
                action_name=action_key,
                suggested_time_window="0-12h", # Default/Placeholder heuristic
                comparative_effect=f"Associated with {int(pct)}% lower casualties in similar cases ({int(avg_cas_with)} vs {int(avg_cas_without)})",
                confidence_score=round(conf, 2),
                supporting_experience_count=len(group_with),
                notes="Observational correlation only."
            )
            
        return None

    def _get_avg_casualties(self, group: List[SimilarityResult]) -> Optional[float]:
        vals = []
        for res in group:
            out = res.experience_unit.subsequent_outcomes
            if out and out.casualties and out.casualties.value is not None:
                vals.append(out.casualties.value)
        if not vals: 
            return None
        return mean(vals)
