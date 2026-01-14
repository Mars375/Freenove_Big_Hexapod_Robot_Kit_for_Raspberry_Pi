"""Unit tests for PCA9685ServoController with Dual Board support."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from core.hardware.drivers.pca9685_servo import PCA9685ServoController

@pytest.mark.asyncio
async def test_dual_board_initialization():
    pca_low = AsyncMock()
    pca_high = AsyncMock()
    pca_low.is_available.return_value = True
    pca_high.is_available.return_value = True
    
    controller = PCA9685ServoController(pca_low, pca_high)
    await controller.initialize()
    
    assert controller.is_available()

@pytest.mark.asyncio
async def test_channel_routing():
    pca_low = AsyncMock()
    pca_high = AsyncMock()
    pca_low.is_available.return_value = True
    pca_high.is_available.return_value = True
    
    controller = PCA9685ServoController(pca_low, pca_high)
    
    # Test Low Channel (0-15) -> Board 1 (pca_low)
    # Channel 2 -> pca_low channel 2
    await controller.set_angle_async(2, 90)
    pca_low.set_servo_pulse.assert_called_once()
    args, _ = pca_low.set_servo_pulse.call_args
    assert args[0] == 2
    pca_high.set_servo_pulse.assert_not_called()
    
    # Reset mocks
    pca_low.reset_mock()
    pca_high.reset_mock()
    
    # Test High Channel (16-31) -> Board 0 (pca_high)
    # Channel 18 -> pca_high channel 2 (18-16=2)
    await controller.set_angle_async(18, 90)
    pca_high.set_servo_pulse.assert_called_once()
    args, _ = pca_high.set_servo_pulse.call_args
    assert args[0] == 2  # 18 - 16 = 2
    pca_low.set_servo_pulse.assert_not_called()

@pytest.mark.asyncio
async def test_invalid_channels():
    pca_low = AsyncMock()
    pca_high = AsyncMock()
    controller = PCA9685ServoController(pca_low, pca_high)
    
    with pytest.raises(ValueError, match="hors limites"):
        await controller.set_angle_async(32, 90)
        
    with pytest.raises(ValueError, match="hors limites"):
        await controller.set_angle_async(-1, 90)
