import logging
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from tachikoma.core.hardware.interfaces.base import IHardwareComponent, HardwareStatus
from tachikoma.core.hardware.devices.servo import ServoController


class HexapodController(IHardwareComponent):
    """Contrôleur principal pour la locomotion de l'hexapode"""
    
    # Définition des pattes (servo IDs)
    LEGS = {
        "front_right": {"hip": 0, "knee": 1, "ankle": 2},
        "middle_right": {"hip": 3, "knee": 4, "ankle": 5},
        "rear_right": {"hip": 6, "knee": 7, "ankle": 8},
        "front_left": {"hip": 9, "knee": 10, "ankle": 11},
        "middle_left": {"hip": 12, "knee": 13, "ankle": 14},
        "rear_left": {"hip": 15, "knee": 16, "ankle": 17}
    }
    
    # Positions neutres (degrés)
    NEUTRAL_POSITIONS = {
        "hip": 90,
        "knee": 90,
        "ankle": 90
    }
    
    def __init__(self, servo_controller: Optional[ServoController] = None):
        self.servo = servo_controller
        self.logger = logging.getLogger(__name__)
        self._status = HardwareStatus.UNINITIALIZED
        self._current_gait = "tripod"
        self._speed = 5  # 1-10
    
    async def initialize(self) -> bool:
        try:
            self._status = HardwareStatus.INITIALIZING
            
            if not self.servo:
                self.servo = ServoController()
                await self.servo.initialize()
            
            if not self.servo.is_available():
                raise Exception("Servo controller not available")
            
            # Position neutre
            await self.reset_position()
            
            self._status = HardwareStatus.READY
            self.logger.info("Hexapod controller initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize hexapod controller: {e}")
            self._status = HardwareStatus.ERROR
            return False
    
    async def cleanup(self) -> None:
        try:
            await self.reset_position()
            if self.servo:
                await self.servo.cleanup()
            self._status = HardwareStatus.DISCONNECTED
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    async def reset_position(self) -> bool:
        if not self.is_available():
            return False
        
        try:
            for leg_name, joints in self.LEGS.items():
                for joint_name, servo_id in joints.items():
                    angle = self.NEUTRAL_POSITIONS[joint_name]
                    self.servo.set_angle(servo_id, angle)
                    await asyncio.sleep(0.01)
            
            self.logger.info("Reset to neutral position")
            return True
        except Exception as e:
            self.logger.error(f"Failed to reset position: {e}")
            return False
    
    async def move_forward(self, steps: int = 1, speed: Optional[int] = None) -> bool:
        if not self.is_available():
            return False
        
        speed = speed or self._speed
        delay = (11 - speed) * 0.05
        
        try:
            for _ in range(steps):
                if self._current_gait == "tripod":
                    await self._tripod_gait_forward(delay)
                else:
                    await self._wave_gait_forward(delay)
            return True
        except Exception as e:
            self.logger.error(f"Failed to move forward: {e}")
            return False
    
    async def move_backward(self, steps: int = 1, speed: Optional[int] = None) -> bool:
        if not self.is_available():
            return False
        
        speed = speed or self._speed
        delay = (11 - speed) * 0.05
        
        try:
            for _ in range(steps):
                if self._current_gait == "tripod":
                    await self._tripod_gait_backward(delay)
                else:
                    await self._wave_gait_backward(delay)
            return True
        except Exception as e:
            self.logger.error(f"Failed to move backward: {e}")
            return False
    
    async def turn_left(self, angle: float = 30, speed: Optional[int] = None) -> bool:
        if not self.is_available():
            return False
        
        try:
            # Rotation sur place
            steps = int(angle / 15)
            for _ in range(steps):
                await self._rotate_left_step()
                await asyncio.sleep((11 - (speed or self._speed)) * 0.05)
            return True
        except Exception as e:
            self.logger.error(f"Failed to turn left: {e}")
            return False
    
    async def turn_right(self, angle: float = 30, speed: Optional[int] = None) -> bool:
        if not self.is_available():
            return False
        
        try:
            steps = int(angle / 15)
            for _ in range(steps):
                await self._rotate_right_step()
                await asyncio.sleep((11 - (speed or self._speed)) * 0.05)
            return True
        except Exception as e:
            self.logger.error(f"Failed to turn right: {e}")
            return False
    
    async def _tripod_gait_forward(self, delay: float) -> None:
        # Groupe 1: front_right, middle_left, rear_right
        # Groupe 2: front_left, middle_right, rear_left
        
        # Lever groupe 1
        for leg in ["front_right", "middle_left", "rear_right"]:
            self.servo.set_angle(self.LEGS[leg]["knee"], 60)
        await asyncio.sleep(delay)
        
        # Avancer groupe 1
        for leg in ["front_right", "middle_left", "rear_right"]:
            self.servo.set_angle(self.LEGS[leg]["hip"], 110)
        await asyncio.sleep(delay)
        
        # Poser groupe 1
        for leg in ["front_right", "middle_left", "rear_right"]:
            self.servo.set_angle(self.LEGS[leg]["knee"], 90)
        await asyncio.sleep(delay)
        
        # Lever groupe 2
        for leg in ["front_left", "middle_right", "rear_left"]:
            self.servo.set_angle(self.LEGS[leg]["knee"], 60)
        await asyncio.sleep(delay)
        
        # Avancer groupe 2 et reculer groupe 1
        for leg in ["front_left", "middle_right", "rear_left"]:
            self.servo.set_angle(self.LEGS[leg]["hip"], 70)
        for leg in ["front_right", "middle_left", "rear_right"]:
            self.servo.set_angle(self.LEGS[leg]["hip"], 90)
        await asyncio.sleep(delay)
        
        # Poser groupe 2
        for leg in ["front_left", "middle_right", "rear_left"]:
            self.servo.set_angle(self.LEGS[leg]["knee"], 90)
        await asyncio.sleep(delay)
    
    async def _tripod_gait_backward(self, delay: float) -> None:
        # Même logique mais angles inversés
        for leg in ["front_right", "middle_left", "rear_right"]:
            self.servo.set_angle(self.LEGS[leg]["knee"], 60)
        await asyncio.sleep(delay)
        
        for leg in ["front_right", "middle_left", "rear_right"]:
            self.servo.set_angle(self.LEGS[leg]["hip"], 70)
        await asyncio.sleep(delay)
        
        for leg in ["front_right", "middle_left", "rear_right"]:
            self.servo.set_angle(self.LEGS[leg]["knee"], 90)
        await asyncio.sleep(delay)
        
        for leg in ["front_left", "middle_right", "rear_left"]:
            self.servo.set_angle(self.LEGS[leg]["knee"], 60)
        await asyncio.sleep(delay)
        
        for leg in ["front_left", "middle_right", "rear_left"]:
            self.servo.set_angle(self.LEGS[leg]["hip"], 110)
        for leg in ["front_right", "middle_left", "rear_right"]:
            self.servo.set_angle(self.LEGS[leg]["hip"], 90)
        await asyncio.sleep(delay)
        
        for leg in ["front_left", "middle_right", "rear_left"]:
            self.servo.set_angle(self.LEGS[leg]["knee"], 90)
        await asyncio.sleep(delay)
    
    async def _wave_gait_forward(self, delay: float) -> None:
        # Vague : une patte à la fois
        leg_order = ["front_right", "middle_right", "rear_right", 
                     "rear_left", "middle_left", "front_left"]
        
        for leg in leg_order:
            self.servo.set_angle(self.LEGS[leg]["knee"], 60)
            await asyncio.sleep(delay)
            self.servo.set_angle(self.LEGS[leg]["hip"], 110)
            await asyncio.sleep(delay)
            self.servo.set_angle(self.LEGS[leg]["knee"], 90)
            await asyncio.sleep(delay)
    
    async def _wave_gait_backward(self, delay: float) -> None:
        leg_order = ["front_left", "middle_left", "rear_left",
                     "rear_right", "middle_right", "front_right"]
        
        for leg in leg_order:
            self.servo.set_angle(self.LEGS[leg]["knee"], 60)
            await asyncio.sleep(delay)
            self.servo.set_angle(self.LEGS[leg]["hip"], 70)
            await asyncio.sleep(delay)
            self.servo.set_angle(self.LEGS[leg]["knee"], 90)
            await asyncio.sleep(delay)
    
    async def _rotate_left_step(self) -> None:
        # Rotation sur place vers la gauche
        for leg in ["front_right", "middle_right", "rear_right"]:
            self.servo.set_angle(self.LEGS[leg]["hip"], 110)
        for leg in ["front_left", "middle_left", "rear_left"]:
            self.servo.set_angle(self.LEGS[leg]["hip"], 110)
    
    async def _rotate_right_step(self) -> None:
        for leg in ["front_right", "middle_right", "rear_right"]:
            self.servo.set_angle(self.LEGS[leg]["hip"], 70)
        for leg in ["front_left", "middle_left", "rear_left"]:
            self.servo.set_angle(self.LEGS[leg]["hip"], 70)
    
    def set_gait(self, gait: str) -> bool:
        if gait in ["tripod", "wave"]:
            self._current_gait = gait
            self.logger.info(f"Gait changed to {gait}")
            return True
        return False
    
    def set_speed(self, speed: int) -> bool:
        if 1 <= speed <= 10:
            self._speed = speed
            return True
        return False
    
    def is_available(self) -> bool:
        return self._status == HardwareStatus.READY and self.servo and self.servo.is_available()
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "type": "hexapod_controller",
            "status": self._status.value,
            "available": self.is_available(),
            "gait": self._current_gait,
            "speed": self._speed
        }
    
    def get_health(self) -> Dict[str, Any]:
        return {
            "healthy": self.is_available(),
            "servo_status": self.servo.get_status() if self.servo else None,
            "gait": self._current_gait
        }
