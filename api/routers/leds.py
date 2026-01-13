from fastapi import APIRouter, HTTPException
from api.models import (
    StandardResponse,
    LEDColorRequest,
    LEDBrightnessRequest,
    LEDRainbowRequest,
)
from core.hardware.factory import get_hardware_factory
from core.exceptions import HardwareNotAvailableError
import structlog

router = APIRouter()
logger = structlog.get_logger()

@router.post("/color", response_model=StandardResponse)
async def set_color(request: LEDColorRequest):
    """Set all LEDs to a single color."""
    logger.info("leds.color", color=(request.r, request.g, request.b))
    try:
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()
        if not led_strip.is_available():
            raise HardwareNotAvailableError("LED strip is not available")
        
        if not led_strip.set_color(request.r, request.g, request.b):
            raise HTTPException(status_code=500, detail="Failed to set LED color")

        return StandardResponse(
            success=True,
            message="LED color set successfully",
            data={"color": [request.r, request.g, request.b]}
        )
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/brightness", response_model=StandardResponse)
async def set_brightness(request: LEDBrightnessRequest):
    """Adjust LED brightness."""
    logger.info("leds.brightness", brightness=request.brightness)
    try:
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()
        if not led_strip.is_available():
            raise HardwareNotAvailableError("LED strip is not available")
        
        if not led_strip.set_brightness(request.brightness):
            raise HTTPException(status_code=500, detail="Failed to set LED brightness")

        return StandardResponse(
            success=True,
            message=f"LED brightness set to {request.brightness}",
            data={"brightness": request.brightness}
        )
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/rainbow", response_model=StandardResponse)
async def start_rainbow(request: LEDRainbowRequest):
    """Start rainbow animation."""
    logger.info("leds.rainbow", iterations=request.iterations)
    try:
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()
        if not led_strip.is_available():
            raise HardwareNotAvailableError("LED strip is not available")

        if not led_strip.rainbow_cycle(request.iterations):
            raise HTTPException(status_code=500, detail="Failed to start rainbow animation")

        return StandardResponse(
            success=True,
            message=f"Rainbow animation started for {request.iterations} iterations",
            data={"iterations": request.iterations}
        )
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/off", response_model=StandardResponse)
async def turn_off():
    """Turn off all LEDs."""
    logger.info("leds.off")
    try:
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()
        if not led_strip.is_available():
            raise HardwareNotAvailableError("LED strip is not available")

        if not led_strip.off():
            raise HTTPException(status_code=500, detail="Failed to turn off LEDs")

        return StandardResponse(success=True, message="LEDs turned off")
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/status", response_model=StandardResponse)
async def get_status():
    """Get the current status of the LED strip."""
    logger.info("leds.status")
    try:
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()
        if not led_strip.is_available():
            raise HardwareNotAvailableError("LED strip is not available")

        status = led_strip.get_status()
        return StandardResponse(success=True, message="LED status retrieved successfully", data=status)
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
