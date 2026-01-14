"""Tests for ultrasonic sensor."""
import pytest
import asyncio
from unittest.mock import Mock, patch

# Mock the RPi.GPIO library before importing the UltrasonicSensor
import sys
mock_gpio = Mock()
sys.modules['RPi.GPIO'] = mock_gpio

from core.hardware.drivers.ultrasonic import UltrasonicSensor


class TestUltrasonicSensor:
    """Test HC-SR04 ultrasonic sensor."""

    @pytest.fixture
    def sensor(self):
        """Initialize sensor with a mocked GPIO."""
        sensor = UltrasonicSensor(trigger_pin=16, echo_pin=18)
        # We don't initialize here to test initialization separately
        return sensor

    async def test_initialization(self, sensor):
        """Sensor initializes GPIO correctly."""
        await sensor.initialize()
        mock_gpio.setmode.assert_called_with(mock_gpio.BCM)
        mock_gpio.setup.assert_any_call(16, mock_gpio.OUT)
        mock_gpio.setup.assert_any_call(18, mock_gpio.IN)
        mock_gpio.output.assert_called_with(16, mock_gpio.LOW)

    async def test_measure_distance(self, sensor):
        """Distance measurement returns correct value."""
        await sensor.initialize()

        # Simulate a 10cm distance measurement
        pulse_duration = (10 * 2) / sensor.SPEED_OF_SOUND # ~0.000583s

        with patch('time.time') as mock_time:
            # Sequence of time values for a successful measurement
            mock_time.side_effect = [
                0.0,      # Call at the beginning
                0.001,    # Echo HIGH start time
                0.001 + pulse_duration # Echo LOW end time
            ]

            # Simulate GPIO input sequence
            mock_gpio.input.side_effect = [
                mock_gpio.LOW,  # Waiting for echo to go high
                mock_gpio.HIGH, # Pulse starts
                mock_gpio.LOW   # Pulse ends
            ]

            distance = await sensor.measure_distance()

            assert distance is not None
            assert 9.9 < distance < 10.1

    async def test_trigger_pulse_sent(self, sensor):
        """Trigger sends 10µs pulse."""
        await sensor.initialize()
        # Mock a successful measurement to ensure the trigger logic runs
        with patch('time.time', side_effect=[0.0, 0.1, 0.2]):
            mock_gpio.input.side_effect = [mock_gpio.LOW, mock_gpio.HIGH, mock_gpio.LOW]
            await sensor.measure_distance()

        # Check for HIGH then LOW pulse on trigger pin
        mock_gpio.output.assert_any_call(16, mock_gpio.HIGH)
        mock_gpio.output.assert_any_call(16, mock_gpio.LOW)

    async def test_timeout_returns_none(self, sensor):
        """Timeout waiting for echo to go HIGH returns None."""
        await sensor.initialize()
        with patch('time.time') as mock_time:
            # Simulate time advancing beyond the timeout
            mock_time.side_effect = [0.0, sensor.TIMEOUT_SECONDS + 0.1]
            mock_gpio.input.return_value = mock_gpio.LOW

            distance = await sensor.measure_distance()
            assert distance is None

    async def test_out_of_range_returns_none(self, sensor):
        """Out of range measurement returns None."""
        await sensor.initialize()
        # Simulate a 500cm distance (out of range)
        pulse_duration = (500 * 2) / sensor.SPEED_OF_SOUND
        with patch('time.time', side_effect=[0.0, 0.1, 0.1 + pulse_duration]):
            mock_gpio.input.side_effect = [mock_gpio.LOW, mock_gpio.HIGH, mock_gpio.LOW]
            distance = await sensor.measure_distance()
            assert distance is None

    async def test_averaging_multiple_samples(self, sensor):
        """Multiple samples are averaged correctly."""
        await sensor.initialize()

        pulse_10cm = (10 * 2) / sensor.SPEED_OF_SOUND
        pulse_12cm = (12 * 2) / sensor.SPEED_OF_SOUND

        with patch('time.time') as mock_time:
            mock_time.side_effect = [
                0.0, 0.1, 0.1 + pulse_10cm,  # First sample (10cm)
                0.2, 0.3, 0.3 + pulse_12cm,  # Second sample (12cm)
            ]

        mock_gpio.input.side_effect = [
            mock_gpio.LOW, mock_gpio.HIGH, mock_gpio.LOW, # Sample 1
            mock_gpio.LOW, mock_gpio.HIGH, mock_gpio.LOW, # Sample 2
        ]

        distance = await sensor.measure_distance(samples=2)
        assert 10.9 < distance < 11.1 # Average of 10 and 12 is 11

    async def test_obstacle_detection(self, sensor):
        """Obstacle is detected within the threshold."""
        await sensor.initialize()
        with patch.object(sensor, '_single_measurement', new=AsyncMock(return_value=10.0)):
            is_detected = await sensor.is_obstacle_detected(threshold_cm=30.0)
            assert is_detected is True

            is_detected = await sensor.is_obstacle_detected(threshold_cm=5.0)
            assert is_detected is False

    async def test_not_initialized_raises(self, sensor):
        """Test that RuntimeError is raised if not initialized."""
        with pytest.raises(RuntimeError, match="Ultrasonic sensor not initialized"):
            await sensor.measure_distance()
