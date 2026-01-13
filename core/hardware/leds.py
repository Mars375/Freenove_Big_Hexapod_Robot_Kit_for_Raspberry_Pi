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
        self._num_leds = 7  # Robot has 7 LEDs
        self._initialize_hardware()

    def _initialize_hardware(self):
        """Initialize legacy LED module"""
        try:
            from led import Led
            self._led = Led()
            # Get actual LED count
            try:
                self._num_leds = self._led.strip.get_led_count()
            except:
                self._num_leds = 7  # Default
            logger.info("led_controller.initialized", num_leds=self._num_leds)
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
                # Set all LEDs to the same color using the strip directly
                for i in range(self._num_leds):
                    self._led.strip.set_led_rgb_data(i, [r, g, b])
                self._led.strip.show()  # IMPORTANT: Force refresh!
            elif mode == "rainbow":
                self._led.rainbow()
            elif mode == "rainbow_cycle":
                self._led.rainbow_cycle()
            elif mode == "breathing":
                # Use color_wipe with the color
                color = (r << 16) | (g << 8) | b
                self._led.color_wipe(color)
            elif mode == "off":
                # Turn all LEDs off
                for i in range(self._num_leds):
                    self._led.strip.set_led_rgb_data(i, [0, 0, 0])
                self._led.strip.show()  # IMPORTANT: Force refresh!
            else:
                raise ValueError(f"Unknown LED mode: {mode}")

            logger.info("led_controller.mode_set", mode=mode, r=r, g=g, b=b)
            return True
        except Exception as e:
            logger.error("led_controller.mode_failed", error=str(e))
            raise CommandExecutionError(f"LED mode failed: {e}")
