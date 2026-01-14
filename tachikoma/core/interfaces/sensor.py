"""
Abstract interface for providing sensor data.
"""

from abc import ABC, abstractmethod
from tachikoma.core.types import SensorState


class SensorProvider(ABC):
    """
    Defines the contract for a provider of aggregated sensor data.

    Implementations of this class are responsible for reading from one or more
    physical sensors and returning their state in a structured format.
    """

    @abstractmethod
    def read(self) -> SensorState:
        """
        Performs an instantaneous read of all associated sensors.

        Returns:
            A SensorState object containing the latest sensor data.
        """
        pass

    @abstractmethod
    def health(self) -> bool:
        """
        Checks the health and connectivity of the sensors.

        Returns:
            True if all sensors are responsive and healthy, False otherwise.
        """
        pass
