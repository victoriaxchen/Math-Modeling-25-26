# Quick Reference: Using the Updated Simulation

## Running the Simulation

### Option 1: Main Task 1 Scenario
```bash
python main.py
```
Runs the 11-room office building with 3 firefighters (2 teams).

### Option 2: Advanced Scenarios
```bash
python advanced_scenarios.py
```
Tests smoke scenarios and multi-team configurations.

### Option 3: Experiments
```bash
python experiments.py
```
Compares different sweep strategies and expertise levels.

### Option 4: Smoke Test (Team Redundancy)
```bash
python test_team_redundancy.py
```
Validates the sweep → check → resweep cycle works correctly.

### Option 5: Emergency Types Test (NEW!)
```bash
python test_emergency_types.py
```
Compares different emergency types (fire, gas leak, CO leak, etc.) and their impact on operations.

---

## Emergency Types (NEW FEATURE!)

### Quick Start with Emergency Types

```python
from emergency import EmergencyContext, EmergencyType, PRESET_EMERGENCIES
from building import Building

# Method 1: Use preset
emergency = PRESET_EMERGENCIES["major_fire"]
building = Building("My Building", emergency=emergency)

# Method 2: Create custom
emergency = EmergencyContext(
    emergency_type=EmergencyType.CO_LEAK,
    severity=1.5
)
building = Building("My Building", emergency=emergency)

# Method 3: Use Task 1 with emergency
from task1_scenario import create_task1_building
building = create_task1_building(emergency_type="gas_leak")
```

### Available Emergency Types

**Noticeable** (occupants immediately aware):
- `FIRE` - Active fire with smoke
- `STRUCTURAL_COLLAPSE` - Building damage
- `FLOOD` - Water intrusion
- `SMOKE_NO_FIRE` - Smoke without flames
- `EVACUATION_DRILL` - Practice evacuation

**Unnoticeable** (delayed occupant response):
- `GAS_LEAK` - Natural gas/propane leak (2.0x slower occupant response)
- `CO_LEAK` - Carbon monoxide (2.5x slower, may be unconscious)
- `CHEMICAL_LEAK` - Toxic chemical (2.2x slower)

See `EMERGENCY_TYPES_GUIDE.md` for detailed documentation.

---

## Configuring the Sweep Time Model

### Method 1: Change Global Baseline
```python
# In room.py
SWEEP_TIME_PER_SQM = 2.0  # 2 seconds per m² instead of 1.0
```

### Method 2: Override Per Calculation
```python
from room import Room, RoomType
room = Room("R1", 25.0, RoomType.OFFICE)
# Default: uses SWEEP_TIME_PER_SQM
duration1 = room.calculate_sweep_duration()
# Override for this call:
duration2 = room.calculate_sweep_duration(sweep_time_per_sqm=0.5)
```

### Method 3: Set Room Clutter
```python
# High clutter (C=5, slowest)
room1 = Room("R1", 25.0, RoomType.OFFICE, visible_fraction=0.1)

# Low clutter (C=1, fastest)
room2 = Room("R2", 25.0, RoomType.OFFICE, visible_fraction=0.95)

# Smoky room (auto-sets to 0.3)
room3 = Room("R3", 25.0, RoomType.OFFICE, has_smoke=True)
```

---

## Understanding the Sweep Duration Formula

```
Final Time = (T × A × C × type_mult × occ_mult × vis_penalty) / expertise

Where:
  T = baseline time per m² (SWEEP_TIME_PER_SQM)
  A = room area in m²
  C = clutter multiplier (1-5 based on visible_fraction)
  type_mult = room type multiplier (office=1.2, hallway=0.5, etc.)
  occ_mult = occupant multiplier (high_density=1.3, low_mobility=1.5, etc.)
  vis_penalty = visibility penalty (poor visibility adds 30-200%)
  expertise = responder expertise level (expert=1.3, novice=0.7)
```

---

## Creating Custom Scenarios with Teams

```python
from building import Building
from room import Room, RoomType, OccupantType
from responder import Responder, SweepStrategy, ExpertiseLevel
from simulation import SweepSimulation

# 1. Create building
building = Building("My Custom Building")
room1 = Room("Office1", 30.0, RoomType.OFFICE, expected_occupants=3)
exit1 = Room("Exit1", 5.0, RoomType.EXIT)
building.add_room(room1)
building.add_room(exit1)
building.add_path("Exit1", "Office1", 5.0)

# 2. Create teams
team_a = [
    Responder("R1", "Alice", team_id=1),
    Responder("R2", "Bob", team_id=1)
]
team_b = [
    Responder("R3", "Charlie", team_id=2)
]
responders = team_a + team_b

# 3. Run simulation
sim = SweepSimulation(building, responders)
sim.assign_starting_positions({"R1": "Exit1", "R2": "Exit1", "R3": "Exit1"})
results = sim.run_simulation()

# 4. View results
sim.print_summary(results)
print(f"Re-sweeps due to redundancy: {results['resweep_count']}")
```

---

## Interpreting Room Status

### Sweep Status
- `is_swept = False`: Not yet swept
- `is_swept = True`: Swept by some team

