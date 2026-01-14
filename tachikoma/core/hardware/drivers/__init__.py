"""Package des drivers matériels modernes pour le robot hexapode."""

# Drivers de base
from .adc import ADC
from .imu import MPU6050
from .ultrasonic import UltrasonicSensor
from .camera import CameraDriver

# Drivers servo
from .pca9685 import PCA9685
from .pca9685_servo import PCA9685ServoController
from .mock_servo import MockServoController

__all__ = [
    # Drivers de base
    "ADC",
    "MPU6050",
    # Drivers servo
    "PCA9685",
    "PCA9685ServoController",
    "MockServoController",
    # Sensor drivers
    "UltrasonicSensor",
    "CameraDriver",
]
