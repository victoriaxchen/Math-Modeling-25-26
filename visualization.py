"""Visualization utilities for building layouts and simulation results."""

from building import Building
from room import RoomType
import json
import matplotlib.pyplot as plt
import networkx as nx


def visualize_building_ascii(building: Building) -> str:
    """
    Create a simple ASCII visualization of the building.
    
    Args:
        building: Building to visualize
        
    Returns:
        String with ASCII art representation
    """
    output = []
    output.append("\nBuilding Layout:")
    output.append("=" * 60)
    
    # Group rooms by type
    exits = [r for r in building.get_all_rooms() if r.room_type == RoomType.EXIT]
    hallways = [r for r in building.get_all_rooms() if r.room_type == RoomType.HALLWAY]
    offices = [r for r in building.get_all_rooms() if r.room_type == RoomType.OFFICE]
    
    output.append("\nExits:")
    for room in exits:
        status = "✓" if room.is_swept else "✗"
        output.append(f"  [{status}] {room.room_id:15s} - {room.area:.0f} m²")
    
    output.append("\nHallways:")
    for room in hallways:
        status = "✓" if room.is_swept else "✗"
        output.append(f"  [{status}] {room.room_id:15s} - {room.area:.0f} m²")
    
    output.append("\nOffices:")
    for room in offices:
        status = "✓" if room.is_swept else "✗"
        smoke = "🔥" if room.has_smoke else ""
        visibility = "🌫️" if not room.is_visible and not room.has_smoke else ""
        team_info = ""
        if room.swept_by_team:
            team_info += f" [Swept by T{room.swept_by_team}]"
        if room.checked_by_team:
            team_info += f" [Checked by T{room.checked_by_team}]"
        if room.needs_resweep:
            team_info += " [⚠️ NEEDS RESWEEP]"
        output.append(f"  [{status}] {room.room_id:15s} - {room.area:.0f} m² {smoke}{visibility}{team_info}")
    
    output.append("\nConnections:")
    edges = list(building.graph.edges(data=True))
    for room1, room2, data in edges:
        distance = data.get('distance', 0)
        output.append(f"  {room1:15s} <--{distance:5.1f}m--> {room2}")
    
    output.append("=" * 60)
    return "\n".join(output)


def export_results_json(results: dict, filename: str = "results.json"):
    """
    Export simulation results to JSON file.
    
    Args:
        results: Simulation results dictionary
        filename: Output filename
    """
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results exported to {filename}")


def create_summary_report(results: dict) -> str:
    """
    Create a text summary report of the simulation.
    
    Args:
        results: Simulation results dictionary
        
    Returns:
        Formatted report string
    """
    report = []
    report.append("\n" + "=" * 70)
    report.append("BUILDING SWEEP SIMULATION - EXECUTIVE SUMMARY")
    report.append("=" * 70)
    
    report.append(f"\nSweep Completion Time: {results['completion_time_minutes']:.2f} minutes")
    report.append(f"Total Rooms Swept: {results['building_stats']['swept_rooms']}")
    report.append(f"Total Building Area: {results['building_stats']['total_area']:.0f} m²")
    
    # Add redundancy stats
    if 'resweep_count' in results:
        report.append(f"Rooms Re-swept (due to redundancy): {results['resweep_count']}")
    
    report.append("\nResponder Efficiency (by Team):")
    # Group responders by team
    teams = {}
    for r in results['responder_stats']:
        team_id = r.get('team_id', 'None')
        if team_id not in teams:
            teams[team_id] = []
        teams[team_id].append(r)
    
    for team_id in sorted(teams.keys()):
        team_responders = teams[team_id]
        team_str = f"Team {team_id}" if team_id != 'None' else "Unassigned"
        report.append(f"\n  {team_str}:")
        
        team_swept = sum(r['rooms_swept'] for r in team_responders)
        team_checked = sum(r.get('rooms_checked', 0) for r in team_responders)
        team_distance = sum(r['total_distance'] for r in team_responders)
        
        for r in team_responders:
            efficiency = r['rooms_swept'] / (r['total_time'] / 60) if r['total_time'] > 0 else 0
            report.append(f"    {r['name']}: {r['rooms_swept']} swept, "
                         f"{r.get('rooms_checked', 0)} checked, "
                         f"{efficiency:.2f} rooms/min")
        
        report.append(f"    Team totals: {team_swept} swept, {team_checked} checked, "
                     f"{team_distance:.1f}m traveled")
    
    report.append("\nKey Metrics:")
    total_sweep_time = sum(r['total_sweep_time'] for r in results['responder_stats'])
    total_distance = sum(r['total_distance'] for r in results['responder_stats'])
    report.append(f"  Combined sweep time: {total_sweep_time:.1f} seconds")
    report.append(f"  Combined distance traveled: {total_distance:.1f} meters")
    
    report.append("=" * 70)
    
    return "\n".join(report)


