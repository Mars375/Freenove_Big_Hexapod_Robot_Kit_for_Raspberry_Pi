"""Custom exceptions for robot hardware"""


class HardwareError(Exception):
    """Base exception for hardware errors"""
    pass


class HardwareNotAvailableError(HardwareError):
    """Hardware not initialized or not available"""
    pass


class CommandExecutionError(HardwareError):
    """Command execution failed"""
    pass


class SensorReadError(HardwareError):
    """Sensor reading failed"""
    pass
