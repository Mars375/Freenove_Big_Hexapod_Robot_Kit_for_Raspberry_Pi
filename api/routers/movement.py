from fastapi import APIRouter, HTTPException
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
