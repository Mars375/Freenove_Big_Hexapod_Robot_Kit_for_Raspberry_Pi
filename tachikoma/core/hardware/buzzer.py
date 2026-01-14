"""Buzzer control abstraction"""
import structlog
import asyncio

from tachikoma.core.exceptions import HardwareNotAvailableError, CommandExecutionError
from tachikoma.core.hardware.drivers.buzzer import Buzzer

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

    async def on(self) -> bool:
        """Turn buzzer ON indefinitely."""
        await self._ensure_hardware()
        try:
            await self._buzzer.on()
            return True
        except Exception as e:
            logger.error("buzzer_controller.on_failed", error=str(e))
            return False

    async def off(self) -> bool:
        """Turn buzzer OFF."""
        if self._initialized:
            try:
                await self._buzzer.off()
                return True
            except Exception as e:
                logger.error("buzzer_controller.off_failed", error=str(e))
                return False
        return True

    async def beep(self, duration: float, frequency: int = 1000) -> bool:
        """Activate buzzer
        
        Args:
            duration: Duration in seconds
            frequency: Ignored for active buzzer
        """
        await self._ensure_hardware()

        try:
            await self._buzzer.beep(duration)
            logger.info("buzzer_controller.beep", dur=duration)
            return True
        except Exception as e:
            logger.error("buzzer_controller.beep_failed", error=str(e))
            raise CommandExecutionError(f"Buzzer beep failed: {e}")

