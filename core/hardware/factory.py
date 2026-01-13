import logging
from typing import Dict, Any, Optional
from core.config import Settings
from core.hardware.drivers.pca9685 import PCA9685
from core.hardware.drivers.adc import ADC
from core.hardware.drivers.imu import MPU6050
from core.hardware.devices.servo import ServoController
from core.hardware.devices.ultrasonic import UltrasonicSensor
from core.hardware.devices.led import LEDStrip
from core.hardware.devices.buzzer import Buzzer
from core.hardware.devices.camera import Camera
from core.hardware.controllers.hexapod_controller import HexapodController


class HardwareFactory:
    """Factory pour créer et gérer tous les composants hardware"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self._components: Dict[str, Any] = {}
    
    async def initialize_all(self) -> Dict[str, bool]:
        results = {}
        
        self.logger.info("Initializing hardware components...")
        
        # PWM Driver
        if self.settings.ENABLE_SERVO:
            pwm = PCA9685()
            results["pwm"] = await pwm.initialize()
            if results["pwm"]:
                self._components["pwm"] = pwm
        
        # Servo Controller
        if self.settings.ENABLE_SERVO:
            servo = ServoController(self._components.get("pwm"))
            results["servo"] = await servo.initialize()
            if results["servo"]:
                self._components["servo"] = servo
        
        # Hexapod Controller
        if self.settings.ENABLE_SERVO:
            hexapod = HexapodController(self._components.get("servo"))
            results["hexapod"] = await hexapod.initialize()
            if results["hexapod"]:
                self._components["hexapod"] = hexapod
        
        # ADC (Battery)
        if self.settings.ENABLE_BATTERY_MONITOR:
            adc = ADC()
            results["adc"] = await adc.initialize()
            if results["adc"]:
                self._components["adc"] = adc
        
        # IMU
        if self.settings.ENABLE_IMU:
            imu = MPU6050()
            results["imu"] = await imu.initialize()
            if results["imu"]:
                self._components["imu"] = imu
        
        # Ultrasonic
        if self.settings.ENABLE_ULTRASONIC:
            ultrasonic = UltrasonicSensor()
            results["ultrasonic"] = await ultrasonic.initialize()
            if results["ultrasonic"]:
                self._components["ultrasonic"] = ultrasonic
        
        # LED Strip
        if self.settings.ENABLE_LED:
            led = LEDStrip()
            results["led"] = await led.initialize()
            if results["led"]:
                self._components["led"] = led
        
        # Buzzer
        if self.settings.ENABLE_BUZZER:
            buzzer = Buzzer()
            results["buzzer"] = await buzzer.initialize()
            if results["buzzer"]:
                self._components["buzzer"] = buzzer
        
        # Camera
        if self.settings.ENABLE_CAMERA:
            camera = Camera(
                width=self.settings.CAMERA_WIDTH,
                height=self.settings.CAMERA_HEIGHT
            )
            results["camera"] = await camera.initialize()
            if results["camera"]:
                self._components["camera"] = camera
        
        # Log results
        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        self.logger.info(f"Hardware initialization: {success_count}/{total_count} components ready")
        
        return results
    
    async def cleanup_all(self) -> None:
        self.logger.info("Cleaning up hardware components...")
        
        for name, component in self._components.items():
            try:
                if hasattr(component, 'cleanup'):
                    await component.cleanup()
                self.logger.debug(f"Cleaned up {name}")
            except Exception as e:
                self.logger.error(f"Error cleaning up {name}: {e}")
        
        self._components.clear()
    
    def get_component(self, name: str) -> Optional[Any]:
        return self._components.get(name)
    
    def get_servo_controller(self) -> Optional[ServoController]:
        return self._components.get("servo")
    
    def get_hexapod_controller(self) -> Optional[HexapodController]:
        return self._components.get("hexapod")
    
    def get_adc(self) -> Optional[ADC]:
        return self._components.get("adc")
    
    def get_imu(self) -> Optional[MPU6050]:
        return self._components.get("imu")
    
    def get_ultrasonic(self) -> Optional[UltrasonicSensor]:
        return self._components.get("ultrasonic")
    
    def get_led(self) -> Optional[LEDStrip]:
        return self._components.get("led")
    
    def get_buzzer(self) -> Optional[Buzzer]:
        return self._components.get("buzzer")
    
    def get_camera(self) -> Optional[Camera]:
        return self._components.get("camera")
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        status = {}
        for name, component in self._components.items():
            if hasattr(component, 'get_status'):
                status[name] = component.get_status()
        return status
    
    def get_all_health(self) -> Dict[str, Dict[str, Any]]:
        health = {}
        for name, component in self._components.items():
            if hasattr(component, 'get_health'):
                health[name] = component.get_health()
        return health
    
    def is_ready(self) -> bool:
        if not self._components:
            return False
        
        for component in self._components.values():
            if hasattr(component, 'is_available'):
                if not component.is_available():
                    return False
        return True
