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
import asyncio
from typing import Optional

router = APIRouter()
logger = structlog.get_logger()

# Global task pour l'animation en cours
_running_animation_task: Optional[asyncio.Task] = None
_current_animation_name: Optional[str] = None


async def _cancel_current_animation():
    """Cancel the currently running animation if any."""
    global _running_animation_task, _current_animation_name
    
    if _running_animation_task and not _running_animation_task.done():
        logger.info("leds.cancelling_animation", animation=_current_animation_name)
        _running_animation_task.cancel()
        try:
            await _running_animation_task
        except asyncio.CancelledError:
            pass
        _running_animation_task = None
        _current_animation_name = None


async def _start_animation_task(coro, animation_name: str):
    """Start a new animation task after cancelling the current one."""
    global _running_animation_task, _current_animation_name
    
    # Cancel previous animation
    await _cancel_current_animation()
    
    # Start new animation
    _running_animation_task = asyncio.create_task(coro)
    _current_animation_name = animation_name
    logger.info("leds.animation_started_background", animation=animation_name)


@router.post("/color", response_model=StandardResponse)
async def set_color(request: LEDColorRequest):
    """Set all LEDs to a single color."""
    logger.info("leds.color", color=(request.r, request.g, request.b))
    try:
        # Cancel any running animation
        await _cancel_current_animation()
        
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
    """Start rainbow animation in background."""
    logger.info("leds.rainbow", duration=request.duration, speed=request.speed)
    try:
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()
        if not led_strip.is_available():
            raise HardwareNotAvailableError("LED strip is not available")

        # Start animation in background
        await _start_animation_task(
            led_strip.rainbow_cycle(duration=request.duration, speed=request.speed),
            "rainbow"
        )

        return StandardResponse(
            success=True,
            message=f"Rainbow animation started for {request.duration}s",
            data={"duration": request.duration, "speed": request.speed}
        )
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/police", response_model=StandardResponse)
async def start_police(request: LEDPoliceRequest):
    """Start police siren animation in background."""
    logger.info("leds.police", duration=request.duration, speed=request.speed)
    try:
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()
        if not led_strip.is_available():
            raise HardwareNotAvailableError("LED strip is not available")

        # Start animation in background
        await _start_animation_task(
            led_strip.police(duration=request.duration, speed=request.speed),
            "police"
        )

        return StandardResponse(
            success=True,
            message=f"Police animation started for {request.duration}s",
            data={"duration": request.duration, "speed": request.speed}
        )
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/breathing", response_model=StandardResponse)
async def start_breathing(request: LEDBreathingRequest):
    """Start breathing animation in background."""
    logger.info("leds.breathing", color=(request.r, request.g, request.b), duration=request.duration)
    try:
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()
        if not led_strip.is_available():
            raise HardwareNotAvailableError("LED strip is not available")

        # Start animation in background
        await _start_animation_task(
            led_strip.breathing(
                r=request.r, g=request.g, b=request.b,
                duration=request.duration, speed=request.speed
            ),
            "breathing"
        )

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
    """Start fire animation in background."""
    logger.info("leds.fire", duration=request.duration, intensity=request.intensity)
    try:
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()
        if not led_strip.is_available():
            raise HardwareNotAvailableError("LED strip is not available")

        # Start animation in background
        await _start_animation_task(
            led_strip.fire(duration=request.duration, intensity=request.intensity),
            "fire"
        )

        return StandardResponse(
            success=True,
            message=f"Fire animation started for {request.duration}s",
            data={"duration": request.duration, "intensity": request.intensity}
        )
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/wave", response_model=StandardResponse)
async def start_wave(request: LEDWaveRequest):
    """Start wave animation in background."""
    logger.info("leds.wave", color=(request.r, request.g, request.b), duration=request.duration)
    try:
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()
        if not led_strip.is_available():
            raise HardwareNotAvailableError("LED strip is not available")

        # Start animation in background
        await _start_animation_task(
            led_strip.wave(
                r=request.r, g=request.g, b=request.b,
                duration=request.duration, speed=request.speed
            ),
            "wave"
        )

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
    """Start strobe animation in background."""
    logger.info("leds.strobe", color=(request.r, request.g, request.b), duration=request.duration)
    try:
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()
        if not led_strip.is_available():
            raise HardwareNotAvailableError("LED strip is not available")

        # Start animation in background
        await _start_animation_task(
            led_strip.strobe(
                r=request.r, g=request.g, b=request.b,
                duration=request.duration, speed=request.speed
            ),
            "strobe"
        )

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
    """Start chase animation in background."""
    logger.info("leds.chase", color=(request.r, request.g, request.b), duration=request.duration)
    try:
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()
        if not led_strip.is_available():
            raise HardwareNotAvailableError("LED strip is not available")

        # Start animation in background
        await _start_animation_task(
            led_strip.chase(
                r=request.r, g=request.g, b=request.b,
                duration=request.duration, speed=request.speed
            ),
            "chase"
        )

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
    """Turn off all LEDs and stop any running animation."""
    logger.info("leds.off")
    try:
        # Cancel running animation
        await _cancel_current_animation()
        
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()
        if not led_strip.is_available():
            raise HardwareNotAvailableError("LED strip is not available")

        if not led_strip.off():
            raise HTTPException(status_code=500, detail="Failed to turn off LEDs")

        return StandardResponse(success=True, message="LEDs turned off")
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/stop", response_model=StandardResponse)
async def stop_animation():
    """Stop the currently running animation."""
    logger.info("leds.stop")
    
    global _current_animation_name
    
    if _running_animation_task and not _running_animation_task.done():
        animation_name = _current_animation_name
        await _cancel_current_animation()
        return StandardResponse(
            success=True,
            message=f"Animation '{animation_name}' stopped",
            data={"stopped_animation": animation_name}
        )
    
    return StandardResponse(
        success=True,
        message="No animation running",
        data={"stopped_animation": None}
    )


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
        
        # Add animation status
        status["animation_running"] = _running_animation_task is not None and not _running_animation_task.done()
        status["current_animation"] = _current_animation_name if status["animation_running"] else None
        
        return StandardResponse(
            success=True,
            message="LED status retrieved successfully",
            data=status
        )
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
