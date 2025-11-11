"""
Test scenario demonstrating priority-based redundancy system.

This scenario shows how different room types require different numbers of sweeps:
- DAYCARE (Priority 5): Requires 3 sweeps by 3 different teams
- CLASSROOM (Priority 4): Requires 2 sweeps by 2 different teams  
- OFFICE (Priority 3): Requires 1 sweep + 1 check by different team
- STORAGE (Priority 1): Requires 1 sweep only (no check needed)
"""

from building import Building
from room import Room, RoomType, OccupantType
from responder import Responder, SweepStrategy, ExpertiseLevel
from simulation import SweepSimulation
from emergency import EmergencyContext, EmergencyType


def create_priority_test_building() -> Building:
    """Create a building with various priority levels for testing."""
    building = Building("Priority Test Building")
    
    # Priority 5 - Critical (requires 3 sweeps)
    building.add_room(Room(
        room_id="daycare",
        area=60.0,
        room_type=RoomType.DAYCARE,
        occupant_type=OccupantType.HIGH_DENSITY,
        expected_occupants=15,
        visible_fraction=0.9
    ))
    
    building.add_room(Room(
        room_id="medical",
        area=40.0,
        room_type=RoomType.MEDICAL,
        occupant_type=OccupantType.LOW_MOBILITY,
        expected_occupants=5,
        visible_fraction=0.95
    ))
    
    # Priority 4 - High (requires 2 sweeps)
    building.add_room(Room(
        room_id="classroom",
        area=50.0,
        room_type=RoomType.CLASSROOM,
        occupant_type=OccupantType.HIGH_DENSITY,
        expected_occupants=25,
        visible_fraction=0.9
    ))
    
    building.add_room(Room(
        room_id="dormitory",
        area=45.0,
        room_type=RoomType.DORMITORY,
        occupant_type=OccupantType.NORMAL,
        expected_occupants=8,
        visible_fraction=0.7
    ))
    
    # Priority 3 - Medium (requires 1 sweep + 1 check)
    building.add_room(Room(
        room_id="office1",
        area=30.0,
        room_type=RoomType.OFFICE,
        occupant_type=OccupantType.NORMAL,
        expected_occupants=4,
        visible_fraction=0.85
    ))
    
    building.add_room(Room(
        room_id="conference",
        area=35.0,
        room_type=RoomType.CONFERENCE,
        occupant_type=OccupantType.NORMAL,
        expected_occupants=10,
        visible_fraction=0.95
    ))
    
    # Priority 2 - Low (requires 1 sweep + 1 check)
    building.add_room(Room(
        room_id="restroom",
        area=15.0,
        room_type=RoomType.RESTROOM,
        occupant_type=OccupantType.NONE,
        expected_occupants=0,
        visible_fraction=0.9
    ))
    
    building.add_room(Room(
        room_id="hallway",
        area=25.0,
        room_type=RoomType.HALLWAY,
        occupant_type=OccupantType.NONE,
        expected_occupants=0,
        visible_fraction=1.0
    ))
    
    # Priority 1 - Minimal (requires 1 sweep only, no check)
    building.add_room(Room(
        room_id="storage1",
        area=20.0,
        room_type=RoomType.STORAGE,
        occupant_type=OccupantType.NONE,
        expected_occupants=0,
        visible_fraction=0.6
    ))
    
    building.add_room(Room(
        room_id="mechanical",
        area=18.0,
        room_type=RoomType.MECHANICAL,
        occupant_type=OccupantType.NONE,
        expected_occupants=0,
        visible_fraction=0.5
    ))
    
    # Add entrance as starting point
    building.add_room(Room(
        room_id="entrance",
        area=10.0,
        room_type=RoomType.EXIT,
        occupant_type=OccupantType.NONE,
        expected_occupants=0,
        visible_fraction=1.0
    ))
    
    # Connect rooms in a layout
    # Entrance connects to everything for simplicity
    for room_id in ["daycare", "medical", "classroom", "dormitory", "office1", 
                    "conference", "restroom", "hallway", "storage1", "mechanical"]:
        building.add_path("entrance", room_id, 10.0)
    
    # Cross-connections between priority zones
    building.add_path("daycare", "classroom", 5.0)
    building.add_path("medical", "office1", 8.0)
    building.add_path("classroom", "conference", 6.0)
    building.add_path("dormitory", "restroom", 7.0)
    building.add_path("hallway", "storage1", 5.0)
    building.add_path("storage1", "mechanical", 4.0)
    
    # Entrance is already marked as EXIT, so it's automatically tracked
    
    return building


