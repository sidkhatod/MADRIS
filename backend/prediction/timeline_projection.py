from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from collections import Counter

from multimodal_ingestion.case_study_ingestion import TimePhase
from retrieval.similarity_engine import SimilarityResult
from canonical_state.earthquake_state import EarthquakeSituation, UncertainProperty

@dataclass
class ProjectionResult:
    """
    Projected state for a specific time horizon.
    """
    horizon_label: str # 0-12h, 12-24h, 24-48h
    
    # Human Impact
    casualty_trend: str = "unknown" # increasing, stable, decreasing
    casualty_range: str = "unknown" # e.g. "100-500"
    injury_range: str = "unknown"
    
    # Infrastructure Impact
    collapse_progression: str = "unknown"
    access_disruption: str = "unknown"
    utility_degradation: str = "unknown"
    
    # Secondary Risks
    secondary_risks: List[str] = field(default_factory=list)
    
    # Meta
    confidence_score: float = 0.0
    supporting_experience_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "horizon": self.horizon_label,
            "human_impact": {
                "casualty_trend": self.casualty_trend,
                "casualty_range": self.casualty_range,
                "injury_range": self.injury_range
            },
            "infrastructure": {
                "collapse": self.collapse_progression,
                "access": self.access_disruption,
                "utility": self.utility_degradation
            },
            "secondary_risks": self.secondary_risks,
            "meta": {
                "confidence": self.confidence_score,
                "support_count": self.supporting_experience_count
            }
        }

class TimelineProjector:
    """
    Projects baseline timeline based on similar past experiences.
    Aggregates outcomes from cohort to predict 0-12h, 12-24h, 24-48h.
    """
    
    def project_timeline(self, query_phase: TimePhase, cohort: List[SimilarityResult]) -> Dict[str, ProjectionResult]:
        """
        Main projection method.
        Maps candidates to horizons and aggregates data.
        """
        # Initialize horizons
        horizons = {
            "0-12h": [],
            "12-24h": [],
            "24-48h": []
        }
        
        # Bin candidates into horizons based on their phase relative to query
        # This mapping is approximate and heuristic-based for Step 6 baseline
        for res in cohort:
            cand = res.experience_unit
            
            # If query is T0 (0-6h):
            if query_phase == TimePhase.T0_IMPACT:
                if cand.phase == TimePhase.T0_IMPACT:
                    horizons["0-12h"].append(res)
                elif cand.phase == TimePhase.T1_EARLY_RESPONSE:
                    horizons["12-24h"].append(res)
                elif cand.phase == TimePhase.T2_STABILIZATION:
                    horizons["24-48h"].append(res)
                elif cand.phase == TimePhase.T3_OUTCOME:
                    # Outcomes act as long-term projection for 24-48h+ if needed
                    # or could be used to fill gaps. For now, we map T3 to 24-48h for casualty finalization projection
                    horizons["24-48h"].append(res)
                    
            # If query is T1 (12-24h):
            elif query_phase == TimePhase.T1_EARLY_RESPONSE:
                if cand.phase == TimePhase.T1_EARLY_RESPONSE:
                    horizons["12-24h"].append(res) # Current/Immediate
                elif cand.phase == TimePhase.T2_STABILIZATION:
                    horizons["24-48h"].append(res)
                # T0 is past, T3 is future (24-48h+)
                if cand.phase == TimePhase.T3_OUTCOME:
                    horizons["24-48h"].append(res)

            # (Logic for T2/T3 queries would follow similar forward-looking mapping)
            
        # Aggregate each horizon
        results = {}
        for label, group in horizons.items():
            results[label] = self._aggregate_horizon(label, group)
            
        return results

    def _aggregate_horizon(self, label: str, group: List[SimilarityResult]) -> ProjectionResult:
        if not group:
            return ProjectionResult(horizon_label=label)
            
        # Weighted aggregate counters
        collapse_vals = []
        access_vals = []
        casualty_vals = []
        risks = set()
        
        total_weight = 0.0
        
        for res in group:
            weight = res.score # Use similarity score as weight
            cand = res.experience_unit
            sit = cand.situation
            
            total_weight += weight
            
            # Infrastructure from Situation
            if sit.damage_indicators.building_collapse_severity:
                val = sit.damage_indicators.building_collapse_severity.value
                if val: collapse_vals.append(val)
                
            if sit.damage_indicators.access_disruption:
                val = sit.damage_indicators.access_disruption.value
                if val: access_vals.append(val)
                
            # Secondary Risks
            for risk in sit.spatial_context.secondary_hazards:
                if risk.value: risks.add(risk.value)
            for haz in sit.damage_indicators.visible_hazards:
                if haz.value: risks.add(haz.value)
                
            # Casualties from Outcomes (if present in unit)
            # We look for "subsequent_outcomes" primarily
            out = cand.subsequent_outcomes
            if out and out.casualties and out.casualties.value is not None:
                casualty_vals.append(out.casualties.value)

        # Compute Consensus / Range
        
        # 1. Casualty Range
        c_range = "unknown"
        c_trend = "uncertain"
        if casualty_vals:
            min_c = min(casualty_vals)
            max_c = max(casualty_vals)
            c_range = f"{min_c} - {max_c}"
            # Simple trend heuristic (if max is high)
            c_trend = "increasing" if max_c > 100 else "stabilizing" # Placeholder logic
            
        # 2. Infrastructure Consensus (Mode)
        def get_mode(vals):
            if not vals: return "unknown"
            return Counter(vals).most_common(1)[0][0]
            
        collapse_res = get_mode(collapse_vals)
        access_res = get_mode(access_vals)
        
        # 3. Confidence
        # Heuristic: density of data * avg similarity
        avg_sim = total_weight / len(group) if group else 0
        density_factor = min(1.0, len(group) / 3.0) # Cap at 3 experiences
        confidence = avg_sim * density_factor

        return ProjectionResult(
            horizon_label=label,
            casualty_trend=c_trend,
            casualty_range=c_range,
            collapse_progression=str(collapse_res),
            access_disruption=str(access_res),
            secondary_risks=list(risks),
            confidence_score=round(confidence, 2),
            supporting_experience_count=len(group)
        )
