"""
Abstract interface for controlling the robot's movement.
"""

from abc import ABC, abstractmethod
from tachikoma.core.types import GaitType


class MovementController(ABC):
    """
    Defines the contract for hexapod movement control.

    This interface provides a standardized way to command the robot's locomotion
    and posture, abstracting away the underlying hardware and kinematics.
    Implementations of this class are responsible for translating these high-level
    commands into precise servo actions.
    """

    @abstractmethod
    def move(self, x: float, y: float, rotation: float, speed: int) -> None:
        """
        Commands the robot to move in a specific direction and rotation.

        Args:
            x: Normalized forward/backward movement (-1.0 to 1.0).
            y: Normalized sideways movement (-1.0 to 1.0).
            rotation: Normalized rotational movement (-1.0 to 1.0).
            speed: Bounded movement speed.
        """
        pass

    @abstractmethod
    def set_gait(self, gait: GaitType) -> None:
        """
        Sets the walking gait for the robot.

        Args:
            gait: The desired gait type (e.g., Tripod, Wave).
        """
        pass

    @abstractmethod
    def set_body(self, z: float, pitch: float, roll: float, yaw: float) -> None:
        """
        Adjusts the posture of the robot's body.

        Args:
            z: Body height offset.
            pitch: Body pitch angle.
            roll: Body roll angle.
            yaw: Body yaw angle.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Brings the robot to an immediate and complete stop.
        """
        pass
