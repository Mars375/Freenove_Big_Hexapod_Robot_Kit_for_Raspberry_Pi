from fastapi import APIRouter, HTTPException
from api.models import CameraRotateRequest, StandardResponse
from core.robot_controller import get_robot_controller
from core.exceptions import HardwareNotAvailableError, CommandExecutionError
import structlog
from datetime import datetime, timezone

router = APIRouter()
logger = structlog.get_logger()


@router.post("/rotate", response_model=StandardResponse)
async def rotate_camera(request: CameraRotateRequest):
    """Rotate camera servos"""
    logger.info("camera.rotate", horizontal=request.horizontal, vertical=request.vertical)
    
    try:
        robot = get_robot_controller()
        await robot.camera.rotate(
            horizontal=request.horizontal,
            vertical=request.vertical
        )
        
        return StandardResponse(
            success=True,
            message="Camera rotated successfully",
            data={
                "horizontal": request.horizontal,
                "vertical": request.vertical
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except CommandExecutionError as e:
        raise HTTPException(status_code=500, detail=str(e))
