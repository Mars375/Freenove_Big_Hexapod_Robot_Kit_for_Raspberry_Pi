"""Driver PCA9685 moderne utilisant le HAL."""
import logging
import asyncio
from typing import Optional, Dict, Any
from core.hardware.interfaces.base import IHardwareComponent, HardwareStatus
from unittest.mock import MagicMock
I2CInterface = MagicMock()


class PCA9685(IHardwareComponent):
    """Driver pour le contrôleur PWM PCA9685 (16 canaux) via HAL."""
    
    # Registres PCA9685
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
    
    def __init__(self, i2c: I2CInterface, address: int = 0x40, frequency: int = 50):
        """
        Initialise le driver PCA9685.
        
        Args:
            i2c: Interface I2C HAL
            address: Adresse I2C du PCA9685 (défaut 0x40)
            frequency: Fréquence PWM en Hz (défaut 50Hz pour servos)
        """
        self._i2c = i2c
        self._address = address
        self._frequency = frequency
        self.logger = logging.getLogger(__name__)
        self._status = HardwareStatus.UNINITIALIZED
    
    async def initialize(self) -> bool:
        """Initialise le driver PCA9685."""
        try:
            self._status = HardwareStatus.INITIALIZING
            
            # Reset
            await self._i2c.write_byte_data(self._address, self.MODE1, 0x00)
            
            # Set frequency
            await self._set_pwm_freq(self._frequency)
            
            self._status = HardwareStatus.READY
            self.logger.info(f"PCA9685 initialized at 0x{self._address:02x}, {self._frequency}Hz")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize PCA9685: {e}")
            self._status = HardwareStatus.ERROR
            return False
    
    async def cleanup(self) -> None:
        """Nettoyage du driver PCA9685."""
        try:
            # Turn off all PWM channels
            await self.set_all_pwm(0, 0)
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
        finally:
            self._status = HardwareStatus.DISCONNECTED
            self.logger.info("PCA9685 cleaned up")
    
    async def _set_pwm_freq(self, freq: int) -> None:
        """
        Configure la fréquence PWM.
        
        Args:
            freq: Fréquence en Hz
        """
        prescale_val = 25000000.0
        prescale_val /= 4096.0
        prescale_val /= float(freq)
        prescale_val -= 1.0
        prescale = int(prescale_val + 0.5)
        
        old_mode = await self._i2c.read_byte_data(self._address, self.MODE1)
        if old_mode is None:
            raise RuntimeError("Failed to read MODE1 register")
        
        new_mode = (old_mode & 0x7F) | self.SLEEP
        await self._i2c.write_byte_data(self._address, self.MODE1, new_mode)
        await self._i2c.write_byte_data(self._address, self.PRESCALE, prescale)
        await self._i2c.write_byte_data(self._address, self.MODE1, old_mode)
        await asyncio.sleep(0.005)
        await self._i2c.write_byte_data(self._address, self.MODE1, old_mode | self.RESTART)
    
    async def set_pwm(self, channel: int, on: int, off: int) -> None:
        """
        Configure un canal PWM.
        
        Args:
            channel: Numéro du canal (0-15)
            on: Valeur ON (0-4095)
            off: Valeur OFF (0-4095)
        """
        if not (0 <= channel < 16):
            raise ValueError(f"Channel must be 0-15, got {channel}")
        
        await self._i2c.write_byte_data(self._address, self.LED0_ON_L + 4 * channel, on & 0xFF)
        await self._i2c.write_byte_data(self._address, self.LED0_ON_H + 4 * channel, on >> 8)
        await self._i2c.write_byte_data(self._address, self.LED0_OFF_L + 4 * channel, off & 0xFF)
        await self._i2c.write_byte_data(self._address, self.LED0_OFF_H + 4 * channel, off >> 8)
    
    async def set_servo_pulse(self, channel: int, pulse: int) -> None:
        """
        Configure la durée d'impulsion d'un servo.
        
        Args:
            channel: Numéro du canal (0-15)
            pulse: Durée d'impulsion en microsecondes
        """
        pulse_value = int(pulse * (4096 / 20000.0))
        await self.set_pwm(channel, 0, pulse_value)
    
    async def set_all_pwm(self, on: int, off: int) -> None:
        """
        Configure tous les canaux PWM.
        
        Args:
            on: Valeur ON (0-4095)
            off: Valeur OFF (0-4095)
        """
        await self._i2c.write_byte_data(self._address, self.ALL_LED_ON_L, on & 0xFF)
        await self._i2c.write_byte_data(self._address, self.ALL_LED_ON_H, on >> 8)
        await self._i2c.write_byte_data(self._address, self.ALL_LED_OFF_L, off & 0xFF)
        await self._i2c.write_byte_data(self._address, self.ALL_LED_OFF_H, off >> 8)
    
    def is_available(self) -> bool:
        """Vérifie si le PCA9685 est disponible."""
        return self._status == HardwareStatus.READY
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut du PCA9685."""
        return {
            "type": "pca9685",
            "address": f"0x{self._address:02x}",
            "frequency": self._frequency,
            "status": self._status.value,
            "available": self.is_available()
        }
