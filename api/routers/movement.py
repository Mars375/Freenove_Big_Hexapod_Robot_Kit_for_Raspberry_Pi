from fastapi import APIRouter, HTTPException
import asyncio
from api.models import MoveCommand, AttitudeCommand, StandardResponse
from core.robot_controller import get_robot_controller, initialize_robot
from core.exceptions import HardwareNotAvailableError, CommandExecutionError
import structlog

router = APIRouter()
logger = structlog.get_logger()


@router.post("/move", response_model=StandardResponse)
async def move_robot(command: MoveCommand):
    """Execute movement command"""
    logger.info("movement.move", mode=command.mode, x=command.x, y=command.y, 
                speed=command.speed, angle=command.angle)
    
    try:
        robot = await initialize_robot()
        await robot.movement.move(
            mode=command.mode,
            x=command.x,
            y=command.y,
            speed=command.speed,
            angle=command.angle
        )
        
        return StandardResponse(
            success=True,
            message="Movement command sent successfully",
            command=f"CMD_MOVE#{command.mode}#{command.x}#{command.y}#{command.speed}#{command.angle}"
        )
    
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except CommandExecutionError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/attitude", response_model=StandardResponse)
async def set_attitude(command: AttitudeCommand):
    """Set robot attitude (roll, pitch, yaw)"""
    logger.info("movement.attitude", roll=command.roll, pitch=command.pitch, yaw=command.yaw)
    
    try:
        robot = await initialize_robot()
        await robot.movement.set_attitude(
            roll=command.roll,
            pitch=command.pitch,
            yaw=command.yaw
        )
        
        return StandardResponse(
            success=True,
            message="Attitude set successfully",
            data={
                "roll": command.roll,
                "pitch": command.pitch,
                "yaw": command.yaw
            }
        )
    
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except CommandExecutionError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop", response_model=StandardResponse)
async def stop_robot():
    """Emergency stop"""
    logger.info("movement.stop")
    
    try:
        robot = await initialize_robot()
        await robot.movement.stop()
        
        return StandardResponse(
            success=True,
            message="Robot stopped successfully"
        )
    
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except CommandExecutionError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test_walk", response_model=StandardResponse)
async def test_walk():
    """
    🧪 DEV ONLY: Test endpoint for validating continuous movement.
    Walks forward for 5 seconds then stops.
    """
    logger.info("movement.test_walk.start")

    try:
        robot = await initialize_robot()

        # Start walking forward (tripod gait)
        await robot.movement.move(
            mode="forward",
            speed=5,
            gait_type="1"  # tripod
        )

        # Let it walk for 5 seconds
        await asyncio.sleep(5.0)

        # Stop
        await robot.movement.stop()

        logger.info("movement.test_walk.complete")

        return StandardResponse(
            success=True,
            message="Test walk completed (5s forward, tripod gait)",
            data={
                "duration": 5.0,
                "gait": "tripod",
                "mode": "forward"
            }
        )

    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except CommandExecutionError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error("movement.test_walk.failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Test walk failed: {e}")
