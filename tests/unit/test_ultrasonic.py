"""Tests for ultrasonic sensor."""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

@pytest.fixture
def mock_gpio(mocker):
    """Mocks RPi.GPIO."""
    gpio_mock = mocker.patch('core.hardware.drivers.ultrasonic.GPIO', autospec=True)
    return gpio_mock

@pytest.fixture
async def sensor(mock_gpio):
    """Provides an initialized UltrasonicSensor with mocked GPIO."""
    from core.hardware.drivers.ultrasonic import UltrasonicSensor
    s = UltrasonicSensor(trigger_pin=16, echo_pin=18)
    await s.initialize()
    return s

async def test_initialization(mock_gpio):
    """Sensor initializes GPIO correctly."""
    from core.hardware.drivers.ultrasonic import UltrasonicSensor
    s = UltrasonicSensor(trigger_pin=16, echo_pin=18)
    await s.initialize()

    mock_gpio.setmode.assert_called_with(mock_gpio.BCM)
    mock_gpio.setup.assert_any_call(16, mock_gpio.OUT)
    mock_gpio.setup.assert_any_call(18, mock_gpio.IN)
    mock_gpio.output.assert_called_with(16, mock_gpio.LOW)

async def test_measure_distance(sensor, mock_gpio):
    """Distance measurement returns correct value."""
    pulse_duration = (10 * 2) / sensor.SPEED_OF_SOUND

    with patch('time.time') as mock_time:
        mock_time.side_effect = [0.0, 0.0, 0.1, 0.1, 0.1 + pulse_duration]
        mock_gpio.input.side_effect = [mock_gpio.LOW, mock_gpio.HIGH, mock_gpio.HIGH, mock_gpio.LOW]

        distance = await sensor.measure_distance()
        assert distance is not None
        assert 9.9 < distance < 10.1

async def test_trigger_pulse_sent(sensor, mock_gpio):
    """Trigger sends a 10µs pulse."""
    with patch('time.time', side_effect=[0.0, 0.0, 0.1, 0.1, 0.2]):
        mock_gpio.input.side_effect = [mock_gpio.LOW, mock_gpio.HIGH, mock_gpio.HIGH, mock_gpio.LOW]
        await sensor.measure_distance()

    mock_gpio.output.assert_any_call(16, mock_gpio.HIGH)
    mock_gpio.output.assert_any_call(16, mock_gpio.LOW)

async def test_timeout_returns_none(sensor, mock_gpio):
    """Timeout waiting for echo returns None."""
    with patch('time.time') as mock_time:
        mock_time.side_effect = [0.0, 0.05, 0.1, 0.15, sensor.TIMEOUT_SECONDS + 0.2]
        mock_gpio.input.return_value = mock_gpio.LOW

        distance = await sensor.measure_distance()
        assert distance is None

async def test_out_of_range_returns_none(sensor, mock_gpio):
    """Measurement outside of the valid range (2-400cm) returns None."""
    pulse_duration_too_long = (500 * 2) / sensor.SPEED_OF_SOUND
    with patch('time.time') as mock_time:
        mock_time.side_effect = [0.0, 0.0, 0.1, 0.1, 0.1 + pulse_duration_too_long]
        mock_gpio.input.side_effect = [mock_gpio.LOW, mock_gpio.HIGH, mock_gpio.HIGH, mock_gpio.LOW]

        distance = await sensor.measure_distance()
        assert distance is None

async def test_averaging_multiple_samples(sensor):
    """Multiple samples are correctly averaged by mocking _single_measurement."""
    with patch.object(sensor, '_single_measurement', new=AsyncMock(side_effect=[10.0, 12.0])) as mock_measure:
        distance = await sensor.measure_distance(samples=2)
        assert distance is not None
        assert 10.9 < distance < 11.1
        assert mock_measure.call_count == 2

async def test_obstacle_detection(sensor):
    """Obstacle detection works based on a distance threshold."""
    with patch.object(sensor, 'measure_distance', new=AsyncMock(return_value=15.0)):
        assert await sensor.is_obstacle_detected(threshold_cm=20.0) is True
        assert await sensor.is_obstacle_detected(threshold_cm=10.0) is False

async def test_initialization_fails_if_gpio_missing(mocker):
    """Test that __init__ raises RuntimeError if RPi.GPIO is not found."""
    mocker.patch('core.hardware.drivers.ultrasonic.GPIO', None)
    from core.hardware.drivers.ultrasonic import UltrasonicSensor
    with pytest.raises(RuntimeError, match="RPi.GPIO library not found"):
        UltrasonicSensor()

async def test_not_initialized_raises_error(mock_gpio):
    """Test that methods raise RuntimeError if initialize() has not been awaited."""
    from core.hardware.drivers.ultrasonic import UltrasonicSensor
    s = UltrasonicSensor()
    with pytest.raises(RuntimeError, match="Ultrasonic sensor not initialized"):
        await s.measure_distance()

async def test_failed_measurement_returns_none(sensor):
    """If all measurement samples fail, the result should be None."""
    with patch.object(sensor, '_single_measurement', new=AsyncMock(return_value=None)):
        distance = await sensor.measure_distance(samples=3)
        assert distance is None

async def test_continuous_monitoring(sensor):
    """Test the continuous monitoring callback functionality."""
    results = []
    async def callback(distance):
        results.append(distance)
        if len(results) >= 2:
            raise asyncio.CancelledError

    with patch.object(sensor, 'measure_distance', new=AsyncMock(side_effect=[10.0, 11.0, 12.0])):
        try:
            await sensor.continuous_monitoring(callback, interval=0.01)
        except asyncio.CancelledError:
            pass

    assert results == [10.0, 11.0]
