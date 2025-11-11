# Emergency Types Guide

## Overview

The simulation now supports different types of emergencies that significantly impact sweep operations, movement speed, and occupant response. Emergencies are categorized as **noticeable** (occupants immediately aware) or **unnoticeable** (delayed occupant response).

---

## Emergency Type Categories

### **Noticeable Emergencies** (Immediate Awareness)

Occupants immediately recognize danger and respond quickly.

| Emergency Type | Description | Smoke | Movement Impact | Use Case |
|----------------|-------------|-------|-----------------|----------|
| **FIRE** | Active fire with flames, heat, smoke | Yes | 70% speed | Most common, immediate danger |
| **STRUCTURAL_COLLAPSE** | Building damage, debris | No | 60% speed | Earthquake, explosion aftermath |
| **FLOOD** | Water intrusion | No | 50% speed | Water damage scenarios |
| **SMOKE_NO_FIRE** | Smoke without active flames | Yes | 80% speed | Electrical fire, neighboring fire |
| **EVACUATION_DRILL** | Practice evacuation | No | 100% speed | Training scenarios |

### **Unnoticeable Emergencies** (Delayed Awareness)

Occupants may not recognize danger immediately. May be unconscious or impaired.

| Emergency Type | Description | Smoke | Movement Impact | Occupant Response |
|----------------|-------------|-------|-----------------|-------------------|
| **GAS_LEAK** | Natural gas or propane leak | No | 90% speed | 2.0x slower (resistance to evacuation) |
| **CO_LEAK** | Carbon monoxide poisoning | No | 95% speed | 2.5x slower (may be unconscious) |
| **CHEMICAL_LEAK** | Toxic chemical release | No | 85% speed | 2.2x slower (depends on chemical) |

---

## Key Multipliers

Each emergency type affects operations through multiple multipliers:

### 1. **Movement Speed Multiplier**
Affects how fast responders can move through the building.

```python
# Example: Fire reduces movement to 70% of normal speed
responder.movement_speed = base_speed * 0.70
```

**Impact factors:**
- Smoke/visibility
- Debris/obstacles
- Water resistance
- Need for protective equipment
- Structural stability concerns

### 2. **Visibility Multiplier**
Affects sweep time due to reduced visibility from smoke.

```python
# Increases sweep time based on smoke density
visibility_multiplier = 1.0 + (smoke_density * 2.0)
# Example: 50% smoke density → 2.0x sweep time
```

### 3. **Occupant Response Multiplier**
Affects time spent dealing with occupants during sweep.

**Noticeable emergencies:** 1.0x (normal response)
- Occupants are alert and cooperative
- Quick to evacuate when directed

**Unnoticeable emergencies:** 1.5x - 3.0x (delayed response)
- Occupants may not believe there's danger
- May be impaired or unconscious (CO)
- Require additional search and alert time
- Responders must convince/assist evacuation

### 4. **Sweep Difficulty Multiplier**
Overall complexity of sweep operations.

```python
# Factors include:
# - Environmental hazards
# - Need for detection equipment (gas detector, CO meter)
# - Protective gear requirements
# - Thoroughness required
```

---

## Usage Examples

### Example 1: Create Building with Emergency Type

```python
from building import Building
from emergency import EmergencyContext, EmergencyType

# Method 1: Create emergency context directly
emergency = EmergencyContext(
    emergency_type=EmergencyType.FIRE,
    severity=1.5,
    smoke_density=0.7
)

building = Building(
    name="Office Building",
    emergency=emergency
)
```

### Example 2: Use Preset Emergency

```python
from emergency import PRESET_EMERGENCIES

# Available presets:
# - minor_fire: Fire with light smoke
# - major_fire: Severe fire with dense smoke
# - gas_leak: Natural gas leak scenario
# - co_leak: Carbon monoxide emergency
# - smoke_only: Smoke without active fire
# - drill: Evacuation practice
# - structural_damage: Building collapse
# - chemical_spill: Toxic chemical release

emergency = PRESET_EMERGENCIES["major_fire"]
building = Building("Test Building", emergency=emergency)
```

### Example 3: Task 1 with Different Emergencies

```python
from task1_scenario import create_task1_building, create_task1_responders
from simulation import SweepSimulation

# Fire alarm (default)
building = create_task1_building(emergency_type="fire_alarm")

# Gas leak scenario
building = create_task1_building(emergency_type="gas_leak")

# CO leak scenario
building = create_task1_building(emergency_type="co_leak")

# Evacuation drill
building = create_task1_building(emergency_type="drill")

responders = create_task1_responders()
simulation = SweepSimulation(building, responders)
results = simulation.run_simulation()
```

---

## Impact Comparison

### Completion Time Comparison (3-room building, 2 responders)

| Emergency Type | Time | Movement | Visibility | Occupant Response |
|----------------|------|----------|------------|-------------------|
| Evacuation Drill | 15.7s | 1.00x | 1.00x | 0.80x ⚡ Fast |
| Minor Fire | 71.7s | 0.55x | 1.92x | 0.80x |
| Smoke Only | 98.2s | 0.68x | 2.00x | 1.00x |
| Gas Leak | 263.0s | 0.83x | 1.00x | 3.00x ⚠️ Delayed |
| CO Leak | 347.9s | 0.88x | 1.00x | 3.75x ⚠️⚠️ Very Delayed |
| Major Fire | 1045.9s | 0.47x | 4.80x | 2.00x 🔥 Most Severe |

**Key Observations:**
- **CO Leak:** 22x slower than drill due to delayed occupant response (may be unconscious)
- **Major Fire:** 66x slower than drill due to severe smoke (4.8x visibility penalty)
- **Gas Leak:** Similar to CO but occupants more responsive (still 2-3x delayed)

