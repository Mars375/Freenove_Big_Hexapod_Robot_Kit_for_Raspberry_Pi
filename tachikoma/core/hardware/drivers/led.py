"""LED driver for Freenove Hexapod with WS281X/SPI control."""
from typing import List, Tuple, Optional
from enum import Enum
import logging
from tachikoma.core.config import settings

if settings.MOCK_HARDWARE:
    SPI_AVAILABLE = False
    np = None
else:
    try:
        import spidev
        import numpy as np
        SPI_AVAILABLE = True
    except ImportError:
        SPI_AVAILABLE = False
        np = None

logger = logging.getLogger(__name__)


class LedMode(Enum):
    """LED operation modes."""
    OFF = 0
    SOLID = 1
    COLOR_WIPE = 2
    RAINBOW = 4
    BREATHING = 5      # ✅ AJOUT
    CHASE = 6          # ✅ AJOUT
    BLINK = 7          # ✅ AJOUT (pour strobe/fire)
    WAVE = 8

class ColorSequence(Enum):
    """LED color sequence types for different strips."""
    RGB = 'RGB'
    RBG = 'RBG'
    GRB = 'GRB'
    GBR = 'GBR'
    BRG = 'BRG'
    BGR = 'BGR'


class LEDController:
    """WS281X LED controller via SPI interface.
    
    This controller manages RGB LED strips (like WS2812) using the SPI
    interface to send color data. It supports multiple color sequences,
    brightness control, and various animation modes.
    
    Args:
        led_count: Number of LEDs in the strip
        brightness: Initial brightness (0-255)
        sequence: Color sequence type (default: GRB for WS2812)
        bus: SPI bus number (0 for /dev/spidev0.x)
        device: SPI device number (0 for /dev/spidev0.0)
    """
    
    # Color sequence encoding: each color gets 2 bits for position
    _SEQUENCE_OFFSETS = {
        'RGB': 0x06,  # R=0, G=1, B=2
        'RBG': 0x09,  # R=0, B=1, G=2
        'GRB': 0x12,  # G=0, R=1, B=2
        'GBR': 0x21,  # G=0, B=1, R=2
        'BRG': 0x18,  # B=0, R=1, G=2
        'BGR': 0x24,  # B=0, G=1, R=2
    }
    
    def __init__(
        self,
        led_count: int = 8,
        brightness: int = 255,
        sequence: ColorSequence = ColorSequence.GRB,
        bus: int = 0,
        device: int = 0
    ):
        """Initialize the LED controller."""
        if not SPI_AVAILABLE:
            logger.warning("SPI libraries not available - LED controller in mock mode")
            self._mock_mode = True
            self.led_count = led_count
            self.brightness = brightness
            self.current_mode = LedMode.OFF
            return
            
        self._mock_mode = False
        self.bus = bus
        self.device = device
        self.led_count = led_count
        self.brightness = brightness
        self.current_mode = LedMode.OFF
        
        # Initialize color offsets based on sequence
        self._set_color_sequence(sequence)
        
        # Initialize color arrays
        self._led_color = [0] * (led_count * 3)
        self._led_original_color = [0] * (led_count * 3)
        
        # Initialize SPI
        self._init_spi()
        
        # Turn off all LEDs initially
        if self._spi_initialized:
            self.set_all(0, 0, 0)
    
    def _set_color_sequence(self, sequence: ColorSequence) -> None:
        """Set the color sequence for the LED strip."""
        sequence_str = sequence.value if isinstance(sequence, ColorSequence) else sequence
        offset = self._SEQUENCE_OFFSETS.get(sequence_str, 0x12)  # Default to GRB
        
        self._red_offset = (offset >> 4) & 0x03
        self._green_offset = (offset >> 2) & 0x03
        self._blue_offset = (offset >> 0) & 0x03
    
    def _init_spi(self) -> None:
        """Initialize SPI connection."""
        self._spi_initialized = False
        
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(self.bus, self.device)
            self.spi.mode = 0
            self._spi_initialized = True
            logger.info(f"SPI initialized on bus {self.bus}, device {self.device}")
        except OSError as e:
            logger.error(f"Failed to initialize SPI: {e}")
            logger.error("Check /boot/firmware/config.txt configuration")
            if self.bus == 0:
                logger.error("Enable 'SPI' in 'Interface Options' with 'sudo raspi-config'")
                logger.error("Or ensure 'dtparam=spi=on' is uncommented")
            else:
                logger.error(
                    f"Add 'dtoverlay=spi{self.bus}-2cs' to /boot/firmware/config.txt"
                )
    
    def is_available(self) -> bool:
        """Check if SPI is properly initialized."""
        return not self._mock_mode and self._spi_initialized
    
    def set_color(self, r: int, g: int, b: int, index: int) -> None:
        """Set color of a specific LED.
        
        Args:
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
            index: LED index (0-based)
        """
        if self._mock_mode or not self._spi_initialized:
            return
            
        if not 0 <= index < self.led_count:
            logger.warning(f"LED index {index} out of range (0-{self.led_count-1})")
            return
        
        # Apply brightness scaling
        scaled = [0, 0, 0]
        scaled[self._red_offset] = round(r * self.brightness / 255)
        scaled[self._green_offset] = round(g * self.brightness / 255)
        scaled[self._blue_offset] = round(b * self.brightness / 255)
        
        # Store original colors
        base_idx = index * 3
        self._led_original_color[base_idx + self._red_offset] = r
        self._led_original_color[base_idx + self._green_offset] = g
        self._led_original_color[base_idx + self._blue_offset] = b
        
        # Store scaled colors
        for i in range(3):
            self._led_color[base_idx + i] = scaled[i]
    
    def set_all(self, r: int, g: int, b: int) -> None:
        """Set all LEDs to the same color.
        
        Args:
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
        """
        if self._mock_mode or not self._spi_initialized:
            return
            
        for i in range(self.led_count):
            self.set_color(r, g, b, i)
        self.show()
    
    def set_brightness(self, brightness: int) -> None:
        """Update brightness and refresh all LED colors.
        
        Args:
            brightness: New brightness value (0-255)
        """
        if not 0 <= brightness <= 255:
            logger.warning(f"Brightness {brightness} out of range (0-255)")
            return
            
        self.brightness = brightness
        
        # Reapply colors with new brightness
        if not self._mock_mode and self._spi_initialized:
            for i in range(self.led_count):
                base_idx = i * 3
                r = self._led_original_color[base_idx + self._red_offset]
                g = self._led_original_color[base_idx + self._green_offset]
                b = self._led_original_color[base_idx + self._blue_offset]
                self.set_color(r, g, b, i)
    
    def _encode_ws2812_8bit(self) -> Optional[List[int]]:
        """Encode color data for WS2812 using 8-bit mode.
        
        Each bit is represented by a byte: 0x78 for '1', 0x80 for '0'.
        T0H=1, T0L=7, T1H=5, T1L=3 (timing for WS2812).
        """
        if not np:
            return None
            
        d = self._led_color
        tx = [0] * (len(d) * 8)
        
        for i, val in enumerate(d):
            for ibit in range(8):
                if (val >> ibit) & 1:
                    tx[i * 8 + (7 - ibit)] = 0x78
                else:
                    tx[i * 8 + (7 - ibit)] = 0x80
        
        return tx
    
    def show(self, mode: int = 1) -> None:
        """Update the LED strip with current color data.
        
        Args:
            mode: Encoding mode (1 for 8-bit, other for 4-bit)
        """
        if self._mock_mode or not self._spi_initialized:
            return
        
        if mode == 1:
            tx = self._encode_ws2812_8bit()
            if tx:
                # SPI0 uses 6.4MHz, others use 8MHz
                freq = int(8 / 1.25e-6) if self.bus == 0 else int(8 / 1.0e-6)
                self.spi.xfer(tx, freq)
    
    def wheel(self, pos: int) -> Tuple[int, int, int]:
        """Generate rainbow color based on position (0-255).
        
        Args:
            pos: Position in color wheel (0-255)
            
        Returns:
            RGB tuple (0-255 each)
        """
        pos = pos % 256
        
        if pos < 85:
            return (255 - pos * 3, pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return (0, 255 - pos * 3, pos * 3)
        else:
            pos -= 170
            return (pos * 3, 0, 255 - pos * 3)
    
    def hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB.
        
        Args:
            h: Hue (0-360)
            s: Saturation (0-100)
            v: Value/brightness (0-100)
            
        Returns:
            RGB tuple (0-255 each)
        """
        import colorsys
        
        # Normalize h, s, v to 0-1 range
        h /= 360.0
        s /= 100.0
        v /= 100.0

        r, g, b = colorsys.hsv_to_rgb(h, s, v)

        # Scale r, g, b to 0-255 range and convert to int
        return int(r * 255), int(g * 255), int(b * 255)
    
    def off(self) -> None:
        """Turn off all LEDs."""
        self.set_all(0, 0, 0)
        self.current_mode = LedMode.OFF
    
    def close(self) -> None:
        """Cleanup and close SPI connection."""
        self.off()
        if not self._mock_mode and hasattr(self, 'spi'):
            self.spi.close()
            logger.info("LED controller closed")
