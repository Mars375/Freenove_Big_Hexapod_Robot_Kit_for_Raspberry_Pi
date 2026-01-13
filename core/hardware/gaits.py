"""Hexapod gait patterns - tripod, wave, ripple"""
import math
from typing import List, Tuple
import structlog

logger = structlog.get_logger()


class GaitController:
    """Coordinate leg movements for various gait patterns"""
    
    # Leg groupings for tripod gait
    TRIPOD_GROUP_A = [0, 2, 4]  # Right-front, right-rear, left-middle
    TRIPOD_GROUP_B = [1, 3, 5]  # Right-middle, left-rear, left-front
    
    def __init__(self, step_height: float = 20.0, stride_length: float = 30.0):
        """
        Initialize gait controller
        
        Args:
            step_height: How high to lift legs during swing phase (mm)
            stride_length: Distance to move forward per step (mm)
        """
        self.step_height = step_height
        self.stride_length = stride_length
        self.phase = 0.0  # Current gait phase [0, 1]
    
    def calculate_foot_trajectory(
        self, 
        leg_id: int, 
        phase: float, 
        gait_type: str,
        direction: Tuple[float, float] = (1.0, 0.0)
    ) -> Tuple[float, float, float]:
        """
        Calculate target foot position for a leg at given gait phase
        
        Args:
            leg_id: Leg index (0-5)
            phase: Current gait phase [0, 1]
            gait_type: "tripod", "wave", or "ripple"
            direction: Movement direction as (x, y) unit vector
            
        Returns:
            Target (x, y, z) offset from neutral position
        """
        if gait_type == "tripod":
            return self._tripod_trajectory(leg_id, phase, direction)
        elif gait_type == "wave":
            return self._wave_trajectory(leg_id, phase, direction)
        elif gait_type == "ripple":
            return self._ripple_trajectory(leg_id, phase, direction)
        else:
            logger.warning("gait.unknown_type", type=gait_type)
            return (0.0, 0.0, 0.0)
    
    def _tripod_trajectory(
        self, 
        leg_id: int, 
        phase: float, 
        direction: Tuple[float, float]
    ) -> Tuple[float, float, float]:
        """
        Tripod gait: 2 groups of 3 legs alternate
        Group A lifts while Group B pushes, then switch
        """
        # Determine which group this leg belongs to
        if leg_id in self.TRIPOD_GROUP_A:
            leg_phase = phase
        else:
            leg_phase = (phase + 0.5) % 1.0
        
        # Swing phase (leg in air): 0.0 - 0.5
        # Stance phase (leg on ground): 0.5 - 1.0
        
        dx, dy = direction
        
        if leg_phase < 0.5:
            # Swing phase: lift leg and move forward
            swing_progress = leg_phase * 2.0  # [0, 1]
            
            # Arc trajectory (elliptical)
            x_offset = -self.stride_length/2 + self.stride_length * swing_progress
            y_offset = 0.0
            z_offset = self.step_height * math.sin(math.pi * swing_progress)
            
        else:
            # Stance phase: leg on ground, body moves over it
            stance_progress = (leg_phase - 0.5) * 2.0  # [0, 1]
            
            x_offset = self.stride_length/2 - self.stride_length * stance_progress
            y_offset = 0.0
            z_offset = 0.0
        
        # Apply direction
        x = x_offset * dx - y_offset * dy
        y = x_offset * dy + y_offset * dx
        
        return (x, y, z_offset)
    
    def _wave_trajectory(
        self, 
        leg_id: int, 
        phase: float, 
        direction: Tuple[float, float]
    ) -> Tuple[float, float, float]:
        """
        Wave gait: legs move one at a time sequentially
        Most stable but slowest
        """
        # Each leg gets 1/6 of the cycle for swing
        leg_start_phase = leg_id / 6.0
        leg_phase = (phase - leg_start_phase) % 1.0
        
        dx, dy = direction
        
        if leg_phase < (1.0 / 6.0):
            # This leg is in swing phase
            swing_progress = leg_phase * 6.0
            
            x_offset = -self.stride_length/2 + self.stride_length * swing_progress
            y_offset = 0.0
            z_offset = self.step_height * math.sin(math.pi * swing_progress)
        else:
            # This leg is in stance phase
            stance_progress = (leg_phase - 1.0/6.0) * (6.0/5.0)
            
            x_offset = self.stride_length/2 - self.stride_length * stance_progress
            y_offset = 0.0
            z_offset = 0.0
        
        x = x_offset * dx - y_offset * dy
        y = x_offset * dy + y_offset * dx
        
        return (x, y, z_offset)
    
    def _ripple_trajectory(
        self, 
        leg_id: int, 
        phase: float, 
        direction: Tuple[float, float]
    ) -> Tuple[float, float, float]:
        """
        Ripple gait: 2 legs swing simultaneously with 180° offset
        Balance between speed and stability
        """
        # Pairs: (0,3), (1,4), (2,5)
        pair_id = leg_id % 3
        leg_start_phase = pair_id / 3.0
        leg_phase = (phase - leg_start_phase) % 1.0
        
        dx, dy = direction
        
        if leg_phase < (1.0 / 3.0):
            # Swing phase
            swing_progress = leg_phase * 3.0
            
            x_offset = -self.stride_length/2 + self.stride_length * swing_progress
            y_offset = 0.0
            z_offset = self.step_height * math.sin(math.pi * swing_progress)
        else:
            # Stance phase
            stance_progress = (leg_phase - 1.0/3.0) * (3.0/2.0)
            
            x_offset = self.stride_length/2 - self.stride_length * stance_progress
            y_offset = 0.0
            z_offset = 0.0
        
        x = x_offset * dx - y_offset * dy
        y = x_offset * dy + y_offset * dx
        
        return (x, y, z_offset)
    
    def advance_phase(self, delta: float):
        """Advance gait phase by delta"""
        self.phase = (self.phase + delta) % 1.0
    
    def reset_phase(self):
        """Reset gait phase to start"""
        self.phase = 0.0
