"""Modern hexapod movement controller with HAL"""
import asyncio
import math
from typing import Tuple, Dict, List, Optional
import structlog

from core.exceptions import HardwareNotAvailableError, CommandExecutionError
from core.hardware.interfaces import IServoController
from core.hardware.kinematics import LegKinematics
from core.hardware.gaits import GaitController

logger = structlog.get_logger()


class Leg:
    """Single leg with position, angles, and servo mappings"""
    
    def __init__(
        self, 
        leg_id: int, 
        servo_pins: List[int], 
        body_offset: Tuple[float, float],
        angle_offset: Tuple[float, float] = (0.0, 0.0),
        mirror: bool = False
    ):
        """
        Initialize leg
        
        Args:
            leg_id: Leg index (0-5)
            servo_pins: [coxa_pin, femur_pin, tibia_pin]
            body_offset: (x, y) position relative to body center in mm
            angle_offset: (horizontal, vertical) angle offsets in degrees
            mirror: True for left side legs (inverse femur/tibia mapping)
        """
        self.id = leg_id
        self.servo_pins = servo_pins
        self.body_offset = body_offset
        self.angle_offset = angle_offset
        self.mirror = mirror
        
        # Neutral standing position in leg frame
        self.neutral_x = 140.0  # mm
        self.neutral_y = 0.0
        self.neutral_z = 0.0
        
        # Current state
        self.position = [self.neutral_x, self.neutral_y, self.neutral_z]
        self.angles = [90.0, 90.0, 90.0]
        
        # Kinematics
        self.kinematics = LegKinematics()


