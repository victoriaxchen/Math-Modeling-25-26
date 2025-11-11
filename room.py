"""Room module for building sweep simulation."""

from enum import Enum
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from emergency import EmergencyContext

# Baseline time per square meter (T). This can be tuned for experiments.
# Default keeps prior behaviour (1.0 second per m²).
SWEEP_TIME_PER_SQM = 1.0


class RoomType(Enum):
    """
    Types of rooms in a building.
    
    Each room type has an implicit priority level (1-5) that determines
    redundancy requirements:
    - Priority 5 (Critical): Requires 3 sweeps by different teams
    - Priority 4 (High): Requires 2 sweeps by different teams
    - Priority 3 (Medium): Requires 2 sweeps (1 sweep + 1 check)
    - Priority 2 (Low): Requires 1 sweep + 1 check
    - Priority 1 (Minimal): Requires 1 sweep only
    """
    # Priority 5 - Critical (3 sweeps required)
    DAYCARE = "daycare"                    # Children, high vulnerability
    MEDICAL = "medical"                    # Patients, medical equipment
    ELDERLY_CARE = "elderly_care"          # Elderly, mobility issues
    
    # Priority 4 - High (2 sweeps required)
    CLASSROOM = "classroom"                # Students, high occupancy
    DORMITORY = "dormitory"                # Sleeping occupants
    PATIENT_ROOM = "patient_room"          # Individual patients
    
    # Priority 3 - Medium (1 sweep + 1 check)
    OFFICE = "office"                      # Normal occupancy
    CONFERENCE = "conference"              # Meeting spaces
    LABORATORY = "laboratory"              # Hazardous materials possible
    
    # Priority 2 - Low (1 sweep + 1 check)
    RESTROOM = "restroom"                  # Minimal occupancy
    BREAK_ROOM = "break_room"              # Low occupancy
    HALLWAY = "hallway"                    # Transitional space
    
    # Priority 1 - Minimal (1 sweep only, no check required)
    STORAGE = "storage"                    # No occupants expected
    MECHANICAL = "mechanical"              # Equipment rooms
    JANITOR_CLOSET = "janitor_closet"      # Minimal space
    EXIT = "exit"                          # Just entry/exit point


# Priority level mapping for room types
ROOM_PRIORITY_LEVELS = {
    # Priority 5 - Critical (3 sweeps required)
    RoomType.DAYCARE: 5,
    RoomType.MEDICAL: 5,
    RoomType.ELDERLY_CARE: 5,
    
    # Priority 4 - High (2 sweeps required)
    RoomType.CLASSROOM: 4,
    RoomType.DORMITORY: 4,
    RoomType.PATIENT_ROOM: 4,
    
    # Priority 3 - Medium (1 sweep + 1 check)
    RoomType.OFFICE: 3,
    RoomType.CONFERENCE: 3,
    RoomType.LABORATORY: 3,
    
    # Priority 2 - Low (1 sweep + 1 check)
    RoomType.RESTROOM: 2,
    RoomType.BREAK_ROOM: 2,
    RoomType.HALLWAY: 2,
    
    # Priority 1 - Minimal (1 sweep only)
    RoomType.STORAGE: 1,
    RoomType.MECHANICAL: 1,
    RoomType.JANITOR_CLOSET: 1,
    RoomType.EXIT: 1,
}


def get_required_sweeps(room_type: RoomType, priority_override: Optional[int] = None) -> int:
    """
    Get the number of required sweeps for a room based on its priority level.
    
    Args:
        room_type: Type of room
        priority_override: Optional manual priority override (1-5)
        
    Returns:
        Number of sweeps required by different teams
        
    Priority-to-sweeps mapping:
        5 (Critical): 3 sweeps
        4 (High): 2 sweeps
        3 (Medium): 1 sweep (+ 1 check by different team)
        2 (Low): 1 sweep (+ 1 check by different team)
        1 (Minimal): 1 sweep (no check required)
    """
    priority = priority_override if priority_override is not None else ROOM_PRIORITY_LEVELS.get(room_type, 3)
    
    if priority >= 5:
        return 3  # Critical rooms need 3 full sweeps
    elif priority >= 4:
        return 2  # High priority needs 2 full sweeps
    else:
        return 1  # All others need 1 sweep (+ check for priority 2-3)


def requires_check(room_type: RoomType, priority_override: Optional[int] = None) -> bool:
    """
    Determine if a room requires a check (verification) after sweep.
    
    Priority 1 rooms (storage, mechanical) don't require checks.
    Priority 2-5 rooms all require at least one check.
    
    Args:
        room_type: Type of room
        priority_override: Optional manual priority override
        
    Returns:
        True if room requires check, False otherwise
    """
    priority = priority_override if priority_override is not None else ROOM_PRIORITY_LEVELS.get(room_type, 3)
    return priority >= 2


