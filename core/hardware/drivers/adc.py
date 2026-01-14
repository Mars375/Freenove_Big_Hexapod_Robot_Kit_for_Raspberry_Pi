"""Driver ADC moderne pour PCF8591 utilisant le HAL."""
import logging
from typing import Optional, Dict, Any
from core.hardware.interfaces.base import IHardwareComponent, HardwareStatus
from core.hardware.interfaces.i2c import I2CInterface


class ADC(IHardwareComponent):
    """Driver ADC pour lecture de tension (PCF8591) via HAL."""
    
    def __init__(self, i2c: I2CInterface, address: int = 0x48):
        """
        Initialise le driver ADC.
        
        Args:
            i2c: Interface I2C HAL
            address: Adresse I2C du PCF8591 (défaut 0x48)
        """
        self._i2c = i2c
        self._address = address
        self.logger = logging.getLogger(__name__)
        self._status = HardwareStatus.UNINITIALIZED
    
    async def initialize(self) -> bool:
        """Initialise le driver ADC."""
        try:
            self._status = HardwareStatus.INITIALIZING
            
            # Test de communication avec un read simple
            result = self._i2c.read_byte(self._address)
            if result is None:
                raise RuntimeError("Failed to communicate with ADC")
            
            self._status = HardwareStatus.READY
            self.logger.info(f"ADC initialized at 0x{self._address:02x}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ADC: {e}")
            self._status = HardwareStatus.ERROR
            return False
    
    async def cleanup(self) -> None:
        """Nettoyage du driver ADC."""
        self._status = HardwareStatus.DISCONNECTED
        self.logger.info("ADC cleaned up")
    
    async def read_channel(self, channel: int) -> Optional[int]:
        """
        Lit une valeur brute depuis un canal ADC.
        
        Args:
            channel: Numéro du canal (0-3)
            
        Returns:
            Valeur brute (0-255) ou None en cas d'erreur
        """
        if not self.is_available() or not (0 <= channel < 4):
            return None
        
        try:
            # Sélectionner le canal et activer l'ADC
            self._i2c.write_byte(self._address, 0x40 | channel)
            
            # Lire la valeur (première lecture = ancienne valeur)
            self._i2c.read_byte(self._address)
            
            # Deuxième lecture = nouvelle valeur
            value = self._i2c.read_byte(self._address)
            return value
            
        except Exception as e:
            self.logger.error(f"Failed to read ADC channel {channel}: {e}")
            return None
    
    async def read_voltage(self, channel: int, reference_voltage: float = 3.3) -> Optional[float]:
        """
        Lit une tension depuis un canal ADC.
        
        Args:
            channel: Numéro du canal (0-3)
            reference_voltage: Tension de référence (défaut 3.3V)
            
        Returns:
            Tension en volts ou None en cas d'erreur
        """
        value = await self.read_channel(channel)
        if value is None:
            return None
        
        # Convertir en tension
        voltage = (value / 255.0) * reference_voltage
        return voltage
    
    async def read_battery_voltage(
        self, 
        channel: int = 0, 
        divider_ratio: float = 3.0
    ) -> Optional[float]:
        """
        Lit la tension batterie avec prise en compte du diviseur de tension.
        
        Args:
            channel: Numéro du canal (défaut 0)
            divider_ratio: Ratio du diviseur de tension (défaut 3.0)
            
        Returns:
            Tension batterie en volts ou None en cas d'erreur
        """
        voltage = await self.read_voltage(channel)
        if voltage is None:
            return None
        
        # Appliquer le ratio du diviseur de tension
        return voltage * divider_ratio
    
    def is_available(self) -> bool:
        """Vérifie si l'ADC est disponible."""
        return self._status == HardwareStatus.READY
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut de l'ADC."""
        return {
            "type": "adc",
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
