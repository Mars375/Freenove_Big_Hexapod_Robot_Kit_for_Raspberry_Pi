from fastapi import APIRouter, Depends, HTTPException
from core.dependencies import get_hardware_factory
from core.hardware.factory import HardwareFactory
from api.models.buzzer import BuzzerCommand, BuzzerResponse

router = APIRouter(prefix="/buzzer", tags=["buzzer"])


@router.post("/beep", response_model=BuzzerResponse)
async def beep(
    command: BuzzerCommand,
    hardware: HardwareFactory = Depends(get_hardware_factory)
) -> BuzzerResponse:
    buzzer = hardware.get_buzzer()
    
    if not buzzer or not buzzer.is_available():
        raise HTTPException(status_code=503, detail="Buzzer not available")
    
    success = buzzer.beep(
        frequency=command.frequency,
        duration=command.duration
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to beep")
    
    return BuzzerResponse(
        success=True,
        message=f"Beep at {command.frequency}Hz for {command.duration}s"
    )


@router.post("/stop", response_model=BuzzerResponse)
async def stop_buzzer(
    hardware: HardwareFactory = Depends(get_hardware_factory)
) -> BuzzerResponse:
    buzzer = hardware.get_buzzer()
    
    if not buzzer or not buzzer.is_available():
        raise HTTPException(status_code=503, detail="Buzzer not available")
    
    success = buzzer.stop()
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to stop buzzer")
    
    return BuzzerResponse(
        success=True,
        message="Buzzer stopped"
    )
