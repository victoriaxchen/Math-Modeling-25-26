"""Advanced scenarios with smoke and different building layouts."""

from building import Building
from room import Room, RoomType, OccupantType
from responder import Responder, SweepStrategy, ExpertiseLevel
from simulation import SweepSimulation
from emergency import EmergencyContext, EmergencyType


def create_smoke_scenario():
    """
    Create a scenario where some rooms have smoke.
    This tests priority-based strategies.
    """
    # Create building with smoke emergency
    emergency = EmergencyContext(EmergencyType.SMOKE_NO_FIRE, severity=1.5, smoke_density=0.6)
    building = Building("Smoke Scenario Building", emergency=emergency)
    
    # Create exits
    exit1 = Room("Exit1", area=5.0, room_type=RoomType.EXIT)
    exit2 = Room("Exit2", area=5.0, room_type=RoomType.EXIT)
    
    # Create hallway
    hallway = Room("Hallway", area=30.0, room_type=RoomType.HALLWAY)
    
    # Create rooms - some with poor visibility (smoke)
    room1 = Room(
        "Room1", 
        area=30.0, 
        room_type=RoomType.OFFICE,
        has_smoke=True,  # Smoke present! (also sets is_visible=False)
        expected_occupants=3
    )
    
    room2 = Room(
        "Room2",
        area=30.0,
        room_type=RoomType.OFFICE,
        has_smoke=False,
        expected_occupants=2
    )
    
    room3 = Room(
        "Room3",
        area=30.0,
        room_type=RoomType.OFFICE,
        has_smoke=True,  # Smoke present! (also sets is_visible=False)
        expected_occupants=2
    )
    
    room4 = Room(
        "Room4",
        area=30.0,
        room_type=RoomType.OFFICE,
        has_smoke=False,
        expected_occupants=1
    )
    
    # Add rooms
    for room in [exit1, exit2, hallway, room1, room2, room3, room4]:
        building.add_room(room)
    
    # Connect rooms
    building.add_path("Exit1", "Hallway", distance=5.0)
    building.add_path("Exit2", "Hallway", distance=5.0)
    building.add_path("Hallway", "Room1", distance=8.0)
    building.add_path("Hallway", "Room2", distance=8.0)
    building.add_path("Hallway", "Room3", distance=8.0)
    building.add_path("Hallway", "Room4", distance=8.0)
    
    return building


def run_smoke_scenario_comparison():
    """Compare strategies in a scenario with smoke."""
    print("\n" + "=" * 70)
    print("SMOKE SCENARIO: Comparing Strategies with Smoke Present")
    print("=" * 70)
    print("\nBuilding has 4 rooms: 2 with smoke (Room1, Room3), 2 without")
    print("Priority-based strategy should prioritize smoke rooms...\n")
    
    strategies = [
        (SweepStrategy.NEAREST_FIRST, "Nearest First"),
        (SweepStrategy.PRIORITY_BASED, "Priority Based"),
    ]
    
    for strategy, name in strategies:
        print(f"\n{'=' * 70}")
        print(f"Testing: {name}")
        print("=" * 70)
        
        building = create_smoke_scenario()
        
        ff1 = Responder(
            "FF1", "Firefighter 1",
            strategy=strategy,
            expertise=ExpertiseLevel.INTERMEDIATE,
            team_id=1
        )
        
        ff2 = Responder(
            "FF2", "Firefighter 2",
            strategy=strategy,
            expertise=ExpertiseLevel.INTERMEDIATE,
            team_id=2
        )
        
        simulation = SweepSimulation(building, [ff1, ff2])
        simulation.assign_starting_positions({"FF1": "Exit1", "FF2": "Exit2"})
        results = simulation.run_simulation()
        
        print(f"\nCompletion time: {results['completion_time']:.1f}s ({results['completion_time_minutes']:.2f}min)")
        
        # Show which rooms were swept in what order
        print("\nSweep order:")
        events = sorted(
            [e for e in results['events'] if e[2] == 'SWEPT'],
            key=lambda x: x[0]
        )
        for time, responder, event, room in events:
            room_obj = building.get_room(room)
            smoke_marker = "🔥" if room_obj and room_obj.has_smoke else "  "
            print(f"  {time:6.1f}s - {responder:15s} swept {room:10s} {smoke_marker}")


