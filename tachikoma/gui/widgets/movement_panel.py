"""
Movement Panel - Robot movement control
WASD keyboard control + visual buttons
"""
import asyncio
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QSlider, QLabel, QComboBox, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent

from tachikoma.core.robot_controller import RobotController
from tachikoma.core.logger import get_logger

logger = get_logger(__name__)


class MovementPanel(QWidget):
    """Movement control panel with joystick-style interface."""
    
    def __init__(self, robot: RobotController):
        super().__init__()
        self.robot = robot
        self.keys_pressed = set()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()
        
        # Direction controls
        control_group = QGroupBox("🦿 Direction Control")
        control_layout = QHBoxLayout()
        
        # Directional buttons (left side)
        buttons_layout = QGridLayout()
        
        # Forward button (row 0, col 1)
        self.btn_forward = QPushButton("⬆️\nForward\n(W)")
        self.btn_forward.setMinimumSize(120, 70)
        self.btn_forward.clicked.connect(lambda: self.move("forward"))
        buttons_layout.addWidget(self.btn_forward, 0, 1)
        
        # Left button (row 1, col 0)
        self.btn_left = QPushButton("⬅️\nLeft\n(A)")
        self.btn_left.setMinimumSize(120, 70)
        self.btn_left.clicked.connect(lambda: self.move("left"))
        buttons_layout.addWidget(self.btn_left, 1, 0)
        
        # Stop button (row 1, col 1)
        self.btn_stop = QPushButton("⏹️\nSTOP\n(S)")
        self.btn_stop.setMinimumSize(120, 70)
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #cc0000;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ff0000;
            }
            QPushButton:pressed {
                background-color: #990000;
            }
        """)
        self.btn_stop.clicked.connect(self.emergency_stop)
        buttons_layout.addWidget(self.btn_stop, 1, 1)
        
        # Right button (row 1, col 2)
        self.btn_right = QPushButton("➡️\nRight\n(D)")
        self.btn_right.setMinimumSize(120, 70)
        self.btn_right.clicked.connect(lambda: self.move("right"))
        buttons_layout.addWidget(self.btn_right, 1, 2)
        
        # Backward button (row 2, col 1)
        self.btn_backward = QPushButton("⬇️\nBackward\n(X)")
        self.btn_backward.setMinimumSize(120, 70)
        self.btn_backward.clicked.connect(lambda: self.move("backward"))
        buttons_layout.addWidget(self.btn_backward, 2, 1)
        
        control_layout.addLayout(buttons_layout)
        control_layout.addSpacing(30)
        
        # Settings panel (right side)
        settings_layout = QVBoxLayout()
        
        # Speed control
        speed_group = QGroupBox("⚡ Speed")
        speed_layout = QVBoxLayout()
        
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(20)
        self.speed_slider.setValue(8)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(2)
        speed_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("8")
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speed_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.speed_slider.valueChanged.connect(
            lambda v: self.speed_label.setText(str(v))
        )
        speed_layout.addWidget(self.speed_label)
        
        speed_group.setLayout(speed_layout)
        settings_layout.addWidget(speed_group)
        
        # Step height control
        height_group = QGroupBox("📏 Step Height")
        height_layout = QVBoxLayout()
        
        self.height_slider = QSlider(Qt.Orientation.Horizontal)
        self.height_slider.setMinimum(10)
        self.height_slider.setMaximum(100)
        self.height_slider.setValue(30)
        self.height_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.height_slider.setTickInterval(10)
        height_layout.addWidget(self.height_slider)
        
        self.height_label = QLabel("30 mm")
        self.height_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.height_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.height_slider.valueChanged.connect(
            lambda v: self.height_label.setText(f"{v} mm")
        )
        height_layout.addWidget(self.height_label)
        
        height_group.setLayout(height_layout)
        settings_layout.addWidget(height_group)
        
        # Gait selection
        gait_group = QGroupBox("🚶 Gait Type")
        gait_layout = QVBoxLayout()
        
        self.gait_combo = QComboBox()
        self.gait_combo.addItems(["TRIPOD", "WAVE", "RIPPLE"])
        self.gait_combo.setCurrentText("TRIPOD")
        self.gait_combo.setStyleSheet("font-size: 14px; padding: 8px;")
        gait_layout.addWidget(self.gait_combo)
        
        gait_group.setLayout(gait_layout)
        settings_layout.addWidget(gait_group)
        
        settings_layout.addStretch()
        control_layout.addLayout(settings_layout)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Keyboard instructions
        info_group = QGroupBox("⌨️ Keyboard Shortcuts")
        info_layout = QVBoxLayout()
        info_text = QLabel(
            "W - Forward | A - Left | D - Right | X - Backward\n"
            "S - Emergency Stop | Space - Stop smoothly"
        )
        info_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_text.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def move(self, direction: str):
        """Execute movement command."""
        speed = self.speed_slider.value()
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                self.robot.movement.move(direction, speed=speed)
            )
            logger.info("gui.movement.execute", direction=direction, speed=speed)
        except Exception as e:
            logger.error("gui.movement.failed", error=str(e))
    
    def emergency_stop(self):
        """Emergency stop."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.robot.movement.stop())
            logger.info("gui.movement.emergency_stop")
        except Exception as e:
            logger.error("gui.movement.stop_failed", error=str(e))
    
    def handle_key_press(self, event: QKeyEvent):
        """Handle keyboard press events."""
        key = event.key()
        
        # Prevent key repeat
        if event.isAutoRepeat():
            return
        
        if key in self.keys_pressed:
            return
        
        self.keys_pressed.add(key)
        
        # Map keys to directions
        key_map = {
            Qt.Key.Key_W: "forward",
            Qt.Key.Key_A: "left",
            Qt.Key.Key_D: "right",
            Qt.Key.Key_X: "backward",
            Qt.Key.Key_S: "stop",
            Qt.Key.Key_Space: "stop",
        }
        
        if key in key_map:
            direction = key_map[key]
            if direction == "stop":
                self.emergency_stop()
            else:
                self.move(direction)
    
    def handle_key_release(self, event: QKeyEvent):
        """Handle keyboard release events."""
        if event.isAutoRepeat():
            return
        
        key = event.key()
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
