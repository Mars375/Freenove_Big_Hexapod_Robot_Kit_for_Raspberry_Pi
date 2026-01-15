"""
Tests for LED animations.
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from tachikoma.core.hardware.led_animations import LEDAnimations


@pytest.fixture
def mock_led_strip():
    """Create a mock LED strip."""
    strip = Mock()
    strip.set_pixel = Mock()
    strip.show = Mock()
    strip.clear = Mock()
    return strip


@pytest.fixture
def animator(mock_led_strip):
    """Create LED animator with mock strip."""
    return LEDAnimations(mock_led_strip, num_leds=7)


@pytest.mark.asyncio
class TestLEDAnimations:
    """Test suite for LED animations."""

    async def test_police_animation(self, animator, mock_led_strip):
        """Test police siren animation."""
        result = await animator.police(duration=0.5, speed=0.1)
        assert result is True
        assert mock_led_strip.set_pixel.called
        assert mock_led_strip.show.called

    async def test_breathing_animation(self, animator, mock_led_strip):
        """Test breathing animation."""
        result = await animator.breathing(255, 0, 0, duration=0.5, speed=2.0)
        assert result is True
        assert mock_led_strip.set_pixel.called
        assert mock_led_strip.show.called

    async def test_fire_animation(self, animator, mock_led_strip):
        """Test fire animation."""
        result = await animator.fire(duration=0.5, intensity=1.0)
        assert result is True
        assert mock_led_strip.set_pixel.called
        assert mock_led_strip.show.called

    async def test_wave_animation(self, animator, mock_led_strip):
        """Test wave animation."""
        result = await animator.wave(0, 0, 255, duration=0.5, speed=0.5)
        assert result is True
        assert mock_led_strip.set_pixel.called
        assert mock_led_strip.show.called

    async def test_strobe_animation(self, animator, mock_led_strip):
        """Test strobe animation."""
        result = await animator.strobe(255, 255, 255, duration=0.3, speed=0.05)
        assert result is True
        assert mock_led_strip.set_pixel.called
        assert mock_led_strip.show.called

    async def test_chase_animation(self, animator, mock_led_strip):
        """Test chase animation."""
        result = await animator.chase(0, 255, 0, duration=0.5, speed=0.1)
        assert result is True
        assert mock_led_strip.set_pixel.called
        assert mock_led_strip.show.called

    async def test_stop_animation(self, animator):
        """Test stopping animation."""
        # Start an animation in background
        task = asyncio.create_task(animator.police(duration=10.0))
        await asyncio.sleep(0.1)  # Let it run a bit
        
        animator.stop()  # Request stop
        result = await task
        assert result is True

    async def test_animation_duration(self, animator, mock_led_strip):
        """Test that animations respect duration."""
        import time
        start = time.time()
        await animator.police(duration=0.5, speed=0.1)
        elapsed = time.time() - start
        # Should be close to 0.5s (with some tolerance)
        assert 0.4 < elapsed < 0.7


@pytest.mark.integration
@pytest.mark.asyncio
class TestLEDAnimationsIntegration:
    """Integration tests for LED animations with actual hardware layer."""

    async def test_device_integration(self):
        """Test that device layer properly calls animator."""
        from tachikoma.core.hardware.devices.led import LEDStrip
        
        # This will use mock mode if SPI not available
        strip = LEDStrip(led_count=7)
        await strip.initialize()
        
        try:
            # Test each animation method exists and is callable
            assert hasattr(strip, 'police')
            assert hasattr(strip, 'breathing')
            assert hasattr(strip, 'fire')
            assert hasattr(strip, 'wave')
            assert hasattr(strip, 'strobe')
            assert hasattr(strip, 'chase')
            
            # Test a quick animation
            result = await strip.police(duration=0.1, speed=0.05)
            assert isinstance(result, bool)
            
        finally:
            await strip.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
