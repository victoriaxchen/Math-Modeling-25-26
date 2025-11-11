"""Emergency type module for modeling different emergency scenarios."""

from enum import Enum
from typing import Optional


class EmergencyType(Enum):
    """
    Types of emergencies that affect building sweep operations.
    
    Emergencies are categorized by:
    - Noticeability: How obvious the emergency is to occupants
    - Visibility impact: How much smoke/obscuration affects operations
    - Movement impact: Speed reduction for responders
    - Occupant response: How quickly occupants recognize danger
    """
    
    # Noticeable emergencies (immediate awareness)
    FIRE = "fire"                          # Visible flames, smoke, heat
    STRUCTURAL_COLLAPSE = "structural"     # Visible damage, noise
    FLOOD = "flood"                        # Visible water
    
    # Unnoticeable emergencies (delayed awareness)
    GAS_LEAK = "gas_leak"                  # Odorless/subtle until severe
    CO_LEAK = "carbon_monoxide"            # Completely odorless
    CHEMICAL_LEAK = "chemical"             # May be odorless initially
    
    # Hybrid/variable
    SMOKE_NO_FIRE = "smoke_only"           # Smoke without active fire
    EVACUATION_DRILL = "drill"             # No actual emergency


class EmergencyContext:
    """
    Represents the emergency conditions affecting a building sweep operation.
    
    This class encapsulates all emergency-specific parameters that affect:
    - Room sweep durations
    - Responder movement speeds
    - Visibility and environmental conditions
    - Occupant awareness and response times
    """
    
    def __init__(
        self,
        emergency_type: EmergencyType,
        severity: float = 1.0,
        has_smoke: bool = False,
        smoke_density: float = 0.0,
    ):
        """
        Initialize emergency context.
        
        Args:
            emergency_type: Type of emergency
            severity: Emergency severity multiplier (0.5=minor, 1.0=normal, 2.0=severe)
            has_smoke: Whether smoke is present building-wide
            smoke_density: Density of smoke (0.0=none to 1.0=complete obscuration)
        """
        self.emergency_type = emergency_type
        self.severity = max(0.1, min(3.0, severity))  # Clamp between 0.1 and 3.0
        self.has_smoke = has_smoke
        self.smoke_density = max(0.0, min(1.0, smoke_density))  # Clamp 0-1
        
        # Set smoke properties based on emergency type if not explicitly set
        if not has_smoke:
            if emergency_type in [EmergencyType.FIRE, EmergencyType.SMOKE_NO_FIRE]:
                self.has_smoke = True
                self.smoke_density = 0.7 if emergency_type == EmergencyType.FIRE else 0.5
    
    def is_noticeable(self) -> bool:
        """
        Check if emergency is immediately noticeable to occupants.
        
        Returns:
            True for noticeable emergencies (fire, flood, structural)
            False for unnoticeable emergencies (gas, CO)
        """
        noticeable = {
            EmergencyType.FIRE,
            EmergencyType.STRUCTURAL_COLLAPSE,
            EmergencyType.FLOOD,
            EmergencyType.SMOKE_NO_FIRE,
            EmergencyType.EVACUATION_DRILL,
        }
        return self.emergency_type in noticeable
    
    def get_occupant_response_multiplier(self) -> float:
        """
        Get occupant response time multiplier.
        
        Unnoticeable emergencies have slower occupant response because:
        - Occupants don't realize danger immediately
        - May be unconscious or impaired (CO poisoning)
        - Require responders to actively search and alert
        
        Returns:
            Multiplier for occupant-related sweep time
            1.0 = normal response (noticeable emergency)
            1.5-3.0 = delayed response (unnoticeable emergency)
        """
        if self.emergency_type == EmergencyType.EVACUATION_DRILL:
            return 0.8  # Occupants respond quickly, no panic
        
        if self.is_noticeable():
            # Noticeable emergencies: occupants are alert and responsive
            return 1.0 * self.severity
        else:
            # Unnoticeable emergencies: occupants may be:
            # - Unaware of danger
            # - Impaired (CO poisoning causes confusion/unconsciousness)
            # - Resistant to evacuation ("I don't smell anything")
            response_delays = {
                EmergencyType.CO_LEAK: 2.5,        # Most dangerous: occupants may be unconscious
                EmergencyType.GAS_LEAK: 2.0,       # Occupants slow to recognize danger
                EmergencyType.CHEMICAL_LEAK: 2.2,  # Depends on chemical, assume dangerous
            }
            base_delay = response_delays.get(self.emergency_type, 1.5)
            return base_delay * self.severity
    
    def get_visibility_multiplier(self) -> float:
        """
        Get visibility impact multiplier for sweep operations.
        
        Returns:
            Multiplier for sweep time due to reduced visibility
            1.0 = perfect visibility
            1.5-3.0 = reduced visibility (proportional to smoke density)
        """
        if not self.has_smoke or self.smoke_density == 0:
            return 1.0
        
        # Visibility penalty increases non-linearly with smoke density
        # Light smoke (0.3): 1.3x slower
        # Moderate smoke (0.5): 1.5x slower
        # Heavy smoke (0.7): 2.0x slower
        # Complete obscuration (1.0): 3.0x slower
        base_penalty = 1.0 + (self.smoke_density * 2.0)
        return base_penalty * self.severity
    
    def get_movement_speed_multiplier(self) -> float:
        """
        Get movement speed multiplier for responders.
        
        Smoke, debris, water, etc. slow down movement through building.
        
        Returns:
            Multiplier for movement speed (< 1.0 means slower)
            1.0 = normal speed
            0.5-0.9 = reduced speed
        """
        # Base speed reduction by emergency type
        speed_impacts = {
            EmergencyType.FIRE: 0.7,                   # Heat, smoke, avoiding flames
            EmergencyType.STRUCTURAL_COLLAPSE: 0.6,    # Debris, unstable structure
            EmergencyType.FLOOD: 0.5,                  # Water resistance
            EmergencyType.SMOKE_NO_FIRE: 0.8,          # Smoke without heat
            EmergencyType.GAS_LEAK: 0.9,               # Cautious movement, breathing gear
            EmergencyType.CO_LEAK: 0.95,               # Nearly normal, but cautious
            EmergencyType.CHEMICAL_LEAK: 0.85,         # Protective gear, caution
            EmergencyType.EVACUATION_DRILL: 1.0,       # Normal speed
        }
        
        base_speed = speed_impacts.get(self.emergency_type, 0.9)
        
        # Additional penalty for smoke density
        if self.has_smoke:
            smoke_penalty = 1.0 - (self.smoke_density * 0.3)  # Up to 30% slower
            base_speed *= smoke_penalty
        
        # Severity can further reduce speed (severe = more obstacles/danger)
        if self.severity > 1.0:
            severity_penalty = 1.0 - ((self.severity - 1.0) * 0.15)  # Up to 15% slower per severity point
            base_speed *= severity_penalty
        
        return max(0.3, base_speed)  # Never slower than 30% of normal speed
    
    def get_sweep_difficulty_multiplier(self) -> float:
        """
        Get overall sweep difficulty multiplier.
        
        Combines all emergency-specific factors affecting sweep operations:
        - Environmental hazards
        - Required protective equipment
        - Need for thorough checks vs. quick evacuation
        
        Returns:
            Multiplier for base sweep time
            1.0 = normal difficulty
            1.2-2.0 = increased difficulty
        """
        difficulty_by_type = {
            EmergencyType.FIRE: 1.5,                   # Heat, smoke, evolving conditions
            EmergencyType.STRUCTURAL_COLLAPSE: 1.8,    # Dangerous, need to check debris
            EmergencyType.FLOOD: 1.4,                  # Water obstacles
            EmergencyType.SMOKE_NO_FIRE: 1.3,          # Visibility issues
            EmergencyType.GAS_LEAK: 1.6,               # Need detection equipment, thorough check
            EmergencyType.CO_LEAK: 1.7,                # Invisible threat, need CO detector, check unconscious victims
            EmergencyType.CHEMICAL_LEAK: 1.8,          # Protective gear, decontamination concerns
            EmergencyType.EVACUATION_DRILL: 0.9,       # Easier, no real danger
        }
        
        base_difficulty = difficulty_by_type.get(self.emergency_type, 1.2)
        
        # Severity increases difficulty
        return base_difficulty * self.severity
    
    def requires_detection_equipment(self) -> bool:
        """Check if emergency requires special detection equipment (gas detector, thermal camera, etc.)."""
        return self.emergency_type in [
            EmergencyType.GAS_LEAK,
            EmergencyType.CO_LEAK,
            EmergencyType.CHEMICAL_LEAK,
        ]
    
    def affects_occupant_consciousness(self) -> bool:
        """Check if emergency can render occupants unconscious or impaired."""
        return self.emergency_type in [
            EmergencyType.CO_LEAK,
            EmergencyType.CHEMICAL_LEAK,
        ]
    
    def get_priority_bonus(self) -> float:
        """
        Get priority bonus for PRIORITY_BASED sweep strategy.
        
        More dangerous emergencies get higher priority multipliers.
        
        Returns:
            Priority bonus (added to room priority scores)
        """
        priority_bonuses = {
            EmergencyType.FIRE: 200,                   # Immediate danger
            EmergencyType.STRUCTURAL_COLLAPSE: 250,    # Extreme danger
            EmergencyType.CO_LEAK: 180,                # Silent killer, high priority
            EmergencyType.GAS_LEAK: 170,               # Explosion risk
            EmergencyType.CHEMICAL_LEAK: 190,          # Health hazard
            EmergencyType.FLOOD: 150,                  # Significant danger
            EmergencyType.SMOKE_NO_FIRE: 140,          # Moderate danger
            EmergencyType.EVACUATION_DRILL: 50,        # Low priority
        }
        return priority_bonuses.get(self.emergency_type, 100) * self.severity
    
    def __repr__(self) -> str:
        """String representation of emergency context."""
        smoke_str = f", smoke={self.smoke_density:.1f}" if self.has_smoke else ""
        return (f"EmergencyContext({self.emergency_type.value}, "
                f"severity={self.severity:.1f}{smoke_str})")


