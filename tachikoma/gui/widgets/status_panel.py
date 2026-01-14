"""
Status Panel - Real-time telemetry monitoring
Displays battery, IMU, distance, and other sensors
"""
from collections import deque
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QProgressBar, QLCDNumber
)
from PyQt6.QtCore import Qt
import pyqtgraph as pg


class StatusPanel(QWidget):
    """Real-time status monitoring panel."""
    
    def __init__(self):
        super().__init__()
        self.battery_history = deque(maxlen=100)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()
        
        # Battery section
        battery_group = QGroupBox("🔋 Battery Status")
        battery_layout = QVBoxLayout()
        
        # Battery voltage display
        voltage_layout = QHBoxLayout()
        voltage_layout.addWidget(QLabel("Voltage:"))
        self.battery_lcd = QLCDNumber()
        self.battery_lcd.setDigitCount(4)
        self.battery_lcd.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        self.battery_lcd.display(0.0)
        voltage_layout.addWidget(self.battery_lcd)
        voltage_layout.addWidget(QLabel("V"))
        battery_layout.addLayout(voltage_layout)
        
        # Battery percentage bar
        self.battery_bar = QProgressBar()
        self.battery_bar.setMinimum(0)
        self.battery_bar.setMaximum(100)
        self.battery_bar.setValue(0)
        self.battery_bar.setTextVisible(True)
        self.battery_bar.setFormat("%p% (%.2f V)")
        battery_layout.addWidget(self.battery_bar)
        
        # Battery history graph
        self.battery_plot = pg.PlotWidget(title="Battery Voltage History")
        self.battery_plot.setYRange(6.0, 8.5)
        self.battery_plot.setLabel('left', 'Voltage', units='V')
        self.battery_plot.setLabel('bottom', 'Time', units='samples')
        self.battery_plot.showGrid(x=True, y=True)
        self.battery_curve = self.battery_plot.plot(
            pen=pg.mkPen(color='g', width=2)
        )
        battery_layout.addWidget(self.battery_plot)
        
        battery_group.setLayout(battery_layout)
        layout.addWidget(battery_group)
        
        # IMU section
        imu_group = QGroupBox("🧭 IMU Orientation")
        imu_layout = QHBoxLayout()
        
        # Pitch
        pitch_layout = QVBoxLayout()
        pitch_layout.addWidget(QLabel("Pitch"), alignment=Qt.AlignmentFlag.AlignCenter)
        self.pitch_lcd = QLCDNumber()
        self.pitch_lcd.setDigitCount(6)
        self.pitch_lcd.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        self.pitch_lcd.display(0.0)
        pitch_layout.addWidget(self.pitch_lcd)
        imu_layout.addLayout(pitch_layout)
        
        # Roll
        roll_layout = QVBoxLayout()
        roll_layout.addWidget(QLabel("Roll"), alignment=Qt.AlignmentFlag.AlignCenter)
        self.roll_lcd = QLCDNumber()
        self.roll_lcd.setDigitCount(6)
        self.roll_lcd.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        self.roll_lcd.display(0.0)
        roll_layout.addWidget(self.roll_lcd)
        imu_layout.addLayout(roll_layout)
        
        # Yaw
        yaw_layout = QVBoxLayout()
        yaw_layout.addWidget(QLabel("Yaw"), alignment=Qt.AlignmentFlag.AlignCenter)
        self.yaw_lcd = QLCDNumber()
        self.yaw_lcd.setDigitCount(6)
        self.yaw_lcd.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        self.yaw_lcd.display(0.0)
        yaw_layout.addWidget(self.yaw_lcd)
        imu_layout.addLayout(yaw_layout)
        
        imu_group.setLayout(imu_layout)
        layout.addWidget(imu_group)
        
        # Distance section
        dist_group = QGroupBox("📏 Ultrasonic Distance")
        dist_layout = QVBoxLayout()
        
        distance_display = QHBoxLayout()
        self.distance_lcd = QLCDNumber()
        self.distance_lcd.setDigitCount(5)
        self.distance_lcd.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        self.distance_lcd.display(0.0)
        distance_display.addWidget(self.distance_lcd)
        distance_display.addWidget(QLabel("cm"))
        dist_layout.addLayout(distance_display)
        
        dist_group.setLayout(dist_layout)
        layout.addWidget(dist_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def update_battery(self, voltage: float):
        """Update battery display."""
        self.battery_lcd.display(f"{voltage:.2f}")
        
        # Calculate percentage (6V = 0%, 8.4V = 100%)
        percentage = int(((voltage - 6.0) / 2.4) * 100)
        percentage = max(0, min(100, percentage))
        self.battery_bar.setValue(percentage)
        
        # Update color based on level
        if percentage < 20:
            color = "#ff4444"  # Red
        elif percentage < 50:
            color = "#ffaa00"  # Orange
        else:
            color = "#00ff00"  # Green
        
        self.battery_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
        
        # Update graph
        self.battery_history.append(voltage)
        self.battery_curve.setData(list(self.battery_history))
    
    def update_imu(self, data: dict):
        """Update IMU display."""
        self.pitch_lcd.display(f"{data.get('pitch', 0.0):.2f}")
        self.roll_lcd.display(f"{data.get('roll', 0.0):.2f}")
        self.yaw_lcd.display(f"{data.get('yaw', 0.0):.2f}")
    
    def update_distance(self, distance: float):
        """Update distance display."""
        self.distance_lcd.display(f"{distance:.1f}")
