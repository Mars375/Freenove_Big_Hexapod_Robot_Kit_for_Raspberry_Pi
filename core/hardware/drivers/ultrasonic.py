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
        """Internal synchronous initialization with factory fallback."""
        try:
            self._sensor = DistanceSensor(
                echo=self._echo,
                trigger=self._trigger,
                max_distance=self._max_dist
            )
        except (BadPinFactory, Exception) as e:
            logger.warning("ultrasonic.gpio_issue", error=str(e))
            
            # Try to force a factory if default fails
            try:
                from gpiozero import Device
                # List of factories to try in order of preference
                for factory_name in ['lgpio', 'rpigpio', 'pigpio', 'native']:
                    try:
                        if factory_name == 'lgpio':
                            from gpiozero.pins.lgpio import LGPIOFactory
                            Device.pin_factory = LGPIOFactory()
                        elif factory_name == 'rpigpio':
                            from gpiozero.pins.rpigpio import RPiGPIOFactory
                            Device.pin_factory = RPiGPIOFactory()
                        elif factory_name == 'pigpio':
                            from gpiozero.pins.pigpio import PiGPIOFactory
                            Device.pin_factory = PiGPIOFactory()
                        
                        logger.info("ultrasonic.factory_switch", factory=factory_name)
                        self._sensor = DistanceSensor(
                            echo=self._echo,
                            trigger=self._trigger,
                            max_distance=self._max_dist
                        )
                        return # Success
                    except (ImportError, Exception):
                        continue
                
                # Ultimate fallback to Mock
                logger.warning(
                    "ultrasonic.mock_fallback", 
                    msg="All hardware factories failed. On Pi 4/5 with Python 3.13+, you MUST install 'lgpio' (e.g., sudo apt install python3-lgpio)."
                )
                from gpiozero.pins.mock import MockFactory
                Device.pin_factory = MockFactory()
                self._sensor = DistanceSensor(
                    echo=self._echo,
                    trigger=self._trigger,
                    max_distance=self._max_dist
                )
            except Exception as final_e:
                logger.error("ultrasonic.final_init_failed", error=str(final_e))
                raise

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