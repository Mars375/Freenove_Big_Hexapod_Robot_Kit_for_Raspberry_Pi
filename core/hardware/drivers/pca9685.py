import logging
import time
from typing import Optional
from core.hardware.interfaces.base import IHardwareComponent, HardwareStatus

try:
    import smbus
    I2C_AVAILABLE = True
except ImportError:
    I2C_AVAILABLE = False


class PCA9685:
    """Driver pour le contrôleur PWM PCA9685 (16 canaux)"""
    
    # Registers
    MODE1 = 0x00
    MODE2 = 0x01
    SUBADR1 = 0x02
    SUBADR2 = 0x03
    SUBADR3 = 0x04
    PRESCALE = 0xFE
    LED0_ON_L = 0x06
    LED0_ON_H = 0x07
    LED0_OFF_L = 0x08
    LED0_OFF_H = 0x09
    ALL_LED_ON_L = 0xFA
    ALL_LED_ON_H = 0xFB
    ALL_LED_OFF_L = 0xFC
    ALL_LED_OFF_H = 0xFD
    
    # Bits
    RESTART = 0x80
    SLEEP = 0x10
    ALLCALL = 0x01
    INVRT = 0x10
    OUTDRV = 0x04
    
    def __init__(self, address: int = 0x40, bus_number: int = 1, frequency: int = 50):
        self.address = address
        self.bus_number = bus_number
        self.frequency = frequency
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
            
            # Reset
            self._write_byte(self.MODE1, 0x00)
            
            # Set frequency
            self.set_pwm_freq(self.frequency)
            
            self._status = HardwareStatus.READY
            self.logger.info(f"PCA9685 initialized at 0x{self.address:02x}, {self.frequency}Hz")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize PCA9685: {e}")
            self._status = HardwareStatus.ERROR
            return False
    
    async def cleanup(self) -> None:
        if self._bus:
            try:
                # Turn off all PWM channels
                self.set_all_pwm(0, 0)
                self._bus.close()
            except Exception as e:
                self.logger.error(f"Error during cleanup: {e}")
            finally:
                self._bus = None
                self._status = HardwareStatus.DISCONNECTED
    
    def _write_byte(self, reg: int, value: int) -> None:
        if self._bus:
            self._bus.write_byte_data(self.address, reg, value)
    
    def _read_byte(self, reg: int) -> int:
        if self._bus:
            return self._bus.read_byte_data(self.address, reg)
        return 0
    
    def set_pwm_freq(self, freq: int) -> None:
        prescale_val = 25000000.0
        prescale_val /= 4096.0
        prescale_val /= float(freq)
        prescale_val -= 1.0
        prescale = int(prescale_val + 0.5)
        
        old_mode = self._read_byte(self.MODE1)
        new_mode = (old_mode & 0x7F) | self.SLEEP
        self._write_byte(self.MODE1, new_mode)
        self._write_byte(self.PRESCALE, prescale)
        self._write_byte(self.MODE1, old_mode)
        time.sleep(0.005)
        self._write_byte(self.MODE1, old_mode | self.RESTART)
    
    def set_pwm(self, channel: int, on: int, off: int) -> None:
        if not (0 <= channel < 16):
            raise ValueError(f"Channel must be 0-15, got {channel}")
        
        self._write_byte(self.LED0_ON_L + 4 * channel, on & 0xFF)
        self._write_byte(self.LED0_ON_H + 4 * channel, on >> 8)
        self._write_byte(self.LED0_OFF_L + 4 * channel, off & 0xFF)
        self._write_byte(self.LED0_OFF_H + 4 * channel, off >> 8)
    
    def set_servo_pulse(self, channel: int, pulse: int) -> None:
        pulse = int(pulse * (4096 / 20000.0))
        self.set_pwm(channel, 0, pulse)
    
    def set_all_pwm(self, on: int, off: int) -> None:
        self._write_byte(self.ALL_LED_ON_L, on & 0xFF)
        self._write_byte(self.ALL_LED_ON_H, on >> 8)
        self._write_byte(self.ALL_LED_OFF_L, off & 0xFF)
        self._write_byte(self.ALL_LED_OFF_H, off >> 8)
    
    def is_available(self) -> bool:
        return I2C_AVAILABLE and self._status == HardwareStatus.READY
    
    def get_status(self) -> dict:
        return {
            "type": "pca9685",
            "address": f"0x{self.address:02x}",
            "frequency": self.frequency,
            "status": self._status.value,
            "available": self.is_available()
        }
