"""
Buzzer control endpoints.
Handles buzzer beeps and sounds.
"""
from fastapi import APIRouter, HTTPException, status

from api.models import BuzzerRequest, BuzzerResponse
from core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/beep", response_model=BuzzerResponse)
async def beep_buzzer(request: BuzzerRequest) -> BuzzerResponse:
    """
    Control buzzer beep.
    
    Args:
        request: Buzzer control (enabled, duration)
    
    Returns:
        Buzzer response
    
    Example:
        POST /api/v1/buzzer/beep
        {
            "enabled": true,
            "duration": 0.5
        }
    """
    logger.info("buzzer.beep", enabled=request.enabled, duration=request.duration)
    
    command = f"CMD_BUZZER#{'1' if request.enabled else '0'}"
    
    try:
        # TODO: Send command to robot
        # If duration is set, schedule stop after duration
        
        return BuzzerResponse(
            success=True,
            enabled=request.enabled,
            message=f"Buzzer {'enabled' if request.enabled else 'disabled'}"
        )
    except Exception as e:
        logger.error("buzzer.beep.error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to control buzzer: {str(e)}"
        )
