"""
Abstract interface for the robot's camera controller.
"""

from abc import ABC, abstractmethod


class CameraController(ABC):
    """
    Defines the contract for camera operations.

    This interface provides a standard way to manage the camera stream and
    capture images, independent of the underlying camera hardware.
    """

    @abstractmethod
    def start_stream(self) -> None:
        """
        Starts the camera video stream.
        """
        pass

    @abstractmethod
    def stop_stream(self) -> None:
        """
        Stops the camera video stream.
        """
        pass

    @abstractmethod
    def capture(self) -> bytes:
        """
        Captures a single still image.

        Returns:
            A bytes object containing the image data.
        """
        pass
