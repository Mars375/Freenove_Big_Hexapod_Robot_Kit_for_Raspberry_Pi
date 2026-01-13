"""
LED control endpoints.
Handles LED modes, colors, and effects.
"""
from fastapi import APIRouter, HTTPException, status

from api.models import LEDColorRequest, LEDModeRequest, LEDResponse
from core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/mode", response_model=LEDResponse)
async def set_led_mode(request: LEDModeRequest) -> LEDResponse:
    """
    Set LED mode and optionally color.
    
    Args:
        request: LED mode and color
    
    Returns:
        LED response
    
    Example:
        POST /api/v1/leds/mode
        {
            "mode": "solid",
            "color": {"red": 255, "green": 0, "blue": 0}
        }
    """
    logger.info("leds.mode", mode=request.mode.value, color=request.color)
    
    try:
        if request.mode.value == "off":
            command = "CMD_LED_MOD#0"
        elif request.mode.value == "solid":
            command = "CMD_LED_MOD#1"
            if request.color:
                color_cmd = f"CMD_LED#{request.color.red}#{request.color.green}#{request.color.blue}"
                # TODO: Send both commands
        elif request.mode.value == "chase":
            command = "CMD_LED_MOD#2"
        elif request.mode.value == "blink":
            command = "CMD_LED_MOD#3"
        elif request.mode.value == "breathing":
            command = "CMD_LED_MOD#4"
        elif request.mode.value == "rainbow":
            command = "CMD_LED_MOD#5"
        
        # TODO: Send command to robot
        
        return LEDResponse(
            success=True,
            mode=request.mode.value,
            message=f"LED mode set to {request.mode.value}"
        )
    except Exception as e:
        logger.error("leds.mode.error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set LED mode: {str(e)}"
        )


@router.post("/color", response_model=LEDResponse)
async def set_led_color(request: LEDColorRequest) -> LEDResponse:
    """
    Set LED color (works with solid and blink modes).
    
    Args:
        request: RGB color values
    
    Returns:
        LED response
    """
    logger.info("leds.color", red=request.red, green=request.green, blue=request.blue)
    
    command = f"CMD_LED#{request.red}#{request.green}#{request.blue}"
    
    try:
        # TODO: Send command to robot
        
        return LEDResponse(
            success=True,
            mode="color",
            message=f"LED color set to RGB({request.red},{request.green},{request.blue})"
        )
    except Exception as e:
        logger.error("leds.color.error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set LED color: {str(e)}"
        )
