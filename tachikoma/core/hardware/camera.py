"""Camera control abstraction"""
import structlog

from tachikoma.core.exceptions import HardwareNotAvailableError, CommandExecutionError
from tachikoma.core.hardware.factory import get_hardware_factory

logger = structlog.get_logger()


class CameraController:
    """Abstraction for camera pan/tilt control"""
    
    def __init__(self):
        self.factory = get_hardware_factory()
        self._servo = None
        self._driver = None
        self._horizontal_channel = 1 # Swapped per user report (was 0)
        self._vertical_channel = 0   # Swapped per user report (was 1)
        # Note: If cameras are on specific channels, we need to know. 
        # User reported: 
        # Tilt (Vertical) moved Left/Right -> So Vertical is on Horizontal Channel?
        # Pan (Horizontal) moved Up/Down -> So Horizontal is on Vertical Channel?
        # Swapping defaults to 1 (Pan) and 0 (Tilt) to test.
        
    async def _ensure_hardware(self):
        if not self._servo:
            self._servo = await self.factory.create_servo_controller()
        if not self._driver:
            self._driver = await self.factory.get_camera()
    
    @property
    def is_available(self) -> bool:
        return True # Availability check is done in methods via _ensure_hardware
    
    async def rotate(self, horizontal: int, vertical: int) -> bool:
        """Rotate camera servos
        
        Args:
            horizontal: Pan angle (-90 to 90, 0=center)
            vertical: Tilt angle (-45 to 45, 0=center)
        """
        await self._ensure_hardware()
        
        if not self._servo or not self._servo.is_available():
            raise HardwareNotAvailableError("Camera controller not initialized")
        
        try:
            # Convert angles to servo range (typically 0-180, with 90 as center)
            # Horizontal: -90 to 90 -> 0 to 180
            h_angle = 90 + horizontal
            # Vertical: -45 to 45 -> 45 to 135 (limited tilt range)
            v_angle = 90 + vertical
            
            # Clamp values
            h_angle = max(0, min(180, h_angle))
            v_angle = max(0, min(180, v_angle)) # Full range per user request
            
            # Set servo angles 
            await self._servo.set_angle_async(self._horizontal_channel, h_angle)
            await self._servo.set_angle_async(self._vertical_channel, v_angle)
            
            logger.info("camera_controller.rotated", horizontal=horizontal, vertical=vertical, 
                       h_angle=h_angle, v_angle=v_angle)
            return True
        except Exception as e:
            logger.error("camera_controller.rotate_failed", error=str(e))
            raise CommandExecutionError(f"Camera rotation failed: {e}")
    
    async def get_frame(self) -> bytes:
        """Get the latest frame from the camera driver."""
        await self._ensure_hardware()
        if self._driver:
            return await self._driver.get_frame()
        return b""

    async def center(self) -> bool:
        """Center camera to default position"""
        return await self.rotate(0, 0)
        
    async def start_streaming(self):
        """Start camera streaming"""
        await self._ensure_hardware()
        if self._driver:
            if hasattr(self._driver, 'start_streaming'):
                await self._driver.start_streaming()

    async def stop_streaming(self):
        """Stop camera streaming"""
        await self._ensure_hardware()
        if self._driver:
            if hasattr(self._driver, 'stop_streaming'):
                await self._driver.stop_streaming()
