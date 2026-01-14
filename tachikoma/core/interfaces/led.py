"""
Abstract interface for controlling the robot's LEDs.
"""

from abc import ABC, abstractmethod
from tachikoma.core.types import LedMode


class LedController(ABC):
    """
    Defines the contract for controlling the robot's LEDs.

    This interface provides a simple, high-level API for managing LED color,
    mode, and brightness, abstracting the specific hardware driver.
    """

    @abstractmethod
    def set_color(self, r: int, g: int, b: int) -> None:
        """
        Sets the color of the LEDs.

        Args:
            r: Red component (0-255).
            g: Green component (0-255).
            b: Blue component (0-255).
        """
        pass

    @abstractmethod
    def set_mode(self, mode: LedMode) -> None:
        """
        Sets the operating mode of the LEDs (e.g., solid, rainbow).

        Args:
            mode: The desired LED mode.
        """
        pass

    @abstractmethod
    def set_brightness(self, level: int) -> None:
        """
        Sets the brightness of the LEDs.

        Args:
            level: The brightness level (implementation-specific range).
        """
        pass
