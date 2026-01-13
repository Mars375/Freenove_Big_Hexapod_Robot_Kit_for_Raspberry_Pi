"""Hardware factory for creating controller instances"""
from typing import Optional
import structlog

from core.config import Settings
from core.hardware.interfaces import IServoController
from core.hardware.drivers import PCA9685ServoController

logger = structlog.get_logger()


class HardwareFactory:
    """Factory for creating hardware controller instances
    
    Centralizes hardware instantiation logic and configuration.
    Supports dependency injection and testing.
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize hardware factory
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self._servo_controller: Optional[IServoController] = None
        
        logger.info("hardware_factory.created")
    
    def create_servo_controller(self) -> IServoController:
        """Create servo controller based on configuration
        
        Returns:
            Configured servo controller instance
            
        Raises:
            ValueError: If invalid servo type specified
        """
        if self._servo_controller is not None:
            logger.debug("hardware_factory.reusing_servo_controller")
            return self._servo_controller
        
        # For now, we only support PCA9685
        # In future, could be configured via settings
        servo_type = "pca9685"  # settings.hardware.servo_type
        
        if servo_type == "pca9685":
            logger.info(
                "hardware_factory.creating_pca9685",
                channels=16,
                address="0x40"
            )
            self._servo_controller = PCA9685ServoController(
                channels=16,
                i2c_address=0x40,
                frequency=50,
                min_pulse=500,
                max_pulse=2500
            )
        else:
            raise ValueError(f"Unknown servo type: {servo_type}")
        
        return self._servo_controller
    
    def get_servo_controller(self) -> Optional[IServoController]:
        """Get existing servo controller instance
        
        Returns:
            Existing servo controller or None if not created
        """
        return self._servo_controller
    
    async def cleanup_all(self):
        """Cleanup all hardware resources"""
        logger.info("hardware_factory.cleanup_all")
        
        if self._servo_controller:
            try:
                await self._servo_controller.cleanup()
                self._servo_controller = None
            except Exception as e:
                logger.error(
                    "hardware_factory.servo_cleanup_failed",
                    error=str(e)
                )


# Global factory instance (initialized at startup)
_factory: Optional[HardwareFactory] = None


def get_hardware_factory(settings: Optional[Settings] = None) -> HardwareFactory:
    """Get or create global hardware factory
    
    Args:
        settings: Application settings (required for first call)
        
    Returns:
        Global hardware factory instance
    """
    global _factory
    
    if _factory is None:
        if settings is None:
            from core.config import get_settings
            settings = get_settings()
        
        _factory = HardwareFactory(settings)
    
    return _factory
