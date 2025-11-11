#!/usr/bin/env python3
"""
Test script for emergency type functionality.
Compares different emergency types and their impact on sweep operations.
"""

from building import Building
from room import Room, RoomType, OccupantType
from responder import Responder, SweepStrategy, ExpertiseLevel
from simulation import SweepSimulation
from emergency import EmergencyContext, EmergencyType, PRESET_EMERGENCIES


def create_test_building(emergency: EmergencyContext) -> Building:
    """Create a simple 3-room building for testing."""
    building = Building(name="Emergency Test Building", emergency=emergency)
    
    # Create simple layout: Exit -> Hallway -> Office
    exit_room = Room("Exit", area=5.0, room_type=RoomType.EXIT)
    hallway = Room("Hallway", area=20.0, room_type=RoomType.HALLWAY)
    office = Room(
        "Office",
        area=30.0,
        room_type=RoomType.OFFICE,
        occupant_type=OccupantType.NORMAL,
        expected_occupants=5
    )
    
    building.add_room(exit_room)
    building.add_room(hallway)
    building.add_room(office)
    
    building.add_path("Exit", "Hallway", distance=5.0)
    building.add_path("Hallway", "Office", distance=8.0)
    
    return building


def create_test_responders(emergency: EmergencyContext) -> list:
    """Create 2 responders for testing."""
    ff1 = Responder(
        responder_id="FF1",
        name="Firefighter 1",
        strategy=SweepStrategy.NEAREST_FIRST,
        expertise=ExpertiseLevel.INTERMEDIATE,
        movement_speed=3.0,
        team_id=1,
        emergency_context=emergency
    )
    
    ff2 = Responder(
        responder_id="FF2",
        name="Firefighter 2",
        strategy=SweepStrategy.NEAREST_FIRST,
        expertise=ExpertiseLevel.INTERMEDIATE,
        movement_speed=3.0,
        team_id=2,
        emergency_context=emergency
    )
    
    return [ff1, ff2]


def test_emergency_comparison():
    """Compare different emergency types."""
    print("\n" + "=" * 80)
    print("EMERGENCY TYPE COMPARISON TEST")
    print("=" * 80)
    print("\nComparing sweep times for different emergency types...")
    print("(Same building, same responders, different emergency conditions)\n")
    
    # Emergency types to test
    emergency_scenarios = [
        ("Evacuation Drill", EmergencyContext(EmergencyType.EVACUATION_DRILL, severity=0.5)),
        ("Minor Fire", EmergencyContext(EmergencyType.FIRE, severity=0.8, smoke_density=0.3)),
        ("Major Fire", EmergencyContext(EmergencyType.FIRE, severity=2.0, smoke_density=0.9)),
        ("Gas Leak", EmergencyContext(EmergencyType.GAS_LEAK, severity=1.5)),
        ("CO Leak", EmergencyContext(EmergencyType.CO_LEAK, severity=1.5)),
        ("Smoke Only", EmergencyContext(EmergencyType.SMOKE_NO_FIRE, smoke_density=0.6)),
    ]
    
    results_comparison = []
    
    for name, emergency in emergency_scenarios:
        building = create_test_building(emergency)
        responders = create_test_responders(emergency)
        
        simulation = SweepSimulation(building, responders)
        simulation.assign_starting_positions({"FF1": "Exit", "FF2": "Exit"})
        
        results = simulation.run_simulation()
        
        results_comparison.append({
            'name': name,
            'emergency_type': emergency.emergency_type.value,
            'noticeable': emergency.is_noticeable(),
            'completion_time': results['completion_time'],
            'movement_multiplier': emergency.get_movement_speed_multiplier(),
            'visibility_multiplier': emergency.get_visibility_multiplier(),
            'occupant_response_multiplier': emergency.get_occupant_response_multiplier(),
            'sweep_difficulty': emergency.get_sweep_difficulty_multiplier(),
        })
        
        print(f"✓ {name}: {results['completion_time']:.1f}s ({results['completion_time_minutes']:.2f}min)")
    
    # Print detailed comparison
    print("\n" + "-" * 80)
    print("DETAILED COMPARISON")
    print("-" * 80)
    print(f"{'Emergency':<20} {'Time':<10} {'Movement':<12} {'Visibility':<12} {'Occupant':<12} {'Notice'}")
    print("-" * 80)
    
    for r in results_comparison:
        notice_str = "Yes" if r['noticeable'] else "No"
        print(f"{r['name']:<20} {r['completion_time']:>6.1f}s   "
              f"{r['movement_multiplier']:>6.2f}x     "
              f"{r['visibility_multiplier']:>6.2f}x     "
              f"{r['occupant_response_multiplier']:>6.2f}x     "
              f"{notice_str}")
    
    print("-" * 80)
    
    # Find extremes
    fastest = min(results_comparison, key=lambda x: x['completion_time'])
    slowest = max(results_comparison, key=lambda x: x['completion_time'])
    
    print(f"\n⚡ Fastest: {fastest['name']} ({fastest['completion_time']:.1f}s)")
    print(f"🐌 Slowest: {slowest['name']} ({slowest['completion_time']:.1f}s)")
    print(f"📊 Time difference: {slowest['completion_time'] - fastest['completion_time']:.1f}s "
          f"({((slowest['completion_time'] / fastest['completion_time']) - 1) * 100:.0f}% slower)")


