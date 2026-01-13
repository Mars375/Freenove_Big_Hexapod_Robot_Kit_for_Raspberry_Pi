"""Camera control abstraction"""
import sys
from pathlib import Path
import structlog

legacy_path = Path(__file__).parent.parent.parent / "legacy" / "Code" / "Server"
sys.path.insert(0, str(legacy_path))

from core.exceptions import HardwareNotAvailableError, CommandExecutionError

logger = structlog.get_logger()


class CameraController:
    """Abstraction for camera servo control"""
    
    def __init__(self):
        self._servo = None
        self._initialize_hardware()
    
    def _initialize_hardware(self):
        """Initialize legacy servo module"""
        try:
            from servo import Servo
            self._servo = Servo()
            logger.info("camera_controller.initialized")
        except Exception as e:
            logger.error("camera_controller.init_failed", error=str(e))
            self._servo = None
    
    @property
    def is_available(self) -> bool:
        return self._servo is not None
    
    async def rotate(self, horizontal: int, vertical: int) -> bool:
        """Rotate camera servos"""
        if not self.is_available:
            raise HardwareNotAvailableError("Camera controller not initialized")
        
        try:
            # Servo 0 = horizontal (pan), Servo 1 = vertical (tilt)
            self._servo.set_servo_pwm('0', horizontal)
            self._servo.set_servo_pwm('1', vertical)
            logger.info("camera_controller.rotated", h=horizontal, v=vertical)
            return True
        except Exception as e:
            logger.error("camera_controller.rotate_failed", error=str(e))
            raise CommandExecutionError(f"Camera rotation failed: {e}")
