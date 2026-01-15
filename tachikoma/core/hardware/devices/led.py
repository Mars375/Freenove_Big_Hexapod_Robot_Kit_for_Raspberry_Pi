"""LED Device Layer using SPI-based WS281X driver."""
import logging
from typing import Optional, Dict, Any, Tuple
from tachikoma.core.hardware.interfaces.base import IHardwareComponent, HardwareStatus
from tachikoma.core.hardware.drivers.led import LEDController, ColorSequence, LedMode
from tachikoma.core.hardware.led_animations import LEDAnimations

logger = logging.getLogger(__name__)


class LEDStrip(IHardwareComponent):
    """LED strip device using SPI-based WS281X driver.
    
    This device wraps the low-level LEDController driver to provide
    a high-level interface for controlling LED strips on the hexapod.
    
    Args:
        led_count: Number of LEDs in the strip (default: 8)
        brightness: Initial brightness 0-255 (default: 255)
        sequence: Color sequence type (default: GRB for WS2812)
        bus: SPI bus number (default: 0)
        device: SPI device number (default: 0)
    """
    
    def __init__(
        self,
        led_count: int = 8,
        brightness: int = 255,
        sequence: ColorSequence = ColorSequence.GRB,
        bus: int = 0,
        device: int = 0
    ):
        self.led_count = led_count
        self.brightness = brightness
        self.sequence = sequence
        self.bus = bus
        self.device = device
        
        self._driver: Optional[LEDController] = None
        self._animator: Optional[LEDAnimations] = None
        self._status = HardwareStatus.UNINITIALIZED
        self._current_color: Tuple[int, int, int] = (0, 0, 0)
        self._current_mode = LedMode.OFF
        
        logger.info(
            f"LEDStrip initialized with {led_count} LEDs, "
            f"brightness={brightness}, sequence={sequence.value}"
        )
    
    async def initialize(self) -> bool:
        """Initialize the LED strip.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self._status = HardwareStatus.INITIALIZING
            logger.info("Initializing LED strip...")
            
            # Create the driver
            self._driver = LEDController(
                led_count=self.led_count,
                brightness=self.brightness,
                sequence=self.sequence,
                bus=self.bus,
                device=self.device
            )
            
            # Create animator
            self._animator = LEDAnimations(self, self.led_count)
            
            # Check if driver is available
            if not self._driver.is_available():
                logger.warning("LED driver in mock mode (SPI not available)")
                self._status = HardwareStatus.READY  # Still ready, just in mock mode
            else:
                self._status = HardwareStatus.READY
                logger.info("LED strip initialized successfully")
            
            # Turn off all LEDs initially
            self._driver.off()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize LED strip: {e}", exc_info=True)
            self._status = HardwareStatus.ERROR
            return False
    
    async def cleanup(self) -> None:
        """Clean up LED strip resources."""
        try:
            if self._animator:
                self._animator.stop()
            if self._driver:
                self._driver.close()
                logger.info("LED strip cleaned up")
            self._status = HardwareStatus.DISCONNECTED
        except Exception as e:
            logger.error(f"Error during LED cleanup: {e}", exc_info=True)
    
    def set_color(self, r: int, g: int, b: int) -> bool:
        """Set all LEDs to a single color.
        
        Args:
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
            
        Returns:
            bool: True if successful
        """
        if not self.is_available():
            logger.warning("Cannot set color: LED strip not available")
            return False
        
        try:
            self._driver.set_all(r, g, b)
            self._current_color = (r, g, b)
            self._current_mode = LedMode.SOLID
            return True
        except Exception as e:
            logger.error(f"Failed to set LED color: {e}")
            return False
    
    def set_pixel(self, pixel: int, r: int, g: int, b: int) -> bool:
        """Set a specific LED to a color.
        
        Args:
            pixel: LED index (0-based)
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
            
        Returns:
            bool: True if successful
        """
        if not self.is_available():
            logger.warning("Cannot set pixel: LED strip not available")
            return False
        
        try:
            self._driver.set_color(r, g, b, pixel)
            self._driver.show()
            return True
        except Exception as e:
            logger.error(f"Failed to set pixel {pixel}: {e}")
            return False
    def show(self) -> None:
        """Update the LED strip to display current colors."""
        if not self.is_available():
            return
    
        try:
            self._driver.show()
        except Exception as e:
            logger.error(f"Failed to show LEDs: {e}")

    def set_brightness(self, brightness: int) -> bool:
        """Set overall brightness.
        
        Args:
            brightness: Brightness value (0-255)
            
        Returns:
            bool: True if successful
        """
        if not self.is_available():
            logger.warning("Cannot set brightness: LED strip not available")
            return False
        
        try:
            self._driver.set_brightness(brightness)
            self._driver.show()
            self.brightness = brightness
            return True
        except Exception as e:
            logger.error(f"Failed to set brightness: {e}")
            return False
    
    def rainbow_cycle(self, iterations: int = 1) -> bool:
        """Run rainbow cycle animation.
        
        Args:
            iterations: Number of cycles to run
            
        Returns:
            bool: True if successful
        """
        if not self.is_available():
            logger.warning("Cannot run rainbow: LED strip not available")
            return False
        
        try:
            import time
            for j in range(256 * iterations):
                for i in range(self.led_count):
                    color = self._driver.wheel(
                        (i * 256 // self.led_count + j) % 256
                    )
                    self._driver.set_color(*color, i)
                self._driver.show()
                time.sleep(0.002)
            
            self._current_mode = LedMode.RAINBOW
            return True
        except Exception as e:
            logger.error(f"Failed to run rainbow cycle: {e}")
            return False
    
    # ============= New Animation Methods =============
    
    async def police(self, duration: float = 5.0, speed: float = 0.1) -> bool:
        """Run police siren animation."""
        if not self.is_available() or not self._animator:
            return False
        self._current_mode = LedMode.CHASE  # Using CHASE enum value
        return await self._animator.police(duration, speed)
    
    async def breathing(self, r: int, g: int, b: int, duration: float = 10.0, speed: float = 2.0) -> bool:
        """Run breathing animation."""
        if not self.is_available() or not self._animator:
            return False
        self._current_mode = LedMode.BREATHING
        return await self._animator.breathing(r, g, b, duration, speed)
    
    async def fire(self, duration: float = 10.0, intensity: float = 1.0) -> bool:
        """Run fire animation."""
        if not self.is_available() or not self._animator:
            return False
        self._current_mode = LedMode.BLINK  # Using BLINK enum value
        return await self._animator.fire(duration, intensity)
    
    async def wave(self, r: int, g: int, b: int, duration: float = 10.0, speed: float = 0.5) -> bool:
        """Run wave animation."""
        if not self.is_available() or not self._animator:
            return False
        self._current_mode = LedMode.CHASE  # Using CHASE enum value
        return await self._animator.wave(r, g, b, duration, speed)
    
    async def strobe(self, r: int, g: int, b: int, duration: float = 5.0, speed: float = 0.05) -> bool:
        """Run strobe animation."""
        if not self.is_available() or not self._animator:
            return False
        self._current_mode = LedMode.BLINK
        return await self._animator.strobe(r, g, b, duration, speed)
    
    async def chase(self, r: int, g: int, b: int, duration: float = 10.0, speed: float = 0.1) -> bool:
        """Run chase animation."""
        if not self.is_available() or not self._animator:
            return False
        self._current_mode = LedMode.CHASE
        return await self._animator.chase(r, g, b, duration, speed)
    
    # ============= End New Animation Methods =============
    
    def off(self) -> bool:
        """Turn off all LEDs.
        
        Returns:
            bool: True if successful
        """
        if not self.is_available():
            logger.warning("Cannot turn off: LED strip not available")
            return False
        
        try:
            if self._animator:
                self._animator.stop()
            self._driver.off()
            self._current_color = (0, 0, 0)
            self._current_mode = LedMode.OFF
            return True
        except Exception as e:
            logger.error(f"Failed to turn off LEDs: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if LED strip is available.
        
        Returns:
            bool: True if ready to use
        """
        return (
            self._status == HardwareStatus.READY and
            self._driver is not None
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current LED strip status.
        
        Returns:
            Dict containing status information
        """
        return {
            "type": "led_strip",
            "led_count": self.led_count,
            "brightness": self.brightness,
            "sequence": self.sequence.value,
            "bus": self.bus,
            "device": self.device,
            "status": self._status.value,
            "available": self.is_available(),
            "current_color": self._current_color,
            "current_mode": self._current_mode.value,
            "mock_mode": self._driver is not None and self._driver._mock_mode
        }
    
    def get_health(self) -> Dict[str, Any]:
        """Get LED strip health status.
        
        Returns:
            Dict containing health information
        """
        return {
            "healthy": self.is_available(),
            "status": self._status.value,
            "driver_available": self._driver.is_available() if self._driver else False
        }
