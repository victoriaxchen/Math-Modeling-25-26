"""Example experiments with different sweep strategies and configurations."""

from simulation import SweepSimulation
from task1_scenario import create_task1_building, get_task1_starting_positions
from responder import Responder, SweepStrategy, ExpertiseLevel
from visualization import visualize_building_ascii, create_summary_report


def experiment_different_strategies():
    """Compare different sweep strategies."""
    print("\n" + "=" * 70)
    print("EXPERIMENT: Comparing Different Sweep Strategies")
    print("=" * 70)
    
    strategies = [
        SweepStrategy.NEAREST_FIRST,
        SweepStrategy.PRIORITY_BASED,
        SweepStrategy.SYSTEMATIC
    ]
    
    results_comparison = []
    
    for strategy in strategies:
        print(f"\n📊 Testing {strategy.value} strategy...")
        
        # Create building and responders
        building = create_task1_building()
        
        firefighter1 = Responder(
            responder_id="FF1",
            name="Firefighter 1",
            strategy=strategy,
            expertise=ExpertiseLevel.INTERMEDIATE,
            team_id=1
        )
        
        firefighter2 = Responder(
            responder_id="FF2",
            name="Firefighter 2",
            strategy=strategy,
            expertise=ExpertiseLevel.INTERMEDIATE,
            team_id=2
        )
        
        responders = [firefighter1, firefighter2]
        
        # Run simulation
        simulation = SweepSimulation(building, responders)
        simulation.assign_starting_positions(get_task1_starting_positions())
        results = simulation.run_simulation()
        
        results_comparison.append({
            'strategy': strategy.value,
            'time': results['completion_time'],
            'time_minutes': results['completion_time_minutes']
        })
        
        print(f"   Completion time: {results['completion_time']:.1f}s ({results['completion_time_minutes']:.2f}min)")
    
    print("\n" + "=" * 70)
    print("RESULTS COMPARISON")
    print("=" * 70)
    for r in results_comparison:
        print(f"  {r['strategy']:20s}: {r['time']:6.1f}s ({r['time_minutes']:.2f}min)")
    
    best = min(results_comparison, key=lambda x: x['time'])
    print(f"\n🏆 Best strategy: {best['strategy']} ({best['time']:.1f}s)")
    print("=" * 70)


def experiment_expertise_levels():
    """Compare different expertise levels."""
    print("\n" + "=" * 70)
    print("EXPERIMENT: Impact of Expertise Levels")
    print("=" * 70)
    
    expertise_configs = [
        (ExpertiseLevel.NOVICE, ExpertiseLevel.NOVICE, "Two Novices"),
        (ExpertiseLevel.INTERMEDIATE, ExpertiseLevel.INTERMEDIATE, "Two Intermediates"),
        (ExpertiseLevel.EXPERT, ExpertiseLevel.EXPERT, "Two Experts"),
        (ExpertiseLevel.EXPERT, ExpertiseLevel.NOVICE, "Expert + Novice"),
    ]
    
    results_comparison = []
    
    for exp1, exp2, name in expertise_configs:
        print(f"\n📊 Testing {name}...")
        
        # Create building and responders
        building = create_task1_building()
        
        firefighter1 = Responder(
            responder_id="FF1",
            name="Firefighter 1",
            strategy=SweepStrategy.NEAREST_FIRST,
            expertise=exp1,
            team_id=1
        )
        
        firefighter2 = Responder(
            responder_id="FF2",
            name="Firefighter 2",
            strategy=SweepStrategy.NEAREST_FIRST,
            expertise=exp2,
            team_id=2
        )
        
        responders = [firefighter1, firefighter2]
        
        # Run simulation
        simulation = SweepSimulation(building, responders)
        simulation.assign_starting_positions(get_task1_starting_positions())
        results = simulation.run_simulation()
        
        results_comparison.append({
            'config': name,
            'time': results['completion_time'],
            'time_minutes': results['completion_time_minutes']
        })
        
        print(f"   Completion time: {results['completion_time']:.1f}s ({results['completion_time_minutes']:.2f}min)")
    
    print("\n" + "=" * 70)
    print("RESULTS COMPARISON")
    print("=" * 70)
    for r in results_comparison:
        print(f"  {r['config']:20s}: {r['time']:6.1f}s ({r['time_minutes']:.2f}min)")
    
    best = min(results_comparison, key=lambda x: x['time'])
    print(f"\n🏆 Best configuration: {best['config']} ({best['time']:.1f}s)")
    print("=" * 70)


def visualize_task1_building():
    """Visualize the Task 1 building layout."""
    building = create_task1_building()
    print(visualize_building_ascii(building))


if __name__ == "__main__":
    # Visualize building
    visualize_task1_building()
    
    # Run experiments
    experiment_different_strategies()
    experiment_expertise_levels()
