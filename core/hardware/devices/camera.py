import logging
from typing import Optional, Dict, Any
import numpy as np
from core.hardware.interfaces.base import IHardwareComponent, HardwareStatus

try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False
    try:
        import cv2
        CV2_AVAILABLE = True
    except ImportError:
        CV2_AVAILABLE = False


class Camera(IHardwareComponent):
    """Contrôleur pour caméra (Picamera2 ou OpenCV fallback)"""
    
    def __init__(self, width: int = 640, height: int = 480, camera_index: int = 0):
        self.width = width
        self.height = height
        self.camera_index = camera_index
        
        self._camera = None
        self.logger = logging.getLogger(__name__)
        self._status = HardwareStatus.UNINITIALIZED
        self._using_picamera = False
    
    async def initialize(self) -> bool:
        self._status = HardwareStatus.INITIALIZING
        
        # Try Picamera2 first
        if PICAMERA_AVAILABLE:
            try:
                self._camera = Picamera2()
                config = self._camera.create_preview_configuration(
                    main={"size": (self.width, self.height)}
                )
                self._camera.configure(config)
                self._camera.start()
                
                self._using_picamera = True
                self._status = HardwareStatus.READY
                self.logger.info(f"Picamera2 initialized ({self.width}x{self.height})")
                return True
                
            except Exception as e:
                self.logger.warning(f"Failed to initialize Picamera2: {e}")
        
        # Fallback to OpenCV
        if CV2_AVAILABLE:
            try:
                self._camera = cv2.VideoCapture(self.camera_index)
                self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                
                if not self._camera.isOpened():
                    raise Exception("Cannot open camera")
                
                self._using_picamera = False
                self._status = HardwareStatus.READY
                self.logger.info(f"OpenCV camera initialized ({self.width}x{self.height})")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenCV camera: {e}")
        
        self._status = HardwareStatus.ERROR
        self.logger.error("No camera available")
        return False
    
    async def cleanup(self) -> None:
        try:
            if self._camera:
                if self._using_picamera:
                    self._camera.stop()
                else:
                    self._camera.release()
            
            self._camera = None
            self._status = HardwareStatus.DISCONNECTED
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def capture_frame(self) -> Optional[np.ndarray]:
        if not self.is_available():
            return None
        
        try:
            if self._using_picamera:
                frame = self._camera.capture_array()
                return frame
            else:
                ret, frame = self._camera.read()
                return frame if ret else None
                
        except Exception as e:
            self.logger.error(f"Failed to capture frame: {e}")
            return None
    
    def get_frame_size(self) -> tuple:
        return (self.width, self.height)
    
    def is_available(self) -> bool:
        return self._status == HardwareStatus.READY and self._camera is not None
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "type": "camera",
            "resolution": f"{self.width}x{self.height}",
            "backend": "picamera2" if self._using_picamera else "opencv",
            "status": self._status.value,
            "available": self.is_available()
        }
    
    def get_health(self) -> Dict[str, Any]:
        return {
            "healthy": self.is_available(),
            "backend": "picamera2" if self._using_picamera else "opencv",
            "status": self._status.value
        }
