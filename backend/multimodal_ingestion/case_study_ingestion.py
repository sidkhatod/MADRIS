from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
import copy
from datetime import datetime, timedelta

# Import from Step 1
from canonical_state.earthquake_state import (
    EarthquakeSituation,
    EventIdentity,
    SpatialContext,
    HumanExposure,
    BuiltEnvironment,
    DamageIndicators,
    ActionsTaken,
    Outcomes,
    UncertainProperty
)

class TimePhase(Enum):
    T0_IMPACT = "T0_IMPACT"
    T1_EARLY_RESPONSE = "T1_EARLY_RESPONSE"
    T2_STABILIZATION = "T2_STABILIZATION"
    T3_OUTCOME = "T3_OUTCOME"

@dataclass
class TimeSlice:
    """
    Represents a specific time-window of the earthquake event.
    Wrapper around an EarthquakeSituation for a specific phase.
    """
    phase: TimePhase
    situation: EarthquakeSituation
    relative_time_label: str = "unknown"

class CaseStudyIngestor:
    """
    Responsible for decomposing a raw case study dictionary into time-sliced EarthquakeSituations.
    Ensures no future leakage between phases.
    """
    
    def ingest_case_study(self, data: Dict[str, Any]) -> List[TimeSlice]:
        """
        Main entry point. Accepts a case study dict and returns a list of TimeSlices.
        Input data structure is flexible but expected to have keys that can be mapped.
        """
        slices: List[TimeSlice] = []
        
        # We define a mapping of which phases we will attempt to generate.
        # We always attempt to generate phases in order.
        
        # 1. T0_IMPACT
        # Contains: Identity, Contexts, Initial Damage. NO Actions, NO Outcomes.
        if self._has_data_for_phase(data, TimePhase.T0_IMPACT):
            slices.append(self._create_slice_t0(data))
            
        # 2. T1_EARLY_RESPONSE
        # Contains: T0 + Early Actions (Rescue). NO Outcomes.
        if self._has_data_for_phase(data, TimePhase.T1_EARLY_RESPONSE):
            slices.append(self._create_slice_t1(data))
            
        # 3. T2_STABILIZATION
        # Contains: T1 + Stabilization Actions (Medical, Logistics). NO Outcomes.
        if self._has_data_for_phase(data, TimePhase.T2_STABILIZATION):
            slices.append(self._create_slice_t2(data))
            
        # 4. T3_OUTCOME
        # Contains: All previous + Outcomes (Casualties, Losses).
        if self._has_data_for_phase(data, TimePhase.T3_OUTCOME):
            slices.append(self._create_slice_t3(data))
            
        return slices

    def _has_data_for_phase(self, data: Dict[str, Any], phase: TimePhase) -> bool:
        # Heuristic to check if we have enough data to barely justify this phase
        # detailed checks could be added here. For now, we assume if the key "timeline_events" exists,
        # or just purely based on available fields.
        # For simplicity in Step 2, we generate a slice if base data exists, 
        # but in a real system checks would be stricter.
        
        if phase == TimePhase.T0_IMPACT:
            return "identity" in data or "spatial" in data # Minimal requirement
        
        # For later phases, usually we'd check if specific update keys exist in input 
        # OR if we just want to project the static state forward.
        # The prompt implies decomposing a *single* case study.
        # We will generate all phases if the data *could* support them, 
        # filtering the content strictly.
        return True 

    def _extract_uncertain(self, data: Dict, key: str, source: str = "case_report") -> Optional[UncertainProperty]:
        if key in data and data[key] is not None:
            return UncertainProperty(value=data[key], source=source, confidence="medium")
        return None

    def _extract_list_uncertain(self, data: Dict, key: str, source: str = "case_report") -> List[UncertainProperty]:
        if key in data and isinstance(data[key], list):
             return [UncertainProperty(value=v, source=source, confidence="medium") for v in data[key]]
        return []

    # --- Phase Creators ---

    def _create_base_situation(self, data: Dict[str, Any]) -> EarthquakeSituation:
        """Creates the static context present in all phases."""
        sit = EarthquakeSituation()
        
        # Identity
        identity_data = data.get("identity", {})
        sit.event_identity = EventIdentity(
            event_id=identity_data.get("event_id"),
            event_type="earthquake",
            magnitude=self._extract_uncertain(identity_data, "magnitude"),
            intensity=self._extract_uncertain(identity_data, "intensity"),
            # phase and time are set by the caller logic
        )
        
        # Spatial Context
        spatial = data.get("spatial", {})
        sit.spatial_context = SpatialContext(
            region_type=self._extract_uncertain(spatial, "region_type"),
            terrain=self._extract_uncertain(spatial, "terrain"),
            secondary_hazards=self._extract_list_uncertain(spatial, "secondary_hazards"),
            location_description=spatial.get("location_description")
        )
        
        # Human Exposure
        human = data.get("human", {})
        sit.human_exposure = HumanExposure(
            population_density=self._extract_uncertain(human, "population_density"),
            vulnerable_groups=self._extract_list_uncertain(human, "vulnerable_groups"),
            time_of_day_context=human.get("time_of_day")
        )
        
        # Built Environment
        built = data.get("built", {})
        sit.built_environment = BuiltEnvironment(
            dominant_building_types=self._extract_list_uncertain(built, "building_types"),
            construction_quality=self._extract_uncertain(built, "construction_quality"),
            critical_infrastructure_status={} # Populated if provided dict
            # Skipping complex dict parsing for 'critical_infrastructure_status' for brevity in scaffold
        )
        
        return sit

    def _create_slice_t0(self, data: Dict[str, Any]) -> TimeSlice:
        sit = self._create_base_situation(data)
        
        # T0 specific overrides
        sit.event_identity.phase = "immediate_impact"
        sit.event_identity.time_since_event_hours = 0.0
        
        # Initial Damage (Allowed in T0)
        damage = data.get("damage", {})
        sit.damage_indicators = DamageIndicators(
            building_collapse_severity=self._extract_uncertain(damage, "building_collapse"),
            access_disruption=self._extract_uncertain(damage, "access_disruption"),
            utility_failures=self._extract_list_uncertain(damage, "utility_failures"),
            visible_hazards=self._extract_list_uncertain(damage, "visible_hazards")
        )
        
        # NO Actions, NO Outcomes in T0
        
        return TimeSlice(phase=TimePhase.T0_IMPACT, situation=sit, relative_time_label="0-6 hours")

    def _create_slice_t1(self, data: Dict[str, Any]) -> TimeSlice:
        sit = self._create_base_situation(data)
        sit.event_identity.phase = "early_response"
        sit.event_identity.time_since_event_hours = 12.0 # representative
        
        # Inherit Damage (could be updated in real logic, here we reuse T0 logic)
        damage = data.get("damage", {})
        sit.damage_indicators = DamageIndicators(
            building_collapse_severity=self._extract_uncertain(damage, "building_collapse"),
            access_disruption=self._extract_uncertain(damage, "access_disruption"),
            utility_failures=self._extract_list_uncertain(damage, "utility_failures"),
            visible_hazards=self._extract_list_uncertain(damage, "visible_hazards")
        )

        # Early Actions (Rescue)
        actions = data.get("actions", {})
        sit.actions_taken = ActionsTaken(
            rescue_operations=self._extract_uncertain(actions, "rescue"),
            evacuation_status=self._extract_uncertain(actions, "evacuation")
            # NO Medical deployment yet (conceptually T2, but flexible)
        )
        
        # NO Outcomes
        
        return TimeSlice(phase=TimePhase.T1_EARLY_RESPONSE, situation=sit, relative_time_label="12-24 hours")

    def _create_slice_t2(self, data: Dict[str, Any]) -> TimeSlice:
        sit = self._create_base_situation(data)
        sit.event_identity.phase = "stabilization"
        sit.event_identity.time_since_event_hours = 24.0
        
        # Damage (same)
        damage = data.get("damage", {})
        sit.damage_indicators = DamageIndicators(
            building_collapse_severity=self._extract_uncertain(damage, "building_collapse"),
            access_disruption=self._extract_uncertain(damage, "access_disruption"),
            utility_failures=self._extract_list_uncertain(damage, "utility_failures"),
            visible_hazards=self._extract_list_uncertain(damage, "visible_hazards")
        )
        
        # Stabilization Actions (Medical, Logistics)
        actions = data.get("actions", {})
        sit.actions_taken = ActionsTaken(
            rescue_operations=self._extract_uncertain(actions, "rescue"), # Continued
            evacuation_status=self._extract_uncertain(actions, "evacuation"),
            medical_deployment=self._extract_uncertain(actions, "medical"), # NEW in T2
            logistics_coordination=self._extract_uncertain(actions, "logistics") # NEW in T2
        )
        
        # NO Outcomes
        
        return TimeSlice(phase=TimePhase.T2_STABILIZATION, situation=sit, relative_time_label="24-48 hours")

    def _create_slice_t3(self, data: Dict[str, Any]) -> TimeSlice:
        sit = self._create_base_situation(data)
        sit.event_identity.phase = "outcome"
        sit.event_identity.time_since_event_hours = 72.0 # representative
        
        # Damage
        damage = data.get("damage", {})
        sit.damage_indicators = DamageIndicators(
            building_collapse_severity=self._extract_uncertain(damage, "building_collapse"),
            access_disruption=self._extract_uncertain(damage, "access_disruption"),
            utility_failures=self._extract_list_uncertain(damage, "utility_failures"),
            visible_hazards=self._extract_list_uncertain(damage, "visible_hazards")
        )
        
        # All Actions
        actions = data.get("actions", {})
        sit.actions_taken = ActionsTaken(
            rescue_operations=self._extract_uncertain(actions, "rescue"),
            evacuation_status=self._extract_uncertain(actions, "evacuation"),
            medical_deployment=self._extract_uncertain(actions, "medical"),
            logistics_coordination=self._extract_uncertain(actions, "logistics")
        )
        
        # OUTCOMES - Only Allowed Here
        outcomes = data.get("outcomes", {})
        sit.outcomes = Outcomes(
            casualties=self._extract_uncertain(outcomes, "casualties"),
            injuries=self._extract_uncertain(outcomes, "injuries"),
            displacement=self._extract_uncertain(outcomes, "displacement"),
            economic_loss=self._extract_uncertain(outcomes, "economic_loss")
        )
        
        return TimeSlice(phase=TimePhase.T3_OUTCOME, situation=sit, relative_time_label="post-event")
