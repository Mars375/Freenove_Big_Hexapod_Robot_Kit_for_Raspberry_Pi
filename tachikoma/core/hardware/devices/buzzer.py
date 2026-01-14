import logging
import time
from typing import Dict, Any
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


class Buzzer(IHardwareComponent):
    """Contrôleur pour buzzer piezo"""
    
    def __init__(self, pin: int = 17):
        self.pin = pin
        self.logger = logging.getLogger(__name__)
        self._status = HardwareStatus.UNINITIALIZED
        self._pwm = None
    
    async def initialize(self) -> bool:
        if not GPIO_AVAILABLE:
            self.logger.error("RPi.GPIO not available")
            self._status = HardwareStatus.ERROR
            return False
        
        try:
            self._status = HardwareStatus.INITIALIZING
            
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.pin, GPIO.OUT)
            
            # Create PWM instance at 1000Hz
            self._pwm = GPIO.PWM(self.pin, 1000)
            
            self._status = HardwareStatus.READY
            self.logger.info(f"Buzzer initialized on pin {self.pin}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize buzzer: {e}")
            self._status = HardwareStatus.ERROR
            return False
    
    async def cleanup(self) -> None:
        try:
            self.stop()
            if self._pwm:
                self._pwm.stop()
            GPIO.cleanup([self.pin])
            self._status = HardwareStatus.DISCONNECTED
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def beep(self, frequency: int = 1000, duration: float = 0.1) -> bool:
        if not self.is_available():
            return False
        
        try:
            self._pwm.ChangeFrequency(frequency)
            self._pwm.start(50)  # 50% duty cycle
            time.sleep(duration)
            self._pwm.stop()
            return True
        except Exception as e:
            self.logger.error(f"Failed to beep: {e}")
            return False
    
    def play_tone(self, frequency: int, duty_cycle: int = 50) -> bool:
        if not self.is_available():
            return False
        
        try:
            self._pwm.ChangeFrequency(frequency)
            self._pwm.ChangeDutyCycle(duty_cycle)
            self._pwm.start(duty_cycle)
            return True
        except Exception as e:
            self.logger.error(f"Failed to play tone: {e}")
            return False
    
    def stop(self) -> bool:
        if not self.is_available():
            return False
        
        try:
            self._pwm.stop()
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop buzzer: {e}")
            return False
    
    def play_melody(self, notes: list, tempo: float = 0.5) -> bool:
        if not self.is_available():
            return False
        
        try:
            for note in notes:
                if note > 0:
                    self.beep(note, tempo)
                else:
                    time.sleep(tempo)
            return True
        except Exception as e:
            self.logger.error(f"Failed to play melody: {e}")
            return False
    
    def is_available(self) -> bool:
        return GPIO_AVAILABLE and self._status == HardwareStatus.READY
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "type": "buzzer",
            "pin": self.pin,
            "status": self._status.value,
            "available": self.is_available()
        }
    
    def get_health(self) -> Dict[str, Any]:
        return {
            "healthy": self.is_available(),
            "status": self._status.value
        }
