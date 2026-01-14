"""Hardware factory for creating controller instances with HAL architecture."""
from typing import Optional
import structlog

from core.config import Settings
from core.hardware.interfaces import IServoController
from core.hardware.interfaces.i2c import I2CInterface, SMBusI2CInterface
from core.hardware.drivers import (
    PCA9685,
    PCA9685ServoController,
    ADC,
    MPU6050,
)
from core.hardware.devices.led import LEDStrip

logger = structlog.get_logger()


class HardwareFactory:
    """Factory for creating hardware controller instances.
    
    Centralizes hardware instantiation logic and configuration.
    Implements proper HAL architecture with I2C interface abstraction.
    Supports dependency injection and testing.
    
    Architecture:
        1. I2C Interface (HAL bas niveau)
        2. Drivers de base (PCA9685, ADC, MPU6050) utilisant I2C
        3. Contrôleurs de haut niveau (PCA9685ServoController)
    """
    
    def __init__(self, settings: Settings):
        """Initialise la factory hardware.
        
        Args:
            settings: Configuration de l'application
        """
        self.settings = settings
        
        # HAL bas niveau
        self._i2c: Optional[I2CInterface] = None
        
        # Drivers de base
        self._pca9685: Optional[PCA9685] = None
        self._adc: Optional[ADC] = None
        self._imu: Optional[MPU6050] = None
        
        # Contrôleurs haut niveau
        self._servo_controller: Optional[IServoController] = None
                
        # Devices
        self._led_strip: Optional[LEDStrip] = None
        
        logger.info("hardware_factory.created")
    
    async def get_i2c_interface(self) -> I2CInterface:
        """Récupère ou crée l'interface I2C.
        
        Returns:
            Interface I2C HAL configurée
        """
        if self._i2c is None:
            logger.info("hardware_factory.creating_i2c_interface")
            self._i2c = SMBusI2CInterface(bus_number=1)
            await self._i2c.initialize()
        
        return self._i2c
    
    async def get_pca9685(self, address: int = 0x40, frequency: int = 50) -> PCA9685:
        """Récupère ou crée le driver PCA9685.
        
        Args:
            address: Adresse I2C du PCA9685 (défaut 0x40)
            frequency: Fréquence PWM en Hz (défaut 50Hz pour servos)
            
        Returns:
            Driver PCA9685 initialisé
        """
        # Initialize cache if needed (replaces single instance self._pca9685)
        if not hasattr(self, "_pca_cache"):
            self._pca_cache = {}
            
        # Check cache
        cache_key = f"{address}_{frequency}"
        if cache_key in self._pca_cache:
            return self._pca_cache[cache_key]
            
        logger.info(
            "hardware_factory.creating_pca9685",
            address=hex(address),
            frequency=frequency
        )
        i2c = await self.get_i2c_interface()
        pca = PCA9685(i2c=i2c, address=address, frequency=frequency)
        await pca.initialize()
        
        self._pca_cache[cache_key] = pca
        return pca
    
    async def get_adc(self, address: int = 0x48) -> ADC:
        """Récupère ou crée le driver ADC.
        
        Args:
            address: Adresse I2C de l'ADC (défaut 0x48)
            
        Returns:
            Driver ADC initialisé
        """
        if self._adc is None:
            logger.info(
                "hardware_factory.creating_adc",
                address=hex(address)
            )
            i2c = await self.get_i2c_interface()
            self._adc = ADC(i2c=i2c, address=address)
            await self._adc.initialize()
        
        return self._adc
    
    async def get_imu(self, address: int = 0x68) -> MPU6050:
        """Récupère ou crée le driver IMU (MPU6050).
        
        Args:
            address: Adresse I2C du MPU6050 (défaut 0x68)
            
        Returns:
            Driver MPU6050 initialisé
        """
        if self._imu is None:
            logger.info(
                "hardware_factory.creating_imu",
                address=hex(address)
            )
            i2c = await self.get_i2c_interface()
            self._imu = MPU6050(i2c=i2c, address=address)
            await self._imu.initialize()
        
        return self._imu
    
    async def create_servo_controller(self) -> IServoController:
        """Crée le contrôleur de servos basé sur la configuration.
        
        Returns:
            Instance du contrôleur de servos configuré
            
        Raises:
            ValueError: Si le type de servo est invalide
        """
        if self._servo_controller is not None:
            logger.debug("hardware_factory.reusing_servo_controller")
            return self._servo_controller
        
        # Pour l'instant, on supporte uniquement PCA9685
        # Pourrait être configuré via settings dans le futur
        servo_type = "pca9685"  # settings.hardware.servo_type
        
        if servo_type == "pca9685":
            logger.info(
                "hardware_factory.creating_servo_controller",
                type="pca9685_dual",
                channels=32
            )
            # Board 1: Channels 0-15 (Logiciel) -> Address 0x41
            pca_low = await self.get_pca9685(address=0x41, frequency=50)
            
            # Board 2: Channels 16-31 (Logiciel) -> Address 0x40
            pca_high = await self.get_pca9685(address=0x40, frequency=50)
            
            # Créer le contrôleur de servos avec les deux boards
            self._servo_controller = PCA9685ServoController(
                pca_low=pca_low,
                pca_high=pca_high,
                min_pulse=500,
                max_pulse=2500
            )
            await self._servo_controller.initialize()
        else:
            raise ValueError(f"Type de servo inconnu: {servo_type}")
        
        return self._servo_controller
    
    def get_servo_controller(self) -> Optional[IServoController]:
        """Récupère l'instance existante du contrôleur de servos.
        
        Returns:
            Contrôleur de servos existant ou None si non créé
        """
        return self._servo_controller

    async def get_led_strip(
        self,
        led_count: int = 8,
        brightness: int = 255,
        bus: int = 0,
        device: int = 0
    ) -> LEDStrip:
        """Récupère ou crée le device LED strip.
        
        Args:
            led_count: Nombre de LEDs (défaut 8)
            brightness: Luminosité initiale 0-255 (défaut 255)
            bus: Bus SPI (défaut 0)
            device: Device SPI (défaut 0)
            
        Returns:
            Device LED strip initialisé
        """
        if self._led_strip is None:
            logger.info(
                "hardware_factory.creating_led_strip",
                led_count=led_count,
                brightness=brightness,
                bus=bus,
                device=device
            )
            self._led_strip = LEDStrip(
                led_count=led_count,
                brightness=brightness,
                bus=bus,
                device=device
            )
            await self._led_strip.initialize()
        
        return self._led_strip
    
    async def cleanup_all(self):
        """Nettoyage de toutes les ressources hardware."""
        logger.info("hardware_factory.cleanup_all")
        
        # Nettoyer les contrôleurs haut niveau
        if self._servo_controller:
            try:
                await self._servo_controller.cleanup()
                self._servo_controller = None
            except Exception as e:
                logger.error(
                    "hardware_factory.servo_cleanup_failed",
                    error=str(e)
                )

                # Nettoyer les devices
        if self._led_strip:
            try:
                await self._led_strip.cleanup()
                self._led_strip = None
            except Exception as e:
                logger.error(
                    "hardware_factory.led_cleanup_failed",
                    error=str(e)
                )
        
        # Nettoyer les drivers de base
        if self._imu:
            try:
                await self._imu.cleanup()
                self._imu = None
            except Exception as e:
                logger.error(
                    "hardware_factory.imu_cleanup_failed",
                    error=str(e)
                )
        
        if self._adc:
            try:
                await self._adc.cleanup()
                self._adc = None
            except Exception as e:
                logger.error(
                    "hardware_factory.adc_cleanup_failed",
                    error=str(e)
                )
        
        if self._pca9685:
            try:
                await self._pca9685.cleanup()
                self._pca9685 = None
            except Exception as e:
                logger.error(
                    "hardware_factory.pca9685_cleanup_failed",
                    error=str(e)
                )
        
        # Nettoyer l'interface I2C (en dernier)
        if self._i2c:
            try:
                await self._i2c.cleanup()
                self._i2c = None
            except Exception as e:
                logger.error(
                    "hardware_factory.i2c_cleanup_failed",
                    error=str(e)
                )
        
        logger.info("hardware_factory.cleanup_complete")


# Instance globale de la factory (initialisée au démarrage)
_factory: Optional[HardwareFactory] = None


def get_hardware_factory(settings: Optional[Settings] = None) -> HardwareFactory:
    """Récupère ou crée la factory hardware globale.
    
    Args:
        settings: Configuration de l'application (requis au premier appel)
        
    Returns:
        Instance globale de la factory hardware
    """
    global _factory
    
    if _factory is None:
        if settings is None:
            from core.config import get_settings
            settings = get_settings()
        
        _factory = HardwareFactory(settings)
    
    return _factory
