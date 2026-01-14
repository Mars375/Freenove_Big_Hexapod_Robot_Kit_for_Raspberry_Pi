"""
Camera Panel - Live camera feed viewer
Display video stream from robot camera
"""
import asyncio
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QLabel, QComboBox
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap

from tachikoma.core.robot_controller import RobotController
from tachikoma.core.logger import get_logger

logger = get_logger(__name__)


class CameraPanel(QWidget):
    """Camera feed viewer panel."""
    
    def __init__(self, robot: RobotController):
        super().__init__()
        self.robot = robot
        self.camera_active = False
        self.camera_timer = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()
        
        # Controls
        controls_group = QGroupBox("📹 Camera Controls")
        controls_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("▶️ Start Camera")
        self.btn_start.setMinimumHeight(50)
        self.btn_start.clicked.connect(self.start_camera)
        controls_layout.addWidget(self.btn_start)
        
        self.btn_stop = QPushButton("⏹️ Stop Camera")
        self.btn_stop.setMinimumHeight(50)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_camera)
        controls_layout.addWidget(self.btn_stop)
        
        self.btn_snapshot = QPushButton("📸 Snapshot")
        self.btn_snapshot.setMinimumHeight(50)
        self.btn_snapshot.setEnabled(False)
        self.btn_snapshot.clicked.connect(self.take_snapshot)
        controls_layout.addWidget(self.btn_snapshot)
        
        # Resolution selector
        controls_layout.addWidget(QLabel("Resolution:"))
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["640x480", "1280x720", "1920x1080"])
        self.resolution_combo.setCurrentText("640x480")
        controls_layout.addWidget(self.resolution_combo)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Video feed display
        feed_group = QGroupBox("📺 Live Feed")
        feed_layout = QVBoxLayout()
        
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: #000000;
                border: 2px solid #3c3c3c;
                color: #666666;
            }
        """)
        self.video_label.setText("📹 Camera feed will appear here\n\nClick 'Start Camera' to begin")
        
        feed_layout.addWidget(self.video_label)
        
        # Status info
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        feed_layout.addWidget(self.status_label)
        
        feed_group.setLayout(feed_layout)
        layout.addWidget(feed_group)
        
        self.setLayout(layout)
    
    def start_camera(self):
        """Start camera feed."""
        try:
            logger.info("gui.camera.starting")
            
            # Initialize camera
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.robot.camera.start())
            
            self.camera_active = True
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.btn_snapshot.setEnabled(True)
            self.status_label.setText("Status: 🟢 Camera active")
            
            # Start timer for frame updates
            self.camera_timer = QTimer()
            self.camera_timer.timeout.connect(self.update_frame)
            self.camera_timer.start(33)  # ~30 FPS
            
            logger.info("gui.camera.started")
            
        except Exception as e:
            logger.error("gui.camera.start_failed", error=str(e))
            self.status_label.setText(f"Status: ❌ Failed to start: {e}")
    
    def stop_camera(self):
        """Stop camera feed."""
        try:
            if self.camera_timer:
                self.camera_timer.stop()
                self.camera_timer = None
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.robot.camera.stop())
            
            self.camera_active = False
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.btn_snapshot.setEnabled(False)
            
            self.video_label.setText("📹 Camera stopped\n\nClick 'Start Camera' to resume")
            self.status_label.setText("Status: ⚫ Camera stopped")
            
            logger.info("gui.camera.stopped")
            
        except Exception as e:
            logger.error("gui.camera.stop_failed", error=str(e))
    
    def update_frame(self):
        """Update video frame."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            frame = loop.run_until_complete(self.robot.camera.get_frame())
            
            if frame is not None:
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                
                # Convert to QImage
                qt_image = QImage(
                    rgb_frame.data,
                    w, h,
                    bytes_per_line,
                    QImage.Format.Format_RGB888
                )
                
                # Scale to fit label while maintaining aspect ratio
                pixmap = QPixmap.fromImage(qt_image)
                scaled_pixmap = pixmap.scaled(
                    self.video_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                
                self.video_label.setPixmap(scaled_pixmap)
                
        except Exception as e:
            logger.error("gui.camera.frame_update_failed", error=str(e))
    
    def take_snapshot(self):
        """Take a snapshot and save to file."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            frame = loop.run_until_complete(self.robot.camera.get_frame())
            
            if frame is not None:
                from datetime import datetime
                filename = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                filepath = f"logs/{filename}"
                
                cv2.imwrite(filepath, frame)
                logger.info("gui.camera.snapshot_saved", file=filepath)
                self.status_label.setText(f"Status: 📸 Snapshot saved: {filename}")
            
        except Exception as e:
            logger.error("gui.camera.snapshot_failed", error=str(e))
            self.status_label.setText(f"Status: ❌ Snapshot failed: {e}")
