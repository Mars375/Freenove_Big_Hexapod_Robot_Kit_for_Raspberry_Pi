import logging
import time
from typing import Optional, Dict, Any, Tuple
from core.hardware.interfaces.base import IHardwareComponent, HardwareStatus

try:
    import smbus
    I2C_AVAILABLE = True
except ImportError:
    I2C_AVAILABLE = False


class MPU6050:
    """Driver pour capteur IMU MPU6050 (accéléromètre + gyroscope)"""
    
    # Registers
    PWR_MGMT_1 = 0x6B
    SMPLRT_DIV = 0x19
    CONFIG = 0x1A
    GYRO_CONFIG = 0x1B
    ACCEL_CONFIG = 0x1C
    INT_ENABLE = 0x38
    
    ACCEL_XOUT_H = 0x3B
    GYRO_XOUT_H = 0x43
    TEMP_OUT_H = 0x41
    
    def __init__(self, address: int = 0x68, bus_number: int = 1):
        self.address = address
        self.bus_number = bus_number
        self._bus: Optional[smbus.SMBus] = None
        self.logger = logging.getLogger(__name__)
        self._status = HardwareStatus.UNINITIALIZED
        
        # Scale factors
        self.accel_scale = 16384.0  # for ±2g
        self.gyro_scale = 131.0     # for ±250°/s
    
    async def initialize(self) -> bool:
        if not I2C_AVAILABLE:
            self.logger.error("smbus not available")
            self._status = HardwareStatus.ERROR
            return False
        
        try:
            self._status = HardwareStatus.INITIALIZING
            self._bus = smbus.SMBus(self.bus_number)
            
            # Wake up MPU6050
            self._bus.write_byte_data(self.address, self.PWR_MGMT_1, 0)
            time.sleep(0.1)
            
            # Configure
            self._bus.write_byte_data(self.address, self.SMPLRT_DIV, 7)
            self._bus.write_byte_data(self.address, self.CONFIG, 0)
            self._bus.write_byte_data(self.address, self.GYRO_CONFIG, 0)
            self._bus.write_byte_data(self.address, self.ACCEL_CONFIG, 0)
            
            self._status = HardwareStatus.READY
            self.logger.info(f"MPU6050 initialized at 0x{self.address:02x}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MPU6050: {e}")
            self._status = HardwareStatus.ERROR
            return False
    
    async def cleanup(self) -> None:
        if self._bus:
            try:
                # Put MPU6050 to sleep
                self._bus.write_byte_data(self.address, self.PWR_MGMT_1, 0x40)
                self._bus.close()
            except Exception as e:
                self.logger.error(f"Error during cleanup: {e}")
            finally:
                self._bus = None
                self._status = HardwareStatus.DISCONNECTED
    
    def _read_word(self, reg: int) -> int:
        high = self._bus.read_byte_data(self.address, reg)
        low = self._bus.read_byte_data(self.address, reg + 1)
        value = (high << 8) + low
        
        # Convert to signed
        if value >= 0x8000:
            return -((65535 - value) + 1)
        return value
    
    def read_accel(self) -> Optional[Tuple[float, float, float]]:
        if not self.is_available():
            return None
        
        try:
            x = self._read_word(self.ACCEL_XOUT_H) / self.accel_scale
            y = self._read_word(self.ACCEL_XOUT_H + 2) / self.accel_scale
            z = self._read_word(self.ACCEL_XOUT_H + 4) / self.accel_scale
            return (x, y, z)
        except Exception as e:
            self.logger.error(f"Failed to read accelerometer: {e}")
            return None
    
    def read_gyro(self) -> Optional[Tuple[float, float, float]]:
        if not self.is_available():
            return None
        
        try:
            x = self._read_word(self.GYRO_XOUT_H) / self.gyro_scale
            y = self._read_word(self.GYRO_XOUT_H + 2) / self.gyro_scale
            z = self._read_word(self.GYRO_XOUT_H + 4) / self.gyro_scale
            return (x, y, z)
        except Exception as e:
            self.logger.error(f"Failed to read gyroscope: {e}")
            return None
    
    def read_temperature(self) -> Optional[float]:
        if not self.is_available():
            return None
        
        try:
            raw_temp = self._read_word(self.TEMP_OUT_H)
            temp = (raw_temp / 340.0) + 36.53
            return temp
        except Exception as e:
            self.logger.error(f"Failed to read temperature: {e}")
            return None
    
    def is_available(self) -> bool:
        return I2C_AVAILABLE and self._status == HardwareStatus.READY
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "type": "mpu6050",
            "address": f"0x{self.address:02x}",
            "status": self._status.value,
            "available": self.is_available()
        }
