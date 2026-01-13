"""Driver IMU moderne pour MPU6050 utilisant le HAL."""
import logging
import asyncio
from typing import Optional, Dict, Any, Tuple
from core.hardware.interfaces.base import IHardwareComponent, HardwareStatus
from core.hardware.interfaces.i2c import I2CInterface


class MPU6050(IHardwareComponent):
    """Driver pour capteur IMU MPU6050 (accéléromètre + gyroscope) via HAL."""
    
    # Registres MPU6050
    PWR_MGMT_1 = 0x6B
    SMPLRT_DIV = 0x19
    CONFIG = 0x1A
    GYRO_CONFIG = 0x1B
    ACCEL_CONFIG = 0x1C
    INT_ENABLE = 0x38
    
    ACCEL_XOUT_H = 0x3B
    GYRO_XOUT_H = 0x43
    TEMP_OUT_H = 0x41
    
    def __init__(self, i2c: I2CInterface, address: int = 0x68):
        """
        Initialise le driver IMU.
        
        Args:
            i2c: Interface I2C HAL
            address: Adresse I2C du MPU6050 (défaut 0x68)
        """
        self._i2c = i2c
        self._address = address
        self.logger = logging.getLogger(__name__)
        self._status = HardwareStatus.UNINITIALIZED
        
        # Facteurs d'échelle
        self.accel_scale = 16384.0  # pour ±2g
        self.gyro_scale = 131.0  # pour ±250°/s
    
    async def initialize(self) -> bool:
        """Initialise le driver IMU."""
        try:
            self._status = HardwareStatus.INITIALIZING
            
            # Réveiller le MPU6050
            await self._i2c.write_byte_data(self._address, self.PWR_MGMT_1, 0)
            await asyncio.sleep(0.1)
            
            # Configuration
            await self._i2c.write_byte_data(self._address, self.SMPLRT_DIV, 7)
            await self._i2c.write_byte_data(self._address, self.CONFIG, 0)
            await self._i2c.write_byte_data(self._address, self.GYRO_CONFIG, 0)
            await self._i2c.write_byte_data(self._address, self.ACCEL_CONFIG, 0)
            
            self._status = HardwareStatus.READY
            self.logger.info(f"MPU6050 initialized at 0x{self._address:02x}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MPU6050: {e}")
            self._status = HardwareStatus.ERROR
            return False
    
    async def cleanup(self) -> None:
        """Nettoyage du driver IMU."""
        try:
            # Mettre le MPU6050 en veille
            await self._i2c.write_byte_data(self._address, self.PWR_MGMT_1, 0x40)
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
        finally:
            self._status = HardwareStatus.DISCONNECTED
            self.logger.info("MPU6050 cleaned up")
    
    async def _read_word(self, reg: int) -> int:
        """
        Lit un mot (16 bits) depuis un registre.
        
        Args:
            reg: Adresse du registre
            
        Returns:
            Valeur signée du mot
        """
        high = await self._i2c.read_byte_data(self._address, reg)
        low = await self._i2c.read_byte_data(self._address, reg + 1)
        
        if high is None or low is None:
            raise RuntimeError(f"Failed to read from register 0x{reg:02x}")
        
        value = (high << 8) + low
        
        # Convertir en signé
        if value >= 0x8000:
            return -((65535 - value) + 1)
        return value
    
    async def read_accel(self) -> Optional[Tuple[float, float, float]]:
        """
        Lit les données de l'accéléromètre.
        
        Returns:
            Tuple (x, y, z) en g ou None en cas d'erreur
        """
        if not self.is_available():
            return None
        
        try:
            x = await self._read_word(self.ACCEL_XOUT_H) / self.accel_scale
            y = await self._read_word(self.ACCEL_XOUT_H + 2) / self.accel_scale
            z = await self._read_word(self.ACCEL_XOUT_H + 4) / self.accel_scale
            return (x, y, z)
        except Exception as e:
            self.logger.error(f"Failed to read accelerometer: {e}")
            return None
    
    async def read_gyro(self) -> Optional[Tuple[float, float, float]]:
        """
        Lit les données du gyroscope.
        
        Returns:
            Tuple (x, y, z) en °/s ou None en cas d'erreur
        """
        if not self.is_available():
            return None
        
        try:
            x = await self._read_word(self.GYRO_XOUT_H) / self.gyro_scale
            y = await self._read_word(self.GYRO_XOUT_H + 2) / self.gyro_scale
            z = await self._read_word(self.GYRO_XOUT_H + 4) / self.gyro_scale
            return (x, y, z)
        except Exception as e:
            self.logger.error(f"Failed to read gyroscope: {e}")
            return None
    
    async def read_temperature(self) -> Optional[float]:
        """
        Lit la température du capteur.
        
        Returns:
            Température en °C ou None en cas d'erreur
        """
        if not self.is_available():
            return None
        
        try:
            raw_temp = await self._read_word(self.TEMP_OUT_H)
            temp = (raw_temp / 340.0) + 36.53
            return temp
        except Exception as e:
            self.logger.error(f"Failed to read temperature: {e}")
            return None
    
    def is_available(self) -> bool:
        """Vérifie si l'IMU est disponible."""
        return self._status == HardwareStatus.READY
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut de l'IMU."""
        return {
            "type": "mpu6050",
            "address": f"0x{self._address:02x}",
            "status": self._status.value,
            "available": self.is_available()
        }
