"""Responder module for firefighters and other emergency responders."""

from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from room import Room

if TYPE_CHECKING:
    from emergency import EmergencyContext


class SweepStrategy(Enum):
    """Different sweeping strategies for responders."""
    NEAREST_FIRST = "nearest_first"  # Sweep nearest unswept room first
    SYSTEMATIC = "systematic"  # Sweep rooms in a systematic order
    PRIORITY_BASED = "priority_based"  # Prioritize based on occupancy/smoke
    SPLIT_COVERAGE = "split_coverage"  # Divide building into zones


class ExpertiseLevel(Enum):
    """Expertise levels for responders."""
    NOVICE = 0.7  # Slower, less efficient
    INTERMEDIATE = 1.0  # Standard speed
    EXPERT = 1.3  # Faster, more efficient
    VETERAN = 1.5  # Very fast and efficient


class Responder:
    """Represents a firefighter or emergency responder."""
    
    def __init__(
        self,
        responder_id: str,
        name: str,
        strategy: SweepStrategy = SweepStrategy.NEAREST_FIRST,
        expertise: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE,
        movement_speed: float = 3.0,  # meters per second (updated default)
        team_id: Optional[int] = None,
        emergency_context: Optional['EmergencyContext'] = None,
    ):
        """
        Initialize a Responder.
        
        Args:
            responder_id: Unique identifier
            name: Name of the responder
            strategy: Sweeping strategy to use
            expertise: Expertise level
            movement_speed: Speed of movement in meters per second
            team_id: Team identifier (e.g., 1 for team A, 2 for team B)
            emergency_context: Emergency conditions affecting operations
        """
        self.responder_id = responder_id
        self.name = name
        self.strategy = strategy
        self.expertise = expertise
        self.base_movement_speed = movement_speed  # Store base speed
        self.movement_speed = movement_speed
        self.team_id = team_id
        self.emergency_context = emergency_context
        
        # Apply emergency speed reduction if applicable
        if self.emergency_context:
            self.movement_speed = self.base_movement_speed * self.emergency_context.get_movement_speed_multiplier()
        
        # State tracking
        self.current_room_id: Optional[str] = None
        self.rooms_swept: List[str] = []
        self.rooms_checked: List[str] = []
        self.total_distance_traveled: float = 0.0
        self.total_sweep_time: float = 0.0
        self.current_time: float = 0.0
        self.is_available: bool = True  # Whether responder is available for next task
        
    def set_emergency_context(self, emergency_context: 'EmergencyContext'):
        """
        Set or update the emergency context.
        
        Args:
            emergency_context: New emergency conditions
        """
        self.emergency_context = emergency_context
        # Recalculate movement speed
        if self.emergency_context:
            self.movement_speed = self.base_movement_speed * self.emergency_context.get_movement_speed_multiplier()
        else:
            self.movement_speed = self.base_movement_speed
        
    def get_expertise_multiplier(self) -> float:
        """Get the expertise multiplier for sweep duration calculation."""
        return self.expertise.value
    
    def calculate_travel_time(self, distance: float) -> float:
        """
        Calculate time to travel a given distance.
        
        Args:
            distance: Distance in meters
            
        Returns:
            Time in seconds
        """
        return distance / self.movement_speed
    
    def move_to_room(self, room_id: str, distance: float, current_time: float):
        """
        Move to a new room.
        
        Args:
            room_id: ID of the room to move to
            distance: Distance to travel
            current_time: Current simulation time
        """
        travel_time = self.calculate_travel_time(distance)
        self.current_room_id = room_id
        self.total_distance_traveled += distance
        self.current_time = current_time + travel_time
        
    def sweep_room(self, room: Room) -> float:
        """
        Sweep a room and return the time taken.
        
        Args:
            room: Room to sweep
            
        Returns:
            Time taken to sweep in seconds
        """
        sweep_duration = room.calculate_sweep_duration(
            self.get_expertise_multiplier(),
            emergency_context=self.emergency_context
        )
        self.total_sweep_time += sweep_duration
        self.rooms_swept.append(room.room_id)
        room.mark_swept(self.current_time + sweep_duration, team_id=self.team_id)
        self.current_time += sweep_duration
        return sweep_duration
    
    def check_room(self, room: Room) -> bool:
        """
        Check/verify a previously swept room.
        
        Args:
            room: Room to check
            
        Returns:
            True if re-sweep is needed, False otherwise
        """
        # A quick check takes 10% of a full sweep
        check_duration = room.calculate_sweep_duration(
            self.get_expertise_multiplier(),
            emergency_context=self.emergency_context
        ) * 0.1
        self.rooms_checked.append(room.room_id)
        room.mark_checked(self.current_time + check_duration, team_id=self.team_id)
        self.current_time += check_duration
        # Return whether re-sweep is needed
        return room.needs_resweep
    
    def get_priority_score(self, room: Room, distance: float) -> float:
        """
        Calculate priority score for a room (higher = more priority).
        Used in PRIORITY_BASED strategy.
        
        Args:
            room: Room to evaluate
            distance: Distance to the room
            
        Returns:
            Priority score
        """
        score = 0.0
        
        # Add emergency-specific priority bonus
        if self.emergency_context:
            score += self.emergency_context.get_priority_bonus()
        
        # Prioritize rooms with smoke (highest priority)
        if room.has_smoke:
            score += 150
        
        # Prioritize rooms with poor visibility (smoke/darkness)
        if not room.is_visible:
            score += 100
            
        # Prioritize rooms with occupants
        score += room.expected_occupants * 10
        
        # Prefer closer rooms (inverse of distance)
        if distance > 0:
            score += 50 / distance
            
        return score
    
    def reset(self):
        """Reset responder state for a new simulation."""
        self.current_room_id = None
        self.rooms_swept = []
        self.rooms_checked = []
        self.total_distance_traveled = 0.0
        self.total_sweep_time = 0.0
        self.current_time = 0.0
        self.is_available = True
        
    def get_stats(self) -> dict:
        """Get statistics about this responder's performance."""
        return {
            'responder_id': self.responder_id,
            'name': self.name,
            'team_id': self.team_id,
            'rooms_swept': len(self.rooms_swept),
            'rooms_checked': len(self.rooms_checked),
            'total_distance': round(self.total_distance_traveled, 2),
            'total_sweep_time': round(self.total_sweep_time, 2),
            'total_time': round(self.current_time, 2),
            'expertise': self.expertise.name,
            'strategy': self.strategy.value
        }
    
    def __repr__(self) -> str:
        """String representation of the responder."""
        team_str = f", team {self.team_id}" if self.team_id else ""
        return (f"Responder({self.name}, {self.expertise.name}{team_str}, "
                f"swept {len(self.rooms_swept)} rooms, checked {len(self.rooms_checked)})")
