"""Hexapod kinematics - inverse and forward calculations.

This module provides the mathematical foundation for converting between
Cartesian foot positions and servo joint angles.
"""
import math
from typing import Tuple, Optional, List
import structlog

logger = structlog.get_logger()


class HexapodKinematics:
    """3-DOF leg kinematics for hexapod robot.
    
    Implements inverse kinematics to convert foot positions to joint angles.
    Uses the same proven algorithm as the original Freenove implementation.
    
    Coordinate system (leg-local):
        - X: Forward from coxa joint (horizontal, in leg direction)
        - Y: Lateral from coxa joint  
        - Z: Vertical (positive = down from coxa)
    
    Joint angles:
        - Coxa (α): Rotation around vertical axis at hip
        - Femur (β): Rotation of thigh segment
        - Tibia (γ): Rotation of shin segment
    
    Segment lengths (default, mm):
        - L1 (coxa): 33mm
        - L2 (femur): 90mm
        - L3 (tibia): 110mm
    """
    
    def __init__(
        self, 
        coxa_length: float = 33.0, 
        femur_length: float = 90.0, 
        tibia_length: float = 110.0
    ):
        """Initialize kinematics with segment lengths.
        
        Args:
            coxa_length: Length of coxa (hip) segment in mm
            femur_length: Length of femur (thigh) segment in mm
            tibia_length: Length of tibia (shin) segment in mm
        """
        self.L1 = coxa_length
        self.L2 = femur_length
        self.L3 = tibia_length
        
        # Workspace limits
        self.max_reach = self.L1 + self.L2 + self.L3
        self.min_reach = max(0, abs(self.L2 - self.L3) - self.L1)
    
    @staticmethod
    def _clamp(value: float, min_val: float, max_val: float) -> float:
        """Clamp value to range [min_val, max_val]."""
        return max(min_val, min(max_val, value))
    
    def inverse(self, x: float, y: float, z: float) -> Optional[Tuple[int, int, int]]:
        """Calculate joint angles from foot position (inverse kinematics).
        
        This is the proven algorithm from the original Freenove implementation.
        
        Args:
            x: Forward distance from coxa joint (mm)
            y: Lateral distance from coxa joint (mm)
            z: Vertical distance from coxa joint (mm, positive = down)
            
        Returns:
            Tuple of (coxa_deg, femur_deg, tibia_deg) as integers,
            or None if position is unreachable.
        """
        try:
            # Coxa angle: rotation in the horizontal plane
            # α = π/2 - atan2(z, y)
            alpha = math.pi / 2 - math.atan2(z, y)
            
            # Position of coxa joint endpoint
            x_3 = 0
            x_4 = self.L1 * math.sin(alpha)
            x_5 = self.L1 * math.cos(alpha)
            
            # Distance from coxa endpoint to foot
            l23 = math.sqrt(
                (z - x_5) ** 2 + 
                (y - x_4) ** 2 + 
                (x - x_3) ** 2
            )
            
            # Check reachability
            if l23 > (self.L2 + self.L3) or l23 < abs(self.L2 - self.L3):
                logger.warning(
                    "kinematics.unreachable",
                    x=x, y=y, z=z,
                    distance=l23,
                    max_reach=self.L2 + self.L3
                )
                return None
            
            # Intermediate calculations with clamping for numerical stability
            w = self._clamp((x - x_3) / l23, -1.0, 1.0)
            v = self._clamp(
                (self.L2**2 + l23**2 - self.L3**2) / (2 * self.L2 * l23),
                -1.0, 1.0
            )
            u = self._clamp(
                (self.L2**2 + self.L3**2 - l23**2) / (2 * self.L3 * self.L2),
                -1.0, 1.0
            )
            
            # Femur angle: β = asin(w) - acos(v)
            beta = math.asin(round(w, 2)) - math.acos(round(v, 2))
            
            # Tibia angle: γ = π - acos(u)
            gamma = math.pi - math.acos(round(u, 2))
            
            # Convert to degrees and return as integers
            return (
                round(math.degrees(alpha)),
                round(math.degrees(beta)),
                round(math.degrees(gamma))
            )
            
        except (ValueError, ZeroDivisionError) as e:
            logger.error("kinematics.inverse_failed", x=x, y=y, z=z, error=str(e))
            return None
    
    def forward(self, alpha: float, beta: float, gamma: float) -> Tuple[float, float, float]:
        """Calculate foot position from joint angles (forward kinematics).
        
        Args:
            alpha: Coxa angle in degrees
            beta: Femur angle in degrees
            gamma: Tibia angle in degrees
            
        Returns:
            Tuple of (x, y, z) position in mm
        """
        # Convert to radians
        a = math.radians(alpha)
        b = math.radians(beta)
        g = math.radians(gamma)
        
        # Calculate position
        x = self.L3 * math.sin(b + g) + self.L2 * math.sin(b)
        y = (
            self.L3 * math.sin(a) * math.cos(b + g) + 
            self.L2 * math.sin(a) * math.cos(b) + 
            self.L1 * math.sin(a)
        )
        z = (
            self.L3 * math.cos(a) * math.cos(b + g) + 
            self.L2 * math.cos(a) * math.cos(b) + 
            self.L1 * math.cos(a)
        )
        
        return (round(x, 2), round(y, 2), round(z, 2))
    
    def check_validity(self, positions: List[List[float]]) -> bool:
        """Check if all leg positions are within valid range.
        
        Args:
            positions: List of 6 leg positions [[x, y, z], ...]
            
        Returns:
            True if all positions are valid, False otherwise
        """
        for pos in positions:
            length = math.sqrt(pos[0]**2 + pos[1]**2 + pos[2]**2)
            if length > 248 or length < 90:
                return False
        return True


# Backward compatibility alias
LegKinematics = HexapodKinematics
