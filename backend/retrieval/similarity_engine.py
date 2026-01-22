from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Any
import math

from canonical_state.earthquake_state import EarthquakeSituation, UncertainProperty
from memory.experience_unit import ExperienceUnit
from multimodal_ingestion.case_study_ingestion import TimePhase

@dataclass
class SimilarityResult:
    """
    Structured output of the similarity comparison.
    Explains WHY an experience is considered similar.
    """
    experience_unit: ExperienceUnit
    score: float # 0.0 to 1.0
    dimension_scores: Dict[str, float]
    penalties: List[str]
    confidence_modifier: float = 1.0

class SimilarityEngine:
    """
    Deterministic, explainable similarity engine.
    Compares a query EarthquakeSituation against candidate ExperienceUnits.
    No learning, no black box.
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        # Default weights if none provided
        self.weights = weights or {
            "scale": 0.3,
            "spatial": 0.25,
            "human": 0.2,
            "built": 0.25
        }
        # Normalize weights to sum to 1.0
        total_weight = sum(self.weights.values())
        if total_weight > 0:
            self.weights = {k: v / total_weight for k, v in self.weights.items()}

    def rank_candidates(self, query: EarthquakeSituation, candidates: List[ExperienceUnit]) -> List[SimilarityResult]:
        """
        Scores and ranks a list of candidates against the query.
        """
        results = []
        for cand in candidates:
            # Check implicit phase (Step 1 doesn't have explicit TimePhase enum in EarthquakeSituation, 
            # but Step 2 injected it into ExperienceUnit. We use the query's implicit phase if available,
            # or rely on the caller to provide context. 
            # For this step, we assume query situation might contain phase info in 'event_identity').
            
            result = self.compute_similarity(query, cand)
            results.append(result)
        
        # Rank by score descending
        results.sort(key=lambda x: x.score, reverse=True)
        return results

    def compute_similarity(self, query: EarthquakeSituation, candidate: ExperienceUnit) -> SimilarityResult:
        """
        Computes the similarity between a query situation and a candidate experience.
        """
        cand_sit = candidate.situation
        
        dim_scores = {}
        penalties = []
        
        # 1. Disaster Scale Similarity (Magnitude/Intensity)
        dim_scores["scale"] = self._compute_scale_similarity(query, cand_sit)
        
        # 2. Spatial/Environmental Context
        dim_scores["spatial"] = self._compute_spatial_similarity(query, cand_sit)
        
        # 3. Human Exposure
        dim_scores["human"] = self._compute_human_similarity(query, cand_sit)
        
        # 4. Built Environment
        dim_scores["built"] = self._compute_built_similarity(query, cand_sit)
        
        # Weighted Aggregation
        raw_score = sum(dim_scores[k] * self.weights.get(k, 0.0) for k in dim_scores)
        
        # Phase Penalty
        # Extract phase string from query if present
        query_phase_str = query.event_identity.phase
        
        # Try to map query string to TimePhase enum for rigorous comparison, 
        # or just compare broadly. Candidate has strict TimePhase.
        if query_phase_str:
            # Simple string normalization comparison
            # e.g. "immediate_impact" vs T0_IMPACT
            if not self._is_phase_compatible(query_phase_str, candidate.phase):
                penalty_factor = 0.8 # 20% penalty for phase mismatch
                raw_score *= penalty_factor
                penalties.append(f"Phase mismatch: Query '{query_phase_str}' vs Candidate '{candidate.phase.value}'")
        
        return SimilarityResult(
            experience_unit=candidate,
            score=round(raw_score, 4),
            dimension_scores={k: round(v, 4) for k, v in dim_scores.items()},
            penalties=penalties
        )

    # --- Dimension Scorers ---

    def _compute_scale_similarity(self, q: EarthquakeSituation, c: EarthquakeSituation) -> float:
        """Compares magnitude and intensity."""
        # Magnitude logic: 1.0 - (delta / range)
        q_mag = self._get_val(q.event_identity.magnitude)
        c_mag = self._get_val(c.event_identity.magnitude)
        
        score = 0.5 # Default neutral if both missing
        
        if q_mag is not None and c_mag is not None:
            delta = abs(q_mag - c_mag) # type: ignore
            # Assume max relevant delta is 3.0 (e.g. 6.0 vs 9.0)
            score = max(0.0, 1.0 - (delta / 3.0))
        elif q_mag is not None or c_mag is not None:
            score = 0.4 # Slightly lower confidence if one missing
            
        # Could blend intensity here, keeping simpler for now
        return score

    def _compute_spatial_similarity(self, q: EarthquakeSituation, c: EarthquakeSituation) -> float:
        """Compares region type and terrain."""
        q_reg = self._get_val(q.spatial_context.region_type)
        c_reg = self._get_val(c.spatial_context.region_type)
        
        # Exact match for categorical
        if q_reg and c_reg:
            return 1.0 if q_reg == c_reg else 0.0
        
        # Fallback to defaults
        return 0.5

    def _compute_human_similarity(self, q: EarthquakeSituation, c: EarthquakeSituation) -> float:
        """Compares population density."""
        q_pop = self._get_val(q.human_exposure.population_density)
        c_pop = self._get_val(c.human_exposure.population_density)
        
        if q_pop and c_pop:
            # Handle numeric vs string
            if isinstance(q_pop, (int, float)) and isinstance(c_pop, (int, float)):
                 delta = abs(q_pop - c_pop)
                 # Arbitrary max delta for density per sq/km? 
                 # Let's assume categorical strings for Step 1/2 usually ("sparse", "dense")
                 return 1.0 if q_pop == c_pop else 0.0
            return 1.0 if str(q_pop) == str(c_pop) else 0.0
            
        return 0.5

    def _compute_built_similarity(self, q: EarthquakeSituation, c: EarthquakeSituation) -> float:
        """Compares building types using Jaccard index."""
        q_types = self._get_list_vals(q.built_environment.dominant_building_types)
        c_types = self._get_list_vals(c.built_environment.dominant_building_types)
        
        if not q_types and not c_types:
            return 0.5
        
        if not q_types or not c_types:
            return 0.3
            
        intersection = len(q_types.intersection(c_types))
        union = len(q_types.union(c_types))
        
        return intersection / union if union > 0 else 0.0

    # --- Helpers ---

    def _get_val(self, prop: Optional[UncertainProperty]) -> Any:
        return prop.value if prop else None

    def _get_list_vals(self, props: List[UncertainProperty]) -> Set[Any]:
        return {p.value for p in props if p.value is not None}

    def _is_phase_compatible(self, query_phase: str, cand_phase: TimePhase) -> bool:
        """
        Heuristic mapping between free-text phase strings and strict TimePhase enum.
        """
        qp = query_phase.upper()
        cp = cand_phase.value.upper()
        
        # Direct substring match sufficient for now? 
        # e.g. "IMPACT" in "T0_IMPACT"?
        if "IMPACT" in qp and "IMPACT" in cp: return True
        if "RESPONSE" in qp and "RESPONSE" in cp: return True
        if "STABIL" in qp and "STABIL" in cp: return True
        if "OUTCOME" in qp and "OUTCOME" in cp: return True
        if "RECOVER" in qp and "OUTCOME" in cp: return True # Maybe?
        
        return False
