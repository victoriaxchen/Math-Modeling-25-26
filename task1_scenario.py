"""Task 1 scenario: Basic office building sweep with 2 firefighters."""

from building import Building
from room import Room, RoomType, OccupantType
from responder import Responder, SweepStrategy, ExpertiseLevel
from emergency import EmergencyContext, EmergencyType


def create_task1_building(emergency_type: str = "fire_alarm") -> Building:
    """
    Create the Task 1 building scenario:
    - One-story office building
    - Two exits on opposite sides (left and right ends)
    - Three similar-sized rooms on each side of central hallway
    - Central hallway connecting all rooms
    
    Layout:
    
                 Room1A     Room1B      Room1C
                   |           |           |
    Exit1 --- Hallway_L --- Hallway_C --- Hallway_R --- Exit2
                   |           |           |
                 Room2A     Room2B      Room2C

    Args:
        emergency_type: Type of emergency ("fire_alarm", "gas_leak", "co_leak", "drill")
    
    Returns:
        Building object configured for Task 1
    """
    # Create appropriate emergency context
    emergency_contexts = {
        "fire_alarm": EmergencyContext(EmergencyType.FIRE, severity=1.0, smoke_density=0.3),
        "gas_leak": EmergencyContext(EmergencyType.GAS_LEAK, severity=1.5),
        "co_leak": EmergencyContext(EmergencyType.CO_LEAK, severity=1.5),
        "drill": EmergencyContext(EmergencyType.EVACUATION_DRILL, severity=0.5),
        "major_fire": EmergencyContext(EmergencyType.FIRE, severity=2.0, smoke_density=0.8),
    }
    emergency = emergency_contexts.get(emergency_type, emergency_contexts["fire_alarm"])
    
    building = Building(name="Task 1 Office Building", emergency=emergency)
    
    # Create exits on opposite sides (left and right ends of building)
    exit1 = Room(
        room_id="Exit1",
        area=5.0,
        room_type=RoomType.EXIT,
        occupant_type=OccupantType.NONE
    )
    
    exit2 = Room(
        room_id="Exit2",
        area=5.0,
        room_type=RoomType.EXIT,
        occupant_type=OccupantType.NONE
    )
    
    # Create central hallway sections
    hallway_left = Room(
        room_id="Hallway_L",
        area=20.0,
        room_type=RoomType.HALLWAY,
        occupant_type=OccupantType.NONE
    )
    
    hallway_center = Room(
        room_id="Hallway_C",
        area=20.0,
        room_type=RoomType.HALLWAY,
        occupant_type=OccupantType.NONE
    )
    
    hallway_right = Room(
        room_id="Hallway_R",
        area=20.0,
        room_type=RoomType.HALLWAY,
        occupant_type=OccupantType.NONE
    )
    
    # Create rooms on side 1 (top side)
    room1a = Room(
        room_id="Room1A",
        area=30.0,
        room_type=RoomType.OFFICE,
        occupant_type=OccupantType.NORMAL,
        expected_occupants=2
    )
    
    room1b = Room(
        room_id="Room1B",
        area=30.0,
        room_type=RoomType.OFFICE,
        occupant_type=OccupantType.NORMAL,
        expected_occupants=3
    )
    
    room1c = Room(
        room_id="Room1C",
        area=30.0,
        room_type=RoomType.OFFICE,
        occupant_type=OccupantType.NORMAL,
        expected_occupants=2
    )
    
    # Create rooms on side 2 (bottom side)
    room2a = Room(
        room_id="Room2A",
        area=30.0,
        room_type=RoomType.OFFICE,
        occupant_type=OccupantType.NORMAL,
        expected_occupants=2
    )
    
    room2b = Room(
        room_id="Room2B",
        area=30.0,
        room_type=RoomType.OFFICE,
        occupant_type=OccupantType.NORMAL,
        expected_occupants=2
    )
    
    room2c = Room(
        room_id="Room2C",
        area=30.0,
        room_type=RoomType.OFFICE,
        occupant_type=OccupantType.NORMAL,
        expected_occupants=5
    )
    
    # Add all rooms to building
    for room in [exit1, exit2, hallway_left, hallway_center, hallway_right,
                 room1a, room1b, room1c, room2a, room2b, room2c]:
        building.add_room(room)
    
    # Connect hallway sections (forming central corridor)
    building.add_path("Hallway_L", "Hallway_C", distance=10.0)
    building.add_path("Hallway_C", "Hallway_R", distance=10.0)
    
    # Connect exits to opposite ends of hallway
    building.add_path("Exit1", "Hallway_L", distance=5.0)
    building.add_path("Exit2", "Hallway_R", distance=5.0)
    
    # Connect side 1 rooms to hallway
    building.add_path("Room1A", "Hallway_L", distance=8.0)
    building.add_path("Room1B", "Hallway_C", distance=8.0)
    building.add_path("Room1C", "Hallway_R", distance=8.0)
    
    # Connect side 2 rooms to hallway
    building.add_path("Room2A", "Hallway_L", distance=8.0)
    building.add_path("Room2B", "Hallway_C", distance=8.0)
    building.add_path("Room2C", "Hallway_R", distance=8.0)
    
    return building


def create_task1_responders() -> list[Responder]:
    """
    Create 3 firefighters for Task 1, split into 2 teams for redundancy:
    - Team 1: Firefighter 1 and 3 (sweep)
    - Team 2: Firefighter 2 (check/verify)
    
    Returns:
        List of Responder objects
    """
    firefighter1 = Responder(
        responder_id="FF1",
        name="Firefighter 1",
        strategy=SweepStrategy.NEAREST_FIRST,
        expertise=ExpertiseLevel.INTERMEDIATE,
        movement_speed=3.0,  # Updated to 3 m/s per specification
        team_id=1
    )
    
    firefighter2 = Responder(
        responder_id="FF2",
        name="Firefighter 2",
        strategy=SweepStrategy.NEAREST_FIRST,
        expertise=ExpertiseLevel.INTERMEDIATE,
        movement_speed=3.0,
        team_id=2
    )
    
    firefighter3 = Responder(
        responder_id="FF3",
        name="Firefighter 3",
        strategy=SweepStrategy.NEAREST_FIRST,
        expertise=ExpertiseLevel.INTERMEDIATE,
        movement_speed=3.0,
        team_id=1
    )
    
    return [firefighter1, firefighter2, firefighter3]


def get_task1_starting_positions() -> dict[str, str]:
    """
    Get starting positions for Task 1 firefighters.
    Firefighters start at different positions.
    
    Returns:
        Dictionary mapping responder_id to starting room_id
    """
    return {
        "FF1": "Exit1",
        "FF2": "Exit2",
        "FF3": "Exit1"  # Third firefighter starts at Exit1
    }
