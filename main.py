"""Main entry point for the building sweep simulation."""

from simulation import SweepSimulation
from task1_scenario import (
    create_task1_building,
    create_task1_responders,
    get_task1_starting_positions
)
from visualization import plot_building_layout


def main():
    """Run the Task 1 building sweep simulation."""
    print("\n🚨 EMERGENCY BUILDING SWEEP SIMULATION 🚨\n")
    print("Task 1: Three firefighters sweeping a one-story office building")
    print("-" * 70)
    
    # Create the building
    print("\n📐 Creating building layout...")
    building = create_task1_building()
    print(f"   {building}")
    
    # Plot the initial building layout
    print("\n📊 Generating building layout plot...")
    plot_building_layout(building, save_path="building_layout_initial.png", show=False)
    print("   Initial layout saved to building_layout_initial.png")
    
    # Create responders
    print("\n👨‍🚒 Creating firefighter team...")
    responders = create_task1_responders()
    for r in responders:
        print(f"   {r}")
    
    # Create simulation
    print("\n🎬 Initializing simulation...")
    simulation = SweepSimulation(building, responders)
    
    # Assign starting positions
    starting_positions = get_task1_starting_positions()
    simulation.assign_starting_positions(starting_positions)
    print(f"   Starting positions: {starting_positions}")
    
    # Run simulation
    print("\n▶️  Running simulation...\n")
    results = simulation.run_simulation()
    
    # Print results
    simulation.print_summary(results)
    
    # Plot the final building state (with swept rooms)
    print("\n📊 Generating final building state plot...")
    plot_building_layout(building, save_path="building_layout_final.png", show=False)
    print("   Final state saved to building_layout_final.png")
    
    # Answer the key question
    print("\n🔑 KEY ANSWER:")
    print(f"   The three firefighters will complete the sweep in approximately")
    print(f"   {results['completion_time']:.1f} seconds ({results['completion_time_minutes']:.2f} minutes)")
    print()


if __name__ == "__main__":
    main()
