import logging
from typing import Optional, Dict, Any
from core.hardware.interfaces.base import IHardwareComponent, HardwareStatus

try:
    import smbus
    I2C_AVAILABLE = True
except ImportError:
    I2C_AVAILABLE = False


class ADC:
    """Driver ADC pour lecture de la tension batterie (PCF8591)"""
    
    def __init__(self, address: int = 0x48, bus_number: int = 1):
        self.address = address
        self.bus_number = bus_number
        self._bus: Optional[smbus.SMBus] = None
        self.logger = logging.getLogger(__name__)
        self._status = HardwareStatus.UNINITIALIZED
    
    async def initialize(self) -> bool:
        if not I2C_AVAILABLE:
            self.logger.error("smbus not available")
            self._status = HardwareStatus.ERROR
            return False
        
        try:
            self._status = HardwareStatus.INITIALIZING
            self._bus = smbus.SMBus(self.bus_number)
            
            # Test read
            self._bus.read_byte(self.address)
            
            self._status = HardwareStatus.READY
            self.logger.info(f"ADC initialized at 0x{self.address:02x}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ADC: {e}")
            self._status = HardwareStatus.ERROR
            return False
    
    async def cleanup(self) -> None:
        if self._bus:
            try:
                self._bus.close()
            except Exception as e:
                self.logger.error(f"Error during cleanup: {e}")
            finally:
                self._bus = None
                self._status = HardwareStatus.DISCONNECTED
    
    def read_channel(self, channel: int) -> Optional[int]:
        if not self.is_available() or not (0 <= channel < 4):
            return None
        
        try:
            # Select channel and enable ADC
            self._bus.write_byte(self.address, 0x40 | channel)
            # Read value (first read is old value, second is new)
            self._bus.read_byte(self.address)
            value = self._bus.read_byte(self.address)
            return value
        except Exception as e:
            self.logger.error(f"Failed to read ADC channel {channel}: {e}")
            return None
    
    def read_voltage(self, channel: int, reference_voltage: float = 3.3) -> Optional[float]:
        value = self.read_channel(channel)
        if value is None:
            return None
        
        # Convert to voltage
        voltage = (value / 255.0) * reference_voltage
        return voltage
    
    def read_battery_voltage(self, channel: int = 0, divider_ratio: float = 3.0) -> Optional[float]:
        voltage = self.read_voltage(channel)
        if voltage is None:
            return None
        
        # Account for voltage divider
        return voltage * divider_ratio
    
    def is_available(self) -> bool:
        return I2C_AVAILABLE and self._status == HardwareStatus.READY
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "type": "adc",
            "address": f"0x{self.address:02x}",
            "status": self._status.value,
            "available": self.is_available()
        }
