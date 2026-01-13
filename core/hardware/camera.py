"""Camera control abstraction"""
import sys
from pathlib import Path
import structlog

legacy_path = Path(__file__).parent.parent.parent / "legacy" / "Code" / "Server"
sys.path.insert(0, str(legacy_path))

from core.exceptions import HardwareNotAvailableError, CommandExecutionError

logger = structlog.get_logger()


class CameraController:
    """Abstraction for camera pan/tilt control"""
    
    def __init__(self):
        self._servo = None
        self._horizontal_channel = 0  # Pan servo channel
        self._vertical_channel = 1    # Tilt servo channel
        self._initialize_hardware()
    
    def _initialize_hardware(self):
        """Initialize servo controller for camera"""
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
        """Rotate camera servos
        
        Args:
            horizontal: Pan angle (-90 to 90, 0=center)
            vertical: Tilt angle (-45 to 45, 0=center)
        """
        if not self.is_available:
            raise HardwareNotAvailableError("Camera controller not initialized")
        
        try:
            # Convert angles to servo range (typically 0-180, with 90 as center)
            # Horizontal: -90 to 90 -> 0 to 180
            h_angle = 90 + horizontal
            # Vertical: -45 to 45 -> 45 to 135 (limited tilt range)
            v_angle = 90 + vertical
            
            # Clamp values
            h_angle = max(0, min(180, h_angle))
            v_angle = max(45, min(135, v_angle))
            
            # Set servo angles using the correct method
            self._servo.set_servo_angle(self._horizontal_channel, h_angle)
            self._servo.set_servo_angle(self._vertical_channel, v_angle)
            
            logger.info("camera_controller.rotated", horizontal=horizontal, vertical=vertical, 
                       h_angle=h_angle, v_angle=v_angle)
            return True
        except Exception as e:
            logger.error("camera_controller.rotate_failed", error=str(e))
            raise CommandExecutionError(f"Camera rotation failed: {e}")
    
    async def center(self) -> bool:
        """Center camera to default position"""
        return await self.rotate(0, 0)
