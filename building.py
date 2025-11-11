"""Building module for representing floor plans with rooms and hallways."""

import networkx as nx
from typing import Dict, List, Tuple, Optional
from room import Room, RoomType
from emergency import EmergencyContext, EmergencyType


class Building:
    """Represents a building with rooms connected by hallways."""
    
    def __init__(self, name: str = "Building", emergency: Optional[EmergencyContext] = None):
        """
        Initialize a Building.
        
        Args:
            name: Name of the building
            emergency: Emergency context affecting the building (None = normal conditions)
        """
        self.name = name
        self.graph = nx.Graph()  # Undirected graph for room connections
        self.rooms: Dict[str, Room] = {}
        self.exits: List[str] = []  # List of room IDs that are exits
        self.emergency = emergency or EmergencyContext(EmergencyType.EVACUATION_DRILL, severity=0.5)
        
    def add_room(self, room: Room):
        """
        Add a room to the building.
        
        Args:
            room: Room object to add
        """
        self.rooms[room.room_id] = room
        self.graph.add_node(room.room_id, room=room)
        
        # Track exits
        if room.room_type == RoomType.EXIT:
            self.exits.append(room.room_id)
            
    def add_path(self, room1_id: str, room2_id: str, distance: float):
        """
        Add a path (connection) between two rooms.
        
        Args:
            room1_id: ID of the first room
            room2_id: ID of the second room
            distance: Distance between rooms in meters
        """
        if room1_id not in self.rooms:
            raise ValueError(f"Room {room1_id} not found in building")
        if room2_id not in self.rooms:
            raise ValueError(f"Room {room2_id} not found in building")
            
        self.graph.add_edge(room1_id, room2_id, distance=distance)
        
    def get_room(self, room_id: str) -> Optional[Room]:
        """Get a room by its ID."""
        return self.rooms.get(room_id)
    
    def get_distance(self, room1_id: str, room2_id: str) -> float:
        """
        Get the distance between two connected rooms.
        
        Args:
            room1_id: ID of the first room
            room2_id: ID of the second room
            
        Returns:
            Distance in meters, or float('inf') if not connected
        """
        if self.graph.has_edge(room1_id, room2_id):
            return self.graph[room1_id][room2_id]['distance']
        return float('inf')
    
    def get_neighbors(self, room_id: str) -> List[str]:
        """Get all rooms connected to the given room."""
        if room_id in self.graph:
            return list(self.graph.neighbors(room_id))
        return []
    
    def get_shortest_path(self, start_id: str, end_id: str) -> Tuple[List[str], float]:
        """
        Get the shortest path between two rooms.
        
        Args:
            start_id: Starting room ID
            end_id: Ending room ID
            
        Returns:
            Tuple of (path as list of room IDs, total distance)
        """
        try:
            path = nx.shortest_path(
                self.graph, 
                start_id, 
                end_id, 
                weight='distance'
            )
            distance = nx.shortest_path_length(
                self.graph, 
                start_id, 
                end_id, 
                weight='distance'
            )
            return path, distance
        except nx.NetworkXNoPath:
            return [], float('inf')
    
    def get_all_rooms(self) -> List[Room]:
        """Get all rooms in the building."""
        return list(self.rooms.values())
    
    def get_unswept_rooms(self) -> List[Room]:
        """
        Get all rooms that haven't been fully swept yet.
        
        For priority-based redundancy, this returns rooms where:
        actual_sweeps_count < required_sweeps_count
        
        For backward compatibility, also returns rooms with is_swept=False.
        """
        return [room for room in self.rooms.values() if not room.is_fully_swept()]
    
    def has_unswept_rooms(self) -> bool:
        """Check if there are any rooms needing more sweeps."""
        return any(not room.is_fully_swept() for room in self.rooms.values())
    
    def is_fully_swept(self) -> bool:
        """Check if all rooms have received all required sweeps."""
        return all(room.is_fully_swept() for room in self.rooms.values())
    
    def reset_sweep_status(self):
        """Reset all rooms to unswept state and clear team tracking."""
        for room in self.rooms.values():
            room.is_swept = False
            room.is_checked = False
            room.sweep_time = None
            room.swept_by_team = None
            room.checked_by_team = None
            room.needs_resweep = False
            # Reset priority tracking
            room.actual_sweeps_count = 0
            room.sweep_history = []
            
    def get_building_stats(self) -> Dict:
        """Get statistics about the building."""
        total_rooms = len(self.rooms)
        swept_rooms = sum(1 for room in self.rooms.values() if room.is_swept)
        total_area = sum(room.area for room in self.rooms.values())
        
        return {
            'total_rooms': total_rooms,
            'swept_rooms': swept_rooms,
            'unswept_rooms': total_rooms - swept_rooms,
            'total_area': total_area,
            'num_exits': len(self.exits),
            'completion': swept_rooms / total_rooms if total_rooms > 0 else 0
        }
    
    def __repr__(self) -> str:
        """String representation of the building."""
        stats = self.get_building_stats()
        emergency_str = f", {self.emergency.emergency_type.value}" if self.emergency else ""
        return (f"Building({self.name}, "
                f"{stats['total_rooms']} rooms, "
                f"{stats['num_exits']} exits{emergency_str})")
