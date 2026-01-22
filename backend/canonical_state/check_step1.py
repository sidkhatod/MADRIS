from earthquake_state import EarthquakeSituation, EventIdentity, UncertainProperty, BuiltEnvironment
import json
from datetime import datetime

def test_canonical_state():
    print("Test 1: Empty Initialization")
    empty_sit = EarthquakeSituation()
    print("Success: Empty situation created.")
    
    print("\nTest 2: Populated Initialization with Uncertainty")
    situation = EarthquakeSituation(
        event_identity=EventIdentity(
            event_id="evt_123",
            magnitude=UncertainProperty(value=7.8, source="USGS", confidence=0.95),
            phase="immediate_impact",
            time_since_event_hours=2.5
        ),
        built_environment=BuiltEnvironment(
            construction_quality=UncertainProperty(value="poor", source="drone_footage", confidence="medium")
        )
    )
    print(f"Success: Created situation for event {situation.event_identity.event_id}")
    print(f"Magnitude: {situation.event_identity.magnitude.value} (conf: {situation.event_identity.magnitude.confidence})")
    
    print("\nTest 3: Serialization")
    # Setting timestamp for deterministic output locally if needed, or just let it be current
    situation.created_at = datetime(2023, 10, 1, 12, 0, 0)
    data = situation.to_dict()
    json_str = json.dumps(data, indent=2)
    print("Serialized JSON snippet:")
    print(json_str[:500] + "...") # Print first 500 chars
    
    assert data["event_identity"]["magnitude"]["value"] == 7.8
    assert data["built_environment"]["construction_quality"]["source"] == "drone_footage"
    print("\nTest 4: Assertions Passed")

if __name__ == "__main__":
    test_canonical_state()
