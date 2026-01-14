"""
HC-SR04 Ultrasonic distance sensor driver.
"""
import asyncio
import time
from typing import Optional

try:
    import RPi.GPIO as GPIO
except (RuntimeError, ModuleNotFoundError):
    GPIO = None


class UltrasonicSensor:
    """
    HC-SR04 ultrasonic distance sensor.

    Hardware:
        - Trigger GPIO (output): sends 10µs pulse
        - Echo GPIO (input): receives pulse duration
        - Range: 2cm - 400cm
        - Accuracy: ±3mm

    Measurement:
        1. Send 10µs trigger pulse
        2. Wait for echo HIGH
        3. Measure echo pulse width
        4. Distance = (pulse_width * speed_of_sound) / 2

    Speed of sound: 34300 cm/s at 20°C
    Formula: distance_cm = (pulse_duration_s * 34300) / 2

    Usage:
        >>> sensor = UltrasonicSensor(trigger_pin=16, echo_pin=18)
        >>> await sensor.initialize()
        >>> distance = await sensor.measure_distance()
        >>> print(f"Distance: {distance:.1f} cm")
    """

    SPEED_OF_SOUND = 34300  # cm/s at 20°C
    TIMEOUT_SECONDS = 0.1  # 100ms timeout (max ~17m)
    MIN_DISTANCE_CM = 2
    MAX_DISTANCE_CM = 400

    def __init__(self, trigger_pin: int = 16, echo_pin: int = 18):
        """
        Initialize ultrasonic sensor.

        Args:
            trigger_pin: GPIO pin for trigger (BCM mode)
            echo_pin: GPIO pin for echo (BCM mode)
        """
        if GPIO is None:
            raise RuntimeError("RPi.GPIO library not found. Cannot control hardware.")
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self._initialized: bool = False

    async def initialize(self) -> None:
        """Initialize GPIO pins."""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

        # Ensure trigger is LOW
        GPIO.output(self.trigger_pin, GPIO.LOW)
        await asyncio.sleep(0.1)  # Settle time

        self._initialized = True

    async def measure_distance(self, samples: int = 1) -> Optional[float]:
        """
        Measure distance in centimeters.

        Args:
            samples: Number of samples to average (reduces noise)

        Returns:
            Distance in cm, or None if measurement failed

        Raises:
            RuntimeError: If not initialized
        """
        if not self._initialized:
            raise RuntimeError("Ultrasonic sensor not initialized")

        measurements = []

        for _ in range(samples):
            distance = await self._single_measurement()
            if distance is not None:
                measurements.append(distance)

            # Small delay between samples
            if samples > 1:
                await asyncio.sleep(0.06)  # 60ms = min time between measurements

        if not measurements:
            return None

        # Return average
        return sum(measurements) / len(measurements)

    async def _single_measurement(self) -> Optional[float]:
        """
        Perform single distance measurement.

        Returns:
            Distance in cm, or None if timeout/error
        """
        # Send 10µs trigger pulse
        GPIO.output(self.trigger_pin, GPIO.HIGH)
        await asyncio.sleep(0.00001)  # 10µs
        GPIO.output(self.trigger_pin, GPIO.LOW)

        # Wait for echo to go HIGH (with timeout)
        start_time = time.time()
        timeout_time = start_time + self.TIMEOUT_SECONDS

        while GPIO.input(self.echo_pin) == GPIO.LOW:
            if time.time() > timeout_time:
                return None  # Timeout
            await asyncio.sleep(0)  # Yield to event loop

        pulse_start = time.time()

        # Wait for echo to go LOW (with timeout)
        timeout_time = pulse_start + self.TIMEOUT_SECONDS

        while GPIO.input(self.echo_pin) == GPIO.HIGH:
            if time.time() > timeout_time:
                return None  # Timeout
            await asyncio.sleep(0)

        pulse_end = time.time()

        # Calculate distance
        pulse_duration = pulse_end - pulse_start
        distance_cm = (pulse_duration * self.SPEED_OF_SOUND) / 2

        # Validate range
        if not (self.MIN_DISTANCE_CM <= distance_cm <= self.MAX_DISTANCE_CM):
            return None

        return distance_cm

    async def is_obstacle_detected(self, threshold_cm: float = 30.0) -> bool:
        """
        Check if obstacle is within threshold distance.

        Args:
            threshold_cm: Distance threshold in cm

        Returns:
            True if obstacle detected within threshold
        """
        distance = await self.measure_distance(samples=3)

        if distance is None:
            return False

        return distance <= threshold_cm

    async def continuous_monitoring(
        self,
        callback,
        interval: float = 0.1,
        samples: int = 3
    ) -> None:
        """
        Continuously monitor distance and call callback.

        Args:
            callback: Async function(distance_cm) called on each measurement
            interval: Time between measurements in seconds
            samples: Samples per measurement

        Example:
            >>> async def on_distance(dist):
            ...     print(f"Distance: {dist:.1f} cm")
            >>> await sensor.continuous_monitoring(on_distance, interval=0.5)
        """
        while True:
            distance = await self.measure_distance(samples=samples)

            if distance is not None:
                await callback(distance)

            await asyncio.sleep(interval)

    async def cleanup(self) -> None:
        """Cleanup GPIO resources."""
        GPIO.cleanup([self.trigger_pin, self.echo_pin])
        self._initialized = False