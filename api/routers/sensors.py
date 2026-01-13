"""
Sensor data endpoints.
Provides access to IMU, ultrasonic, and battery sensors.
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from api.models import AllSensorsData, BatteryData, IMUData, UltrasonicData
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/imu", response_model=IMUData)
async def get_imu_data() -> IMUData:
    """
    Get IMU (Inertial Measurement Unit) sensor data.
    
    Returns accelerometer and gyroscope readings.
    
    Returns:
        IMU data with accel and gyro values
    """
    logger.debug("sensors.imu")
    
    if not settings.imu_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="IMU sensor is disabled"
        )
    
    try:
        # TODO: Read actual IMU data from mpu6050
        # For now, return simulated data
        return IMUData(
            accel_x=0.1,
            accel_y=0.0,
            accel_z=9.8,
            gyro_x=0.0,
            gyro_y=0.0,
            gyro_z=0.0,
            temperature=25.5
        )
    except Exception as e:
        logger.error("sensors.imu.error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read IMU data: {str(e)}"
        )


@router.get("/ultrasonic", response_model=UltrasonicData)
async def get_ultrasonic_data() -> UltrasonicData:
    """
    Get ultrasonic distance sensor data.
    
    Returns distance to nearest obstacle in centimeters.
    
    Returns:
        Ultrasonic distance measurement
    """
    logger.debug("sensors.ultrasonic")
    
    if not settings.ultrasonic_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ultrasonic sensor is disabled"
        )
    
    try:
        # TODO: Read actual ultrasonic sensor
        # For now, return simulated data
        return UltrasonicData(distance=50.0)
    except Exception as e:
        logger.error("sensors.ultrasonic.error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read ultrasonic data: {str(e)}"
        )


@router.get("/battery", response_model=BatteryData)
async def get_battery_data() -> BatteryData:
    """
    Get battery status and voltage.
    
    Returns voltage, percentage, and status flags.
    
    Returns:
        Battery data with voltage and status
    """
    logger.debug("sensors.battery")
    
    try:
        # TODO: Read actual battery voltage
        # For now, return simulated data
        voltage = 7.4  # Simulated 7.4V battery
        percentage = 85
        
        return BatteryData(
            voltage=voltage,
            percentage=percentage,
            is_charging=False,
            is_low=percentage < 20,
            is_critical=percentage < 10
        )
    except Exception as e:
        logger.error("sensors.battery.error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read battery data: {str(e)}"
        )


@router.get("/all", response_model=AllSensorsData)
async def get_all_sensors() -> AllSensorsData:
    """
    Get data from all sensors at once.
    
    Combines IMU, ultrasonic, and battery data in a single response.
    
    Returns:
        All sensor data combined
    """
    logger.debug("sensors.all")
    
    imu: Optional[IMUData] = None
    ultrasonic: Optional[UltrasonicData] = None
    battery: Optional[BatteryData] = None
    
    # Try to read each sensor, but don't fail if one is unavailable
    if settings.imu_enabled:
        try:
            imu = await get_imu_data()
        except Exception as e:
            logger.warning("sensors.all.imu.error", error=str(e))
    
    if settings.ultrasonic_enabled:
        try:
            ultrasonic = await get_ultrasonic_data()
        except Exception as e:
            logger.warning("sensors.all.ultrasonic.error", error=str(e))
    
    try:
        battery = await get_battery_data()
    except Exception as e:
        logger.warning("sensors.all.battery.error", error=str(e))
    
    return AllSensorsData(
        imu=imu,
        ultrasonic=ultrasonic,
        battery=battery
    )
