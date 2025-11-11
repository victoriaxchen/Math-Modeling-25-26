#!/usr/bin/env python3
"""
Test script for team-based redundancy: sweep, check, resweep cycle.
"""

from building import Building
from room import Room, RoomType, OccupantType
from responder import Responder, SweepStrategy, ExpertiseLevel
from simulation import SweepSimulation


def create_minimal_building() -> Building:
    """
    Create a minimal building with 3 rooms for testing redundancy.
    Simple linear layout: Exit1 - Hallway - Room1
    """
    building = Building("Test Redundancy Building")
    
    # Create simple rooms
    exit1 = Room("Exit1", area=5.0, room_type=RoomType.EXIT)
    hallway = Room("Hallway", area=15.0, room_type=RoomType.HALLWAY)
    room1 = Room("Room1", area=25.0, room_type=RoomType.OFFICE, expected_occupants=2)
    
    # Add rooms
    for room in [exit1, hallway, room1]:
        building.add_room(room)
    
    # Connect rooms
    building.add_path("Exit1", "Hallway", distance=5.0)
    building.add_path("Hallway", "Room1", distance=8.0)
    
    return building


def test_sweep_check_resweep_cycle():
    """Test the full sweep -> check -> resweep cycle."""
    print("\n" + "=" * 70)
    print("TEST: Team-Based Redundancy Sweep -> Check -> Resweep Cycle")
    print("=" * 70)
    
    # Create minimal building
    building = create_minimal_building()
    print(f"\n🏢 Building: {building.name}")
    print(f"   Rooms: {', '.join([r.room_id for r in building.get_all_rooms()])}")
    
    # Create two responders in different teams
    team1_responder = Responder(
        "R1",
        "Responder 1 (Team 1)",
        strategy=SweepStrategy.NEAREST_FIRST,
        expertise=ExpertiseLevel.INTERMEDIATE,
        team_id=1
    )
    
    team2_responder = Responder(
        "R2",
        "Responder 2 (Team 2)",
        strategy=SweepStrategy.NEAREST_FIRST,
        expertise=ExpertiseLevel.INTERMEDIATE,
        team_id=2
    )
    
    responders = [team1_responder, team2_responder]
    print(f"\n👨‍🚒 Responders:")
    for r in responders:
        print(f"   {r.name} - Team {r.team_id}")
    
    # Run simulation
    print("\n🔄 Running simulation...")
    simulation = SweepSimulation(building, responders)
    simulation.assign_starting_positions({"R1": "Exit1", "R2": "Exit1"})
    results = simulation.run_simulation()
    
    # Print results
    print("\n📊 Simulation Results:")
    print(f"   Completion time: {results['completion_time']:.1f}s")
    print(f"   Fully swept: {results['fully_swept']}")
    print(f"   Re-sweeps due to redundancy: {results.get('resweep_count', 0)}")
    
    # Print building stats
    stats = results['building_stats']
    print(f"\n🏢 Building Stats:")
    print(f"   Total rooms: {stats['total_rooms']}")
    print(f"   Rooms swept: {stats['swept_rooms']}")
    print(f"   Total area: {stats['total_area']:.1f} m²")
    
    # Print responder stats
    print(f"\n👨‍🚒 Responder Stats:")
    for r_stats in results['responder_stats']:
        team_str = f" (Team {r_stats['team_id']})" if r_stats.get('team_id') else ""
        print(f"   {r_stats['name']}{team_str}:")
        print(f"      Rooms swept: {r_stats['rooms_swept']}")
        print(f"      Rooms checked: {r_stats.get('rooms_checked', 0)}")
        print(f"      Total time: {r_stats['total_time']:.1f}s")
    
    # Print events
    print(f"\n📝 Event Timeline:")
    for time, responder, event, room in results['events']:
        print(f"   {time:6.1f}s - {responder:20s} {event:12s} {room}")
    
    # Verify sweep/check behavior
    print("\n✅ Verification:")
    room_obj = building.get_room("Room1")
    if room_obj:
        print(f"   Room1 swept by team: {room_obj.swept_by_team}")
        print(f"   Room1 checked by team: {room_obj.checked_by_team}")
        print(f"   Room1 needs resweep: {room_obj.needs_resweep}")
        
        if room_obj.swept_by_team == room_obj.checked_by_team:
            print(f"   ⚠️  Same team swept and checked (should have triggered resweep)")
        else:
            print(f"   ✓ Different teams performed sweep and check (redundancy working)")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    test_sweep_check_resweep_cycle()
    print("✅ Test completed successfully!")
