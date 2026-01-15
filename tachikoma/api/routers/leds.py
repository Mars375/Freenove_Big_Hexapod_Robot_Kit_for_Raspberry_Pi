from fastapi import APIRouter, HTTPException
from tachikoma.api.models import (
    StandardResponse,
    LEDColorRequest,
    LEDBrightnessRequest,
    LEDRainbowRequest,
    LEDPoliceRequest,
    LEDBreathingRequest,
    LEDFireRequest,
    LEDWaveRequest,
    LEDStrobeRequest,
    LEDChaseRequest,
)
from tachikoma.core.hardware.factory import get_hardware_factory
from tachikoma.core.exceptions import HardwareNotAvailableError
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

@router.post("/police", response_model=StandardResponse)
async def start_police(request: LEDPoliceRequest):
    """Start police siren animation (red/blue alternating)."""
    logger.info("leds.police", duration=request.duration, speed=request.speed)
    try:
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()
        if not led_strip.is_available():
            raise HardwareNotAvailableError("LED strip is not available")

        # ✅ AJOUT de await
        if not await led_strip.police(duration=request.duration, speed=request.speed):
            raise HTTPException(status_code=500, detail="Failed to start police animation")

        return StandardResponse(
            success=True,
            message=f"Police animation started for {request.duration}s",
            data={"duration": request.duration, "speed": request.speed}
        )
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/breathing", response_model=StandardResponse)
async def start_breathing(request: LEDBreathingRequest):
    """Start breathing animation (fade in/out)."""
    logger.info("leds.breathing", color=(request.r, request.g, request.b), duration=request.duration)
    try:
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()
        if not led_strip.is_available():
            raise HardwareNotAvailableError("LED strip is not available")

        # ✅ AJOUT de await
        if not await led_strip.breathing(
            r=request.r, g=request.g, b=request.b,
            duration=request.duration, speed=request.speed
        ):
            raise HTTPException(status_code=500, detail="Failed to start breathing animation")

        return StandardResponse(
            success=True,
            message=f"Breathing animation started for {request.duration}s",
            data={
                "color": [request.r, request.g, request.b],
                "duration": request.duration,
                "speed": request.speed
            }
        )
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/fire", response_model=StandardResponse)
async def start_fire(request: LEDFireRequest):
    """Start fire animation (flickering red/orange/yellow)."""
    logger.info("leds.fire", duration=request.duration, intensity=request.intensity)
    try:
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()
        if not led_strip.is_available():
            raise HardwareNotAvailableError("LED strip is not available")

        # ✅ AJOUT de await
        if not await led_strip.fire(duration=request.duration, intensity=request.intensity):
            raise HTTPException(status_code=500, detail="Failed to start fire animation")

        return StandardResponse(
            success=True,
            message=f"Fire animation started for {request.duration}s",
            data={"duration": request.duration, "intensity": request.intensity}
        )
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/wave", response_model=StandardResponse)
async def start_wave(request: LEDWaveRequest):
    """Start wave animation (color wave propagation)."""
    logger.info("leds.wave", color=(request.r, request.g, request.b), duration=request.duration)
    try:
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()
        if not led_strip.is_available():
            raise HardwareNotAvailableError("LED strip is not available")

        # ✅ AJOUT de await
        if not await led_strip.wave(
            r=request.r, g=request.g, b=request.b,
            duration=request.duration, speed=request.speed
        ):
            raise HTTPException(status_code=500, detail="Failed to start wave animation")

        return StandardResponse(
            success=True,
            message=f"Wave animation started for {request.duration}s",
            data={
                "color": [request.r, request.g, request.b],
                "duration": request.duration,
                "speed": request.speed
            }
        )
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/strobe", response_model=StandardResponse)
async def start_strobe(request: LEDStrobeRequest):
    """Start strobe animation (rapid on/off flashing)."""
    logger.info("leds.strobe", color=(request.r, request.g, request.b), duration=request.duration)
    try:
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()
        if not led_strip.is_available():
            raise HardwareNotAvailableError("LED strip is not available")

        # ✅ AJOUT de await
        if not await led_strip.strobe(
            r=request.r, g=request.g, b=request.b,
            duration=request.duration, speed=request.speed
        ):
            raise HTTPException(status_code=500, detail="Failed to start strobe animation")

        return StandardResponse(
            success=True,
            message=f"Strobe animation started for {request.duration}s",
            data={
                "color": [request.r, request.g, request.b],
                "duration": request.duration,
                "speed": request.speed
            }
        )
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/chase", response_model=StandardResponse)
async def start_chase(request: LEDChaseRequest):
    """Start chase animation (LEDs running in sequence)."""
    logger.info("leds.chase", color=(request.r, request.g, request.b), duration=request.duration)
    try:
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()
        if not led_strip.is_available():
            raise HardwareNotAvailableError("LED strip is not available")

        # ✅ AJOUT de await
        if not await led_strip.chase(
            r=request.r, g=request.g, b=request.b,
            duration=request.duration, speed=request.speed
        ):
            raise HTTPException(status_code=500, detail="Failed to start chase animation")

        return StandardResponse(
            success=True,
            message=f"Chase animation started for {request.duration}s",
            data={
                "color": [request.r, request.g, request.b],
                "duration": request.duration,
                "speed": request.speed
            }
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