# Preset emergency contexts for common scenarios
PRESET_EMERGENCIES = {
    "minor_fire": EmergencyContext(EmergencyType.FIRE, severity=0.8, smoke_density=0.4),
    "major_fire": EmergencyContext(EmergencyType.FIRE, severity=2.0, smoke_density=0.9),
    "gas_leak": EmergencyContext(EmergencyType.GAS_LEAK, severity=1.5),
    "co_leak": EmergencyContext(EmergencyType.CO_LEAK, severity=1.5),
    "smoke_only": EmergencyContext(EmergencyType.SMOKE_NO_FIRE, smoke_density=0.6),
    "drill": EmergencyContext(EmergencyType.EVACUATION_DRILL, severity=0.5),
    "structural_damage": EmergencyContext(EmergencyType.STRUCTURAL_COLLAPSE, severity=1.8),
    "chemical_spill": EmergencyContext(EmergencyType.CHEMICAL_LEAK, severity=1.7),
}


def get_preset_emergency(preset_name: str) -> Optional[EmergencyContext]:
    """
    Get a preset emergency context by name.
    
    Args:
        preset_name: Name of preset (e.g., "major_fire", "co_leak")
        
    Returns:
        EmergencyContext or None if preset not found
    """
    return PRESET_EMERGENCIES.get(preset_name)
