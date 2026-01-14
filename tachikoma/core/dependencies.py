from typing import Optional
from fastapi import Depends, HTTPException, status
from tachikoma.core.hardware.factory import HardwareFactory
from tachikoma.core.config import get_settings


_hardware_factory: Optional[HardwareFactory] = None


def get_hardware_factory() -> HardwareFactory:
    global _hardware_factory
    if _hardware_factory is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Hardware not initialized"
        )
    return _hardware_factory


def set_hardware_factory(factory: HardwareFactory) -> None:
    global _hardware_factory
    _hardware_factory = factory


def reset_hardware_factory() -> None:
    global _hardware_factory
    _hardware_factory = None
