"""Camera driver for Freenove Hexapod with picamera2.

Based on Freenove camera.py analysis.
"""
import io
from typing import Optional
from threading import Condition

try:
    from picamera2 import Picamera2
    from picamera2.encoders import JpegEncoder, H264Encoder
    from picamera2.outputs import FileOutput
    from libcamera import Transform
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False


class StreamingOutput(io.BufferedIOBase):
    """Streaming output for JPEG frames."""
    
    def __init__(self):
        self.frame = None
        self.condition = Condition()
    
    def write(self, buf: bytes) -> int:
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
        return len(buf)


class CameraController:
    """Camera controller with streaming and recording."""
    
    def __init__(
        self,
        preview_size: tuple = (640, 480),
        stream_size: tuple = (400, 300),
        hflip: bool = False,
        vflip: bool = False
    ):
        self.preview_size = preview_size
        self.stream_size = stream_size
        self.streaming = False
        
        if not PICAMERA2_AVAILABLE:
            print("picamera2 not available, using mock camera")
            self.camera = None
            return
        
        try:
            self.camera = Picamera2()
            self.transform = Transform(hflip=1 if hflip else 0, vflip=1 if vflip else 0)
            self.streaming_output = StreamingOutput()
        except Exception as e:
            print(f"Camera init error: {e}")
            self.camera = None
    
    def start_preview(self):
        """Start camera preview."""
        if self.camera:
            config = self.camera.create_preview_configuration(
                main={"size": self.preview_size},
                transform=self.transform
            )
            self.camera.configure(config)
            self.camera.start()
    
    def start_streaming(self):
        """Start JPEG streaming."""
        if self.camera and not self.streaming:
            config = self.camera.create_video_configuration(
                main={"size": self.stream_size},
                transform=self.transform
            )
            self.camera.configure(config)
            encoder = JpegEncoder()
            self.camera.start_recording(encoder, FileOutput(self.streaming_output))
            self.streaming = True
    
    def get_frame(self) -> Optional[bytes]:
        """Get current JPEG frame."""
        if self.streaming:
            with self.streaming_output.condition:
                self.streaming_output.condition.wait()
                return self.streaming_output.frame
        return None
    
    def stop_streaming(self):
        """Stop streaming."""
        if self.camera and self.streaming:
            self.camera.stop_recording()
            self.streaming = False
    
    def capture_image(self, filename: str):
        """Capture still image."""
        if self.camera:
            return self.camera.capture_file(filename)
    
    def close(self):
        """Cleanup."""
        if self.streaming:
            self.stop_streaming()
        if self.camera:
            self.camera.close()
