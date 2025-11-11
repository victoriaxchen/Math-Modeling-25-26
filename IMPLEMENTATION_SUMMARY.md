# Implementation Summary: Team-Based Redundancy with Clutter-Based Sweep Time

## Overview
Successfully implemented the user's requested features:
1. **Clutter-based sweep-time model** using the formula T × A × C
2. **Responder movement speed** set to 3.0 m/s
3. **Team-based redundancy system** with sweep, check, and re-sweep workflow

## Key Changes by File

### 1. `room.py`
- **Added module-level constant**: `SWEEP_TIME_PER_SQM = 1.0` (configurable baseline time per m²)
- **Added `visible_fraction` parameter** to Room initializer (defaults to 1.0, 0.3 for smoky rooms)
- **Implemented clutter multiplier C mapping** based on visible_fraction ranges:
  - C=1 if r ∈ (0.8, 1]
  - C=2 if r ∈ (0.6, 0.8]
  - C=3 if r ∈ (0.4, 0.6]
  - C=4 if r ∈ (0.2, 0.4]
  - C=5 if r ∈ [0.0, 0.2]
- **Implemented formula**: `base_time = T × A × C` with existing multipliers for type, occupants, and visibility
- **Added team tracking fields**: `swept_by_team`, `checked_by_team`, `needs_resweep`
- **Added methods**:
  - `mark_swept(time, team_id)`: Records which team swept the room
  - `mark_checked(time, team_id)`: Records check by another team; sets `needs_resweep` if same team

### 2. `responder.py`
- **Added `team_id` parameter** to Responder initializer (integer identifier)
- **Updated default `movement_speed`** to 3.0 m/s
- **Added `rooms_checked` tracking** list for rooms verified by the responder
- **Updated `sweep_room()`** to pass `team_id` to `room.mark_swept()`
- **Added `check_room()` method** that:
  - Performs a quick check (10% of sweep time)
  - Calls `room.mark_checked(time, team_id)`
  - Returns whether re-sweep is needed
- **Updated stats** to include team_id and rooms_checked
- **Updated `__repr__`** to show team information

### 3. `simulation.py`
- **Added team grouping logic**: `_group_responders_by_team()` method
- **Added checker selection**: `_get_checker_from_different_team()` to enforce redundancy
- **Implemented 3-phase simulation**:
  1. **Sweep phase**: Teams sweep unswept rooms
  2. **Check phase**: Different teams check swept rooms
  3. **Re-sweep phase**: Handle rooms that triggered re-sweep (checked by same team)
- **Added redundancy tracking**: `resweep_queue`, `resweep_count` in results
- **Updated `print_summary()`** to display:
  - Re-sweep count due to redundancy
  - Team-level statistics (swept, checked, distances)
  - Team-aware event logging

### 4. `building.py`
- **Updated `reset_sweep_status()`** to clear all team-related fields:
  - `swept_by_team`, `checked_by_team`, `needs_resweep`
- **Added `has_unswept_rooms()` helper** for convenience

### 5. Scenario Files
- **`task1_scenario.py`**: Assigned team IDs (1 and 2) to responders, updated speed to 3.0 m/s
- **`advanced_scenarios.py`**: Added team alternation in large building tests
- **`experiments.py`**: Updated both strategy and expertise experiments to use teams

### 6. `visualization.py`
- **Enhanced ASCII visualization** to show team information in room descriptions
- **Updated `create_summary_report()`** to show:
  - Re-sweep count due to redundancy
  - Team-level statistics with separate summaries
  - Per-team swept/checked/distance metrics

### 7. New Test File
- **`test_team_redundancy.py`**: Standalone smoke test that verifies:
  - Sweep by one team → check by another team → successful verification
  - Same-team check triggers re-sweep flag
  - Full end-to-end redundancy cycle

## Results

### Main Simulation (Task 1)
- **Completion time**: ~2.3 minutes for 11-room building
- **All rooms fully swept**: Yes
- **Team distribution**:
  - Team 1 (Firefighters 1 & 3): 7 rooms swept, 4 rooms checked
  - Team 2 (Firefighter 2): 4 rooms swept, 7 rooms checked
- **Re-sweeps due to redundancy**: 0 (successful cross-team verification)

### Smoke Test (Minimal Building)
- **Building**: 3 rooms (Exit1, Hallway, Room1)
- **Teams**: Responder 1 (Team 1) and Responder 2 (Team 2)
- **Results**:
  - ✓ Team 1 swept 2 rooms
  - ✓ Team 2 swept 1 room  
  - ✓ Different teams performed checks (redundancy working)
  - ✓ No re-sweeps triggered (successful verification)

## Configuration

### Tunable Parameters
1. **`SWEEP_TIME_PER_SQM`** in `room.py` (default: 1.0 s/m²)
   - Affects all sweep duration calculations
   - Can be overridden per-call via `room.calculate_sweep_duration(sweep_time_per_sqm=value)`

2. **`visible_fraction`** per room (default: 1.0, 0.3 if smoky)
   - Controls clutter multiplier C
   - Higher fraction → lower C → faster sweeps

3. **Team assignments** in scenario files
   - Responders assigned team IDs (integer or string)
   - Affects check prioritization and re-sweep logic

## Redundancy Rules

1. **Sweep**: Any team sweeps unswept rooms
2. **Check**: Different team checks swept room
3. **Re-sweep**: If same team checks own sweep, mark `needs_resweep=True`
4. **Resolution**: Another team performs re-sweep
5. **Completion**: All rooms must be swept by one team AND checked by a different team

## Files Modified
- `room.py` — Core model changes (T×A×C formula, team tracking)
- `responder.py` — Team support and check_room method
- `simulation.py` — 3-phase redundancy workflow
- `building.py` — Reset logic and helper methods
- `task1_scenario.py`, `advanced_scenarios.py`, `experiments.py` — Team assignments
- `visualization.py` — Team-aware reporting

## Files Created
- `test_team_redundancy.py` — Standalone smoke test

## Validation
✅ Syntax validation passed (pyflakes)
✅ All imports resolve correctly
✅ Team-based sweep/check/resweep cycle verified
✅ Main simulation runs with new model
✅ Responder speed set to 3.0 m/s
✅ T×A×C formula implemented correctly
✅ Clutter multiplier mapping validated
✅ Cross-team checking enforced
✅ Reports show redundancy metrics
