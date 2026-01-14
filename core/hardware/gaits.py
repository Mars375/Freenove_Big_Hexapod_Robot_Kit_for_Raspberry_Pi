"""Hexapod gait patterns - tripod and wave gaits.

This module implements the proven gait algorithms from the original
Freenove hexapod, modernized with clean async code.
"""
import asyncio
import math
import copy
from typing import List, Tuple, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger()


class GaitType(Enum):
    """Available gait patterns."""
    TRIPOD = "1"  # Fast, 2 groups of 3 legs alternate
    WAVE = "2"    # Slow, legs move one at a time


@dataclass
class GaitConfig:
    """Gait configuration parameters."""
    step_height: float = 40.0     # Height to lift legs (mm)
    frame_count: int = 64         # Steps per gait cycle (smoothness)
    delay: float = 0.01           # Delay between frames (seconds)
    
    
class GaitExecutor:
    """Execute hexapod gait patterns.
    
    This implements the proven algorithm from the original Freenove code,
    using discrete frame stepping with proper timing.
    
    The gait works by:
    1. Calculating per-leg XY movement offsets based on direction + rotation
    2. Dividing the gait cycle into 8 phases (for tripod) or 6 phases (for wave)
    3. Each phase lifts/moves/lowers specific legs
    4. Calling the provided callback to update servo positions
    """
    
    def __init__(
        self,
        body_points: List[List[float]],
        update_callback: Callable[[List[List[float]]], Awaitable[None]],
        config: GaitConfig = None
    ):
        """Initialize gait executor.
        
        Args:
            body_points: Initial body-frame foot positions for each leg
                        [[x, y, z], ...] for legs 0-5
            update_callback: Async function to call with new positions
            config: Gait configuration
        """
        self.body_points = copy.deepcopy(body_points)
        self.update_callback = update_callback
        self.config = config or GaitConfig()
        self._running = False
    
    @staticmethod
    def _map_speed_to_frames(speed: int, gait_type: GaitType) -> int:
        """Map speed (2-10) to frame count for smooth movement.
        
        Higher speed = fewer frames = faster movement.
        
        Args:
            speed: Speed value 2-10
            gait_type: Gait type affects frame count range
            
        Returns:
            Frame count for gait cycle
        """
        if gait_type == GaitType.TRIPOD:
            # Tripod: 126 frames at speed 2, 22 frames at speed 10
            return round((126 - 22) * (10 - speed) / 8 + 22)
        else:
            # Wave: 171 frames at speed 2, 45 frames at speed 10
            return round((171 - 45) * (10 - speed) / 8 + 45)
    
    def _calculate_leg_offsets(
        self,
        x: float,
        y: float,
        angle: float,
        frame_count: int
    ) -> List[List[float]]:
        """Calculate per-leg XY offsets for one frame.
        
        Combines translational (x, y) and rotational (angle) movement.
        
        Args:
            x: Forward movement amount (-35 to 35)
            y: Lateral movement amount (-35 to 35)
            angle: Rotation angle (degrees)
            frame_count: Total frames in gait cycle
            
        Returns:
            List of [dx, dy] offsets for each leg per frame
        """
        offsets = []
        angle_rad = math.radians(angle)
        
        for i in range(6):
            bp = self.body_points[i]
            
            # Rotation component
            rot_x = (
                bp[0] * math.cos(angle_rad) + 
                bp[1] * math.sin(angle_rad) - 
                bp[0]
            )
            rot_y = (
                -bp[0] * math.sin(angle_rad) + 
                bp[1] * math.cos(angle_rad) - 
                bp[1]
            )
            
            # Combined translation + rotation, divided by frame count
            dx = (rot_x + x) / frame_count
            dy = (rot_y + y) / frame_count
            
            offsets.append([dx, dy])
        
        return offsets
    
    async def execute_tripod(
        self,
        x: float,
        y: float,
        speed: int,
        angle: float,
        duration: float = None
    ) -> None:
        """Execute tripod gait pattern.
        
        Tripod gait alternates between two groups of 3 legs:
        - Group A (even legs: 0, 2, 4): Move together
        - Group B (odd legs: 1, 3, 5): Move together
        
        The gait cycle has 8 phases:
        1. Group B lifts, Group A pushes back
        2. Group B moves forward in air, Group A continues pushing
        3. Group B lowers, Group A starts lifting
        4. Group A lifts, Group B pushes back
        5-8. Mirror of 1-4
        
        Args:
            x: Forward movement (-35 to 35)
            y: Lateral movement (-35 to 35)
            speed: Speed 2-10
            angle: Rotation angle (degrees)
            duration: Optional duration limit (seconds)
        """
        logger.info(
            "gait.tripod.start",
            x=x, y=y, speed=speed, angle=angle
        )
        
        self._running = True
        F = self._map_speed_to_frames(speed, GaitType.TRIPOD)
        Z = self.config.step_height
        z = Z / F  # Height increment per frame
        delay = self.config.delay
        
        # Calculate per-leg offsets
        offsets = self._calculate_leg_offsets(x, y, angle, F)
        
        # Working copy of positions
        points = copy.deepcopy(self.body_points)
        
        # If no movement, just stand
        if x == 0 and y == 0 and angle == 0:
            await self.update_callback(points)
            return
        
        start_time = asyncio.get_event_loop().time()
        
        while self._running:
            # One complete gait cycle
            for j in range(F):
                if not self._running:
                    break
                    
                # Check duration limit
                if duration and (asyncio.get_event_loop().time() - start_time) >= duration:
                    self._running = False
                    break
                
                # Update each leg pair
                for i in range(3):
                    even = 2 * i      # Legs 0, 2, 4
                    odd = 2 * i + 1   # Legs 1, 3, 5
                    
                    if j < (F / 8):
                        # Phase 1: Odd legs lift, even legs push back
                        points[even][0] -= 4 * offsets[even][0]
                        points[even][1] -= 4 * offsets[even][1]
                        points[odd][0] += 8 * offsets[odd][0]
                        points[odd][1] += 8 * offsets[odd][1]
                        points[odd][2] = Z + self.body_points[odd][2]
                        
                    elif j < (F / 4):
                        # Phase 2: Odd legs lower, even legs continue
                        points[even][0] -= 4 * offsets[even][0]
                        points[even][1] -= 4 * offsets[even][1]
                        points[odd][2] -= z * 8
                        
                    elif j < (3 * F / 8):
                        # Phase 3: Even legs lift, odd legs push
                        points[even][2] += z * 8
                        points[odd][0] -= 4 * offsets[odd][0]
                        points[odd][1] -= 4 * offsets[odd][1]
                        
                    elif j < (5 * F / 8):
                        # Phase 4: Even legs move forward, odd legs push
                        points[even][0] += 8 * offsets[even][0]
                        points[even][1] += 8 * offsets[even][1]
                        points[odd][0] -= 4 * offsets[odd][0]
                        points[odd][1] -= 4 * offsets[odd][1]
                        
                    elif j < (3 * F / 4):
                        # Phase 5: Even legs lower, odd legs continue
                        points[even][2] -= z * 8
                        points[odd][0] -= 4 * offsets[odd][0]
                        points[odd][1] -= 4 * offsets[odd][1]
                        
                    elif j < (7 * F / 8):
                        # Phase 6: Odd legs lift, even legs push
                        points[even][0] -= 4 * offsets[even][0]
                        points[even][1] -= 4 * offsets[even][1]
                        points[odd][2] += z * 8
                        
                    else:
                        # Phase 7-8: Complete the cycle
                        points[even][0] -= 4 * offsets[even][0]
                        points[even][1] -= 4 * offsets[even][1]
                        points[odd][0] += 8 * offsets[odd][0]
                        points[odd][1] += 8 * offsets[odd][1]
                
                # Update servos
                await self.update_callback(points)
                await asyncio.sleep(delay)
        
        logger.info("gait.tripod.complete")
    
    async def execute_wave(
        self,
        x: float,
        y: float,
        speed: int,
        angle: float,
        duration: float = None
    ) -> None:
        """Execute wave gait pattern.
        
        Wave gait moves one leg at a time in sequence:
        Leg 5 -> 2 -> 1 -> 0 -> 3 -> 4
        
        Most stable but slowest gait.
        
        Args:
            x: Forward movement (-35 to 35)
            y: Lateral movement (-35 to 35)
            speed: Speed 2-10
            angle: Rotation angle (degrees)
            duration: Optional duration limit (seconds)
        """
        logger.info(
            "gait.wave.start",
            x=x, y=y, speed=speed, angle=angle
        )
        
        self._running = True
        F = self._map_speed_to_frames(speed, GaitType.WAVE)
        Z = self.config.step_height
        z = Z / F
        delay = self.config.delay
        
        offsets = self._calculate_leg_offsets(x, y, angle, F)
        points = copy.deepcopy(self.body_points)
        
        if x == 0 and y == 0 and angle == 0:
            await self.update_callback(points)
            return
        
        # Wave sequence order
        leg_order = [5, 2, 1, 0, 3, 4]
        
        start_time = asyncio.get_event_loop().time()
        
        while self._running:
            # Process each leg in sequence
            for leg_idx, current_leg in enumerate(leg_order):
                frames_per_leg = int(F / 6)
                
                for j in range(frames_per_leg):
                    if not self._running:
                        break
                        
                    if duration and (asyncio.get_event_loop().time() - start_time) >= duration:
                        self._running = False
                        break
                    
                    # Update all legs
                    for k in range(6):
                        if k == current_leg:
                            # This leg is moving
                            if j < int(frames_per_leg / 3):
                                # Lift phase
                                points[k][2] += 18 * z
                            elif j < int(2 * frames_per_leg / 3):
                                # Forward phase
                                points[k][0] += 30 * offsets[k][0]
                                points[k][1] += 30 * offsets[k][1]
                            else:
                                # Lower phase
                                points[k][2] -= 18 * z
                        else:
                            # Other legs push back slowly
                            points[k][0] -= 2 * offsets[k][0]
                            points[k][1] -= 2 * offsets[k][1]
                    
                    await self.update_callback(points)
                    await asyncio.sleep(delay)
        
        logger.info("gait.wave.complete")
    
    async def execute(
        self,
        gait_type: GaitType,
        x: float,
        y: float,
        speed: int,
        angle: float = 0,
        duration: float = None
    ) -> None:
        """Execute specified gait pattern.
        
        Args:
            gait_type: TRIPOD or WAVE
            x: Forward movement (-35 to 35)
            y: Lateral movement (-35 to 35)
            speed: Speed 2-10
            angle: Rotation angle (degrees)
            duration: Optional duration limit (seconds)
        """
        # Clamp inputs to valid ranges
        x = max(-35, min(35, x))
        y = max(-35, min(35, y))
        speed = max(2, min(10, speed))
        
        if gait_type == GaitType.TRIPOD:
            await self.execute_tripod(x, y, speed, angle, duration)
        else:
            await self.execute_wave(x, y, speed, angle, duration)
    
    def stop(self) -> None:
        """Stop gait execution."""
        self._running = False
        logger.info("gait.stopped")
