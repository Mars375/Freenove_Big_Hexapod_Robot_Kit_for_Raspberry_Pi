"""Buzzer control abstraction"""
import structlog
import asyncio

from core.exceptions import HardwareNotAvailableError, CommandExecutionError
from core.hardware.drivers.buzzer import Buzzer

logger = structlog.get_logger()


class BuzzerController:
    """Abstraction for buzzer control"""

    def __init__(self):
        self._buzzer = Buzzer(pin=17) # Default pin, adjust if needed
        self._initialized = False

    async def _ensure_hardware(self):
        if not self._initialized:
            await self._buzzer.initialize()
            self._initialized = True

    @property
    def is_available(self) -> bool:
        return self._initialized

    async def beep(self, frequency: int, duration: float) -> bool:
        """Activate buzzer
        
        Args:
            frequency: Ignored for active buzzer
            duration: Duration in seconds
        """
        await self._ensure_hardware()

        try:
            await self._buzzer.beep(duration)
            logger.info("buzzer_controller.beep", dur=duration)
            return True
        except Exception as e:
            logger.error("buzzer_controller.beep_failed", error=str(e))
            raise CommandExecutionError(f"Buzzer beep failed: {e}")


