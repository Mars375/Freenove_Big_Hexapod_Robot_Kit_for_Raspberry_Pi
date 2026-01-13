from fastapi import APIRouter, HTTPException
from api.models import LEDModeRequest, StandardResponse
from core.robot_controller import get_robot_controller
from core.exceptions import HardwareNotAvailableError, CommandExecutionError
import structlog

router = APIRouter()
logger = structlog.get_logger()


@router.post("/mode", response_model=StandardResponse)
async def set_led_mode(request: LEDModeRequest):
    """Set LED mode (solid, rainbow, breathing, off)"""
    logger.info("leds.mode", mode=request.mode, color=request.color)
    
    try:
        robot = get_robot_controller()
        
        if request.color:
            await robot.leds.set_mode(
                request.mode,
                request.color.red,
                request.color.green,
                request.color.blue
            )
        else:
            await robot.leds.set_mode(request.mode)
        
        return StandardResponse(
            success=True,
            message=f"LED mode set to {request.mode}",
            mode=request.mode
        )
    
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except CommandExecutionError as e:
        raise HTTPException(status_code=500, detail=str(e))
