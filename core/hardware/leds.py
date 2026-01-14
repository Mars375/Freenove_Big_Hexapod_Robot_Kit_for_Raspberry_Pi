"""LED control abstraction"""
import structlog
from core.exceptions import HardwareNotAvailableError, CommandExecutionError
from core.hardware.factory import get_hardware_factory

logger = structlog.get_logger()


class LEDController:
    """Abstraction for LED control"""

    def __init__(self):
        self.factory = get_hardware_factory()
        self._led = None
        self._num_leds = 7  # Robot has 7 LEDs
        
    async def _ensure_hardware(self):
        if not self._led:
            self._led = await self.factory.get_led_strip(led_count=self._num_leds)

    @property
    def is_available(self) -> bool:
        # We assume available if we can try to get it, or check internal state
        return True 

    async def set_mode(self, mode: str, r: int = 0, g: int = 0, b: int = 0) -> bool:
        """Set LED mode"""
        await self._ensure_hardware()
        
        if not self._led:
             raise HardwareNotAvailableError("LED controller not initialized")

        try:
            if mode == "solid":
                # Set all LEDs to the same color
                await self._led.fill(r, g, b)
            elif mode == "rainbow":
                await self._led.rainbow()
            elif mode == "rainbow_cycle":
                 await self._led.rainbow_cycle()
            elif mode == "breathing":
                # Not implemented in basic driver, fallback to solid or implement later
                await self._led.fill(r, g, b)
            elif mode == "off":
                await self._led.clear()
            else:
                raise ValueError(f"Unknown LED mode: {mode}")

            logger.info("led_controller.mode_set", mode=mode, r=r, g=g, b=b)
            return True
            else:
                raise ValueError(f"Unknown LED mode: {mode}")

            logger.info("led_controller.mode_set", mode=mode, r=r, g=g, b=b)
            return True
        except Exception as e:
            logger.error("led_controller.mode_failed", error=str(e))
            raise CommandExecutionError(f"LED mode failed: {e}")
