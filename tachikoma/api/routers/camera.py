from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from tachikoma.api.models import CameraRotateRequest, StandardResponse
from tachikoma.core.robot_controller import get_robot_controller
from tachikoma.core.exceptions import HardwareNotAvailableError, CommandExecutionError
import structlog
from datetime import datetime, timezone
import asyncio

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


async def gen_frames():
    """Generator for camera frames."""
    robot = get_robot_controller()
    # Ensure camera driver is initialized
    # We use the raw driver from the factory via the camera controller abstraction if needed,
    # but the CameraController in core/hardware/camera.py is just a pan/tilt abstraction.
    # The actual driver is in core/hardware/drivers/camera.py.
    # Let's get the camera driver from the factory.
    from tachikoma.core.hardware.factory import get_hardware_factory
    factory = get_hardware_factory()
    camera_driver = await factory.get_camera()
    
    # Create a small red "No Signal" JPEG as fallback
    import cv2
    import numpy as np
    no_signal = np.zeros((240, 320, 3), dtype=np.uint8)
    no_signal[:, :] = [50, 50, 150] # Dark Red
    cv2.putText(no_signal, "NO SIGNAL", (80, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    _, buffer = cv2.imencode('.jpg', no_signal)
    NO_SIGNAL_FRAME = buffer.tobytes()

    empty_count = 0
    while True:
        try:
            frame = await camera_driver.get_frame()
            if frame:
                empty_count = 0
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                empty_count += 1
                if empty_count > 300: # Approx 3 seconds
                    # Yield a NO SIGNAL frame periodically to keep connection alive
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + NO_SIGNAL_FRAME + b'\r\n')
                    
                    if empty_count % 500 == 0:
                        logger.warning("camera.stream_stalled", msg="No frames received for 5s")
            await asyncio.sleep(0.01) # Yield to other tasks
        except Exception as e:
            logger.error("camera.feed_error", error=str(e))
            break


@router.get("/video_feed")
async def video_feed():
    """MJPEG video streaming feed."""
    return StreamingResponse(
        gen_frames(),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )
