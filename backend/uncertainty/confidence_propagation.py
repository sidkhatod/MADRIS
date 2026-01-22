from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from prediction.timeline_projection import ProjectionResult
from reasoning.intervention_reasoner import InterventionRecommendation

@dataclass
class ConfidenceAssessment:
    """
    Calibrated confidence metadata.
    """
    score: float # 0.0 - 1.0
    label: str # "Low", "Medium", "High"
    explanation: str # Why this score?
    drivers: List[str] # Specific factors (e.g. "Low similarity", "Sparse data")

class ConfidenceIntegrator:
    """
    Central engine for uncertainty propagation and confidence calibration.
    Ensures confidence reflects evidence quality and never increases downstream.
    """

    def calibrate_projections(self, projections: Dict[str, ProjectionResult]) -> Dict[str, ConfidenceAssessment]:
        """
        Calibrates confidence for baseline timeline projections.
        """
        assessments = {}
        for horizon, proj in projections.items():
            assessments[horizon] = self._assess_projection(proj)
        return assessments

    def calibrate_interventions(self, recommendations: List[InterventionRecommendation], base_Assessments: Dict[str, ConfidenceAssessment]) -> List[tuple[InterventionRecommendation, ConfidenceAssessment]]:
        """
        Calibrates confidence for interventions, strictly capped by baseline confidence.
        Returns list of (recommendation, assessment) tuples.
        """
        results = []
        for rec in recommendations:
            assess = self._assess_intervention(rec, base_Assessments)
            results.append((rec, assess))
        return results

    def _assess_projection(self, proj: ProjectionResult) -> ConfidenceAssessment:
        # Start with the raw score calculated in Step 6
        raw_score = proj.confidence_score
        
        drivers = []
        
        # 1. Data Density Check
        if proj.supporting_experience_count < 3:
            drivers.append("Sparse data (<3 cases)")
            # Penalty already likely in raw_score, but we enforce cap
            raw_score = min(raw_score, 0.6)
        
        # 2. Similarity / Quality Check (Implicit in raw score, but we interpret)
        if raw_score < 0.4:
            drivers.append("Weak similarity matches")
        
        # 3. Variance Check (Heuristic based on range strings)
        # If range is identical (e.g. "500-500"), likely single data point or artifical consensus -> reduced trust unless count high
        if proj.casualty_range != "unknown" and "-" in proj.casualty_range:
            try:
                parts = proj.casualty_range.split("-")
                if len(parts) == 2 and parts[0].strip() == parts[1].strip() and proj.supporting_experience_count < 2:
                     drivers.append("Single data point source")
                     raw_score *= 0.8
            except: pass
            
        # Determine Label
        label = self._get_label(raw_score)
        
        explanation = f"Confidence is {label} ({raw_score:.2f}). Driven by: {', '.join(drivers) if drivers else 'adequate evidence'}."
        
        return ConfidenceAssessment(
            score=round(raw_score, 2),
            label=label,
            explanation=explanation,
            drivers=drivers
        )

    def _assess_intervention(self, rec: InterventionRecommendation, base_assessments: Dict[str, ConfidenceAssessment]) -> ConfidenceAssessment:
        # Base confidence from Step 7 logic
        raw_score = rec.confidence_score
        drivers = []
        
        # 1. Inherit limitation from baseline (Usually Horizon 0-12h or 12-24h relevant to action)
        # We define a ceiling based on the *best* available baseline confidence to be charitable, 
        # or the specific window. 
        # Strategy: Use the baseline confidence of the window the action maps to.
        # Fallback: Max of all baselines.
        
        baseline_ceiling = 0.0
        if base_assessments:
            baseline_ceiling = max(a.score for a in base_assessments.values())
        else:
            drivers.append("No baseline projection")
            
        # Cap intervention confidence
        if raw_score > baseline_ceiling:
            raw_score = baseline_ceiling
            drivers.append("Capped by baseline uncertainty")
            
        # 2. Support check
        if rec.supporting_experience_count < 2:
            drivers.append("Very low support for action")
            raw_score = min(raw_score, 0.4)
            
        label = self._get_label(raw_score)
        explanation = f"Confidence is {label} ({raw_score:.2f}). {'; '.join(drivers)}."
        
        return ConfidenceAssessment(
            score=round(raw_score, 2),
            label=label,
            explanation=explanation,
            drivers=drivers
        )

    def _get_label(self, score: float) -> str:
        if score >= 0.8: return "High"
        if score >= 0.5: return "Medium"
        return "Low"
