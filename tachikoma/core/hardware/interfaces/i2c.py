"""I2C hardware interface abstraction"""
from abc import ABC, abstractmethod
from typing import Optional
import structlog
try:
    import smbus2
except ImportError:
    smbus2 = None

logger = structlog.get_logger()


class I2CInterface(ABC):
    """Abstract interface for I2C communication"""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the I2C bus"""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up and close the I2C bus"""
        pass

    @abstractmethod
    def write_byte_data(self, address: int, register: int, value: int) -> None:
        """Write a byte to a specific register"""
        pass

    @abstractmethod
    def write_byte(self, address: int, value: int) -> None:
        """Write a single byte to the device"""
        pass

    @abstractmethod
    def read_byte(self, address: int) -> int:
        """Read a single byte from the device"""
        pass

    @abstractmethod
    def read_byte_data(self, address: int, register: int) -> int:
        """Read a byte from a specific register"""
        pass

    @abstractmethod
    def read_word_data(self, address: int, register: int) -> int:
        """Read a word (2 bytes) from a specific register"""
        pass


class SMBusI2CInterface(I2CInterface):
    """I2C interface implementation using the smbus2 library"""

    def __init__(self, bus_number: int = 1):
        self._bus_number = bus_number
        self._bus: Optional[smbus2.SMBus] = None
        logger.info("i2c.smbus.created", bus=bus_number)

    async def initialize(self) -> None:
        if smbus2 is None:
            logger.warning("i2c.smbus.not_found", message="smbus2 library not found. Running in mock mode.")
            return

        try:
            self._bus = smbus2.SMBus(self._bus_number)
            logger.info("i2c.smbus.initialized", bus=self._bus_number)
        except Exception as e:
            logger.error("i2c.smbus.init_failed", error=str(e))
            self._bus = None

    async def cleanup(self) -> None:
        if self._bus:
            try:
                self._bus.close()
                logger.info("i2c.smbus.closed")
            except Exception as e:
                logger.error("i2c.smbus.close_failed", error=str(e))
        self._bus = None

    def write_byte_data(self, address: int, register: int, value: int) -> None:
        if not self._bus:
            return
        try:
            self._bus.write_byte_data(address, register, value)
        except Exception as e:
            logger.error("i2c.smbus.write_failed", error=str(e))
            raise

    def write_byte(self, address: int, value: int) -> None:
        if not self._bus:
            return
        try:
            self._bus.write_byte(address, value)
        except Exception as e:
            logger.error("i2c.smbus.write_byte_failed", error=str(e))
            raise

    def read_byte(self, address: int) -> int:
        if not self._bus:
            return 0
        try:
            return self._bus.read_byte(address)
        except Exception as e:
            logger.error("i2c.smbus.read_byte_failed", error=str(e))
            raise

    def read_byte_data(self, address: int, register: int) -> int:
        if not self._bus:
            # logger.warning("i2c.smbus.read_mocked", address=address, register=register)
            return 0
        try:
            return self._bus.read_byte_data(address, register)
        except Exception as e:
            logger.error("i2c.smbus.read_failed", error=str(e))
            raise

    def read_word_data(self, address: int, register: int) -> int:
        if not self._bus:
            # logger.warning("i2c.smbus.read_word_mocked", address=address, register=register)
            return 0
        try:
            return self._bus.read_word_data(address, register)
        except Exception as e:
            logger.error("i2c.smbus.read_word_failed", error=str(e))
            raise
