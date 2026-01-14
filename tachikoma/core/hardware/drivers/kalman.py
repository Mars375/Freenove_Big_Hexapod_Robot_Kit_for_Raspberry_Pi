"""Kalman filter for IMU sensor stabilization.

Based on Freenove kalman.py analysis (Q=0.001, R=0.1).
"""

class KalmanFilter:
    """1D Kalman filter for ADC/IMU stabilization."""
    
    def __init__(self, process_noise: float = 0.001, measurement_noise: float = 0.1):
        """Initialize Kalman filter.
        
        Args:
            process_noise: Process noise covariance (Q)
            measurement_noise: Measurement noise covariance (R)
        """
        self.Q = process_noise
        self.R = measurement_noise
        self.P = 1.0  # Estimate error covariance
        self.K = 0.0  # Kalman gain
        self.x = 0.0  # State estimate
        self.x_prev = 0.0  # Previous estimate
    
    def update(self, measurement: float) -> float:
        """Update filter with new measurement.
        
        Args:
            measurement: New sensor reading
            
        Returns:
            Filtered value
        """
        # Handle large changes (>= 60 units)
        if abs(self.x_prev - measurement) >= 60:
            # Use weighted average for large jumps
            self.x = measurement * 0.4 + self.x_prev * 0.6
        else:
            self.x = self.x_prev
        
        # Update estimate error covariance
        self.P = self.P + self.Q
        
        # Calculate Kalman gain
        self.K = self.P / (self.P + self.R)
        
        # Update estimate
        filtered_value = self.x + self.K * (measurement - self.x_prev)
        
        # Update posterior error covariance
        self.P = (1 - self.K) * self.P
        
        # Save for next iteration
        self.x_prev = filtered_value
        
        return filtered_value
    
    def reset(self):
        """Reset filter state."""
        self.P = 1.0
        self.K = 0.0
        self.x = 0.0
        self.x_prev = 0.0
