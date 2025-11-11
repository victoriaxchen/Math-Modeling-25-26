"""Simulation engine for building sweep operations."""

from typing import List, Dict, Tuple, Optional
from building import Building
from responder import Responder, SweepStrategy
from room import Room
import heapq


class SweepSimulation:
    """Simulates the sweep operation of a building by responders."""
    
    def __init__(self, building: Building, responders: List[Responder]):
        """
        Initialize a sweep simulation.
        
        Args:
            building: Building to sweep
            responders: List of responders performing the sweep
        """
        self.building = building
        self.responders = responders
        self.events: List[Tuple[float, str, str, str]] = []  # (time, responder, event, room)
        # Track teams for redundancy
        self.teams_by_id: Dict[int, List[Responder]] = self._group_responders_by_team()
        self.resweep_queue: List[str] = []  # Rooms needing re-sweep
        
        # Set emergency context for all responders from building
        for responder in self.responders:
            if not responder.emergency_context and self.building.emergency:
                responder.set_emergency_context(self.building.emergency)
        
    def reset(self):
        """Reset the simulation state."""
        self.building.reset_sweep_status()
        for responder in self.responders:
            responder.reset()
        self.events = []
        self.resweep_queue = []
        self.teams_by_id = self._group_responders_by_team()
        
    def _group_responders_by_team(self) -> Dict[int, List[Responder]]:
        """Group responders by team_id for coordination."""
        teams = {}
        for responder in self.responders:
            if responder.team_id:
                if responder.team_id not in teams:
                    teams[responder.team_id] = []
                teams[responder.team_id].append(responder)
        return teams
    
    def _get_checker_from_different_team(self, sweeper_team_id: int) -> Optional[Responder]:
        """
        Get an available responder from a different team to check a room.
        
        Args:
            sweeper_team_id: Team ID that performed the sweep
            
        Returns:
            An available responder from a different team, or None
        """
        for team_id, responders in self.teams_by_id.items():
            if team_id != sweeper_team_id:
                # Return the first available responder from the other team
                for r in responders:
                    if r.is_available:
                        return r
        return None
        
    def assign_starting_positions(self, assignments: Dict[str, str]):
        """
        Assign starting positions for responders.
        
        Args:
            assignments: Dict mapping responder_id to starting room_id
        """
        for responder in self.responders:
            if responder.responder_id in assignments:
                room_id = assignments[responder.responder_id]
                responder.current_room_id = room_id
                responder.current_time = 0.0
                self.log_event(0.0, responder.name, "START", room_id)
                
    def get_next_room(self, responder: Responder) -> Optional[str]:
        """
        Determine the next room for a responder to sweep based on their strategy.
        
        With priority-based redundancy:
        - Filters out rooms already swept by this responder's team
        - Prioritizes rooms needing more sweeps based on priority level
        
        Args:
            responder: The responder
            
        Returns:
            Room ID of next room to sweep, or None if all done
        """
        unswept_rooms = self.building.get_unswept_rooms()
        if not unswept_rooms:
            return None
            
        # Filter out rooms already swept by this team (for priority-based redundancy)
        team_id_str = str(responder.team_id) if responder.team_id else responder.responder_id
        available_rooms = [
            room for room in unswept_rooms 
            if not room.was_swept_by_team(team_id_str)
        ]
        
        if not available_rooms:
            return None
            
        current_room = responder.current_room_id
        if not current_room:
            return None
            
        strategy = responder.strategy
        
        if strategy == SweepStrategy.NEAREST_FIRST:
            # Find nearest unswept room, prioritizing higher priority rooms
            # First, sort by priority level (descending), then by distance
            candidates = []
            for room in available_rooms:
                _, distance = self.building.get_shortest_path(current_room, room.room_id)
                # Priority: higher priority rooms first, then nearest
                priority_score = room.priority_level * 1000 - distance
                candidates.append((priority_score, room.room_id, distance))
            
            if candidates:
                candidates.sort(reverse=True)  # Highest priority_score first
                return candidates[0][1]  # Return room_id
            return None
            
        elif strategy == SweepStrategy.PRIORITY_BASED:
            # Find highest priority unswept room
            max_priority = -float('inf')
            next_room = None
            
            for room in available_rooms:
                _, distance = self.building.get_shortest_path(current_room, room.room_id)
                priority = responder.get_priority_score(room, distance)
                if priority > max_priority:
                    max_priority = priority
                    next_room = room.room_id
                    
            return next_room
            
        elif strategy == SweepStrategy.SYSTEMATIC:
            # Sweep rooms in order of priority first, then by room ID
            sorted_rooms = sorted(
                available_rooms,
                key=lambda r: (-r.priority_level, r.room_id)
            )
            return sorted_rooms[0].room_id if sorted_rooms else None
            
        else:
            # Default to nearest first with priority weighting
            return self.get_next_room_nearest(responder, available_rooms)
            
    def get_next_room_nearest(self, responder: Responder, unswept_rooms: List[Room]) -> Optional[str]:
        """Helper method to find nearest unswept room."""
        current_room = responder.current_room_id
        min_distance = float('inf')
        next_room = None
        
        for room in unswept_rooms:
            _, distance = self.building.get_shortest_path(current_room, room.room_id)
            if distance < min_distance:
                min_distance = distance
                next_room = room.room_id
                
        return next_room
    
    def simulate_step(self, responder: Responder) -> bool:
        """
        Simulate one step (sweep one room) for a responder.
        
        Args:
            responder: The responder
            
        Returns:
            True if a room was swept, False if no more rooms available
        """
        next_room_id = self.get_next_room(responder)
        
        if not next_room_id:
            return False
            
        # Calculate travel time
        current_room = responder.current_room_id
        path, distance = self.building.get_shortest_path(current_room, next_room_id)
        
        if not path:
            return False
            
        # Move to room
        travel_time = responder.calculate_travel_time(distance)
        responder.total_distance_traveled += distance
        responder.current_time += travel_time
        responder.current_room_id = next_room_id
        
        self.log_event(
            responder.current_time,
            responder.name,
            "ARRIVE",
            next_room_id
        )
        
        # Sweep the room
        room = self.building.get_room(next_room_id)
        if room and not room.is_fully_swept():
            # Check if this team has already swept this room
            team_id_str = str(responder.team_id) if responder.team_id else responder.responder_id
            if not room.was_swept_by_team(team_id_str):
                sweep_duration = responder.sweep_room(room)
                # Mark room as swept by this team
                room.mark_swept(responder.current_time, team_id_str)
                self.log_event(
                    responder.current_time,
                    responder.name,
                    "SWEPT",
                    next_room_id
                )
            
        return True
    
    def run_simulation(self, max_iterations: int = 1000) -> Dict:
        """
        Run the complete simulation with team-based redundancy:
        1. Teams sweep unswept rooms
        2. Different teams check swept rooms
        3. Re-sweep rooms that need it (checked by same team)
        
        Args:
            max_iterations: Maximum number of iterations to prevent infinite loops
            
        Returns:
            Dictionary with simulation results
        """
        iteration = 0
        resweep_count = 0
        
        while iteration < max_iterations:
            # Phase 1: Sweep unswept rooms
            any_action = False
            for responder in self.responders:
                if self.building.has_unswept_rooms():
                    if self.simulate_step(responder):
                        any_action = True
            
            # Phase 2: Check swept but unchecked rooms (with different teams)
            rooms_to_check = [
                room for room in self.building.get_all_rooms()
                if room.is_swept and room.checked_by_team is None
            ]
            
            for room in rooms_to_check[:5]:  # Check up to 5 rooms per iteration
                checker = self._get_checker_from_different_team(room.swept_by_team or 1)
                if checker and room.swept_by_team:
                    # Move checker to room (simplified - instant)
                    checker.current_room_id = room.room_id
                    needs_resweep = checker.check_room(room)
                    self.log_event(
                        checker.current_time,
                        checker.name,
                        "CHECKED",
                        room.room_id
                    )
                    if needs_resweep:
                        resweep_count += 1
                        self.resweep_queue.append(room.room_id)
                        self.log_event(
                            checker.current_time,
                            checker.name,
                            "RESWEEP-NEEDED",
                            room.room_id
                        )
                    any_action = True
            
            # Phase 3: Re-sweep rooms that need it
            if self.resweep_queue:
                room_to_resweep = self.resweep_queue.pop(0)
                room = self.building.get_room(room_to_resweep)
                if room:
                    for responder in self.responders:
                        if responder.team_id != room.swept_by_team:
                            responder.current_room_id = room_to_resweep
                            responder.sweep_room(room)
                            self.log_event(
                                responder.current_time,
                                responder.name,
                                "RESWEEP",
                                room_to_resweep
                            )
                            any_action = True
                            break
            
            # Stop if no more actions needed
            if not any_action and not self.resweep_queue:
                break
                
            iteration += 1
            
        # Calculate results
        completion_time = max(r.current_time for r in self.responders) if self.responders else 0
        
        results = {
            'completion_time': round(completion_time, 2),
            'completion_time_minutes': round(completion_time / 60, 2),
            'fully_swept': self.building.is_fully_swept(),
            'building_stats': self.building.get_building_stats(),
            'responder_stats': [r.get_stats() for r in self.responders],
            'iterations': iteration,
            'resweep_count': resweep_count,
            'events': self.events
        }
        
        return results
    
    def log_event(self, time: float, responder: str, event: str, room: str):
        """Log a simulation event."""
        self.events.append((time, responder, event, room))
        
    def print_summary(self, results: Dict):
        """Print a summary of the simulation results."""
        print("\n" + "=" * 70)
        print(f"BUILDING SWEEP SIMULATION RESULTS - {self.building.name}")
        print("=" * 70)
        
        # Show emergency type if applicable
        if self.building.emergency:
            emergency = self.building.emergency
            print(f"\n🚨 Emergency Type: {emergency.emergency_type.value.upper()}")
            print(f"   Severity: {emergency.severity:.1f}x")
            if emergency.has_smoke:
                print(f"   Smoke Density: {emergency.smoke_density:.1f}")
            print(f"   Noticeable: {'Yes' if emergency.is_noticeable() else 'No (delayed occupant response)'}")
        
        print(f"\n📊 Overall Performance:")
        print(f"  Total Time: {results['completion_time']:.1f} seconds ({results['completion_time_minutes']:.1f} minutes)")
        print(f"  Building Fully Swept: {'✓ Yes' if results['fully_swept'] else '✗ No'}")
        if 'resweep_count' in results:
            print(f"  Rooms Re-swept (due to redundancy): {results['resweep_count']}")
        
        stats = results['building_stats']
        print(f"\n🏢 Building Stats:")
        print(f"  Total Rooms: {stats['total_rooms']}")
        print(f"  Rooms Swept: {stats['swept_rooms']}/{stats['total_rooms']}")
        print(f"  Total Area: {stats['total_area']:.1f} m²")
        print(f"  Number of Exits: {stats['num_exits']}")
        
        print(f"\n👨‍🚒 Responder Performance:")
        for r_stats in results['responder_stats']:
            team_str = f" (Team {r_stats['team_id']})" if r_stats.get('team_id') else ""
            print(f"\n  {r_stats['name']} ({r_stats['expertise']}){team_str}:")
            print(f"    Rooms Swept: {r_stats['rooms_swept']}")
            print(f"    Rooms Checked: {r_stats.get('rooms_checked', 0)}")
            print(f"    Distance Traveled: {r_stats['total_distance']:.1f} m")
            print(f"    Time Sweeping: {r_stats['total_sweep_time']:.1f} s")
            print(f"    Total Time: {r_stats['total_time']:.1f} s")
            print(f"    Strategy: {r_stats['strategy']}")
            
        print(f"\n📝 Event Timeline (first 20 events):")
        for i, (time, responder, event, room) in enumerate(results['events'][:20]):
            print(f"  {time:6.1f}s - {responder:12s} {event:12s} {room}")
            
        if len(results['events']) > 20:
            print(f"  ... ({len(results['events']) - 20} more events)")
            
        print("\n" + "=" * 70 + "\n")
