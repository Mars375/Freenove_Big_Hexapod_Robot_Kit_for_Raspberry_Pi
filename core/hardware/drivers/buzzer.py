"""Buzzer Driver using gpiozero."""
import asyncio
import structlog
try:
    from gpiozero import Buzzer as GpioBuzzer
    HAS_GPIOZERO = True
except ImportError:
    HAS_GPIOZERO = False

logger = structlog.get_logger()

class Buzzer:
    """Driver pour buzzer actif sur GPIO."""
    
    def __init__(self, pin: int = 17):
        """Initialise le buzzer.
        
        Args:
            pin: Numéro de pin BCM (défaut 17)
        """
        self.pin = pin
        self._buzzer = None
        self._available = False
        
    async def initialize(self):
        """Initialise le buzzer via gpiozero."""
        if HAS_GPIOZERO:
            try:
                self._buzzer = GpioBuzzer(self.pin, active_high=True)
                self._available = True
                logger.info("buzzer.initialized", pin=self.pin)
            except Exception as e:
                logger.error("buzzer.init_failed", error=str(e))
                self._available = False
        else:
            logger.warning("gpiozero not found, buzzer disabled")
            
    async def beep(self, duration: float):
        """Emet un bip."""
        if not self._available or not self._buzzer:
            return
            
        try:
            self._buzzer.on()
            await asyncio.sleep(duration)
            self._buzzer.off()
        except Exception as e:
            logger.error("buzzer.beep_failed", error=str(e))
            
    async def on(self):
        """Active le buzzer."""
        if self._available and self._buzzer:
            self._buzzer.on()

    async def off(self):
        """Désactive le buzzer."""
        if self._available and self._buzzer:
            self._buzzer.off()
            
    async def cleanup(self):
        if self._buzzer:
            self._buzzer.close()
