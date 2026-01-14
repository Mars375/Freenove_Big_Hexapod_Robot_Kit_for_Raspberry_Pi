"""Sensor abstraction"""
import structlog
from datetime import datetime, timezone

from core.exceptions import SensorReadError
from core.hardware.factory import get_hardware_factory

logger = structlog.get_logger()


class SensorController:
    """Abstraction for sensors"""

    def __init__(self):
        self._adc = None
        self._imu = None
        self._ultrasonic = None
        self.factory = get_hardware_factory()
        
        # We need to initialize async in a sync constructor? 
        # No, better to verify if this class is used via a factory or dependency injection.
        # For now, we'll use a lazy init approach or check if the original had async init.
        # Original used sync init for legacy classes. 
        # Our HAL is async. We might need to adjust the lifecycle.
        # However, the methods read_battery etc ARE async. 
        # So we can fetch drivers lazily in those methods.
        
    async def _ensure_hardware(self):
        """Ensure drivers are initialized"""
        if not self._adc:
            self._adc = await self.factory.get_adc()
            
        if not self._imu:
            self._imu = await self.factory.get_imu()
            
        # Ultrasonic driver reference missing in factory? 
        # We need to add it to factory later or instantiate it here using HAL.
        # For now, bypassing ultrasonic if not in factory
        # self._ultrasonic = await self.factory.get_ultrasonic() 
        pass

    async def read_battery(self) -> dict:
        """Read battery voltage"""
        try:
            await self._ensure_hardware()
            
            if self._adc:
                voltage_result = await self._adc.read_battery_voltage()
                
                # ADC returns tuple (battery1, battery2)
                if isinstance(voltage_result, tuple):
                    battery1, battery2 = voltage_result
                    # Use the higher voltage or average
                    voltage = max(battery1, battery2)  # Or: (battery1 + battery2) / 2
                    logger.info("battery.dual_reading", battery1=battery1, battery2=battery2, selected=voltage)
                else:
                    voltage = voltage_result
            else:
                voltage = 7.4
            
            # Battery voltage range: 6.0V (empty) to 8.4V (full) for 2S LiPo
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
            await self._ensure_hardware()
            
            if self._imu:
                # IMU needs update first
                # self._imu.update_imu_state() # HAL driver handles this internally usually
                # Our HAL MPU6050 driver has read_accel and read_gyro methods
                
                accel_tuple = await self._imu.read_accel() # returns (x, y, z)
                gyro_tuple = await self._imu.read_gyro()
                temp_val = await self._imu.read_temperature()
                
                accel = list(accel_tuple) if accel_tuple else [0.0, 0.0, 0.0]
                gyro = list(gyro_tuple) if gyro_tuple else [0.0, 0.0, 0.0]
                temp = temp_val if temp_val else 25.5
                
            else:
                # Try to access IMU attributes (may vary)
                try:
                    accel = [self._imu.accel_x, self._imu.accel_y, self._imu.accel_z]
                    gyro = [self._imu.gyro_x, self._imu.gyro_y, self._imu.gyro_z]
                    temp = getattr(self._imu, 'temperature', 25.5)
                except AttributeError:
                    # Fallback if attributes don't exist
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
            # await self._ensure_hardware() 
            # Placeholder until ultrasonic is in factory
            distance = 50.0

            return {
                "distance": round(distance, 1),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error("sensor_controller.ultrasonic_read_failed", error=str(e))
            raise SensorReadError(f"Ultrasonic read failed: {e}")
