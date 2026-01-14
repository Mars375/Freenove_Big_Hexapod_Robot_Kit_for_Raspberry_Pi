"""
Calibration Panel - Servo calibration interface
Fine-tune each servo angle and save to point.txt
"""
import asyncio
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QComboBox, QLabel, QDial, QLCDNumber, QMessageBox
)
from PyQt6.QtCore import Qt

from tachikoma.core.robot_controller import RobotController
from tachikoma.core.logger import get_logger

logger = get_logger(__name__)


class CalibrationPanel(QWidget):
    """Servo calibration interface."""
    
    def __init__(self, robot: RobotController):
        super().__init__()
        self.robot = robot
        self.current_leg = 0
        self.current_joint = "coxa"
        self.calibration_data = {}
        self.init_ui()
        self.load_calibration()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()
        
        # Leg selection
        leg_group = QGroupBox("⚙️ Leg Selection")
        leg_layout = QVBoxLayout()
        
        self.leg_combo = QComboBox()
        self.leg_combo.addItems([
            "Leg 0: Front Right",
            "Leg 1: Middle Right",
            "Leg 2: Back Right",
            "Leg 3: Back Left",
            "Leg 4: Middle Left",
            "Leg 5: Front Left"
        ])
        self.leg_combo.currentIndexChanged.connect(self.on_leg_changed)
        self.leg_combo.setStyleSheet("font-size: 14px; padding: 8px;")
        leg_layout.addWidget(self.leg_combo)
        
        leg_group.setLayout(leg_layout)
        layout.addWidget(leg_group)
        
        # Joint selection
        joint_group = QGroupBox("🔧 Joint Selection")
        joint_layout = QHBoxLayout()
        
        self.btn_coxa = QPushButton("Coxa (Hip)")
        self.btn_coxa.setCheckable(True)
        self.btn_coxa.setChecked(True)
        self.btn_coxa.clicked.connect(lambda: self.select_joint("coxa"))
        self.btn_coxa.setMinimumHeight(50)
        
        self.btn_femur = QPushButton("Femur (Upper)")
        self.btn_femur.setCheckable(True)
        self.btn_femur.clicked.connect(lambda: self.select_joint("femur"))
        self.btn_femur.setMinimumHeight(50)
        
        self.btn_tibia = QPushButton("Tibia (Lower)")
        self.btn_tibia.setCheckable(True)
        self.btn_tibia.clicked.connect(lambda: self.select_joint("tibia"))
        self.btn_tibia.setMinimumHeight(50)
        
        joint_layout.addWidget(self.btn_coxa)
        joint_layout.addWidget(self.btn_femur)
        joint_layout.addWidget(self.btn_tibia)
        
        joint_group.setLayout(joint_layout)
        layout.addWidget(joint_group)
        
        # Angle control
        angle_group = QGroupBox("🎯 Angle Control")
        angle_layout = QVBoxLayout()
        
        # Big dial for visual feedback
        dial_layout = QHBoxLayout()
        dial_layout.addStretch()
        
        self.angle_dial = QDial()
        self.angle_dial.setMinimum(0)
        self.angle_dial.setMaximum(180)
        self.angle_dial.setValue(90)
        self.angle_dial.setNotchesVisible(True)
        self.angle_dial.setMinimumSize(200, 200)
        self.angle_dial.valueChanged.connect(self.on_angle_changed)
        dial_layout.addWidget(self.angle_dial)
        
        dial_layout.addStretch()
        angle_layout.addLayout(dial_layout)
        
        # LCD display
        lcd_layout = QHBoxLayout()
        lcd_layout.addStretch()
        self.angle_lcd = QLCDNumber()
        self.angle_lcd.setDigitCount(3)
        self.angle_lcd.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        self.angle_lcd.display(90)
        self.angle_lcd.setMinimumHeight(80)
        lcd_layout.addWidget(self.angle_lcd)
        lcd_layout.addWidget(QLabel("°"))
        lcd_layout.addStretch()
        angle_layout.addLayout(lcd_layout)
        
        # Fine control buttons
        fine_layout = QHBoxLayout()
        
        btn_minus_10 = QPushButton("-10")
        btn_minus_10.clicked.connect(lambda: self.adjust_angle(-10))
        btn_minus_10.setMinimumSize(80, 40)
        
        btn_minus_1 = QPushButton("-1")
        btn_minus_1.clicked.connect(lambda: self.adjust_angle(-1))
        btn_minus_1.setMinimumSize(80, 40)
        
        btn_reset = QPushButton("Reset (90°)")
        btn_reset.clicked.connect(lambda: self.angle_dial.setValue(90))
        btn_reset.setMinimumSize(100, 40)
        
        btn_plus_1 = QPushButton("+1")
        btn_plus_1.clicked.connect(lambda: self.adjust_angle(1))
        btn_plus_1.setMinimumSize(80, 40)
        
        btn_plus_10 = QPushButton("+10")
        btn_plus_10.clicked.connect(lambda: self.adjust_angle(10))
        btn_plus_10.setMinimumSize(80, 40)
        
        fine_layout.addWidget(btn_minus_10)
        fine_layout.addWidget(btn_minus_1)
        fine_layout.addWidget(btn_reset)
        fine_layout.addWidget(btn_plus_1)
        fine_layout.addWidget(btn_plus_10)
        
        angle_layout.addLayout(fine_layout)
        
        angle_group.setLayout(angle_layout)
        layout.addWidget(angle_group)
        
        # Save button
        self.btn_save = QPushButton("💾 SAVE CALIBRATION TO point.txt")
        self.btn_save.setMinimumHeight(60)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #00aa00;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00cc00;
            }
            QPushButton:pressed {
                background-color: #008800;
            }
        """)
        self.btn_save.clicked.connect(self.save_calibration)
        layout.addWidget(self.btn_save)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def select_joint(self, joint: str):
        """Select joint for calibration."""
        self.current_joint = joint
        self.btn_coxa.setChecked(joint == "coxa")
        self.btn_femur.setChecked(joint == "femur")
        self.btn_tibia.setChecked(joint == "tibia")
        
        # Load saved angle if exists
        key = f"leg{self.current_leg}_{joint}"
        if key in self.calibration_data:
            self.angle_dial.setValue(self.calibration_data[key])
    
    def on_leg_changed(self, index: int):
        """Handle leg selection change."""
        self.current_leg = index
        # Reload angle for current joint
        self.select_joint(self.current_joint)
    
    def on_angle_changed(self, value: int):
        """Update servo angle in real-time."""
        self.angle_lcd.display(value)
        
        # Save to calibration data
        key = f"leg{self.current_leg}_{self.current_joint}"
        self.calibration_data[key] = value
        
        # Send to robot
        asyncio.create_task(self.set_servo_angle(value))
    
    async def set_servo_angle(self, angle: int):
        """Set servo to specific angle."""
        try:
            joint_map = {"coxa": 0, "femur": 1, "tibia": 2}
            servo_channel = (self.current_leg * 3) + joint_map[self.current_joint]
            
            # Use servo controller directly
            self.robot.movement.servo_controller.set_servo_angle(servo_channel, angle)
            
        except Exception as e:
            logger.error("gui.calibration.set_angle_failed", error=str(e))
    
    def adjust_angle(self, delta: int):
        """Fine-tune angle."""
        new_value = max(0, min(180, self.angle_dial.value() + delta))
        self.angle_dial.setValue(new_value)
    
    def load_calibration(self):
        """Load existing calibration from point.txt."""
        try:
            point_file = Path("data/point.txt")
            if point_file.exists():
                with open(point_file, 'r') as f:
                    content = f.read().strip()
                    # Parse point.txt format (18 values)
                    values = [int(x) for x in content.split(',')]
                    
                    if len(values) == 18:
                        for leg in range(6):
                            for joint_idx, joint_name in enumerate(["coxa", "femur", "tibia"]):
                                key = f"leg{leg}_{joint_name}"
                                self.calibration_data[key] = values[leg * 3 + joint_idx]
                        
                        logger.info("gui.calibration.loaded")
        except Exception as e:
            logger.error("gui.calibration.load_failed", error=str(e))
    
    def save_calibration(self):
        """Save calibration to point.txt."""
        try:
            # Build array of 18 values (6 legs × 3 joints)
            values = []
            for leg in range(6):
                for joint_name in ["coxa", "femur", "tibia"]:
                    key = f"leg{leg}_{joint_name}"
                    values.append(self.calibration_data.get(key, 90))
            
            # Write to point.txt
            point_file = Path("data/point.txt")
            with open(point_file, 'w') as f:
                f.write(','.join(map(str, values)))
            
            logger.info("gui.calibration.saved", file=str(point_file))
            
            QMessageBox.information(
                self,
                "✅ Calibration Saved",
                f"Calibration saved successfully to:\n{point_file}"
            )
            
        except Exception as e:
            logger.error("gui.calibration.save_failed", error=str(e))
            QMessageBox.critical(
                self,
                "❌ Save Failed",
                f"Failed to save calibration:\n{e}"
            )