def run_priority_test():
    """Run priority-based redundancy test."""
    print("\n" + "="*80)
    print("PRIORITY-BASED REDUNDANCY TEST SCENARIO")
    print("="*80)
    
    # Create building
    building = create_priority_test_building()
    
    print(f"\n📋 Building: {building.name}")
    print(f"   Total Rooms: {len(building.get_all_rooms())}")
    print(f"   Exits: {len(building.exits)}")
    
    print("\n🏢 Room Priority Breakdown:")
    rooms_by_priority = {}
    for room in building.get_all_rooms():
        priority = room.priority_level
        if priority not in rooms_by_priority:
            rooms_by_priority[priority] = []
        rooms_by_priority[priority].append(room)
    
    for priority in sorted(rooms_by_priority.keys(), reverse=True):
        rooms = rooms_by_priority[priority]
        print(f"\n   Priority {priority} ({len(rooms)} rooms):")
        for room in rooms:
            print(f"      • {room.room_id:12s} ({room.room_type.value:15s}) - "
                  f"Requires {room.required_sweeps_count} sweep(s)")
    
    # Create 3 teams of responders
    responders = [
        # Team 1
        Responder(
            responder_id="FF-Alpha",
            name="Alpha",
            strategy=SweepStrategy.NEAREST_FIRST,
            expertise=ExpertiseLevel.EXPERT,
            team_id=1
        ),
        # Team 2
        Responder(
            responder_id="FF-Bravo",
            name="Bravo",
            strategy=SweepStrategy.NEAREST_FIRST,
            expertise=ExpertiseLevel.INTERMEDIATE,
            team_id=2
        ),
        # Team 3
        Responder(
            responder_id="FF-Charlie",
            name="Charlie",
            strategy=SweepStrategy.NEAREST_FIRST,
            expertise=ExpertiseLevel.INTERMEDIATE,
            team_id=3
        ),
    ]
    
    print(f"\n👨‍🚒 Responders: {len(responders)} firefighters in {len(set(r.team_id for r in responders))} teams")
    for r in responders:
        print(f"   • {r.name} (Team {r.team_id}, {r.expertise.name})")
    
    # Create and run simulation
    sim = SweepSimulation(building, responders)
    
    # All start at entrance
    sim.assign_starting_positions({
        "FF-Alpha": "entrance",
        "FF-Bravo": "entrance",
        "FF-Charlie": "entrance",
    })
    
    print("\n🔄 Running simulation...")
    results = sim.run_simulation(max_iterations=2000)
    
    # Print results
    print("\n" + "="*80)
    print("SIMULATION RESULTS")
    print("="*80)
    
    print(f"\n⏱️  Completion Time: {results['completion_time']:.1f} seconds "
          f"({results['completion_time_minutes']:.1f} minutes)")
    print(f"✅ Building Fully Swept: {'YES' if results['fully_swept'] else 'NO'}")
    print(f"🔁 Iterations: {results['iterations']}")
    
    # Detailed room analysis
    print("\n📊 Room-by-Room Analysis:")
    print(f"{'Room ID':<15} {'Type':<15} {'Priority':<10} {'Required':<10} {'Actual':<10} {'Teams':<20} {'Status'}")
    print("-" * 90)
    
    for room in sorted(building.get_all_rooms(), key=lambda r: -r.priority_level):
        teams = room.get_sweeping_teams()
        status = "✅ Complete" if room.is_fully_swept() else "❌ Incomplete"
        print(f"{room.room_id:<15} {room.room_type.value:<15} {room.priority_level:<10} "
              f"{room.required_sweeps_count:<10} {room.actual_sweeps_count:<10} "
              f"{','.join(str(t) for t in teams):<20} {status}")
    
    # Verify priority requirements
    print("\n🔍 Priority Requirement Verification:")
    all_correct = True
    
    for priority in sorted(rooms_by_priority.keys(), reverse=True):
        rooms = rooms_by_priority[priority]
        priority_name = {5: "Critical", 4: "High", 3: "Medium", 2: "Low", 1: "Minimal"}
        
        print(f"\n   Priority {priority} ({priority_name.get(priority, 'Unknown')}):")
        for room in rooms:
            expected = room.required_sweeps_count
            actual = room.actual_sweeps_count
            teams = room.get_sweeping_teams()
            
            if actual >= expected and len(teams) >= expected:
                print(f"      ✅ {room.room_id}: {actual}/{expected} sweeps by {len(teams)} teams")
            else:
                print(f"      ❌ {room.room_id}: {actual}/{expected} sweeps by {len(teams)} teams (FAILED)")
                all_correct = False
    
    print("\n" + "="*80)
    if all_correct and results['fully_swept']:
        print("🎉 SUCCESS! All priority requirements met!")
    else:
        print("⚠️  WARNING: Some priority requirements not met")
    print("="*80 + "\n")
    
    return results


