from fastapi import APIRouter, HTTPException
from tachikoma.api.models import BuzzerCommand, StandardResponse
from tachikoma.core.robot_controller import get_robot_controller
from tachikoma.core.exceptions import HardwareNotAvailableError, CommandExecutionError
import structlog

router = APIRouter()
logger = structlog.get_logger()


@router.post("/beep", response_model=StandardResponse)
async def beep_buzzer(command: BuzzerCommand):
    """Activate buzzer with specified frequency and duration (non-blocking)"""
    logger.info("buzzer.beep", frequency=command.frequency, duration=command.duration, enabled=command.enabled)
    
    if not command.enabled:
        return StandardResponse(
            success=True,
            message="Buzzer disabled by request"
        )
    
    try:
        robot = get_robot_controller()
        await robot.buzzer.beep(
            frequency=command.frequency,
            duration=command.duration
        )
        
        return StandardResponse(
            success=True,
            message=f"Buzzer started: {command.frequency}Hz for {command.duration}s",
            data={
                "frequency": command.frequency,
                "duration": command.duration
            }
        )
    
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except CommandExecutionError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop", response_model=StandardResponse)
async def stop_buzzer():
    """Stop buzzer immediately"""
    logger.info("buzzer.stop")
    
    try:
        robot = get_robot_controller()
        stopped = await robot.buzzer.stop_async()
        
        return StandardResponse(
            success=True,
            message="Buzzer stopped" if stopped else "Buzzer was not running",
            data={"was_running": stopped}
        )
    
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except CommandExecutionError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=StandardResponse)
async def get_buzzer_status():
    """Get buzzer status"""
    try:
        robot = get_robot_controller()
        status = robot.buzzer.get_status()
        
        return StandardResponse(
            success=True,
            message="Buzzer status retrieved",
            data=status
        )
    
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
