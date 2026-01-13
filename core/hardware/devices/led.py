import logging
from typing import Optional, Dict, Any, Tuple
from core.hardware.interfaces.base import IHardwareComponent, HardwareStatus

try:
    from rpi_ws281x import PixelStrip, Color
    LED_AVAILABLE = True
except ImportError:
    LED_AVAILABLE = False


class LEDStrip(IHardwareComponent):
    """Contrôleur pour bande LED WS281x (NeoPixel)"""
    
    def __init__(self, led_count: int = 8, led_pin: int = 18, 
                 led_freq_hz: int = 800000, led_dma: int = 10,
                 led_brightness: int = 255, led_invert: bool = False,
                 led_channel: int = 0):
        self.led_count = led_count
        self.led_pin = led_pin
        self.led_freq_hz = led_freq_hz
        self.led_dma = led_dma
        self.led_brightness = led_brightness
        self.led_invert = led_invert
        self.led_channel = led_channel
        
        self._strip: Optional[PixelStrip] = None
        self.logger = logging.getLogger(__name__)
        self._status = HardwareStatus.UNINITIALIZED
        self._current_color: Tuple[int, int, int] = (0, 0, 0)
    
    async def initialize(self) -> bool:
        if not LED_AVAILABLE:
            self.logger.error("rpi_ws281x not available")
            self._status = HardwareStatus.ERROR
            return False
        
        try:
            self._status = HardwareStatus.INITIALIZING
            
            self._strip = PixelStrip(
                self.led_count,
                self.led_pin,
                self.led_freq_hz,
                self.led_dma,
                self.led_invert,
                self.led_brightness,
                self.led_channel
            )
            
            self._strip.begin()
            
            # Turn off all LEDs
            self.clear()
            
            self._status = HardwareStatus.READY
            self.logger.info(f"LED strip initialized ({self.led_count} LEDs on pin {self.led_pin})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LED strip: {e}")
            self._status = HardwareStatus.ERROR
            return False
    
    async def cleanup(self) -> None:
        try:
            self.clear()
            self._strip = None
            self._status = HardwareStatus.DISCONNECTED
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def set_color(self, r: int, g: int, b: int) -> bool:
        if not self.is_available():
            return False
        
        try:
            color = Color(r, g, b)
            for i in range(self.led_count):
                self._strip.setPixelColor(i, color)
            self._strip.show()
            self._current_color = (r, g, b)
            return True
        except Exception as e:
            self.logger.error(f"Failed to set LED color: {e}")
            return False
    
    def set_pixel(self, pixel: int, r: int, g: int, b: int) -> bool:
        if not self.is_available() or not (0 <= pixel < self.led_count):
            return False
        
        try:
            self._strip.setPixelColor(pixel, Color(r, g, b))
            self._strip.show()
            return True
        except Exception as e:
            self.logger.error(f"Failed to set pixel {pixel}: {e}")
            return False
    
    def clear(self) -> bool:
        return self.set_color(0, 0, 0)
    
    def rainbow_cycle(self, wait_ms: int = 20, iterations: int = 1) -> bool:
        if not self.is_available():
            return False
        
        try:
            import time
            for j in range(256 * iterations):
                for i in range(self.led_count):
                    pixel_index = (i * 256 // self.led_count) + j
                    color = self._wheel(pixel_index & 255)
                    self._strip.setPixelColor(i, color)
                self._strip.show()
                time.sleep(wait_ms / 1000.0)
            return True
        except Exception as e:
            self.logger.error(f"Failed to run rainbow cycle: {e}")
            return False
    
    def _wheel(self, pos: int) -> int:
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)
    
    def is_available(self) -> bool:
        return LED_AVAILABLE and self._status == HardwareStatus.READY
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "type": "led_strip",
            "led_count": self.led_count,
            "pin": self.led_pin,
            "status": self._status.value,
            "available": self.is_available(),
            "current_color": self._current_color
        }
    
    def get_health(self) -> Dict[str, Any]:
        return {
            "healthy": self.is_available(),
            "status": self._status.value
        }
