"""Unified robot controller (Singleton)"""

import structlog
from typing import Optional

from tachikoma.core.hardware import (
    MovementController,
    LEDController,
    SensorController,
    CameraController,
    BuzzerController
)
from tachikoma.core.hardware.factory import get_hardware_factory

logger = structlog.get_logger()


class RobotController:
    """Singleton unified robot controller"""

    _instance: Optional['RobotController'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if hasattr(self, '_init_done'):
            return

        logger.info("robot_controller.creating_controllers")

        # Create hardware controllers
        self.leds = LEDController()
        self.sensors = SensorController()
        self.camera = CameraController()
        self.buzzer = BuzzerController()

        # Movement needs async initialization
        self.movement = MovementController()

        self._initialized = False
        self._init_done = True

    async def initialize(self):
        """Initialize movement controller (async)"""
        if self._initialized:
            return

        try:
            logger.info("robot_controller.initializing")

            # Get hardware components from factory
            factory = get_hardware_factory()

            # Initialize servos and inject into movement
            servo = await factory.create_servo_controller()
            self.movement.set_servo_controller(servo)

            # Inject IMU if available for balancing
            imu = await factory.get_imu()
            self.movement._imu = imu

            # Final movement initialization
            await self.movement.initialize()

            self._initialized = True
            logger.info("robot_controller.ready")

        except Exception as e:
            logger.error("robot_controller.initialization_failed", error=str(e))
            raise

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


async def initialize_robot() -> RobotController:
    """Get and initialize robot controller"""
    robot = get_robot_controller()
    await robot.initialize()
    return robot
