from fastapi import APIRouter, HTTPException
from tachikoma.api.models import BuzzerCommand, StandardResponse
from tachikoma.core.robot_controller import get_robot_controller
from tachikoma.core.exceptions import HardwareNotAvailableError, CommandExecutionError
import structlog

router = APIRouter()
logger = structlog.get_logger()


@router.post("/beep", response_model=StandardResponse)
async def beep_buzzer(command: BuzzerCommand):
    """Activate buzzer with specified frequency and duration"""
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
            message=f"Buzzer activated: {command.frequency}Hz for {command.duration}s"
        )
    
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except CommandExecutionError as e:
        raise HTTPException(status_code=500, detail=str(e))
