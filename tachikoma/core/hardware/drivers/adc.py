"""Driver ADC moderne pour ADS7830 (utilisé dans le kit Freenove Big Hexapod) utilisant le HAL."""
import logging
from typing import Optional, Dict, Any, Tuple
from tachikoma.core.hardware.interfaces.base import IHardwareComponent, HardwareStatus
from tachikoma.core.hardware.interfaces.i2c import I2CInterface


class ADC(IHardwareComponent):
    """Driver ADC pour ADS7830 via HAL.
    
    L'ADS7830 est un ADC 8-bit, 8-canaux utilisé pour la lecture de batterie.
    """
    
    ADS7830_COMMAND = 0x84  # Commande de base pour ADS7830
    
    def __init__(self, i2c: I2CInterface, address: int = 0x48):
        """
        Initialise le driver ADC.
        
        Args:
            i2c: Interface I2C HAL
            address: Adresse I2C de l'ADS7830 (défaut 0x48)
        """
        self._i2c = i2c
        self._address = address
        self.logger = logging.getLogger(__name__)
        self._status = HardwareStatus.UNINITIALIZED
        self._voltage_coefficient = 3.0  # Ratio du diviseur de tension sur le PCB
        self._ref_voltage = 5.0          # Tension de référence
    
    async def initialize(self) -> bool:
        """Initialise le driver ADC."""
        try:
            self._status = HardwareStatus.INITIALIZING
            
            # Test de communication (lecture simple)
            # Utilise read_byte sans commande pour tester la présence
            result = self._i2c.read_byte_data(self._address, 0x00)
            
            self._status = HardwareStatus.READY
            self.logger.info(f"ADS7830 initialized at 0x{self._address:02x}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ADS7830: {e}")
            self._status = HardwareStatus.ERROR
            return False
    
    async def cleanup(self) -> None:
        """Nettoyage du driver."""
        self._status = HardwareStatus.DISCONNECTED
        self.logger.info("ADC cleaned up")
    
    async def read_channel(self, channel: int) -> Optional[int]:
        """
        Lit une valeur brute depuis un canal ADC.
        
        Args:
            channel: Numéro du canal (0-7)
            
        Returns:
            Valeur brute (0-255) ou None en cas d'erreur
        """
        if not self.is_available() or not (0 <= channel < 8):
            return None
        
        try:
            # Calcul de la commande pour le canal spécifié (Logique legacy ADS7830)
            command_set = self.ADS7830_COMMAND | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)
            
            # Ecrire la commande
            self._i2c.write_byte(self._address, command_set)
            
            # Lecture stable (deux lectures consécutives identiques pour filtrer le bruit)
            # Sur I2C, la lecture brute renvoie la valeur convertie
            val1 = self._i2c.read_byte(self._address)
            val2 = self._i2c.read_byte(self._address)
            
            return val2 if val1 == val2 else val1
            
        except Exception as e:
            self.logger.error(f"Failed to read ADC channel {channel}: {e}")
            return None
    
    async def read_battery_voltage(self) -> Tuple[float, float]:
        """
        Lit les tensions des deux circuits batterie.
        
        Returns:
            Tuple (batterie1, batterie2) en Volts
        """
        v1_raw = await self.read_channel(0)
        v2_raw = await self.read_channel(4)
        
        v1 = (v1_raw / 255.0) * self._ref_voltage * self._voltage_coefficient if v1_raw is not None else 0.0
        v2 = (v2_raw / 255.0) * self._ref_voltage * self._voltage_coefficient if v2_raw is not None else 0.0
        
        return v1, v2
    
    def is_available(self) -> bool:
        """Vérifie si l'ADC est disponible."""
        return self._status == HardwareStatus.READY
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut de l'ADC."""
        return {
            "type": "ads7830",
            "address": f"0x{self._address:02x}",
            "status": self._status.value,
            "available": self.is_available()
        }

    def get_health(self) -> Dict[str, Any]:
        """Retourne l'état de santé du composant."""
        return {
            "healthy": self._status == HardwareStatus.READY,
            "error": None if self._status == HardwareStatus.READY else "Driver not ready"
        }
