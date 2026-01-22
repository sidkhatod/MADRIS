from dataclasses import dataclass, field, asdict
from typing import Optional, List, Any, Dict, Generic, TypeVar, Union
from datetime import datetime

T = TypeVar('T')

@dataclass
class UncertainProperty(Generic[T]):
    """
    Represents a value that may be uncertain, originating from a specific source
    with a degree of confidence.
    """
    value: Optional[T] = None
    source: str = "unknown" # e.g., "text_report", "satellite_image", "social_media"
    confidence: Union[float, str] = "unknown" # 0.0-1.0 or "low", "medium", "high"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "source": self.source,
            "confidence": self.confidence
        }

@dataclass
class EventIdentity:
    """Core identity and timing of the event."""
    # All fields are optional and can be uncertain where applicable
    event_id: Optional[str] = None # Unique ID for the earthquake event itself
    event_type: str = "earthquake"
    magnitude: Optional[UncertainProperty[float]] = None
    intensity: Optional[UncertainProperty[str]] = None # e.g., MMI scale
    phase: Optional[str] = None # e.g., "immediate_impact", "response", "recovery"
    
    # Time context
    timestamp: Optional[datetime] = None # Absolute time of this situation report
    time_since_event_hours: Optional[float] = None # Relative time crucial for timeline logic
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "magnitude": self.magnitude.to_dict() if self.magnitude else None,
            "intensity": self.intensity.to_dict() if self.intensity else None,
            "phase": self.phase,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "time_since_event_hours": self.time_since_event_hours
        }

@dataclass
class SpatialContext:
    """Geographic and environmental setting."""
    region_type: Optional[UncertainProperty[str]] = None # "urban", "rural", "mixed"
    terrain: Optional[UncertainProperty[str]] = None
    secondary_hazards: List[UncertainProperty[str]] = field(default_factory=list) # landslides, fires, etc.
    location_description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "region_type": self.region_type.to_dict() if self.region_type else None,
            "terrain": self.terrain.to_dict() if self.terrain else None,
            "secondary_hazards": [h.to_dict() for h in self.secondary_hazards],
            "location_description": self.location_description
        }

@dataclass
class HumanExposure:
    """Population and vulnerability context."""
    population_density: Optional[UncertainProperty[str]] = None # "sparse", "dense", or numeric
    vulnerable_groups: List[UncertainProperty[str]] = field(default_factory=list)
    time_of_day_context: Optional[str] = None # e.g., "night", "rush_hour" - affects exposure
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "population_density": self.population_density.to_dict() if self.population_density else None,
            "vulnerable_groups": [g.to_dict() for g in self.vulnerable_groups],
            "time_of_day_context": self.time_of_day_context
        }

@dataclass
class BuiltEnvironment:
    """Infrastructure and building context."""
    dominant_building_types: List[UncertainProperty[str]] = field(default_factory=list)
    construction_quality: Optional[UncertainProperty[str]] = None
    critical_infrastructure_status: Dict[str, UncertainProperty[str]] = field(default_factory=dict) # e.g. {"hospitals": ..., "power": ...}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "dominant_building_types": [b.to_dict() for b in self.dominant_building_types],
            "construction_quality": self.construction_quality.to_dict() if self.construction_quality else None,
            "critical_infrastructure_status": {k: v.to_dict() for k, v in self.critical_infrastructure_status.items()}
        }

@dataclass
class DamageIndicators:
    """Observed physical damage."""
    building_collapse_severity: Optional[UncertainProperty[str]] = None # "none", "minor", "widespread"
    access_disruption: Optional[UncertainProperty[str]] = None # "clear", "blocked"
    utility_failures: List[UncertainProperty[str]] = field(default_factory=list)
    visible_hazards: List[UncertainProperty[str]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "building_collapse_severity": self.building_collapse_severity.to_dict() if self.building_collapse_severity else None,
            "access_disruption": self.access_disruption.to_dict() if self.access_disruption else None,
            "utility_failures": [u.to_dict() for u in self.utility_failures],
            "visible_hazards": [h.to_dict() for h in self.visible_hazards]
        }

@dataclass
class ActionsTaken:
    """Interventions already underway."""
    rescue_operations: Optional[UncertainProperty[str]] = None
    evacuation_status: Optional[UncertainProperty[str]] = None
    medical_deployment: Optional[UncertainProperty[str]] = None
    logistics_coordination: Optional[UncertainProperty[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rescue_operations": self.rescue_operations.to_dict() if self.rescue_operations else None,
            "evacuation_status": self.evacuation_status.to_dict() if self.evacuation_status else None,
            "medical_deployment": self.medical_deployment.to_dict() if self.medical_deployment else None,
            "logistics_coordination": self.logistics_coordination.to_dict() if self.logistics_coordination else None
        }

@dataclass
class Outcomes:
    """Known impacts (human and extra-human)."""
    casualties: Optional[UncertainProperty[int]] = None
    injuries: Optional[UncertainProperty[int]] = None
    displacement: Optional[UncertainProperty[int]] = None # Number of displaced people
    economic_loss: Optional[UncertainProperty[str]] = None # Qualitative or quantitative
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "casualties": self.casualties.to_dict() if self.casualties else None,
            "injuries": self.injuries.to_dict() if self.injuries else None,
            "displacement": self.displacement.to_dict() if self.displacement else None,
            "economic_loss": self.economic_loss.to_dict() if self.economic_loss else None
        }

@dataclass
class EarthquakeSituation:
    """
    Canonical representation of an earthquake situation at a specific time T.
    Acts as a semantic container for heterogeneous, uncertain, and partial information.
    """
    event_identity: EventIdentity = field(default_factory=EventIdentity)
    spatial_context: SpatialContext = field(default_factory=SpatialContext)
    human_exposure: HumanExposure = field(default_factory=HumanExposure)
    built_environment: BuiltEnvironment = field(default_factory=BuiltEnvironment)
    damage_indicators: DamageIndicators = field(default_factory=DamageIndicators)
    actions_taken: ActionsTaken = field(default_factory=ActionsTaken)
    outcomes: Outcomes = field(default_factory=Outcomes)
    
    # Metadata for the situation record itself
    record_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "created_at": self.created_at.isoformat(),
            "event_identity": self.event_identity.to_dict(),
            "spatial_context": self.spatial_context.to_dict(),
            "human_exposure": self.human_exposure.to_dict(),
            "built_environment": self.built_environment.to_dict(),
            "damage_indicators": self.damage_indicators.to_dict(),
            "actions_taken": self.actions_taken.to_dict(),
            "outcomes": self.outcomes.to_dict(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EarthquakeSituation':
        # NOTE: A full robust deserializer would be needed for production,
        # but for Step 1, we acknowledge that simple reconstruction is sufficient.
        # This is a placeholder to show intent for serialization support.
        # Implementing a full recursive deserializer is outside the immediate scope
        # unless strictly required, but the structure allows it.
        pass