def test_noticeable_vs_unnoticeable():
    """Test the impact of noticeable vs unnoticeable emergencies."""
    print("\n" + "=" * 80)
    print("NOTICEABLE vs UNNOTICEABLE EMERGENCY TEST")
    print("=" * 80)
    print("\nTesting occupant response time differences...\n")
    
    # Noticeable emergency (fire)
    fire = EmergencyContext(EmergencyType.FIRE, severity=1.0, smoke_density=0.5)
    building_fire = create_test_building(fire)
    responders_fire = create_test_responders(fire)
    sim_fire = SweepSimulation(building_fire, responders_fire)
    sim_fire.assign_starting_positions({"FF1": "Exit", "FF2": "Exit"})
    results_fire = sim_fire.run_simulation()
    
    # Unnoticeable emergency (CO leak)
    co = EmergencyContext(EmergencyType.CO_LEAK, severity=1.0)
    building_co = create_test_building(co)
    responders_co = create_test_responders(co)
    sim_co = SweepSimulation(building_co, responders_co)
    sim_co.assign_starting_positions({"FF1": "Exit", "FF2": "Exit"})
    results_co = sim_co.run_simulation()
    
    print(f"🔥 FIRE (noticeable):")
    print(f"   Completion time: {results_fire['completion_time']:.1f}s")
    print(f"   Occupant response: {fire.get_occupant_response_multiplier():.2f}x (normal)")
    print(f"   Movement speed: {fire.get_movement_speed_multiplier():.2f}x")
    
    print(f"\n☠️  CO LEAK (unnoticeable):")
    print(f"   Completion time: {results_co['completion_time']:.1f}s")
    print(f"   Occupant response: {co.get_occupant_response_multiplier():.2f}x (DELAYED)")
    print(f"   Movement speed: {co.get_movement_speed_multiplier():.2f}x")
    
    time_diff = results_co['completion_time'] - results_fire['completion_time']
    percent_diff = (time_diff / results_fire['completion_time']) * 100
    
    print(f"\n📊 CO leak takes {time_diff:.1f}s longer ({percent_diff:.0f}% increase)")
    print(f"   Reason: Occupants may be unconscious or unaware of danger")
    print(f"   Responders must spend more time searching and alerting occupants")


def test_smoke_impact():
    """Test the impact of smoke density."""
    print("\n" + "=" * 80)
    print("SMOKE DENSITY IMPACT TEST")
    print("=" * 80)
    print("\nTesting how smoke density affects operations...\n")
    
    smoke_levels = [
        ("No Smoke", 0.0),
        ("Light Smoke", 0.3),
        ("Moderate Smoke", 0.5),
        ("Heavy Smoke", 0.7),
        ("Dense Smoke", 1.0),
    ]
    
    results = []
    
    for name, density in smoke_levels:
        emergency = EmergencyContext(
            EmergencyType.FIRE,
            severity=1.0,
            has_smoke=density > 0,
            smoke_density=density
        )
        
        building = create_test_building(emergency)
        responders = create_test_responders(emergency)
        sim = SweepSimulation(building, responders)
        sim.assign_starting_positions({"FF1": "Exit", "FF2": "Exit"})
        result = sim.run_simulation()
        
        results.append({
            'name': name,
            'density': density,
            'time': result['completion_time'],
            'visibility_mult': emergency.get_visibility_multiplier(),
            'movement_mult': emergency.get_movement_speed_multiplier(),
        })
        
        print(f"  {name:<18} (density={density:.1f}): {result['completion_time']:>6.1f}s")
    
    print("\n" + "-" * 80)
    baseline = results[0]['time']
    print(f"Impact of smoke on completion time (baseline = {baseline:.1f}s):")
    print("-" * 80)
    
    for r in results[1:]:  # Skip "No Smoke"
        increase = r['time'] - baseline
        percent = (increase / baseline) * 100
        print(f"  {r['name']:<18}: +{increase:>5.1f}s (+{percent:>4.0f}%)")


def test_preset_emergencies():
    """Test preset emergency configurations."""
    print("\n" + "=" * 80)
    print("PRESET EMERGENCY CONFIGURATIONS TEST")
    print("=" * 80)
    print("\nTesting built-in preset emergencies...\n")
    
    for preset_name, emergency in PRESET_EMERGENCIES.items():
        building = create_test_building(emergency)
        responders = create_test_responders(emergency)
        sim = SweepSimulation(building, responders)
        sim.assign_starting_positions({"FF1": "Exit", "FF2": "Exit"})
        results = sim.run_simulation()
        
        print(f"✓ {preset_name:<20}: {results['completion_time']:>6.1f}s "
              f"({emergency.emergency_type.value}, severity={emergency.severity:.1f})")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚨 EMERGENCY TYPE TESTING SUITE 🚨")
    print("=" * 80)
    
    # Run all tests
    test_emergency_comparison()
    test_noticeable_vs_unnoticeable()
    test_smoke_impact()
    test_preset_emergencies()
    
    print("\n" + "=" * 80)
    print("✅ ALL EMERGENCY TYPE TESTS COMPLETED")
    print("=" * 80)
    print()
