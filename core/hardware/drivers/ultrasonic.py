"""Ultrasonic sensor driver using gpiozero."""
import asyncio
from typing import Dict, Any, Optional
import structlog
from gpiozero import DistanceSensor, BadPinFactory
from core.hardware.interfaces.base import IHardwareComponent, HardwareStatus

logger = structlog.get_logger()


class UltrasonicSensor(IHardwareComponent):
    """Driver for HC-SR04 ultrasonic distance sensor.
    
    Uses gpiozero for hardware abstraction.
    Pins: Trigger=27, Echo=22 (default for Freenove Hexapod)
    """
    
    def __init__(
        self,
        trigger_pin: int = 27,
        echo_pin: int = 22,
        max_distance: float = 3.0
    ):
        """Initialize ultrasonic sensor.
        
        Args:
            trigger_pin: GPIO pin for trigger pulse
            echo_pin: GPIO pin for echo reception
            max_distance: Maximum distance to measure in meters
        """
        self._trigger = trigger_pin
        self._echo = echo_pin
        self._max_dist = max_distance
        self._sensor: Optional[DistanceSensor] = None
        self._status = HardwareStatus.UNINITIALIZED
    
    async def initialize(self) -> bool:
        """Initialize the sensor hardware."""
        try:
            self._status = HardwareStatus.INITIALIZING
            logger.info(
                "ultrasonic.initializing",
                trigger=self._trigger,
                echo=self._echo
            )
            
            # Initialize gpiozero sensor
            # Run in executor to avoid blocking if pin factory is slow
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._init_device)
            
            self._status = HardwareStatus.READY
            return True
            
        except ImportError:
            logger.error("ultrasonic.import_error", error="gpiozero not installed")
            self._status = HardwareStatus.ERROR
            return False
        except Exception as e:
            logger.error("ultrasonic.init_failed", error=str(e))
            self._status = HardwareStatus.ERROR
            return False

    def _init_device(self):
        """Internal synchronous initialization."""
        try:
            self._sensor = DistanceSensor(
                echo=self._echo,
                trigger=self._trigger,
                max_distance=self._max_dist
            )
        except BadPinFactory:
            # Fallback for non-Pi environments
            logger.warning("ultrasonic.gpio_fallback", msg="Using MockPinFactory")
            from gpiozero.pins.mock import MockFactory
            from gpiozero import Device
            Device.pin_factory = MockFactory()
            self._sensor = DistanceSensor(
                echo=self._echo,
                trigger=self._trigger,
                max_distance=self._max_dist
            )

    async def get_distance(self) -> Optional[float]:
        """Get distance measurement in centimeters.
        
        Returns:
            Distance in cm, or None if measurement failed
        """
        if self._status != HardwareStatus.READY or not self._sensor:
            return None
            
        try:
            # gpiozero property access is synchronous but fast
            # We can run in executor if it proves blocking
            distance_m = self._sensor.distance
            
            # Convert m to cm and round
            return round(distance_m * 100, 1)
            
        except Exception as e:
            logger.warning("ultrasonic.read_failed", error=str(e))
            return None

    async def cleanup(self) -> None:
        """Release hardware resources."""
        if self._sensor:
            self._sensor.close()
            self._sensor = None
        self._status = HardwareStatus.UNINITIALIZED

    def is_available(self) -> bool:
        return self._status == HardwareStatus.READY

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": self._status.value,
            "trigger_pin": self._trigger,
            "echo_pin": self._echo,
            "max_distance": self._max_dist
        }

    def get_health(self) -> Dict[str, Any]:
        """Return component health status."""
        return {
            "healthy": self._status == HardwareStatus.READY,
            "error": None if self._status == HardwareStatus.READY else "Sensor not ready",
            "connected": self._sensor is not None
        }