def run_priority_test_with_emergency():
    """Run priority test with an emergency scenario."""
    print("\n" + "="*80)
    print("PRIORITY-BASED REDUNDANCY WITH EMERGENCY")
    print("="*80)
    
    # Create building with fire emergency
    emergency = EmergencyContext(
        emergency_type=EmergencyType.FIRE,
        severity=1.2,
        has_smoke=True,
        smoke_density=2.0
    )
    
    building = create_priority_test_building()
    building.emergency = emergency
    
    print(f"\n🚨 Emergency: {emergency.emergency_type.value.upper()}")
    print(f"   Severity: {emergency.severity}x")
    print(f"   Smoke: {'Yes' if emergency.has_smoke else 'No'}")
    if emergency.has_smoke:
        print(f"   Smoke Density: {emergency.smoke_density}")
    
    # Create responders
    responders = [
        Responder("FF-Alpha", "Alpha", SweepStrategy.NEAREST_FIRST, ExpertiseLevel.EXPERT, team_id=1),
        Responder("FF-Bravo", "Bravo", SweepStrategy.NEAREST_FIRST, ExpertiseLevel.INTERMEDIATE, team_id=2),
        Responder("FF-Charlie", "Charlie", SweepStrategy.NEAREST_FIRST, ExpertiseLevel.INTERMEDIATE, team_id=3),
    ]
    
    # Set emergency context for all responders
    for r in responders:
        r.set_emergency_context(emergency)
    
    sim = SweepSimulation(building, responders)
    sim.assign_starting_positions({
        "FF-Alpha": "entrance",
        "FF-Bravo": "entrance", 
        "FF-Charlie": "entrance",
    })
    
    print("\n🔄 Running simulation with emergency conditions...")
    results = sim.run_simulation(max_iterations=2000)
    
    print(f"\n⏱️  Completion Time: {results['completion_time']:.1f} seconds "
          f"({results['completion_time_minutes']:.1f} minutes)")
    print(f"✅ Building Fully Swept: {'YES' if results['fully_swept'] else 'NO'}")
    
    print("\n" + "="*80 + "\n")
    
    return results


if __name__ == "__main__":
    # Run basic priority test
    results1 = run_priority_test()
    
    # Run priority test with emergency
    results2 = run_priority_test_with_emergency()
    
    # Compare results
    print("\n" + "="*80)
    print("COMPARISON: Normal vs Emergency")
    print("="*80)
    print(f"Normal Conditions:   {results1['completion_time']:.1f}s ({results1['completion_time_minutes']:.1f} min)")
    print(f"Fire Emergency:      {results2['completion_time']:.1f}s ({results2['completion_time_minutes']:.1f} min)")
    print(f"Time Increase:       {results2['completion_time'] - results1['completion_time']:.1f}s "
          f"({((results2['completion_time'] / results1['completion_time']) - 1) * 100:.1f}% slower)")
    print("="*80 + "\n")
