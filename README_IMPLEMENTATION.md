# Building Sweep Simulation Model

A Python simulation model for optimizing emergency building sweep strategies during evacuations. This project addresses the HiMCM mathematical modeling challenge of ensuring all rooms are cleared in the shortest possible time while prioritizing occupant safety and responder efficiency.

## Overview

This package models emergency building sweeps using graph-based representations of floor plans, intelligent responder agents with different strategies and expertise levels, and discrete event simulation to determine optimal sweep times.

## Features

- **Graph-based Floor Plans**: Buildings represented as graphs with rooms as nodes and hallways as weighted edges
- **Flexible Room Attributes**: Rooms have area, type, occupancy patterns, and smoke conditions
- **Intelligent Responders**: Firefighters with configurable:
  - Sweep strategies (nearest-first, systematic, priority-based)
  - Expertise levels (novice, intermediate, expert, veteran)
  - Movement speeds
- **Realistic Simulation**: Accounts for travel time, sweep duration, smoke effects, and occupancy types
- **Multiple Scenarios**: Task 1 baseline scenario with extensible framework for more complex buildings

## Installation

This project uses `uv` for Python package management:

```bash
# Install dependencies
uv sync

# Run the main simulation
uv run python main.py

# Run experiments
uv run python experiments.py
```

## Project Structure

```
himcm_a/
├── room.py              # Room class with attributes (area, type, occupancy)
├── building.py          # Building class with graph-based floor plan
├── responder.py         # Responder class with strategies and expertise
├── simulation.py        # Simulation engine for sweep operations
├── task1_scenario.py    # Task 1 specific scenario setup
├── visualization.py     # Visualization and reporting utilities
├── experiments.py       # Experiments with different configurations
├── main.py             # Main entry point
└── pyproject.toml      # Project dependencies
```

## Task 1: Basic Office Building

**Scenario**: Two firefighters sweep a one-story office building
- **Layout**: 6 office rooms, 3 on each side of a central hallway
- **Exits**: 2 exits on opposite sides of the building
- **Responders**: 2 firefighters with intermediate expertise

**Result**: The sweep completes in approximately **2.8 minutes** (167.7 seconds)

## Usage Examples

### Run the basic Task 1 simulation:

```python
from simulation import SweepSimulation
from task1_scenario import (
    create_task1_building,
    create_task1_responders,
    get_task1_starting_positions
)

# Create components
building = create_task1_building()
responders = create_task1_responders()

# Run simulation
simulation = SweepSimulation(building, responders)
simulation.assign_starting_positions(get_task1_starting_positions())
results = simulation.run_simulation()

# Display results
simulation.print_summary(results)
```

### Create a custom building:

```python
from building import Building
from room import Room, RoomType, OccupantType

building = Building("Custom Building")

# Add rooms
office = Room("Office1", area=25.0, room_type=RoomType.OFFICE)
hallway = Room("Hall1", area=15.0, room_type=RoomType.HALLWAY)

building.add_room(office)
building.add_room(hallway)

# Connect with hallway
building.add_path("Office1", "Hall1", distance=5.0)
```

### Experiment with different strategies:

```python
from responder import Responder, SweepStrategy, ExpertiseLevel

# Create responder with priority-based strategy
expert_ff = Responder(
    responder_id="EXP1",
    name="Expert FF",
    strategy=SweepStrategy.PRIORITY_BASED,
    expertise=ExpertiseLevel.EXPERT
)
```

## Model Components

### Room Attributes
- **Area**: Size in square meters (affects sweep time)
- **Room Type**: Office, conference, storage, restroom, hallway, exit
- **Occupant Type**: None, normal, low mobility, high density
- **Smoke**: Boolean flag affecting sweep time
- **Expected Occupants**: Number of people expected

### Sweep Strategies
- **Nearest First**: Sweep the closest unswept room
- **Systematic**: Sweep rooms in systematic order
- **Priority Based**: Prioritize based on smoke, occupancy, and distance

### Expertise Levels
- **Novice** (0.7x): Slower sweep times
- **Intermediate** (1.0x): Standard speed
- **Expert** (1.3x): 30% faster
- **Veteran** (1.5x): 50% faster

## Key Metrics

The simulation tracks:
- Total sweep completion time
- Individual responder performance
- Distance traveled by each responder
- Time spent sweeping vs. moving
- Event timeline with detailed logs

## Extensions

This framework can be extended to model:
- Multi-floor buildings with stairwells
- More than 2 responders
- Dynamic smoke spread
- Varying visibility conditions
- Resource constraints (oxygen, equipment)
- Different building layouts and complexities

## Dependencies

- Python >= 3.12
- NetworkX >= 3.5 (for graph-based building representation)

## License

This project is for educational purposes as part of the HiMCM mathematical modeling challenge.
