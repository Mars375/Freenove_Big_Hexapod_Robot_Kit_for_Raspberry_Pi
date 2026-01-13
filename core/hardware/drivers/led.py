"""LED driver for Freenove Hexapod with WS281X/SPI abstraction."""
from typing import List, Tuple
from enum import Enum

class LedMode(Enum):
    OFF = 0
    SOLID = 1
    COLOR_WIPE = 2
    RAINBOW = 4

class LEDController:
    """Mock LED controller - full implementation pending."""
    
    def __init__(self, led_count: int = 7, brightness: int = 255):
        self.led_count = led_count
        self.brightness = brightness
        self.current_mode = LedMode.OFF
    
    def set_color(self, r: int, g: int, b: int, index: int = None):
        """Set LED color."""
        pass
    
    def set_all(self, r: int, g: int, b: int):
        """Set all LEDs to same color."""
        pass
    
    def set_mode(self, mode: LedMode):
        """Set animation mode."""
        self.current_mode = mode
    
    def off(self):
        """Turn off all LEDs."""
        self.set_all(0, 0, 0)
    
    def close(self):
        """Cleanup."""
        self.off()
