import logging
import time
from typing import Optional, Dict, Any
from tachikoma.core.config import settings
from tachikoma.core.hardware.interfaces.base import IHardwareComponent, HardwareStatus

if not settings.MOCK_HARDWARE:
    try:
        import RPi.GPIO as GPIO
        GPIO_AVAILABLE = True
    except ImportError:
        GPIO_AVAILABLE = False
else:
    GPIO = None
    GPIO_AVAILABLE = False


class UltrasonicSensor(IHardwareComponent):
    """Capteur de distance ultrasonique HC-SR04"""
    
    def __init__(self, trigger_pin: int = 27, echo_pin: int = 22):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.logger = logging.getLogger(__name__)
        self._status = HardwareStatus.UNINITIALIZED
        self._last_distance: Optional[float] = None
    
    async def initialize(self) -> bool:
        if not GPIO_AVAILABLE:
            self.logger.error("RPi.GPIO not available")
            self._status = HardwareStatus.ERROR
            return False
        
        try:
            self._status = HardwareStatus.INITIALIZING
            
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            GPIO.setup(self.trigger_pin, GPIO.OUT)
            GPIO.setup(self.echo_pin, GPIO.IN)
            
            # Initial state
            GPIO.output(self.trigger_pin, GPIO.LOW)
            time.sleep(0.1)
            
            self._status = HardwareStatus.READY
            self.logger.info(f"Ultrasonic sensor initialized (trigger={self.trigger_pin}, echo={self.echo_pin})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ultrasonic sensor: {e}")
            self._status = HardwareStatus.ERROR
            return False
    
    async def cleanup(self) -> None:
        try:
            GPIO.output(self.trigger_pin, GPIO.LOW)
            GPIO.cleanup([self.trigger_pin, self.echo_pin])
            self._status = HardwareStatus.DISCONNECTED
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def get_distance(self, timeout: float = 0.5) -> Optional[float]:
        if not self.is_available():
            return None
        
        try:
            # Send trigger pulse
            GPIO.output(self.trigger_pin, GPIO.HIGH)
            time.sleep(0.00001)  # 10µs pulse
            GPIO.output(self.trigger_pin, GPIO.LOW)
            
            # Wait for echo
            start_time = time.time()
            pulse_start = start_time
            pulse_end = start_time
            
            # Wait for echo start
            while GPIO.input(self.echo_pin) == GPIO.LOW:
                pulse_start = time.time()
                if pulse_start - start_time > timeout:
                    return None
            
            # Wait for echo end
            while GPIO.input(self.echo_pin) == GPIO.HIGH:
                pulse_end = time.time()
                if pulse_end - start_time > timeout:
                    return None
            
            # Calculate distance
            pulse_duration = pulse_end - pulse_start
            distance = (pulse_duration * 34300) / 2  # cm
            
            # Filter invalid readings
            if 2 <= distance <= 400:
                self._last_distance = distance
                return distance
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to read distance: {e}")
            return None
    
    def is_available(self) -> bool:
        return GPIO_AVAILABLE and self._status == HardwareStatus.READY
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "type": "ultrasonic",
            "trigger_pin": self.trigger_pin,
            "echo_pin": self.echo_pin,
            "status": self._status.value,
            "available": self.is_available(),
            "last_distance": self._last_distance
        }
    
    def get_health(self) -> Dict[str, Any]:
        return {
            "healthy": self.is_available(),
            "last_reading": self._last_distance is not None,
            "status": self._status.value
        }
