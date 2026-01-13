from fastapi import APIRouter, HTTPException
from core.robot_controller import get_robot_controller
from core.exceptions import SensorReadError
import structlog
from datetime import datetime, timezone

router = APIRouter()
logger = structlog.get_logger()


@router.get("/battery")
async def get_battery():
    """Get battery status"""
    try:
        robot = get_robot_controller()
        data = await robot.sensors.read_battery()
        return data
    except SensorReadError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/imu")
async def get_imu():
    """Get IMU data (accelerometer, gyroscope, temperature)"""
    try:
        robot = get_robot_controller()
        data = await robot.sensors.read_imu()
        return data
    except SensorReadError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ultrasonic")
async def get_ultrasonic():
    """Get ultrasonic distance"""
    try:
        robot = get_robot_controller()
        data = await robot.sensors.read_ultrasonic()
        return data
    except SensorReadError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
async def get_all_sensors():
    """Get all sensor data"""
    try:
        robot = get_robot_controller()
        
        battery = await robot.sensors.read_battery()
        imu = await robot.sensors.read_imu()
        ultrasonic = await robot.sensors.read_ultrasonic()
        
        return {
            "battery": battery,
            "imu": imu,
            "ultrasonic": ultrasonic,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except SensorReadError as e:
        raise HTTPException(status_code=500, detail=str(e))
