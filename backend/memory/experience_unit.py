from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from canonical_state.earthquake_state import EarthquakeSituation, Outcomes
from multimodal_ingestion.case_study_ingestion import TimePhase, TimeSlice

@dataclass(frozen=True)
class ExperienceUnit:
    """
    Represents a single atomic unit of earthquake experience.
    "When the situation looked like X at phase P, this is what happened Y."
    
    Immutable by design to ensure data integrity during retrieval and learning.
    """
    situation: EarthquakeSituation
    phase: TimePhase
    source_case_id: str
    subsequent_outcomes: Optional[Outcomes] = None
    
    @classmethod
    def from_timeslice(cls, slice: TimeSlice, source_case_id: str, outcomes: Optional[Outcomes] = None) -> 'ExperienceUnit':
        """
        Factory method to create an ExperienceUnit from a TimeSlice.
        """
        return cls(
            situation=slice.situation,
            phase=slice.phase,
            source_case_id=source_case_id,
            subsequent_outcomes=outcomes
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the ExperienceUnit to a dictionary.
        """
        return {
            "source_case_id": self.source_case_id,
            "phase": self.phase.value,
            "situation": self.situation.to_dict(),
            "subsequent_outcomes": self.subsequent_outcomes.to_dict() if self.subsequent_outcomes else None
        }
