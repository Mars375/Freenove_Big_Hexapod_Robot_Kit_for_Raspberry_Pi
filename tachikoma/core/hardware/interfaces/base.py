from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from enum import Enum


class HardwareStatus(Enum):
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    DISCONNECTED = "disconnected"


class IHardwareComponent(ABC):
    """Interface de base pour tous les composants hardware"""
    
    @abstractmethod
    async def initialize(self) -> bool:
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_health(self) -> Dict[str, Any]:
        pass
