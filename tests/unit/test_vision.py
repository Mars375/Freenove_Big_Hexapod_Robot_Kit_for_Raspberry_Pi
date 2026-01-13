"""Unit tests for vision modules."""
from features.vision.object_detection import DetectedObject, ObjectDetector
from features.vision.qr_scanner import QRCode, QRScanner


def test_detected_object_creation():
    """Test DetectedObject creation and conversion."""
    obj = DetectedObject("person", 0.95, (100, 100, 50, 150))
    
    assert obj.label == "person"
    assert obj.confidence == 0.95
    
    obj_dict = obj.to_dict()
    assert obj_dict["label"] == "person"
    assert obj_dict["bbox"]["x"] == 100


def test_object_detector_initialization():
    """Test ObjectDetector initialization."""
    detector = ObjectDetector()
    
    assert detector.model_name == "yolov8n"
    assert detector.confidence_threshold == 0.5
    assert not detector.model_loaded


def test_qr_code_creation():
    """Test QRCode creation and conversion."""
    qr = QRCode("https://example.com", "QRCODE", (50, 50, 100, 100))
    
    assert qr.data == "https://example.com"
    assert qr.type == "QRCODE"
    
    qr_dict = qr.to_dict()
    assert qr_dict["data"] == "https://example.com"


def test_qr_scanner_initialization():
    """Test QRScanner initialization."""
    scanner = QRScanner()
    
    assert not scanner.scanner_ready
