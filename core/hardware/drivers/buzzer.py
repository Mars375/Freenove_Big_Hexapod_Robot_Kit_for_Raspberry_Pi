"""Buzzer Driver using RPi.GPIO."""
import asyncio
import structlog
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

logger = structlog.get_logger()

class Buzzer:
    """Driver pour buzzer actif/passif sur GPIO."""
    
    def __init__(self, pin: int = 17):
        """Initialise le buzzer.
        
        Args:
            pin: Numéro de pin BCM (défaut 17, à vérifier)
        """
        self.pin = pin
        self._available = False
        
    async def initialize(self):
        """Initialise le GPIO."""
        if GPIO:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.pin, GPIO.OUT)
                GPIO.output(self.pin, GPIO.LOW)
                self._available = True
                logger.info(f"Buzzer initialized on pin {self.pin}")
            except Exception as e:
                logger.error(f"Failed to init buzzer GPIO: {e}")
                self._available = False
        else:
            logger.warning("RPi.GPIO not found, buzzer disabled")
            
    async def beep(self, duration: float):
        """Emet un bip."""
        if not self._available:
            return
            
        try:
            GPIO.output(self.pin, GPIO.HIGH)
            await asyncio.sleep(duration)
            GPIO.output(self.pin, GPIO.LOW)
        except Exception as e:
            logger.error(f"Beep failed: {e}")
            
    async def cleanup(self):
        if self._available:
            GPIO.cleanup(self.pin)
