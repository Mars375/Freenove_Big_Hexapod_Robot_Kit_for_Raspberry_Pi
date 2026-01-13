from abc import ABC, abstractmethod
from typing import List
import logging

try:
    import smbus2
    SMBUS_AVAILABLE = True
except ImportError:
    SMBUS_AVAILABLE = False

logger = logging.getLogger(__name__)

class I2CInterface(ABC):
    """Abstract base class for I2C communication."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the I2C bus."""
        pass

    @abstractmethod
    async def write_byte_data(self, address: int, register: int, value: int) -> None:
        """Write a byte to a specific register."""
        pass

    @abstractmethod
    async def read_byte_data(self, address: int, register: int) -> int:
        """Read a byte from a specific register."""
        pass

    @abstractmethod
    async def read_i2c_block_data(self, address: int, register: int, length: int) -> List[int]:
        """Read a block of data from a specific register."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up and close the I2C bus."""
        pass

class SMBusI2CInterface(I2CInterface):
    """I2C interface implementation using smbus2."""

    def __init__(self, bus_number: int = 1):
        self._bus_number = bus_number
        self._bus = None

    async def initialize(self) -> None:
        if SMBUS_AVAILABLE:
            try:
                self._bus = smbus2.SMBus(self._bus_number)
                logger.info(f"I2C bus {self._bus_number} initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize I2C bus: {e}")
                self._bus = None
        else:
            logger.warning("smbus2 not available. I2C in mock mode.")

    async def write_byte_data(self, address: int, register: int, value: int) -> None:
        if self._bus:
            try:
                self._bus.write_byte_data(address, register, value)
            except Exception as e:
                logger.error(f"I2C write error: {e}")

    async def read_byte_data(self, address: int, register: int) -> int:
        if self._bus:
            try:
                return self._bus.read_byte_data(address, register)
            except Exception as e:
                logger.error(f"I2C read error: {e}")
                return 0
        return 0

    async def read_i2c_block_data(self, address: int, register: int, length: int) -> List[int]:
        if self._bus:
            try:
                return self._bus.read_i2c_block_data(address, register, length)
            except Exception as e:
                logger.error(f"I2C block read error: {e}")
                return []
        return []

    async def cleanup(self) -> None:
        if self._bus:
            self._bus.close()
            logger.info("I2C bus closed.")
