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
        if not HAS_PICAMERA:
            logger.error("camera.init_failed", error="picamera2 not installed")
            self._status = HardwareStatus.ERROR
            return False
            
        try:
            self._status = HardwareStatus.INITIALIZING
            
            # Use run_in_executor for blocking camera init
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._init_camera)
            
            self._status = HardwareStatus.READY
            logger.info("camera.initialized", resolution=self._resolution)
            return True
            
        except Exception as e:
            logger.error("camera.init_failed", error=str(e))
            self._status = HardwareStatus.ERROR
            return False

    def _init_camera(self):
        """Internal camera init."""
        self._camera = Picamera2()
        transform = Transform(hflip=1 if self._hflip else 0, vflip=1 if self._vflip else 0)
        
        # Configure for preview/capture
        config = self._camera.create_preview_configuration(
            main={"size": self._resolution},
            transform=transform
        )
        self._camera.configure(config)
        self._camera.start()

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
            await loop.run_in_executor(None, self._camera.stop_recording)
            self._streaming = False
            logger.info("camera.streaming_stopped")
        except Exception as e:
            logger.error("camera.stop_streaming_failed", error=str(e))

    async def get_frame(self) -> bytes:
        """Get the latest frame as bytes."""
        if not self._streaming:
            await self.start_streaming()
            
        # This is a blocking wait on a condition variable
        # Should be run in executor or replaced with an async-friendly condition
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._wait_for_frame)

    def _wait_for_frame(self) -> bytes:
        with self._streaming_output.condition:
            self._streaming_output.condition.wait(timeout=1.0)
            return self._streaming_output.frame

    async def cleanup(self) -> None:
        """Release camera resources."""
        if self._camera:
            if self._streaming:
                await self.stop_streaming()
            
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._camera.close)
            self._camera = None
            
        self._status = HardwareStatus.UNINITIALIZED

    def is_available(self) -> bool:
        return self._status == HardwareStatus.READY and HAS_PICAMERA

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": self._status.value,
            "resolution": self._resolution,
            "streaming": self._streaming,
            "has_picamera": HAS_PICAMERA
        }

    def get_health(self) -> Dict[str, Any]:
        return {
            "healthy": self._status == HardwareStatus.READY,
            "error": None if self._status == HardwareStatus.READY else "Camera not ready"
        }
