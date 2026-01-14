"""Tests for MockServoController"""
import pytest
import asyncio
from core.hardware.drivers import MockServoController
from core.exceptions import HardwareNotAvailableError


@pytest.fixture
def mock_servo():
    """Create mock servo controller fixture"""
    return MockServoController(channels=16)


@pytest.fixture
async def initialized_mock_servo():
    """Create and initialize mock servo controller"""
    servo = MockServoController(channels=16)
    await servo.initialize()
    yield servo
    await servo.cleanup()


class TestMockServoInit:
    """Test MockServoController initialization"""
    
    def test_init_default_params(self, mock_servo):
        """Test initialization with default parameters"""
        assert mock_servo.channels == 16
        assert not mock_servo.simulate_errors
        assert not mock_servo.is_initialized
        assert not mock_servo.is_running
    
    def test_init_custom_params(self):
        """Test initialization with custom parameters"""
        servo = MockServoController(
            channels=32,
            simulate_errors=True,
            delay_ms=10
        )
        assert servo.channels == 32
        assert servo.simulate_errors
        assert servo.delay_ms == 10
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, mock_servo):
        """Test successful initialization"""
        await mock_servo.initialize()
        assert mock_servo.is_initialized
        assert mock_servo.is_running
        # Check all servos initialized to neutral
        for i in range(16):
            assert mock_servo.get_angle(i) == 90
        await mock_servo.cleanup()
    
    @pytest.mark.asyncio
    async def test_initialize_with_error_simulation(self):
        """Test initialization with error simulation"""
        servo = MockServoController(simulate_errors=True)
        with pytest.raises(HardwareNotAvailableError):
            await servo.initialize()


class TestMockServoOperations:
    """Test MockServoController operations"""
    
    @pytest.mark.asyncio
    async def test_set_angle_valid(self, initialized_mock_servo):
        """Test setting valid servo angle"""
        await initialized_mock_servo
        servo = initialized_mock_servo
        
        servo.set_angle(0, 45)
        assert servo.get_angle(0) == 45
        
        servo.set_angle(15, 135)
        assert servo.get_angle(15) == 135
    
    @pytest.mark.asyncio
    async def test_set_angle_not_initialized(self, mock_servo):
        """Test setting angle without initialization"""
        with pytest.raises(HardwareNotAvailableError):
            mock_servo.set_angle(0, 90)
    
    @pytest.mark.asyncio
    async def test_set_angle_invalid_channel(self, initialized_mock_servo):
        """Test setting angle on invalid channel"""
        await initialized_mock_servo
        servo = initialized_mock_servo
        
        with pytest.raises(ValueError):
            servo.set_angle(-1, 90)
        
        with pytest.raises(ValueError):
            servo.set_angle(16, 90)
    
    @pytest.mark.asyncio
    async def test_set_angle_invalid_range(self, initialized_mock_servo):
        """Test setting angle outside valid range"""
        await initialized_mock_servo
        servo = initialized_mock_servo
        
        with pytest.raises(ValueError):
            servo.set_angle(0, -1)
        
        with pytest.raises(ValueError):
            servo.set_angle(0, 181)
    
    @pytest.mark.asyncio
    async def test_set_pulse_width(self, initialized_mock_servo):
        """Test setting servo by pulse width"""
        await initialized_mock_servo
        servo = initialized_mock_servo
        
        # 500us = 0 degrees
        servo.set_pulse_width(0, 500)
        assert servo.get_angle(0) == 0
        
        # 1500us = 90 degrees
        servo.set_pulse_width(0, 1500)
        assert servo.get_angle(0) == 90
        
        # 2500us = 180 degrees
        servo.set_pulse_width(0, 2500)
        assert servo.get_angle(0) == 180


class TestMockServoTracking:
    """Test MockServoController command tracking"""
    
    @pytest.mark.asyncio
    async def test_command_history(self, initialized_mock_servo):
        """Test command history tracking"""
        await initialized_mock_servo
        servo = initialized_mock_servo
        
        servo.clear_history()
        
        servo.set_angle(0, 45)
        servo.set_angle(1, 90)
        servo.set_angle(0, 135)
        
        history = servo.get_command_history()
        assert len(history) == 3
        assert history[0][0] == 0  # channel
        assert history[0][1] == 45  # angle
        assert history[1][0] == 1
        assert history[1][1] == 90
    
    @pytest.mark.asyncio
    async def test_command_count(self, initialized_mock_servo):
        """Test command count tracking"""
        await initialized_mock_servo
        servo = initialized_mock_servo
        
        servo.clear_history()
        
        servo.set_angle(0, 45)
        servo.set_angle(1, 90)
        servo.set_angle(0, 135)
        
        assert servo.get_command_count() == 3
        assert servo.get_command_count(channel=0) == 2
        assert servo.get_command_count(channel=1) == 1
        assert servo.get_command_count(channel=5) == 0


class TestMockServoErrorSimulation:
    """Test MockServoController error simulation"""
    
    @pytest.mark.asyncio
    async def test_simulate_channel_error(self, initialized_mock_servo):
        """Test error simulation on specific channel"""
        await initialized_mock_servo
        servo = initialized_mock_servo
        
        # Enable error on channel 5
        servo.simulate_error_on_channel(5)
        
        # Channel 5 should fail
        with pytest.raises(HardwareNotAvailableError):
            servo.set_angle(5, 90)
        
        # Other channels should work
        servo.set_angle(0, 90)
        assert servo.get_angle(0) == 90
        
        # Clear error
        servo.clear_error_simulation()
        servo.set_angle(5, 90)
        assert servo.get_angle(5) == 90
    
    @pytest.mark.asyncio
    async def test_cleanup(self, mock_servo):
        """Test cleanup resets state"""
        await mock_servo.initialize()
        mock_servo.set_angle(0, 45)
        
        assert mock_servo.is_initialized
        assert mock_servo.is_running
        
        await mock_servo.cleanup()
        
        assert not mock_servo.is_initialized
        assert not mock_servo.is_running