class MovementController:
    """Modern hexapod movement controller with full gait support
    
    Uses dependency injection for servo controller, enabling:
    - Hardware abstraction
    - Easy testing with mocks
    - Multiple servo implementations
    - Clean separation of concerns
    """
    
    def __init__(self, servo_controller: Optional[IServoController] = None):
        """
        Initialize movement controller
        
        Args:
            servo_controller: Servo controller implementation (injected)
                            If None, will need to be set before use
        """
        self._servo = servo_controller
        self._initialized = False
        self._moving = False
        self._gait_task = None
        
        # Body parameters
        self.body_height = -25.0  # mm below neutral
        
        # Define all 6 legs with proper configuration
        # Leg layout (top view):
        #     0   5
        #   1   ○   4
        #     2   3
        
        self.legs = [
            # Right side (0, 1, 2)
            # Leg 0 (Right Front): Servos 15, 14, 13 (Board 1 @ 0x41)
            Leg(0, [15, 14, 13], (137.1, 189.4), (0, 0), False),
            
            # Leg 1 (Right Middle): Servos 12, 11, 10 (Board 1 @ 0x41)
            Leg(1, [12, 11, 10], (225.0, 0.0), (0, 0), False),
            
            # Leg 2 (Right Rear): Servos 9, 8, 31 (Mixed: 9,8 @ 0x41, 31 @ 0x40)
            # Board 1 channels 9,8. Board 0 channel 15 (mapped to 31 virtual)
            Leg(2, [9, 8, 31], (137.1, -189.4), (0, 0), False),
            
            # Left side (3, 4, 5)  
            # Leg 3 (Left Rear): Servos 22, 23, 27 (Board 0 @ 0x40)
            # Virtual IDs: 22 (=6+16), 23 (=7+16), 27 (=11+16)
            Leg(3, [22, 23, 27], (-137.1, -189.4), (0, 0), True),
            
            # Leg 4 (Left Middle): Servos 19, 20, 21 (Board 0 @ 0x40)
            # Virtual IDs: 19 (=3+16), 20 (=4+16), 21 (=5+16)
            Leg(4, [19, 20, 21], (-225.0, 0.0), (0, 0), True),
            
            # Leg 5 (Left Front): Servos 16, 17, 18 (Board 0 @ 0x40)
            # Virtual IDs: 16 (=0+16), 17 (=1+16), 18 (=2+16)
            Leg(5, [16, 17, 18], (-137.1, 189.4), (0, 0), True),
        ]
        
        # Gait controller
        self.gait = GaitController(step_height=20.0, stride_length=30.0)
        
        logger.info(
            "movement_controller.created",
            has_servo=servo_controller is not None
        )
    
    def set_servo_controller(self, servo_controller: IServoController):
        """Set servo controller after initialization (for lazy injection)"""
        self._servo = servo_controller
        logger.info("movement_controller.servo_set")
        
    async def initialize(self):
        """Initialize servo controller and stand up"""
        if not self._servo:
            raise HardwareNotAvailableError(
                "No servo controller set. Use set_servo_controller() first."
            )
        
        try:
            logger.info("movement_controller.initializing")
            
            # Initialize servo hardware
            await self._servo.initialize()
            
            # Stand in neutral position
            await self.stand()
            
            self._initialized = True
            logger.info("movement_controller.initialized")
            
        except Exception as e:
            logger.error("movement_controller.init_failed", error=str(e))
            raise
    
    @property
    def is_available(self) -> bool:
        """Check if controller is ready to use"""
        return (
            self._initialized and 
            self._servo is not None and 
            self._servo.is_available()
        )
    
    def _servo_angles_from_leg_angles(
        self, 
        leg: Leg, 
        coxa: float, 
        femur: float, 
        tibia: float
    ) -> Tuple[int, int, int]:
        """
        Convert leg angles to servo angles accounting for mounting orientation
        
        Args:
            leg: Leg object
            coxa, femur, tibia: Joint angles in degrees
            
        Returns:
            Tuple of servo angles (0-180)
        """
        if leg.mirror:  # Left side
            servo_coxa = int(max(0, min(180, 180 - coxa)))
            servo_femur = int(max(0, min(180, 90 + femur)))
            servo_tibia = int(max(0, min(180, 180 - tibia)))
        else:  # Right side
            servo_coxa = int(max(0, min(180, coxa)))
            servo_femur = int(max(0, min(180, 90 - femur)))
            servo_tibia = int(max(0, min(180, tibia)))
        
        return (servo_coxa, servo_femur, servo_tibia)
    
    async def _set_leg_position(self, leg: Leg, x: float, y: float, z: float):
        """
        Move leg to target position using inverse kinematics
        
        Args:
            leg: Leg to move
            x, y, z: Target position in leg coordinate frame (mm)
        """
        if not self._servo:
            return
        
        # Calculate joint angles
        angles = leg.kinematics.inverse(x, y, z)
        
        if angles is None:
            logger.warning("movement.unreachable_position", leg_id=leg.id, x=x, y=y, z=z)
            return
        
        coxa, femur, tibia = angles
        
        # Convert to servo angles
        servo_angles = self._servo_angles_from_leg_angles(leg, coxa, femur, tibia)
        
        # Send to servos using HAL
        try:

            await self._servo.set_angle_async(leg.servo_pins[0], servo_angles[0])
            await self._servo.set_angle_async(leg.servo_pins[1], servo_angles[1])
            await self._servo.set_angle_async(leg.servo_pins[2], servo_angles[2])
        except Exception as e:
            logger.error(
                "movement.servo_command_failed",
                leg_id=leg.id,
                error=str(e)
            )
            raise
        
        # Update state
        leg.position = [x, y, z]
        leg.angles = [coxa, femur, tibia]
    
    async def stand(self):
        """Stand in neutral position"""
        logger.info("movement.stand")
        
        for leg in self.legs:
        for leg in self.legs:
            await self._set_leg_position(
                leg,
                leg.neutral_x,
                leg.neutral_y,
                self.body_height
            )
        
        await asyncio.sleep(0.5)
    
    async def _execute_gait(
        self, 
        gait_type: str, 
        direction: Tuple[float, float], 
        speed: float,
        duration: float = 5.0
    ):
        """
        Execute continuous gait pattern
        
        Args:
            gait_type: "tripod", "wave", or "ripple"
            direction: (x, y) movement direction (unit vector)
            speed: Movement speed factor (0-10)
            duration: How long to walk (seconds)
        """
        logger.info("movement.execute_gait", type=gait_type, direction=direction, speed=speed)
        
        self._moving = True
        self.gait.reset_phase()
        
        # Speed to phase increment mapping
        phase_delta = 0.02 * (speed / 5.0)  # Adjust multiplier as needed
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            while self._moving and (asyncio.get_event_loop().time() - start_time) < duration:
                # Calculate target position for each leg
                for leg in self.legs:
                    # Get trajectory offset from gait
                    offset = self.gait.calculate_foot_trajectory(
                        leg.id,
                        self.gait.phase,
                        gait_type,
                        direction
                    )
                    
                    # Apply to neutral position
                    target_x = leg.neutral_x + offset[0]
                    target_y = leg.neutral_y + offset[1]
                    target_z = self.body_height + offset[2]
                    
                    # Move leg
                    await self._set_leg_position(leg, target_x, target_y, target_z)
                
                # Advance gait phase
                self.gait.advance_phase(phase_delta)
                
                # Control loop rate (50Hz)
                await asyncio.sleep(0.02)
                
        except Exception as e:
            logger.error("movement.gait_execution_failed", error=str(e))
            self._moving = False
            raise
        
        self._moving = False
        logger.info("movement.gait_completed")
    
    async def move(self, mode: str, x: int, y: int, speed: int, angle: int) -> bool:
        """
        Execute movement command
        
        Args:
            mode: "forward", "backward", "left", "right", "turn_left", "turn_right"
            x, y: Reserved for future use (joystick input)
            speed: Speed factor (1-10)
            angle: Turn angle (degrees) - reserved
        """
        if not self.is_available:
            raise HardwareNotAvailableError("Movement controller not initialized")
        
        try:
            logger.info("movement.move", mode=mode, speed=speed)
            
            # Stop any ongoing movement
            if self._gait_task and not self._gait_task.done():
                self._moving = False
                await self._gait_task
            
            # Map mode to direction vector
            direction_map = {
                "forward": (1.0, 0.0),
                "backward": (-1.0, 0.0),
                "left": (0.0, 1.0),
                "right": (0.0, -1.0),
                "turn_left": (0.5, 0.5),  # Differential turning
                "turn_right": (0.5, -0.5),
            }
            
            direction = direction_map.get(mode, (1.0, 0.0))
            
            # Use tripod gait (fastest and most stable for forward motion)
            # Could be configurable based on terrain/requirements
            self._gait_task = asyncio.create_task(
                self._execute_gait("tripod", direction, speed, duration=2.0)
            )
            
            return True
            
        except Exception as e:
            logger.error("movement.move_failed", error=str(e))
            raise CommandExecutionError(f"Move failed: {e}")
    
    async def stop(self) -> bool:
        """Emergency stop"""
        if not self.is_available:
            raise HardwareNotAvailableError("Movement controller not initialized")
        
        try:
            logger.info("movement.stop")
            
            # Signal stop
            self._moving = False
            
            # Wait for gait task to finish
            if self._gait_task and not self._gait_task.done():
                await self._gait_task
            
            # Return to standing position
            await self.stand()
            
            return True
            
        except Exception as e:
            logger.error("movement.stop_failed", error=str(e))
            raise CommandExecutionError(f"Stop failed: {e}")
    
    async def set_attitude(self, roll: float, pitch: float, yaw: float) -> bool:
        """
        Set robot body attitude
        
        Args:
            roll: Roll angle in degrees (-15 to +15)
            pitch: Pitch angle in degrees (-15 to +15)  
            yaw: Yaw angle in degrees (-15 to +15)
        """
        if not self.is_available:
            raise HardwareNotAvailableError("Movement controller not initialized")
        
        try:
            logger.info("movement.set_attitude", roll=roll, pitch=pitch, yaw=yaw)
            
            # Convert to radians
            roll_rad = math.radians(roll)
            pitch_rad = math.radians(pitch)
            yaw_rad = math.radians(yaw)
            
            # Apply rotation matrix to each leg's body offset
            for leg in self.legs:
                bx, by = leg.body_offset
                
                # Rotate body offset by yaw
                x_rot = bx * math.cos(yaw_rad) - by * math.sin(yaw_rad)
                y_rot = bx * math.sin(yaw_rad) + by * math.cos(yaw_rad)
                
                # Calculate z offset from roll and pitch
                z_offset = (
                    x_rot * math.sin(pitch_rad) +
                    y_rot * math.sin(roll_rad)
                )
                
                # Apply to leg
                new_z = self.body_height + z_offset
                await self._set_leg_position(leg, leg.neutral_x, leg.neutral_y, new_z)
            
            await asyncio.sleep(0.3)
            return True
            
        except Exception as e:
            logger.error("movement.set_attitude_failed", error=str(e))
            raise CommandExecutionError(f"Attitude set failed: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("movement_controller.cleanup")
        
        if self._moving:
            await self.stop()
        
        if self._servo:
            try:
                # Return to standing position
                await self.stand()
                # Cleanup servo hardware
                await self._servo.cleanup()
            except Exception as e:
                logger.error("movement_controller.cleanup_failed", error=str(e))
