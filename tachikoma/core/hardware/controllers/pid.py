"""PID Controller for hexapod stability and movement."""
import time

class PIDController:
    """PID controller implementation matching legacy logic but cleaner."""

    def __init__(self, kp: float = 0.5, ki: float = 0.0, kd: float = 0.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        
        self.target = 0.0
        self.prev_error = 0.0
        self.error_sum = 0.0
        self.last_time = time.time()

    def update(self, current_value: float) -> float:
        """Calculate PID output based on current value."""
        now = time.time()
        dt = now - self.last_time
        if dt <= 0:
            dt = 0.001
            
        error = self.target - current_value
        self.error_sum += error * dt
        derivative = (error - self.prev_error) / dt
        
        output = (self.kp * error) + (self.ki * self.error_sum) + (self.kd * derivative)
        
        self.prev_error = error
        self.last_time = now
        
        return output

    def reset(self):
        """Reset internal state."""
        self.prev_error = 0.0
        self.error_sum = 0.0
        self.last_time = time.time()
