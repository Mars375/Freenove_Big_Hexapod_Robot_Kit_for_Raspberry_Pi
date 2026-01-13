"""LED control abstraction"""
import sys
from pathlib import Path
import structlog

legacy_path = Path(__file__).parent.parent.parent / "legacy" / "Code" / "Server"
sys.path.insert(0, str(legacy_path))

from core.exceptions import HardwareNotAvailableError, CommandExecutionError

logger = structlog.get_logger()


class LEDController:
    """Abstraction for LED control"""
    
    def __init__(self):
        self._led = None
        self._initialize_hardware()
    
    def _initialize_hardware(self):
        """Initialize legacy LED module"""
        try:
            from led import LED
            self._led = LED()
            logger.info("led_controller.initialized")
        except Exception as e:
            logger.error("led_controller.init_failed", error=str(e))
            self._led = None
    
    @property
    def is_available(self) -> bool:
        return self._led is not None
    
    async def set_mode(self, mode: str, r: int = 0, g: int = 0, b: int = 0) -> bool:
        """Set LED mode"""
        if not self.is_available:
            raise HardwareNotAvailableError("LED controller not initialized")
        
        try:
            if mode == "solid":
                self._led.set_color(r, g, b)
            elif mode == "rainbow":
                self._led.rainbow()
            elif mode == "breathing":
                self._led.breathing(r, g, b)
            elif mode == "off":
                self._led.off()
            else:
                raise ValueError(f"Unknown LED mode: {mode}")
            
            logger.info("led_controller.mode_set", mode=mode, r=r, g=g, b=b)
            return True
        except Exception as e:
            logger.error("led_controller.mode_failed", error=str(e))
            raise CommandExecutionError(f"LED mode failed: {e}")
