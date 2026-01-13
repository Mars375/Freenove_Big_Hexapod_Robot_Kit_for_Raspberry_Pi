"""
Camera control endpoints.
Handles camera rotation and configuration.
"""
from fastapi import APIRouter, HTTPException, status

from api.models import CameraConfigResponse, CameraRotateRequest, CommandResponse
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/rotate", response_model=CommandResponse)
async def rotate_camera(request: CameraRotateRequest) -> CommandResponse:
    """
    Rotate camera to specified angles.
    
    Args:
        request: Camera rotation angles (horizontal, vertical)
    
    Returns:
        Command response
    
    Example:
        POST /api/v1/camera/rotate
        {
            "horizontal": 45,
            "vertical": -20
        }
    """
    logger.info(
        "camera.rotate",
        horizontal=request.horizontal,
        vertical=request.vertical
    )
    
    if not settings.camera_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Camera is disabled"
        )
    
    command = f"CMD_CAMERA#{request.horizontal}#{request.vertical}"
    
    try:
        # TODO: Send command to robot
        
        return CommandResponse(
            success=True,
            message="Camera rotated successfully",
            data={
                "horizontal": request.horizontal,
                "vertical": request.vertical
            }
        )
    except Exception as e:
        logger.error("camera.rotate.error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rotate camera: {str(e)}"
        )


@router.get("/config", response_model=CameraConfigResponse)
async def get_camera_config() -> CameraConfigResponse:
    """
    Get current camera configuration.
    
    Returns:
        Camera configuration (enabled, fps, resolution, angles)
    """
    logger.debug("camera.config")
    
    return CameraConfigResponse(
        enabled=settings.camera_enabled,
        fps=settings.camera_fps,
        resolution=settings.camera_resolution,
        horizontal_angle=0,  # TODO: Get actual angle
        vertical_angle=0     # TODO: Get actual angle
    )


@router.post("/config", response_model=CommandResponse)
async def set_camera_config(
    fps: int | None = None,
    resolution: str | None = None
) -> CommandResponse:
    """
    Update camera configuration.
    
    Args:
        fps: New FPS value (optional)
        resolution: New resolution (optional)
    
    Returns:
        Command response
    """
    logger.info("camera.config.update", fps=fps, resolution=resolution)
    
    updates = {}
    if fps is not None:
        updates["fps"] = fps
    if resolution is not None:
        updates["resolution"] = resolution
    
    # TODO: Apply configuration changes
    
    return CommandResponse(
        success=True,
        message="Camera configuration updated",
        data=updates
    )