def plot_building_layout(building: Building, save_path: str = None, show: bool = True):
    """
    Create a network plot of the building layout.
    
    Args:
        building: Building to visualize
        save_path: Optional path to save the plot
        show: Whether to display the plot
    """
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Create custom positions for Task 1 building layout
    # This creates a structured layout matching the building design
    pos = {}
    
    # Define positions manually for a clearer layout
    # Top row (Room1 side)
    pos['Room1A'] = (0, 2)
    pos['Room1B'] = (2, 2)
    pos['Room1C'] = (4, 2)
    
    # Middle row (Hallway)
    pos['Exit1'] = (-1, 1)
    pos['Hallway_L'] = (0, 1)
    pos['Hallway_C'] = (2, 1)
    pos['Hallway_R'] = (4, 1)
    pos['Exit2'] = (5, 1)
    
    # Bottom row (Room2 side)
    pos['Room2A'] = (0, 0)
    pos['Room2B'] = (2, 0)
    pos['Room2C'] = (4, 0)
    
    # For any rooms not in the predefined layout, use spring layout
    predefined_rooms = set(pos.keys())
    all_rooms = set(building.graph.nodes())
    undefined_rooms = all_rooms - predefined_rooms
    
    if undefined_rooms:
        # Use spring layout only for undefined rooms
        temp_graph = building.graph.subgraph(undefined_rooms)
        temp_pos = nx.spring_layout(temp_graph, k=1, iterations=50)
        # Offset to avoid overlap
        for node, coord in temp_pos.items():
            pos[node] = (coord[0] * 2 + 2, coord[1] * 2 - 1)
    
    # Categorize nodes by room type
    exits = [r.room_id for r in building.get_all_rooms() if r.room_type == RoomType.EXIT]
    hallways = [r.room_id for r in building.get_all_rooms() if r.room_type == RoomType.HALLWAY]
    offices = [r.room_id for r in building.get_all_rooms() if r.room_type == RoomType.OFFICE]
    swept_rooms = [r.room_id for r in building.get_all_rooms() if r.is_swept]
    other_rooms = [r.room_id for r in building.get_all_rooms() 
                   if r.room_type not in [RoomType.EXIT, RoomType.HALLWAY, RoomType.OFFICE]]
    
    # Draw edges with distances as labels
    nx.draw_networkx_edges(building.graph, pos, width=3, alpha=0.6, edge_color='gray', ax=ax)
    
    # Draw edge labels (distances)
    edge_labels = nx.get_edge_attributes(building.graph, 'distance')
    edge_labels = {k: f"{v:.1f}m" for k, v in edge_labels.items()}
    nx.draw_networkx_edge_labels(building.graph, pos, edge_labels, font_size=10, 
                                 font_weight='bold', ax=ax)
    
    # Draw nodes by category with different colors
    node_size = 3500
    
    # Draw exits (green)
    if exits:
        nx.draw_networkx_nodes(building.graph, pos, nodelist=exits, 
                              node_color='lightgreen', node_size=node_size,
                              node_shape='s', edgecolors='darkgreen', linewidths=4, ax=ax)
    
    # Draw hallways (light blue)
    if hallways:
        nx.draw_networkx_nodes(building.graph, pos, nodelist=hallways,
                              node_color='lightblue', node_size=node_size,
                              node_shape='o', edgecolors='blue', linewidths=3, ax=ax)
    
    # Draw offices - swept vs unswept
    if offices:
        swept_offices = [r for r in offices if r in swept_rooms]
        unswept_offices = [r for r in offices if r not in swept_rooms]
        
        if swept_offices:
            nx.draw_networkx_nodes(building.graph, pos, nodelist=swept_offices,
                                  node_color='lightcoral', node_size=node_size,
                                  node_shape='o', edgecolors='darkred', linewidths=3, ax=ax)
        if unswept_offices:
            nx.draw_networkx_nodes(building.graph, pos, nodelist=unswept_offices,
                                  node_color='lightyellow', node_size=node_size,
                                  node_shape='o', edgecolors='orange', linewidths=3, ax=ax)
    
    # Draw other rooms
    if other_rooms:
        nx.draw_networkx_nodes(building.graph, pos, nodelist=other_rooms,
                              node_color='lightgray', node_size=node_size,
                              node_shape='o', edgecolors='black', linewidths=3, ax=ax)
    
    # Draw labels
    labels = {}
    for room in building.get_all_rooms():
        area = room.area
        swept = "✓" if room.is_swept else ""
        smoke = "🔥" if room.has_smoke else ""
        visibility = "🌫️" if not room.is_visible and not room.has_smoke else ""
        labels[room.room_id] = f"{room.room_id}\n{area:.0f}m²{swept}{smoke}{visibility}"
    
    nx.draw_networkx_labels(building.graph, pos, labels, font_size=10, 
                           font_weight='bold', ax=ax)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='lightgreen', edgecolor='darkgreen', label='Exit', linewidth=2),
        Patch(facecolor='lightblue', edgecolor='blue', label='Hallway', linewidth=2),
        Patch(facecolor='lightyellow', edgecolor='orange', label='Office (Unswept)', linewidth=2),
        Patch(facecolor='lightcoral', edgecolor='darkred', label='Office (Swept)', linewidth=2),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=12, framealpha=0.9)
    
    # Set title and formatting
    stats = building.get_building_stats()
    title = f"{building.name}\n{stats['total_rooms']} rooms, {stats['swept_rooms']} swept, {stats['total_area']:.0f}m²"
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    # Set axis limits with padding
    ax.set_xlim(-1.5, 5.5)
    ax.set_ylim(-0.5, 2.5)
    
    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"📊 Building plot saved to {save_path}")
    
    # Show if requested
    if show:
        plt.show()
    
    return fig, ax
