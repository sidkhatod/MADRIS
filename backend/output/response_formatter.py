from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

from canonical_state.earthquake_state import EarthquakeSituation
from prediction.timeline_projection import ProjectionResult
from reasoning.intervention_reasoner import InterventionRecommendation
from uncertainty.confidence_propagation import ConfidenceAssessment

@dataclass
class OutputSection:
    """Base class for output sections."""
    pass

@dataclass
class SituationSummary(OutputSection):
    event_id: str
    phase: str
    known_facts: List[str]
    explicit_unknowns: List[str]

@dataclass
class FormattedProjection(OutputSection):
    horizon: str
    trend: str
    range_desc: str
    confidence_label: str
    confidence_score: float

@dataclass
class FormattedIntervention(OutputSection):
    action: str
    window: str
    effect_desc: str
    confidence_label: str
    confidence_score: float
    evidence_count: int

@dataclass
class EvidenceContext(OutputSection):
    cohort_size: int
    dominant_patterns: str = "Based on similar historical cases"
    divergences: str = "None noted"

@dataclass
class ConfidenceOverview(OutputSection):
    overall_level: str # High/Medium/Low
    drivers: List[str]
    risks_gaps: List[str]

@dataclass
class SystemResponse:
    """
    Final structured output contract.
    """
    situation_summary: SituationSummary
    baseline_projections: List[FormattedProjection]
    intervention_options: List[FormattedIntervention]
    evidence_context: EvidenceContext
    confidence_overview: ConfidenceOverview

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ResponseFormatter:
    """
    Formats the raw analysis components into a safe, structured SystemResponse.
    Enforces non-prescriptive language and explicit uncertainty.
    """

    def format_response(
        self,
        situation: EarthquakeSituation,
        projections: Dict[str, ProjectionResult],
        projection_conf: Dict[str, ConfidenceAssessment],
        interventions: List[tuple[InterventionRecommendation, ConfidenceAssessment]],
        cohort_meta: Dict[str, Any]
    ) -> SystemResponse:
        
        # 1. Situation Summary
        summary = self._build_summary(situation)
        
        # 2. Baseline Projections
        fmt_projections = []
        # Sort horizons chronologically if possible, or fixed order
        order = ["0-12h", "12-24h", "24-48h"]
        for horizon in order:
            if horizon in projections and horizon in projection_conf:
                proj = projections[horizon]
                conf = projection_conf[horizon]
                fmt_projections.append(FormattedProjection(
                    horizon=horizon,
                    trend=f"{proj.casualty_trend} casualty trend observed", 
                    range_desc=f"{proj.casualty_range} casualties (est)",
                    confidence_label=conf.label,
                    confidence_score=conf.score
                ))
                
        # 3. Intervention Options
        fmt_interventions = []
        for rec, conf in interventions:
            fmt_interventions.append(FormattedIntervention(
                action=rec.action_name,
                window=rec.suggested_time_window,
                effect_desc=rec.comparative_effect, # e.g. "Associated with..."
                confidence_label=conf.label,
                confidence_score=conf.score,
                evidence_count=rec.supporting_experience_count
            ))
            
        # 4. Evidence Context
        evidence = EvidenceContext(
            cohort_size=cohort_meta.get("cohort_size", 0),
            dominant_patterns=cohort_meta.get("patterns", "Historical patterns from similar events."),
            divergences=cohort_meta.get("divergences", "No major divergences inferred.")
        )
        
        # 5. Confidence Overview
        # Aggregate logic: lowest of the projected horizons? or average?
        # Safety priority: report the lowest confidence or the most critical one.
        # Let's take the minimum of projection confidences as "Overall system confidence" for safety.
        scores = [c.score for c in projection_conf.values()]
        min_score = min(scores) if scores else 0.0
        
        overall_label = "Low"
        if min_score >= 0.8: overall_label = "High"
        elif min_score >= 0.5: overall_label = "Medium"
        
        # Collect drivers
        all_drivers = set()
        for c in projection_conf.values():
            for d in c.drivers: all_drivers.add(d)
        for _, c in interventions:
            for d in c.drivers: all_drivers.add(d)
            
        conf_overview = ConfidenceOverview(
            overall_level=overall_label,
            drivers=list(all_drivers),
            risks_gaps=["Sparse data" if min_score < 0.5 else "None specific"] # Placeholder logic
        )
        
        return SystemResponse(
            situation_summary=summary,
            baseline_projections=fmt_projections,
            intervention_options=fmt_interventions,
            evidence_context=evidence,
            confidence_overview=conf_overview
        )

    def _build_summary(self, sit: EarthquakeSituation) -> SituationSummary:
        knowns = []
        unknowns = []
        
        if sit.event_identity.magnitude and sit.event_identity.magnitude.value:
            knowns.append(f"Magnitude {sit.event_identity.magnitude.value}")
        else:
            unknowns.append("Magnitude")
            
        if sit.spatial_context.region_type and sit.spatial_context.region_type.value:
            knowns.append(f"Region: {sit.spatial_context.region_type.value}")
        
        return SituationSummary(
            event_id=sit.event_identity.event_id or "Unknown",
            phase=sit.event_identity.phase or "Unknown",
            known_facts=knowns,
            explicit_unknowns=unknowns
        )
