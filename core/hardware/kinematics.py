"""Hexapod kinematics - inverse and forward calculations"""
import math
from typing import Tuple, Optional
import structlog

logger = structlog.get_logger()


class LegKinematics:
    """3-DOF leg kinematics (coxa, femur, tibia)"""
    
    def __init__(self, coxa_length: float = 33.0, femur_length: float = 90.0, tibia_length: float = 110.0):
        """
        Initialize leg kinematics
        
        Args:
            coxa_length: Length of coxa (hip) segment in mm
            femur_length: Length of femur segment in mm  
            tibia_length: Length of tibia segment in mm
        """
        self.L1 = coxa_length
        self.L2 = femur_length
        self.L3 = tibia_length
        
        # Workspace limits
        self.max_reach = self.L1 + self.L2 + self.L3
        self.min_reach = abs(self.L2 - self.L3)
    
    def inverse(self, x: float, y: float, z: float) -> Optional[Tuple[float, float, float]]:
        """
        Calculate joint angles from foot position (inverse kinematics)
        
        Args:
            x, y, z: Target foot position in leg coordinate frame (mm)
            
        Returns:
            Tuple of (coxa_angle, femur_angle, tibia_angle) in degrees, or None if unreachable
        """
        try:
            # Distance from origin to foot in XY plane
            l_xy = math.sqrt(x**2 + y**2)
            
            # Coxa angle (rotation around vertical axis)
            if l_xy < 0.001:  # Avoid division by zero
                coxa = 0.0
            else:
                coxa = math.degrees(math.atan2(y, x))
            
            # Distance from coxa joint to foot in XY plane
            l_xz = l_xy - self.L1
            
            # Total distance from femur joint to foot
            l_total = math.sqrt(l_xz**2 + z**2)
            
            # Check if position is reachable
            if l_total > (self.L2 + self.L3) or l_total < abs(self.L2 - self.L3):
                logger.warning("kinematics.unreachable", x=x, y=y, z=z, distance=l_total)
                return None
            
            # Law of cosines for tibia angle
            cos_tibia = (self.L2**2 + self.L3**2 - l_total**2) / (2 * self.L2 * self.L3)
            cos_tibia = max(-1.0, min(1.0, cos_tibia))  # Clamp to valid range
            tibia = math.degrees(math.acos(cos_tibia))
            
            # Angles for femur calculation
            alpha = math.atan2(z, l_xz)
            cos_beta = (self.L2**2 + l_total**2 - self.L3**2) / (2 * self.L2 * l_total)
            cos_beta = max(-1.0, min(1.0, cos_beta))
            beta = math.acos(cos_beta)
            
            # Femur angle
            femur = math.degrees(alpha + beta)
            
            return (coxa, femur, tibia)
            
        except Exception as e:
            logger.error("kinematics.inverse_failed", x=x, y=y, z=z, error=str(e))
            return None
    
    def forward(self, coxa: float, femur: float, tibia: float) -> Tuple[float, float, float]:
        """
        Calculate foot position from joint angles (forward kinematics)
        
        Args:
            coxa, femur, tibia: Joint angles in degrees
            
        Returns:
            Tuple of (x, y, z) position in mm
        """
        # Convert to radians
        c = math.radians(coxa)
        f = math.radians(femur)
        t = math.radians(tibia)
        
        # Calculate position
        x = (self.L1 + self.L2 * math.cos(f) + self.L3 * math.cos(f + t)) * math.cos(c)
        y = (self.L1 + self.L2 * math.cos(f) + self.L3 * math.cos(f + t)) * math.sin(c)
        z = self.L2 * math.sin(f) + self.L3 * math.sin(f + t)
        
        return (x, y, z)
