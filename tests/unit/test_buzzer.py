"""Tests for buzzer controller."""
import pytest
from unittest.mock import Mock, patch

# No need for sys.modules hacking. We use pytest-mock's 'mocker' fixture.

@pytest.fixture
def mock_gpio(mocker):
    """
    Mocks the RPi.GPIO module by patching it where it's imported.
    This is the robust way to handle hardware library mocking.
    """
    pwm_instance = Mock()
    gpio_mock = mocker.patch('core.hardware.drivers.buzzer.GPIO', autospec=True)
    gpio_mock.PWM.return_value = pwm_instance
    return gpio_mock, pwm_instance

@pytest.fixture
async def buzzer(mock_gpio):
    """Provides an initialized BuzzerController with mocked GPIO."""
    from core.hardware.drivers.buzzer import BuzzerController
    b = BuzzerController(gpio_pin=17)
    # The mock_gpio fixture ensures that RPi.GPIO is patched before this runs
    await b.initialize()
    return b

# The test class has been removed. Tests are now standalone functions.
# This is a more common and simpler pattern for pytest that avoids self/fixture issues.

async def test_initialization(mock_gpio):
    """Test that GPIO and PWM are set up correctly on initialization."""
    from core.hardware.drivers.buzzer import BuzzerController
    gpio_mock, pwm_instance = mock_gpio

    b = BuzzerController(gpio_pin=17)
    await b.initialize()

    gpio_mock.setmode.assert_called_once_with(gpio_mock.BCM)
    gpio_mock.setup.assert_called_once_with(17, gpio_mock.OUT)
    gpio_mock.PWM.assert_called_once_with(17, 1000)
    pwm_instance.start.assert_called_once_with(0)

async def test_play_tone(buzzer, mock_gpio):
    """Test that playing a tone sets frequency and duty cycle."""
    _, pwm_instance = mock_gpio
    await buzzer.play_tone(440, duration=0.01, volume=0.5)

    pwm_instance.ChangeFrequency.assert_called_with(440)
    # Check that duty cycle was set to 25.0 (50% of 50) and then back to 0
    pwm_instance.ChangeDutyCycle.assert_any_call(25.0)
    pwm_instance.ChangeDutyCycle.assert_called_with(0)

async def test_play_note(buzzer, mock_gpio):
    """Test that a musical note is converted to the correct frequency."""
    _, pwm_instance = mock_gpio
    await buzzer.play_note('A4', duration=0.01)
    pwm_instance.ChangeFrequency.assert_called_with(440.00)

async def test_invalid_note_raises_error(buzzer):
    """Test that an unknown note raises a ValueError."""
    with pytest.raises(ValueError, match="Unknown note: Z9"):
        await buzzer.play_note('Z9')

async def test_rest_note_is_silent(buzzer, mock_gpio):
    """Test that the REST note does not trigger the PWM."""
    _, pwm_instance = mock_gpio
    pwm_instance.ChangeFrequency.reset_mock()
    await buzzer.play_note('REST', duration=0.01)
    pwm_instance.ChangeFrequency.assert_not_called()

async def test_play_melody(buzzer, mock_gpio):
    """Test that a melody plays a sequence of tones."""
    _, pwm_instance = mock_gpio
    pwm_instance.ChangeFrequency.reset_mock()
    melody = [('C5', 0.01), ('G4', 0.01)]
    await buzzer.play_melody(melody)
    assert pwm_instance.ChangeFrequency.call_count == 2

async def test_frequency_out_of_bounds_raises_error(buzzer):
    """Test that frequencies outside the valid range raise ValueError."""
    with pytest.raises(ValueError, match="Frequency must be"):
        await buzzer.play_tone(10)
    with pytest.raises(ValueError, match="Frequency must be"):
        await buzzer.play_tone(30000)

async def test_volume_control(buzzer, mock_gpio):
    """Test that volume correctly maps to duty cycle."""
    _, pwm_instance = mock_gpio
    await buzzer.play_tone(1000, duration=0.01, volume=1.0)
    pwm_instance.ChangeDutyCycle.assert_any_call(50.0)
    await buzzer.play_tone(1000, duration=0.01, volume=0.1)
    pwm_instance.ChangeDutyCycle.assert_any_call(5.0)

async def test_beep_sequence(buzzer, mock_gpio):
    """Test that beep plays the correct number of tones."""
    _, pwm_instance = mock_gpio
    pwm_instance.ChangeFrequency.reset_mock()
    await buzzer.beep(count=3, duration=0.01, gap=0.01)
    assert pwm_instance.ChangeFrequency.call_count == 3

async def test_stop_method(buzzer, mock_gpio):
    """Test that the stop method immediately silences the buzzer."""
    _, pwm_instance = mock_gpio
    buzzer.stop()
    pwm_instance.ChangeDutyCycle.assert_called_once_with(0)

async def test_cleanup(buzzer, mock_gpio):
    """Test that cleanup stops PWM and cleans up GPIO."""
    gpio_mock, pwm_instance = mock_gpio
    await buzzer.cleanup()
    pwm_instance.stop.assert_called_once()
    gpio_mock.cleanup.assert_called_once_with(buzzer.gpio_pin)
    assert not buzzer._initialized

async def test_runtime_error_if_not_initialized(mocker):
    """
    Test that BuzzerController raises RuntimeError if RPi.GPIO is not found,
    and that other methods raise RuntimeError if initialize() has not been awaited.
    """
    from core.hardware.drivers.buzzer import BuzzerController

    # 1. Test for RuntimeError during __init__ if GPIO is missing
    mocker.patch('core.hardware.drivers.buzzer.GPIO', None)
    with pytest.raises(RuntimeError, match="RPi.GPIO library not found"):
        BuzzerController()

    # 2. Test for RuntimeError if a method is called before initialize()
    # We need to mock GPIO back in for this part of the test
    mocker.patch('core.hardware.drivers.buzzer.GPIO', Mock())
    b = BuzzerController()
    # b._initialized is False here
    with pytest.raises(RuntimeError, match="Buzzer not initialized"):
        await b.play_tone(440)