def create_large_building():
    """Create a larger, more complex building."""
    building = Building("Large Multi-Wing Building")
    
    # Create exits
    exit1 = Room("Exit_North", area=5.0, room_type=RoomType.EXIT)
    exit2 = Room("Exit_South", area=5.0, room_type=RoomType.EXIT)
    exit3 = Room("Exit_East", area=5.0, room_type=RoomType.EXIT)
    
    # Create main hallway
    main_hall = Room("Main_Hallway", area=40.0, room_type=RoomType.HALLWAY)
    
    # Create north wing
    north_hall = Room("North_Hallway", area=20.0, room_type=RoomType.HALLWAY)
    north_rooms = [
        Room(f"North_Office_{i}", area=25.0, room_type=RoomType.OFFICE)
        for i in range(1, 4)
    ]
    
    # Create south wing
    south_hall = Room("South_Hallway", area=20.0, room_type=RoomType.HALLWAY)
    south_rooms = [
        Room(f"South_Office_{i}", area=25.0, room_type=RoomType.OFFICE)
        for i in range(1, 4)
    ]
    
    # Create east wing
    east_hall = Room("East_Hallway", area=20.0, room_type=RoomType.HALLWAY)
    east_rooms = [
        Room(f"East_Office_{i}", area=25.0, room_type=RoomType.OFFICE)
        for i in range(1, 4)
    ]
    
    # Add all rooms
    all_rooms = (
        [exit1, exit2, exit3, main_hall, north_hall, south_hall, east_hall] +
        north_rooms + south_rooms + east_rooms
    )
    
    for room in all_rooms:
        building.add_room(room)
    
    # Connect main structure
    building.add_path("Exit_North", "Main_Hallway", distance=5.0)
    building.add_path("Exit_South", "Main_Hallway", distance=5.0)
    building.add_path("Exit_East", "Main_Hallway", distance=5.0)
    
    building.add_path("Main_Hallway", "North_Hallway", distance=8.0)
    building.add_path("Main_Hallway", "South_Hallway", distance=8.0)
    building.add_path("Main_Hallway", "East_Hallway", distance=8.0)
    
    # Connect north wing rooms
    for i, room in enumerate(north_rooms):
        building.add_path("North_Hallway", room.room_id, distance=6.0 + i * 2)
    
    # Connect south wing rooms
    for i, room in enumerate(south_rooms):
        building.add_path("South_Hallway", room.room_id, distance=6.0 + i * 2)
    
    # Connect east wing rooms
    for i, room in enumerate(east_rooms):
        building.add_path("East_Hallway", room.room_id, distance=6.0 + i * 2)
    
    return building


def run_large_building_scenario():
    """Test sweep of a large building with multiple wings."""
    print("\n" + "=" * 70)
    print("LARGE BUILDING SCENARIO: Multi-wing building with 3 wings")
    print("=" * 70)
    
    building = create_large_building()
    stats = building.get_building_stats()
    print(f"\nBuilding size: {stats['total_rooms']} rooms, {stats['total_area']:.0f} m²")
    
    # Test with different numbers of responders
    for num_responders in [2, 3, 4]:
        print(f"\n{'=' * 70}")
        print(f"Testing with {num_responders} firefighters")
        print("=" * 70)
        
        building = create_large_building()
        
        responders = [
            Responder(
                f"FF{i}",
                f"Firefighter {i}",
                strategy=SweepStrategy.NEAREST_FIRST,
                expertise=ExpertiseLevel.INTERMEDIATE,
                team_id=(i % 2) + 1  # Alternate teams 1 and 2
            )
            for i in range(1, num_responders + 1)
        ]
        
        # Assign to different exits
        exits = ["Exit_North", "Exit_South", "Exit_East"]
        starting_positions = {
            responders[i].responder_id: exits[i % len(exits)]
            for i in range(len(responders))
        }
        
        simulation = SweepSimulation(building, responders)
        simulation.assign_starting_positions(starting_positions)
        results = simulation.run_simulation()
        
        print(f"\nCompletion time: {results['completion_time']:.1f}s ({results['completion_time_minutes']:.2f}min)")
        print(f"Rooms per firefighter: {stats['total_rooms'] / num_responders:.1f}")
        
        for r_stats in results['responder_stats']:
            print(f"  {r_stats['name']}: {r_stats['rooms_swept']} rooms, {r_stats['total_distance']:.0f}m traveled")


if __name__ == "__main__":
    run_smoke_scenario_comparison()
    run_large_building_scenario()