class OccupantType(Enum):
    """Types of occupants that might be in a room."""
    NONE = "none"
    LOW_MOBILITY = "low_mobility"  # Elderly, disabled
    NORMAL = "normal"
    HIGH_DENSITY = "high_density"  # Many people


class Room:
    """Represents a room in a building with various attributes."""
    
    def __init__(
        self,
        room_id: str,
        area: float,  # in square meters
        room_type: RoomType,
        occupant_type: OccupantType = OccupantType.NONE,
        has_smoke: bool = False,
        is_visible: bool = True,
        visible_fraction: float = 1.0,
        is_swept: bool = False,
        is_checked: bool = False,
        expected_occupants: int = 0,
        priority_override: Optional[int] = None
    ):
        """
        Initialize a Room.
        
        Args:
            room_id: Unique identifier for the room
            area: Area of the room in square meters
            room_type: Type of room (office, conference, etc.)
            occupant_type: Type of occupants in the room
            has_smoke: Whether the room has smoke (automatically sets is_visible to False)
            is_visible: Whether the room has good visibility (False = smoke/poor visibility affects sweep time)
            is_swept: Whether the room has been swept
            expected_occupants: Expected number of occupants
            priority_override: Optional manual priority override (1-5), overrides room_type default
        """
        self.room_id = room_id
        self.area = area
        self.room_type = room_type
        self.occupant_type = occupant_type
        self.has_smoke = has_smoke
        # If there's smoke, automatically set visibility to False
        self.is_visible = False if has_smoke else is_visible
        # Fraction of floor area that is visible (0.0 - 1.0). Used to compute
        # a clutter multiplier. If smoke is present and the caller did not
        # supply a visible_fraction, default to a lower visibility.
        self.visible_fraction = visible_fraction
        if self.has_smoke and visible_fraction == 1.0:
            # default reduced visible area for smoky rooms
            self.visible_fraction = 0.3
        self.is_swept = is_swept
        self.is_checked = is_checked
        self.expected_occupants = expected_occupants
        
        # Priority-based redundancy tracking
        self.priority_override = priority_override
        self.priority_level = priority_override if priority_override is not None else ROOM_PRIORITY_LEVELS.get(room_type, 3)
        self.required_sweeps_count = get_required_sweeps(room_type, priority_override)
        self.actual_sweeps_count = 0
        self.sweep_history = []  # List of (time, team_id) tuples
        
        # Team / redundancy tracking (legacy - kept for backward compatibility)
        self.swept_by_team = None  # type: Optional[str]
        self.checked_by_team = None  # type: Optional[str]
        self.needs_resweep = False
        self.sweep_time: Optional[float] = None  # Time when room was swept
        
    def calculate_sweep_duration(
        self,
        responder_expertise: float = 1.0,
        sweep_time_per_sqm: Optional[float] = None,
        emergency_context: Optional['EmergencyContext'] = None,
    ) -> float:
        """
        Calculate how long it takes to sweep this room.
        
        Args:
            responder_expertise: Multiplier based on responder expertise (higher is faster)
            sweep_time_per_sqm: Override for baseline time per square meter
            emergency_context: Emergency conditions affecting sweep operations
            
        Returns:
            Time in seconds to sweep the room
        """
        # Use override if provided, otherwise use module-level constant
        T = sweep_time_per_sqm if sweep_time_per_sqm is not None else SWEEP_TIME_PER_SQM
        # Compute clutter multiplier C based on visible floor fraction r =
        # (visible floor area) / (total area). The user-specified mapping is:
        #   C=1 if r in (0.8, 1]
        #   C=2 if r in (0.6, 0.8]
        #   C=3 if r in (0.4, 0.6]
        #   C=4 if r in (0.2, 0.4]
        #   C=5 if r in [0.0, 0.2]
        r = max(0.0, min(1.0, self.visible_fraction))
        if r > 0.8:
            clutter_C = 1
        elif r > 0.6:
            clutter_C = 2
        elif r > 0.4:
            clutter_C = 3
        elif r > 0.2:
            clutter_C = 4
        else:
            clutter_C = 5

        # Base time uses the requested formula T * A * C
        base_time = T * self.area * clutter_C
        
        # Adjust for room type
        type_multipliers = {
            RoomType.OFFICE: 1.2,  # More places to check
            RoomType.CONFERENCE: 1.0,  # Open layout
            RoomType.STORAGE: 1.5,  # Cluttered
            RoomType.RESTROOM: 0.8,  # Small, simple
            RoomType.HALLWAY: 0.5,  # Quick visual sweep
            RoomType.EXIT: 0.1,  # Just need to check
        }
        base_time *= type_multipliers.get(self.room_type, 1.0)
        
        # Adjust for occupant type
        occupant_multipliers = {
            OccupantType.NONE: 0.8,
            OccupantType.LOW_MOBILITY: 1.5,  # Need extra care
            OccupantType.NORMAL: 1.0,
            OccupantType.HIGH_DENSITY: 1.3,  # More people to check
        }
        base_time *= occupant_multipliers.get(self.occupant_type, 1.0)
        
        # Apply emergency-specific multipliers
        if emergency_context:
            # Visibility impact (smoke reduces visibility)
            base_time *= emergency_context.get_visibility_multiplier()
            
            # Occupant response (unnoticeable emergencies slow down occupant interaction)
            if self.expected_occupants > 0:
                base_time *= emergency_context.get_occupant_response_multiplier()
            
            # Overall sweep difficulty (emergency type, protective gear, etc.)
            base_time *= emergency_context.get_sweep_difficulty_multiplier()
        
        # Poor visibility (smoke/darkness) can further slow down the sweep.
        # We treat `is_visible` as a boolean fallback; if a room is marked not
        # visible, apply an additional penalty proportional to reduced
        # visibility.
        if not self.is_visible:
            # scale by inverse of visible fraction (but cap to avoid extreme values)
            penalty = min(3.0, 1.0 + (0.8 - r))
            base_time *= penalty

        # Quick sweep optimization: visible room with no occupants can be
        # checked faster. We only apply this if visible_fraction is high.
        if self.visible_fraction >= 0.9 and self.expected_occupants == 0:
            base_time /= 5.0  # 5x faster (20% of normal time)

        # Apply expertise factor (higher expertise reduces required time)
        base_time /= responder_expertise

        return base_time
    def mark_swept(self, time: float, team_id: Optional[str] = None):
        """Mark the room as swept at a specific time by a team.

        For priority-based redundancy, tracks multiple sweeps in sweep_history.
        For backward compatibility, also sets is_swept=True and updates swept_by_team
        to the most recent team.
        
        Args:
            time: Time when sweep occurred
            team_id: Identifier for the team performing the sweep
        """
        # Add to sweep history for priority tracking
        if team_id:
            self.sweep_history.append((time, team_id))
            self.actual_sweeps_count = len(self.sweep_history)
        
        # Legacy behavior for backward compatibility
        self.is_swept = True
        self.sweep_time = time
        if team_id:
            self.swept_by_team = team_id
        # Reset check state after a fresh sweep
        self.checked_by_team = None
        self.needs_resweep = False

    def mark_checked(self, time: float, team_id: Optional[str] = None):
        """Mark the room as checked by a team.

        If the checking team is the same as the sweeping team, require a
        re-sweep (redundancy rule). Otherwise, the room is considered
        successfully checked.
        """
        if team_id:
            self.checked_by_team = team_id

        if self.swept_by_team and self.checked_by_team and self.swept_by_team == self.checked_by_team:
            # Same team checked — require re-sweep
            self.needs_resweep = True
            # mark as not swept so it will be scheduled for re-sweep
            self.is_swept = False
            self.sweep_time = None
            self.swept_by_team = None
        else:
            # Successfully checked by a different team
            self.needs_resweep = False
    
    def is_fully_swept(self) -> bool:
        """
        Check if room has received all required sweeps based on its priority level.
        
        Returns:
            True if actual_sweeps_count >= required_sweeps_count, False otherwise
        """
        return self.actual_sweeps_count >= self.required_sweeps_count
    
    def get_sweeping_teams(self) -> list[str]:
        """
        Get list of team IDs that have swept this room.
        
        Returns:
            List of unique team IDs from sweep_history
        """
        return list(set(team_id for _, team_id in self.sweep_history))
    
    def was_swept_by_team(self, team_id: str) -> bool:
        """
        Check if a specific team has already swept this room.
        
        Args:
            team_id: Team identifier to check
            
        Returns:
            True if team has swept this room, False otherwise
        """
        return any(tid == team_id for _, tid in self.sweep_history)
        
    def get_sweep_progress(self) -> str:
        """
        Get human-readable sweep progress string.
        
        Returns:
            String like "2/3 sweeps" or "1/1 sweep (complete)"
        """
        sweep_word = "sweep" if self.required_sweeps_count == 1 else "sweeps"
        status = " (complete)" if self.is_fully_swept() else ""
        return f"{self.actual_sweeps_count}/{self.required_sweeps_count} {sweep_word}{status}"
        
    def __repr__(self) -> str:
        """String representation of the room."""
        status = "✓" if self.is_swept else "✗"
        smoke = "🔥" if self.has_smoke else ""
        visibility = "🌫️" if not self.is_visible and not self.has_smoke else ""
        # Add priority indicator for high-priority rooms
        priority_indicator = ""
        if self.priority_level >= 4:
            priority_indicator = f" [P{self.priority_level}]"
        return f"Room({self.room_id}, {self.room_type.value}, {self.area}m², {status}{smoke}{visibility}{priority_indicator})"
