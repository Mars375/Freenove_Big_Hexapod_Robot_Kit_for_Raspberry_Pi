#!/usr/bin/env python3
"""
Exemple d'utilisation de base des drivers HAL

Ce fichier démontre comment utiliser la stack HAL complète:
- I2CInterface pour la communication bas niveau
- Drivers (ADC, IMU, PCA9685) pour le contrôle matériel
- Controllers (Servo) pour la logique métier
"""

import time
import logging
from core.hardware.interfaces.i2c_interface import I2CInterface
from core.hardware.drivers.adc import ADS7830
from core.hardware.drivers.imu import MPU6050
from core.hardware.drivers.pca9685 import PCA9685
from core.hardware.drivers.pca9685_servo import PCA9685ServoController
from core.hardware.controllers.servo_controller import ServoController

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_i2c_interface():
    """Exemple 1: Utilisation directe de l'interface I2C"""
    logger.info("=== Exemple 1: Interface I2C ===")
    
    i2c = I2CInterface(bus=1)
    
    # Scanner les périphériques I2C
    devices = i2c.scan_bus()
    logger.info(f"Périphériques I2C détectés: {[hex(addr) for addr in devices]}")
    
    i2c.close()


def example_adc_driver():
    """Exemple 2: Lecture ADC avec le driver ADS7830"""
    logger.info("=== Exemple 2: Driver ADC ===")
    
    i2c = I2CInterface(bus=1)
    adc = ADS7830(i2c_interface=i2c, address=0x4b)
    
    if not adc.is_available():
        logger.error("ADC non disponible!")
        return
    
    # Lire tous les canaux
    for channel in range(8):
        value = adc.read_channel(channel)
        voltage = adc.read_voltage(channel)
        logger.info(f"Canal {channel}: {value} (raw) = {voltage:.2f}V")
    
    adc.cleanup()


def example_imu_driver():
    """Exemple 3: Lecture IMU avec le driver MPU6050"""
    logger.info("=== Exemple 3: Driver IMU ===")
    
    i2c = I2CInterface(bus=1)
    imu = MPU6050(i2c_interface=i2c, address=0x68)
    
    if not imu.is_available():
        logger.error("IMU non disponible!")
        return
    
    # Initialiser l'IMU
    imu.initialize()
    
    # Lire les données
    for _ in range(5):
        accel = imu.read_accelerometer()
        gyro = imu.read_gyroscope()
        temp = imu.read_temperature()
        
        logger.info(f"Accéléromètre: X={accel[0]:.2f} Y={accel[1]:.2f} Z={accel[2]:.2f} m/s²")
        logger.info(f"Gyroscope: X={gyro[0]:.2f} Y={gyro[1]:.2f} Z={gyro[2]:.2f} °/s")
        logger.info(f"Température: {temp:.1f}°C")
        
        time.sleep(0.5)
    
    imu.cleanup()


def example_servo_controller():
    """Exemple 4: Contrôle des servos avec le controller HAL"""
    logger.info("=== Exemple 4: Controller Servo ===")
    
    # Stack complète: I2C → PCA9685 → PCA9685ServoController → ServoController
    i2c = I2CInterface(bus=1)
    pca9685 = PCA9685(i2c_interface=i2c, address=0x40)
    pca9685_servo = PCA9685ServoController(pca9685)
    servo_controller = ServoController(pca9685_servo)
    
    if not pca9685.is_available():
        logger.error("PCA9685 non disponible!")
        return
    
    # Initialiser le PCA9685
    pca9685.initialize(frequency=50)  # 50 Hz pour servos
    
    # Déplacer un servo
    servo_id = 0
    
    logger.info(f"Position initiale: {servo_controller.get_angle(servo_id)}°")
    
    # Mouvement fluide de 0° à 180°
    for angle in range(0, 181, 10):
        servo_controller.set_angle(servo_id, angle)
        logger.info(f"Servo {servo_id}: {angle}°")
        time.sleep(0.1)
    
    # Retour à la position neutre
    servo_controller.set_angle(servo_id, 90)
    logger.info("Retour à 90°")
    
    # Utiliser les presets
    servo_controller.move_to_home(servo_id)
    logger.info("Position home")
    
    # Cleanup
    pca9685.cleanup()
    i2c.close()


def example_factory_usage():
    """Exemple 5: Utilisation via la factory (recommandé)"""
    logger.info("=== Exemple 5: Factory Pattern ===")
    
    from core.hardware.factory import HardwareFactory
    
    # La factory gère automatiquement toute la stack
    factory = HardwareFactory()
    
    # Récupérer le servo controller
    servo_controller = factory.get_servo_controller()
    
    # Utiliser directement
    servo_controller.set_angle(0, 90)
    logger.info("Servo 0 à 90° via factory")
    
    # Récupérer l'IMU
    imu = factory.get_imu()
    if imu.is_available():
        accel = imu.read_accelerometer()
        logger.info(f"Accéléromètre via factory: {accel}")
    
    # Cleanup automatique
    factory.cleanup()


def main():
    """Point d'entrée principal"""
    try:
        # Exemple 1: Interface I2C
        example_i2c_interface()
        print()
        
        # Exemple 2: ADC
        example_adc_driver()
        print()
        
        # Exemple 3: IMU
        example_imu_driver()
        print()
        
        # Exemple 4: Servos
        example_servo_controller()
        print()
        
        # Exemple 5: Factory (RECOMMANDÉ)
        example_factory_usage()
        
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur: {e}", exc_info=True)


if __name__ == "__main__":
    main()
