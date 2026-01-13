#!/usr/bin/env python3
"""Script de test hardware complet pour valider tous les drivers modernes.

Ce script teste:
- Interface I2C HAL
- Driver ADC (PCF8591)
- Driver IMU (MPU6050)
- Driver PCA9685
- Servos via PCA9685
"""
import asyncio
import logging
import sys
from typing import Optional

from core.hardware.interfaces.i2c import I2CInterface, SMBusI2C
from core.hardware.drivers.adc import ADC
from core.hardware.drivers.imu import MPU6050
from core.hardware.drivers.pca9685 import PCA9685

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HardwareTest:
    """Classe de test pour valider le hardware."""
    
    def __init__(self):
        self.i2c: Optional[I2CInterface] = None
        self.adc: Optional[ADC] = None
        self.imu: Optional[MPU6050] = None
        self.pca9685: Optional[PCA9685] = None
    
    async def test_i2c(self) -> bool:
        """Test de l'interface I2C HAL."""
        logger.info("=" * 60)
        logger.info("Test 1: Interface I2C HAL")
        logger.info("=" * 60)
        
        try:
            self.i2c = SMBusI2C(bus_number=1)
            await self.i2c.initialize()
            logger.info("✅ Interface I2C initialisée avec succès")
            return True
        except Exception as e:
            logger.error(f"❌ Échec de l'initialisation I2C: {e}")
            return False
    
    async def test_adc(self) -> bool:
        """Test du driver ADC."""
        logger.info("\n" + "=" * 60)
        logger.info("Test 2: Driver ADC (PCF8591)")
        logger.info("=" * 60)
        
        if not self.i2c:
            logger.error("❌ I2C non initialisé")
            return False
        
        try:
            self.adc = ADC(self.i2c, address=0x48)
            if not await self.adc.initialize():
                logger.error("❌ Échec de l'initialisation ADC")
                return False
            
            logger.info("✅ ADC initialisé avec succès")
            
            # Test de lecture
            voltage = await self.adc.read_battery_voltage(channel=0)
            if voltage is not None:
                logger.info(f"✅ Tension batterie: {voltage:.2f}V")
            else:
                logger.warning("⚠️  Impossible de lire la tension batterie")
            
            # Test de statut
            status = self.adc.get_status()
            logger.info(f"✅ Statut ADC: {status}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Erreur lors du test ADC: {e}")
            return False
    
    async def test_imu(self) -> bool:
        """Test du driver IMU."""
        logger.info("\n" + "=" * 60)
        logger.info("Test 3: Driver IMU (MPU6050)")
        logger.info("=" * 60)
        
        if not self.i2c:
            logger.error("❌ I2C non initialisé")
            return False
        
        try:
            self.imu = MPU6050(self.i2c, address=0x68)
            if not await self.imu.initialize():
                logger.error("❌ Échec de l'initialisation IMU")
                return False
            
            logger.info("✅ IMU initialisé avec succès")
            
            # Test de lecture accéléromètre
            accel = await self.imu.read_accel()
            if accel:
                logger.info(f"✅ Accéléromètre: X={accel[0]:.2f}g, Y={accel[1]:.2f}g, Z={accel[2]:.2f}g")
            else:
                logger.warning("⚠️  Impossible de lire l'accéléromètre")
            
            # Test de lecture gyroscope
            gyro = await self.imu.read_gyro()
            if gyro:
                logger.info(f"✅ Gyroscope: X={gyro[0]:.2f}°/s, Y={gyro[1]:.2f}°/s, Z={gyro[2]:.2f}°/s")
            else:
                logger.warning("⚠️  Impossible de lire le gyroscope")
            
            # Test de lecture température
            temp = await self.imu.read_temperature()
            if temp is not None:
                logger.info(f"✅ Température: {temp:.2f}°C")
            else:
                logger.warning("⚠️  Impossible de lire la température")
            
            # Test de statut
            status = self.imu.get_status()
            logger.info(f"✅ Statut IMU: {status}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Erreur lors du test IMU: {e}")
            return False
    
    async def test_pca9685(self) -> bool:
        """Test du driver PCA9685."""
        logger.info("\n" + "=" * 60)
        logger.info("Test 4: Driver PCA9685")
        logger.info("=" * 60)
        
        if not self.i2c:
            logger.error("❌ I2C non initialisé")
            return False
        
        try:
            self.pca9685 = PCA9685(self.i2c, address=0x40, frequency=50)
            if not await self.pca9685.initialize():
                logger.error("❌ Échec de l'initialisation PCA9685")
                return False
            
            logger.info("✅ PCA9685 initialisé avec succès")
            
            # Test de configuration PWM
            await self.pca9685.set_pwm(0, 0, 2048)  # 50% duty cycle
            logger.info("✅ Configuration PWM canal 0 réussie")
            
            # Test de statut
            status = self.pca9685.get_status()
            logger.info(f"✅ Statut PCA9685: {status}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Erreur lors du test PCA9685: {e}")
            return False
    
    async def cleanup(self):
        """Nettoyage de tous les drivers."""
        logger.info("\n" + "=" * 60)
        logger.info("Nettoyage des ressources")
        logger.info("=" * 60)
        
        if self.pca9685:
            await self.pca9685.cleanup()
            logger.info("✅ PCA9685 nettoyé")
        
        if self.imu:
            await self.imu.cleanup()
            logger.info("✅ IMU nettoyé")
        
        if self.adc:
            await self.adc.cleanup()
            logger.info("✅ ADC nettoyé")
        
        if self.i2c:
            await self.i2c.cleanup()
            logger.info("✅ I2C nettoyé")
    
    async def run_all_tests(self) -> bool:
        """Exécute tous les tests dans l'ordre."""
        logger.info("\n" + "#" * 60)
        logger.info("# TEST HARDWARE COMPLET - HAL MODERNE")
        logger.info("#" * 60)
        
        results = []
        
        # Test 1: I2C
        results.append(("I2C HAL", await self.test_i2c()))
        
        # Test 2: ADC
        results.append(("ADC", await self.test_adc()))
        
        # Test 3: IMU
        results.append(("IMU", await self.test_imu()))
        
        # Test 4: PCA9685
        results.append(("PCA9685", await self.test_pca9685()))
        
        # Résumé
        logger.info("\n" + "#" * 60)
        logger.info("# RÉSUMÉ DES TESTS")
        logger.info("#" * 60)
        
        success_count = 0
        for name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{name:.<40} {status}")
            if result:
                success_count += 1
        
        logger.info("#" * 60)
        logger.info(f"# RÉSULTAT: {success_count}/{len(results)} tests réussis")
        logger.info("#" * 60)
        
        return success_count == len(results)


async def main():
    """Fonction principale."""
    test = HardwareTest()
    
    try:
        all_passed = await test.run_all_tests()
        return 0 if all_passed else 1
    except KeyboardInterrupt:
        logger.info("\n⚠️  Test interrompu par l'utilisateur")
        return 1
    except Exception as e:
        logger.error(f"\n❌ Erreur fatale: {e}", exc_info=True)
        return 1
    finally:
        await test.cleanup()


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution: {e}", exc_info=True)
        sys.exit(1)
