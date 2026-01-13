import pytest
from unittest.mock import MagicMock, patch, PropertyMock

# Mock the hardware modules before importing the driver
# This needs to be done before the 'from core...' import
import sys

# Create mock objects for spidev and numpy
mock_spidev_module = MagicMock()
mock_numpy_module = MagicMock()
sys.modules['spidev'] = mock_spidev_module
sys.modules['numpy'] = mock_numpy_module

# Now, we can import the LEDController
from core.hardware.drivers.led import LEDController, ColorSequence


@pytest.fixture
def mock_spidev():
    """Fixture to mock spidev.SpiDev and its methods."""
    with patch('spidev.SpiDev') as mock_spi_constructor:
        mock_spi_instance = MagicMock()
        mock_spi_constructor.return_value = mock_spi_instance
        yield mock_spi_instance

# Test cases for LEDController
def test_led_controller_initialization_mock_mode():
    """Test LEDController initialization when SPI is not available."""
    with patch('core.hardware.drivers.led.SPI_AVAILABLE', False):
        controller = LEDController()
        assert controller._mock_mode is True
        assert controller.led_count == 8
        assert controller.brightness == 255
        assert controller.is_available() is False

def test_led_controller_initialization_spi_mode(mock_spidev):
    """Test LEDController initialization when SPI is available."""
    with patch('core.hardware.drivers.led.SPI_AVAILABLE', True):
        controller = LEDController(led_count=10, brightness=200)
        assert controller._mock_mode is False
        assert controller.led_count == 10
        assert controller.brightness == 200
        mock_spidev.open.assert_called_with(0, 0)
        assert controller.is_available() is True

def test_set_color_with_brightness_scaling(mock_spidev):
    """Test set_color applies brightness scaling correctly."""
    with patch('core.hardware.drivers.led.SPI_AVAILABLE', True):
        controller = LEDController(led_count=1, brightness=128) # 50% brightness
        controller.set_color(255, 100, 50, 0)

        # Check original color storage
        assert controller._led_original_color[controller._red_offset] == 255
        assert controller._led_original_color[controller._green_offset] == 100
        assert controller._led_original_color[controller._blue_offset] == 50

        # Check scaled color storage (approx 50%)
        assert abs(controller._led_color[controller._red_offset] - 128) <= 1
        assert abs(controller._led_color[controller._green_offset] - 50) <= 1
        assert abs(controller._led_color[controller._blue_offset] - 25) <= 1

def test_set_all(mock_spidev):
    """Test set_all calls set_color for all LEDs and show."""
    with patch('core.hardware.drivers.led.SPI_AVAILABLE', True):
        controller = LEDController(led_count=4)
        with patch.object(controller, 'set_color') as mock_set_color, \
             patch.object(controller, 'show') as mock_show:

            controller.set_all(255, 0, 0)

            assert mock_set_color.call_count == 4
            mock_set_color.assert_called_with(255, 0, 0, 3) # Check last call
            mock_show.assert_called_once()

def test_set_brightness_reapplies_colors(mock_spidev):
    """Test that set_brightness updates brightness and reapplies colors."""
    with patch('core.hardware.drivers.led.SPI_AVAILABLE', True):
        controller = LEDController(led_count=1, brightness=255)
        controller.set_color(200, 100, 50, 0)

        # Original colors should be unscaled
        assert controller._led_color[controller._red_offset] == 200
        assert controller._led_color[controller._green_offset] == 100
        assert controller._led_color[controller._blue_offset] == 50

        # Set new brightness
        controller.set_brightness(128) # ~50%

        assert controller.brightness == 128
        # Check if colors are rescaled
        assert abs(controller._led_color[controller._red_offset] - 100) <= 1
        assert abs(controller._led_color[controller._green_offset] - 50) <= 1
        assert abs(controller._led_color[controller._blue_offset] - 25) <= 1

def test_encode_ws2812_8bit():
    """Test the WS2812 8-bit encoding logic."""
    with patch('core.hardware.drivers.led.SPI_AVAILABLE', True), \
         patch('core.hardware.drivers.led.np', mock_numpy_module):

        # Mock numpy array behavior
        mock_numpy_module.array.return_value.ravel.return_value = [0b10101010, 0b11001100, 0b00110011]

        controller = LEDController(led_count=1)
        controller._led_color = [0b10101010, 0b11001100, 0b00110011] # One pixel

        encoded_data = controller._encode_ws2812_8bit()

        # Expect 3 bytes * 8 bits/byte = 24 bytes
        assert len(encoded_data) == 24

        # Test a few values based on the logic: '1' -> 0x78, '0' -> 0x80
        # First byte: 10101010
        assert encoded_data[0] == 0x78 # 1
        assert encoded_data[1] == 0x80 # 0
        assert encoded_data[2] == 0x78 # 1
        assert encoded_data[3] == 0x80 # 0
        assert encoded_data[4] == 0x78 # 1
        assert encoded_data[5] == 0x80 # 0
        assert encoded_data[6] == 0x78 # 1
        assert encoded_data[7] == 0x80 # 0

def test_wheel_utility():
    """Test the wheel color generation utility."""
    controller = LEDController()
    # Test primary colors
    assert controller.wheel(0) == (255, 0, 0) # Red
    assert controller.wheel(85) == (0, 255, 0) # Green
    assert controller.wheel(170) == (0, 0, 255) # Blue
    # Test intermediate color
    r, g, b = controller.wheel(42)
    assert r > 0 and g > 0 and b == 0

def test_hsv_to_rgb_utility():
    """Test the HSV to RGB conversion utility."""
    controller = LEDController()
    # Test primary colors
    assert controller.hsv_to_rgb(0, 100, 100) == (255, 0, 0)       # Red
    assert controller.hsv_to_rgb(120, 100, 100) == (0, 255, 0)   # Green
    assert controller.hsv_to_rgb(240, 100, 100) == (0, 0, 255)   # Blue
    # Test white/grey/black
    assert controller.hsv_to_rgb(0, 0, 100) == (255, 255, 255)    # White
    r, g, b = controller.hsv_to_rgb(0, 0, 50)
    assert abs(r - 128) <= 1 and abs(g - 128) <= 1 and abs(b - 128) <= 1 # Grey with tolerance
    assert controller.hsv_to_rgb(0, 100, 0) == (0, 0, 0)          # Black