### Redundancy Status
- `swept_by_team = 1`: Team 1 performed the sweep
- `checked_by_team = 2`: Team 2 verified the sweep
- `needs_resweep = True`: Same team checked as swept, needs re-verification
- `needs_resweep = False`: Successfully verified by different team

### Example Visualization
```
Room Progression:
  1. [✗] Room1                           (unswept)
  2. [✓] Room1 swept_by_team=1           (swept by team 1)
  3. [✓] Room1 checked_by_team=2         (checked by team 2, OK)
  
  OR (if same team checked):
  3. [✓] Room1 checked_by_team=1         (same team, needs resweep)
  4. [✓] Room1 swept_by_team=2           (re-swept by different team)
  5. [✓] Room1 checked_by_team=1         (verified by team 1)
```

---

## Team Assignment Patterns

### Pattern 1: Two Equal Teams (Current Default)
```python
responders = [
    Responder("R1", "Alice", team_id=1),
    Responder("R2", "Bob", team_id=2),
    Responder("R3", "Charlie", team_id=1)  # Support team 1
]
```

### Pattern 2: Dedicated Verification Team
```python
# Team 1: Sweep
sweep_team = [
    Responder("R1", "Alice", team_id=1),
    Responder("R2", "Bob", team_id=1),
    Responder("R3", "Charlie", team_id=1)
]
# Team 2: Verify
verify_team = [
    Responder("R4", "Diana", team_id=2),
    Responder("R5", "Eve", team_id=2)
]
```

### Pattern 3: Multi-Team (3+)
```python
responders = [
    Responder("R1", "Alice", team_id=1),
    Responder("R2", "Bob", team_id=2),
    Responder("R3", "Charlie", team_id=3),
    Responder("R4", "Diana", team_id=1)
]
```

---

## Checking Results

### Key Metrics
```python
results = sim.run_simulation()

# Overall
print(f"Time: {results['completion_time']:.1f}s")
print(f"Fully swept: {results['fully_swept']}")
print(f"Re-sweeps: {results['resweep_count']}")

# Per responder
for r_stats in results['responder_stats']:
    print(f"{r_stats['name']} (Team {r_stats['team_id']}):")
    print(f"  Swept: {r_stats['rooms_swept']}")
    print(f"  Checked: {r_stats['rooms_checked']}")

# Events
for time, responder, event, room in results['events']:
    print(f"{time:6.1f}s: {responder} {event} {room}")
```

---

## Common Adjustments

### Make Sweeps Faster
```python
# Option 1: Reduce baseline
SWEEP_TIME_PER_SQM = 0.5

# Option 2: Increase visibility (lower clutter)
room.visible_fraction = 0.9  # vs 0.3 for smoky

# Option 3: Add expert responders
responder.expertise = ExpertiseLevel.EXPERT  # multiplier 1.3
```

### Make Sweeps Slower
```python
# Option 1: Increase baseline
SWEEP_TIME_PER_SQM = 2.0

# Option 2: Reduce visibility (increase clutter)
room.visible_fraction = 0.15  # will give C=5

# Option 3: Add novice responders
responder.expertise = ExpertiseLevel.NOVICE  # multiplier 0.7
```

### Enforce Strict Redundancy
```python
# Use dedicated verification team
# Ensures every room checked by different team
verify_team_id = 2
sweep_team_ids = [1]  # Only team 1 sweeps
```

---

## Troubleshooting

### Q: Rooms not getting checked?
A: Ensure you have responders with different team_ids. The simulation only assigns checks to different teams.

### Q: Getting re-sweeps even with different teams?
A: This shouldn't happen - check that your responders have different team_id values set during creation.

### Q: Sweep times seem too fast?
A: Check the visible_fraction for your rooms. Rooms with high visibility (>0.8) get C=1. Increase clutter or reduce SWEEP_TIME_PER_SQM.

### Q: Simulation takes too long?
A: Reduce visible_fraction to lower sweep times, or add more responders. The simulation scales with team coordination overhead.

---

## Files to Modify for Custom Behavior

- **Sweep duration**: Edit `room.py` SWEEP_TIME_PER_SQM or pass override
- **Responder speed**: Edit `responder.py` default movement_speed
- **Team assignment**: Edit scenario files or create custom scenario
- **Redundancy rules**: Edit `simulation.py` run_simulation() phases
- **Reporting**: Edit `simulation.py` print_summary() or `visualization.py`

---

## Example: Minimal Test Script

```python
#!/usr/bin/env python3
from building import Building
from room import Room, RoomType
from responder import Responder, SweepStrategy, ExpertiseLevel
from simulation import SweepSimulation

# Create minimal building
b = Building("Test")
b.add_room(Room("R1", 10.0, RoomType.OFFICE))
b.add_room(Room("R2", 10.0, RoomType.OFFICE))

# Create teams
r1 = Responder("A", "Alice", team_id=1)
r2 = Responder("B", "Bob", team_id=2)

# Run
sim = SweepSimulation(b, [r1, r2])
results = sim.run_simulation()
sim.print_summary(results)
```

Save as `quick_test.py` and run: `python quick_test.py`
