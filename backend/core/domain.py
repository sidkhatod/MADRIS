from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from datetime import datetime
import uuid

@dataclass
class DecisionSnapshot:
    """
    Core abstraction: A probabilistic, analogy-driven narrative snapshot 
    of a decision moment.
    """
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    case_study_id: str = "unknown"
    source_pdf: str = "unknown"
    
    # Inferred Context (Linguistic, not numeric)
    inferred_time_window: str = "unknown" # e.g. "immediate post-impact", "day 2 night"
    location_context: str = "" # e.g. "dense urban center, liquefaction prone"
    
    # Narrative Fields
    decision_context: str = "" # "what was known / what was perceived"
    uncertainties: List[str] = field(default_factory=list) # "casualty count unclear", "utility status unknown"
    risks_perceived: List[str] = field(default_factory=list) # "aftershocks", "looting"
    
    # Action/Inaction
    actions_considered: List[str] = field(default_factory=list)
    action_taken_narrative: str = "" 
    
    # Vector Embedding (Optional wrapper, usually handled separately)
    # vectors: Optional[List[float]] = None 

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "case_study_id": self.case_study_id,
            "source_pdf": self.source_pdf,
            "inferred_time_window": self.inferred_time_window,
            "location_context": self.location_context,
            "decision_context": self.decision_context,
            "uncertainties": self.uncertainties,
            "risks_perceived": self.risks_perceived,
            "actions_considered": self.actions_considered,
            "action_taken_narrative": self.action_taken_narrative
        }
    
    @property
    def narrative_text(self) -> str:
        """
        Constructs the text to be embedded. 
        Focuses on context + uncertainty + decision dilemma.
        """
        return f"""
        Time: {self.inferred_time_window}
        Location: {self.location_context}
        Context: {self.decision_context}
        Uncertainties: {', '.join(self.uncertainties)}
        Risks: {', '.join(self.risks_perceived)}
        Action Narrative: {self.action_taken_narrative}
        """.strip()