---

## Emergency Context Properties

### Creating Custom Emergency

```python
from emergency import EmergencyContext, EmergencyType

emergency = EmergencyContext(
    emergency_type=EmergencyType.FIRE,
    severity=2.0,        # 0.5=minor, 1.0=normal, 2.0=severe
    has_smoke=True,      # Override smoke presence
    smoke_density=0.8    # 0.0=clear to 1.0=dense
)

# Query emergency properties
print(f"Noticeable: {emergency.is_noticeable()}")
print(f"Movement multiplier: {emergency.get_movement_speed_multiplier()}")
print(f"Visibility multiplier: {emergency.get_visibility_multiplier()}")
print(f"Occupant response: {emergency.get_occupant_response_multiplier()}")
print(f"Requires detection equipment: {emergency.requires_detection_equipment()}")
print(f"Can affect consciousness: {emergency.affects_occupant_consciousness()}")
```

### Severity Scaling

The `severity` parameter scales all multipliers:

- **0.5:** Minor emergency (light smoke, small area affected)
- **1.0:** Normal emergency (standard conditions)
- **1.5:** Serious emergency (worsening conditions)
- **2.0:** Severe emergency (extreme conditions)
- **3.0:** Catastrophic (maximum difficulty)

---

## Smoke Density Effects

Smoke density (0.0 to 1.0) affects visibility:

| Density | Description | Visibility Multiplier | Impact |
|---------|-------------|-----------------------|--------|
| 0.0 | No smoke | 1.0x | Normal operations |
| 0.3 | Light smoke | 1.6x | Slightly slower |
| 0.5 | Moderate smoke | 2.0x | Significantly slower |
| 0.7 | Heavy smoke | 2.4x | Very slow operations |
| 1.0 | Dense smoke | 3.0x | Maximum difficulty |

---

## Special Considerations

### Unnoticeable Emergencies

**Why are they slower?**

1. **CO Leak (Carbon Monoxide):**
   - Completely odorless and colorless
   - Causes confusion, drowsiness, unconsciousness
   - Occupants may not realize they're in danger
   - Responders must check every occupant individually
   - May need to carry unconscious victims

2. **Gas Leak:**
   - May have odor (mercaptan), but not always
   - Occupants may dismiss smell or not recognize danger
   - Risk of explosion requires caution
   - Need gas detection equipment

3. **Chemical Leak:**
   - Varies by chemical (some odorless)
   - May cause impairment or unconsciousness
   - Requires protective equipment
   - Decontamination concerns

### Detection Equipment

Some emergencies require special equipment:

```python
if emergency.requires_detection_equipment():
    # Responders need:
    # - Gas detector (GAS_LEAK)
    # - CO meter (CO_LEAK)
    # - Chemical sensors (CHEMICAL_LEAK)
    # This adds to sweep difficulty
```

---

## Integration with Existing Features

### Room-Level Impact

Emergency multipliers are applied in `Room.calculate_sweep_duration()`:

```python
sweep_time = T × A × C × type_mult × occupant_mult × visibility_mult × occupant_response_mult × difficulty_mult / expertise
```

### Responder-Level Impact

Movement speed is adjusted when responder is created or emergency context is set:

```python
responder.movement_speed = base_speed × emergency.get_movement_speed_multiplier()
```

### Priority-Based Strategy

Emergency type adds priority bonus for PRIORITY_BASED strategy:

```python
priority_score += emergency.get_priority_bonus()
# Fire: +200, Structural: +250, CO: +180, etc.
```

---

## Testing Emergency Types

Run the comprehensive test suite:

```bash
python test_emergency_types.py
```

This tests:
- All emergency type comparisons
- Noticeable vs unnoticeable emergencies
- Smoke density impact
- Preset emergency configurations

---

## Best Practices

1. **Choose appropriate emergency type** based on scenario realism
2. **Adjust severity** to model escalating or de-escalating conditions
3. **Consider smoke density** for fire scenarios (0.3-0.9 typical)
4. **Use drills** for training/baseline comparisons
5. **Test unnoticeable emergencies** to model worst-case scenarios (CO leak)

---

## API Reference

### EmergencyType Enum
```python
EmergencyType.FIRE                  # Noticeable
EmergencyType.GAS_LEAK              # Unnoticeable
EmergencyType.CO_LEAK               # Unnoticeable (most dangerous)
EmergencyType.CHEMICAL_LEAK         # Unnoticeable
EmergencyType.STRUCTURAL_COLLAPSE   # Noticeable
EmergencyType.FLOOD                 # Noticeable
EmergencyType.SMOKE_NO_FIRE         # Noticeable
EmergencyType.EVACUATION_DRILL      # Noticeable (training)
```

### EmergencyContext Methods
```python
emergency.is_noticeable() -> bool
emergency.get_occupant_response_multiplier() -> float
emergency.get_visibility_multiplier() -> float
emergency.get_movement_speed_multiplier() -> float
emergency.get_sweep_difficulty_multiplier() -> float
emergency.requires_detection_equipment() -> bool
emergency.affects_occupant_consciousness() -> bool
emergency.get_priority_bonus() -> float
```

---

## Conclusion

Emergency types add critical realism to the simulation by modeling:
- **Environmental conditions** (smoke, debris, water)
- **Occupant awareness** (immediate vs delayed recognition)
- **Responder challenges** (movement restrictions, equipment needs)
- **Operational complexity** (sweep difficulty, detection requirements)

The distinction between **noticeable** and **unnoticeable** emergencies is particularly important for modeling scenarios like CO leaks where occupants may be unconscious or unaware of danger, requiring significantly more time for sweep operations.
