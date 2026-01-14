import logging
from typing import Dict, Any, Optional, List
from tachikoma.core.hardware.interfaces.base import IHardwareComponent, HardwareStatus
from tachikoma.core.hardware.drivers.pca9685 import PCA9685


class ServoController(IHardwareComponent):
    """Contrôleur pour les servomoteurs via PCA9685"""
    
    def __init__(self, pwm_driver: Optional[PCA9685] = None):
        self.pwm = pwm_driver
        self.logger = logging.getLogger(__name__)
        self._status = HardwareStatus.UNINITIALIZED
        
        # Limites par défaut (en microsecondes)
        self.servo_min = 500
        self.servo_max = 2500
        
        # Positions actuelles des servos
        self._positions: Dict[int, float] = {}
    
    async def initialize(self) -> bool:
        try:
            self._status = HardwareStatus.INITIALIZING
            
            if not self.pwm:
                self.pwm = PCA9685()
                await self.pwm.initialize()
            
            if not self.pwm.is_available():
                raise Exception("PWM driver not available")
            
            # Initialiser tous les servos à position neutre
            for i in range(16):
                self.set_angle(i, 90)
            
            self._status = HardwareStatus.READY
            self.logger.info("Servo controller initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize servo controller: {e}")
            self._status = HardwareStatus.ERROR
            return False
    
    async def cleanup(self) -> None:
        try:
            # Retour position neutre
            for i in range(16):
                self.set_angle(i, 90)
            
            if self.pwm:
                await self.pwm.cleanup()
            
            self._status = HardwareStatus.DISCONNECTED
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def set_angle(self, channel: int, angle: float) -> bool:
        try:
            # Limiter l'angle
            angle = max(0, min(180, angle))
            
            # Convertir angle en pulse (500-2500µs)
            pulse = self.servo_min + (angle / 180.0) * (self.servo_max - self.servo_min)
            
            self.pwm.set_servo_pulse(channel, int(pulse))
            self._positions[channel] = angle
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to set servo {channel} angle: {e}")
            return False
    
    def set_pulse(self, channel: int, pulse: int) -> bool:
        try:
            self.pwm.set_servo_pulse(channel, pulse)
            return True
        except Exception as e:
            self.logger.error(f"Failed to set servo {channel} pulse: {e}")
            return False
    
    def get_angle(self, channel: int) -> Optional[float]:
        return self._positions.get(channel)
    
    def is_available(self) -> bool:
        return self._status == HardwareStatus.READY and self.pwm and self.pwm.is_available()
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "type": "servo_controller",
            "status": self._status.value,
            "available": self.is_available(),
            "servo_count": 16,
            "positions": self._positions
        }
    
    def get_health(self) -> Dict[str, Any]:
        return {
            "healthy": self.is_available(),
            "pwm_status": self.pwm.get_status() if self.pwm else None,
            "active_servos": len(self._positions)
        }
