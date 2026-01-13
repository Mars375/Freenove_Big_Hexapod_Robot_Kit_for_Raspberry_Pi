"""Buzzer control abstraction"""
import sys
from pathlib import Path
import structlog
import asyncio

legacy_path = Path(__file__).parent.parent.parent / "legacy" / "Code" / "Server"
sys.path.insert(0, str(legacy_path))

from core.exceptions import HardwareNotAvailableError, CommandExecutionError

logger = structlog.get_logger()


class BuzzerController:
    """Abstraction for buzzer control"""

    def __init__(self):
        self._buzzer = None
        self._initialize_hardware()

    def _initialize_hardware(self):
        """Initialize legacy buzzer module"""
        try:
            from buzzer import Buzzer
            self._buzzer = Buzzer()
            logger.info("buzzer_controller.initialized")
        except Exception as e:
            logger.error("buzzer_controller.init_failed", error=str(e))
            self._buzzer = None

    @property
    def is_available(self) -> bool:
        return self._buzzer is not None

    async def beep(self, frequency: int, duration: float) -> bool:
        """Activate buzzer"""
        if not self.is_available:
            raise HardwareNotAvailableError("Buzzer controller not initialized")

        try:
            # Set buzzer ON
            self._buzzer.set_state(True)
            await asyncio.sleep(duration)
            # Turn off
            self._buzzer.set_state(False)

            logger.info("buzzer_controller.beep", dur=duration)
            return True
        except Exception as e:
            logger.error("buzzer_controller.beep_failed", error=str(e))
            raise CommandExecutionError(f"Buzzer beep failed: {e}")
