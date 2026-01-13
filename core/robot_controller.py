"""Unified robot controller (Singleton)"""
import structlog
from typing import Optional

from core.hardware import (
    MovementController,
    LEDController,
    SensorController,
    CameraController
)

logger = structlog.get_logger()


class RobotController:
    """Singleton unified robot controller"""
    
    _instance: Optional['RobotController'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        logger.info("robot_controller.initializing")
        
        # Initialize hardware controllers
        self.movement = MovementController()
        self.leds = LEDController()
        self.sensors = SensorController()
        self.camera = CameraController()
        
        RobotController._initialized = True
        logger.info("robot_controller.ready")
    
    @property
    def is_hardware_available(self) -> bool:
        """Check if any hardware is available"""
        return any([
            self.movement.is_available,
            self.leds.is_available,
            self.camera.is_available
        ])


# Global instance getter
_robot_instance: Optional[RobotController] = None


def get_robot_controller() -> RobotController:
    """Get singleton robot controller instance"""
    global _robot_instance
    if _robot_instance is None:
        _robot_instance = RobotController()
    return _robot_instance
