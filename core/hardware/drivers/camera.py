"""Camera driver using Picamera2."""
import asyncio
import io
import time
import structlog
from typing import Optional, Dict, Any, Tuple
from threading import Condition

try:
    from picamera2 import Picamera2, Preview
    from picamera2.encoders import JpegEncoder
    from libcamera import Transform
    HAS_PICAMERA = True
except ImportError:
    HAS_PICAMERA = False

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

from core.hardware.interfaces.base import IHardwareComponent, HardwareStatus

logger = structlog.get_logger()

class StreamingOutput(io.BufferedIOBase):
    """Buffered output for camera streaming."""
    def __init__(self):
        self.frame = b""
        self.condition = Condition()

    def write(self, buf: bytes) -> int:
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
        return len(buf)

class CameraDriver(IHardwareComponent):
    """Modern driver for Raspberry Pi Camera using Picamera2."""
    
    def __init__(
        self,
        resolution: Tuple[int, int] = (640, 480),
        framerate: int = 30,
        hflip: bool = False,
        vflip: bool = False
    ):
        self._resolution = resolution
        self._framerate = framerate
        self._hflip = hflip
        self._vflip = vflip
        
        self._camera: Optional[Any] = None
        self._status = HardwareStatus.UNINITIALIZED
        self._streaming_output = StreamingOutput()
        self._streaming = False

    async def initialize(self) -> bool:
        """Initialize the camera."""
        if not HAS_PICAMERA and not HAS_OPENCV:
            logger.error("camera.init_failed", error="Neither picamera2 nor opencv-python installed")
            self._status = HardwareStatus.ERROR
            return False
            
        try:
            self._status = HardwareStatus.INITIALIZING
            
            # Use run_in_executor for blocking camera init
            loop = asyncio.get_running_loop()
            if HAS_PICAMERA:
                await loop.run_in_executor(None, self._init_camera_pi)
            else:
                await loop.run_in_executor(None, self._init_camera_cv2)
            
            self._status = HardwareStatus.READY
            logger.info("camera.initialized", resolution=self._resolution, mode="picamera2" if HAS_PICAMERA else "opencv")
            return True
            
        except Exception as e:
            logger.error("camera.init_failed", error=str(e))
            self._status = HardwareStatus.ERROR
            return False

    def _init_camera_pi(self):
        """Internal camera init using Picamera2."""
        self._camera = Picamera2()
        transform = Transform(hflip=1 if self._hflip else 0, vflip=1 if self._vflip else 0)
        
        # Configure for preview/capture
        config = self._camera.create_preview_configuration(
            main={"size": self._resolution},
            transform=transform
        )
        self._camera.configure(config)
        self._camera.start()

    def _init_camera_cv2(self):
        """Internal camera init using OpenCV."""
        # Force V4L2 backend which is more reliable on Pi
        self._camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
        if self._camera.isOpened():
            self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, self._resolution[0])
            self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self._resolution[1])
            # Set MJPEG format
            self._camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            
            actual_w = self._camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_h = self._camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            logger.info("camera.cv2_opened", requested=self._resolution, actual=(actual_w, actual_h))
            
            # Warm-up: discard frames until SUCCESS or timeout
            start_time = time.time()
            warmup_success = False
            while time.time() - start_time < 2.0:
                ret, _ = self._camera.read()
                if ret:
                    warmup_success = True
                    break
                time.sleep(0.1)
                
            if not warmup_success:
                logger.warning("camera.cv2_warmup_failed", msg="Camera opened but no frames captured during warmup")
        else:
            raise RuntimeError("Could not open OpenCV video capture on index 0")

    async def start_streaming(self):
        """Start JPEG streaming."""
        if not self._camera or self._streaming:
            return
            
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._start_recording)
            self._streaming = True
            logger.info("camera.streaming_started")
        except Exception as e:
            logger.error("camera.streaming_failed", error=str(e))

    def _start_recording(self):
        encoder = JpegEncoder()
        from picamera2.outputs import FileOutput
        output = FileOutput(self._streaming_output)
        self._camera.start_recording(encoder, output)

    async def stop_streaming(self):
        """Stop JPEG streaming."""
        if not self._camera or not self._streaming:
            return
            
        try:
            loop = asyncio.get_running_loop()
            if HAS_PICAMERA:
                await loop.run_in_executor(None, self._camera.stop_recording)
            self._streaming = False
            logger.info("camera.streaming_stopped")
        except Exception as e:
            logger.error("camera.stop_streaming_failed", error=str(e))

    async def get_frame(self) -> bytes:
        """Get the latest frame as bytes."""
        if not self._streaming and HAS_PICAMERA:
            await self.start_streaming()
            
        loop = asyncio.get_running_loop()
        if HAS_PICAMERA:
            return await loop.run_in_executor(None, self._wait_for_frame_pi)
        else:
            return await loop.run_in_executor(None, self._get_frame_cv2)

    def _wait_for_frame_pi(self) -> bytes:
        with self._streaming_output.condition:
            if self._streaming_output.condition.wait(timeout=1.0):
                return self._streaming_output.frame
            return b""

    def _get_frame_cv2(self) -> bytes:
        if not self._camera:
            return b""
            
        ret, frame = self._camera.read()
        if not ret:
            # Log failure occasionally to avoid spam
            if not hasattr(self, "_last_fail_log"):
                self._last_fail_log = 0
            if time.time() - self._last_fail_log > 5:
                logger.warning("camera.cv2_read_failed")
                self._last_fail_log = time.time()
            return b""
            
        if self._hflip:
            frame = cv2.flip(frame, 1)
        if self._vflip:
            frame = cv2.flip(frame, 0)
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return buffer.tobytes() if ret else b""

    async def cleanup(self) -> None:
        """Release camera resources."""
        if self._camera:
            if self._streaming:
                await self.stop_streaming()
            
            loop = asyncio.get_running_loop()
            if HAS_PICAMERA:
                await loop.run_in_executor(None, self._camera.close)
            else:
                await loop.run_in_executor(None, self._camera.release)
            self._camera = None
            
        self._status = HardwareStatus.UNINITIALIZED

    def is_available(self) -> bool:
        return self._status == HardwareStatus.READY and (HAS_PICAMERA or HAS_OPENCV)

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": self._status.value,
            "resolution": self._resolution,
            "streaming": self._streaming,
            "has_picamera": HAS_PICAMERA,
            "has_opencv": HAS_OPENCV,
            "mode": "picamera2" if HAS_PICAMERA else "opencv" if HAS_OPENCV else "none"
        }

    def get_health(self) -> Dict[str, Any]:
        return {
            "healthy": self._status == HardwareStatus.READY,
            "error": None if self._status == HardwareStatus.READY else "Camera not ready"
        }
