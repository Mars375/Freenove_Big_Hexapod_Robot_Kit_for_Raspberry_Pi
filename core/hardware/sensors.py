"""Sensor abstraction"""
import sys
from pathlib import Path
import structlog
from datetime import datetime, timezone

legacy_path = Path(__file__).parent.parent.parent / "legacy" / "Code" / "Server"
sys.path.insert(0, str(legacy_path))

from core.exceptions import SensorReadError

logger = structlog.get_logger()


class SensorController:
    """Abstraction for sensors"""
    
    def __init__(self):
        self._adc = None
        self._imu = None
        self._ultrasonic = None
        self._initialize_hardware()
    
    def _initialize_hardware(self):
        """Initialize sensor modules"""
        try:
            from adc import Adc
            from imu import Imu
            from ultrasonic import Ultrasonic
            
            self._adc = Adc()
            self._imu = Imu()
            self._ultrasonic = Ultrasonic()
            logger.info("sensor_controller.initialized")
        except Exception as e:
            logger.error("sensor_controller.init_failed", error=str(e))
    
    async def read_battery(self) -> dict:
        """Read battery voltage"""
        try:
            voltage = self._adc.get_battery_voltage() if self._adc else 7.4
            percentage = int((voltage - 6.0) / (8.4 - 6.0) * 100)
            percentage = max(0, min(100, percentage))
            
            return {
                "voltage": round(voltage, 2),
                "percentage": percentage,
                "is_charging": False,
                "is_low": percentage < 20,
                "is_critical": percentage < 10
            }
        except Exception as e:
            logger.error("sensor_controller.battery_read_failed", error=str(e))
            raise SensorReadError(f"Battery read failed: {e}")
    
    async def read_imu(self) -> dict:
        """Read IMU data"""
        try:
            if self._imu:
                accel = self._imu.get_accelerometer()
                gyro = self._imu.get_gyroscope()
                temp = self._imu.get_temperature()
            else:
                accel = [0.1, 0.0, 9.8]
                gyro = [0.0, 0.0, 0.0]
                temp = 25.5
            
            return {
                "accel_x": round(accel[0], 2),
                "accel_y": round(accel[1], 2),
                "accel_z": round(accel[2], 2),
                "gyro_x": round(gyro[0], 2),
                "gyro_y": round(gyro[1], 2),
                "gyro_z": round(gyro[2], 2),
                "temperature": round(temp, 1)
            }
        except Exception as e:
            logger.error("sensor_controller.imu_read_failed", error=str(e))
            raise SensorReadError(f"IMU read failed: {e}")
    
    async def read_ultrasonic(self) -> dict:
        """Read ultrasonic distance"""
        try:
            distance = self._ultrasonic.get_distance() if self._ultrasonic else 50.0
            
            return {
                "distance": round(distance, 1),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error("sensor_controller.ultrasonic_read_failed", error=str(e))
            raise SensorReadError(f"Ultrasonic read failed: {e}")
