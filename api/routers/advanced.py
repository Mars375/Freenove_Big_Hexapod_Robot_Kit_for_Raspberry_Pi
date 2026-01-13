"""
Advanced features endpoints.
Provides access to obstacle avoidance, object detection, and QR scanning.
"""
from fastapi import APIRouter, HTTPException, status

from core.logger import get_logger
from features.autonomous.obstacle_avoidance import get_obstacle_avoidance
from features.vision.object_detection import get_object_detector
from features.vision.qr_scanner import get_qr_scanner

logger = get_logger(__name__)
router = APIRouter()


@router.get("/obstacle-avoidance/analyze")
async def analyze_obstacle(distance: float) -> dict:
    """
    Analyze obstacle distance and get avoidance suggestion.
    
    Args:
        distance: Distance from ultrasonic sensor (cm)
        
    Returns:
        Avoidance maneuver suggestion
    """
    logger.info("advanced.obstacle_avoidance.analyze", distance=distance)
    
    avoidance = get_obstacle_avoidance()
    maneuver = avoidance.suggest_maneuver(distance)
    
    return maneuver


@router.get("/vision/detect")
async def detect_objects() -> dict:
    """
    Detect objects in current camera frame.
    
    Returns:
        List of detected objects
    """
    logger.info("advanced.vision.detect")
    
    detector = get_object_detector()
    
    if not detector.model_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Object detection model not loaded"
        )
    
    # TODO: Get actual frame from camera
    frame = None
    objects = detector.detect(frame)
    
    return {
        "objects": [obj.to_dict() for obj in objects],
        "count": len(objects)
    }


@router.get("/vision/scan-qr")
async def scan_qr_codes() -> dict:
    """
    Scan for QR codes in current camera frame.
    
    Returns:
        List of detected QR codes
    """
    logger.info("advanced.vision.scan_qr")
    
    scanner = get_qr_scanner()
    
    if not scanner.scanner_ready:
        scanner.initialize()
    
    # TODO: Get actual frame from camera
    frame = None
    qr_codes = scanner.scan(frame)
    
    return {
        "qr_codes": [qr.to_dict() for qr in qr_codes],
        "count": len(qr_codes)
    }
