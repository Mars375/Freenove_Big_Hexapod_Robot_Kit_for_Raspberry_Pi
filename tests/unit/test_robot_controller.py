"""Unit tests for robot controller."""
from core.robot_controller import RobotController


def test_robot_controller_initialization():
    """Test RobotController initialization."""
    controller = RobotController()
    
    assert not controller.connected
    assert controller.state["moving"] is False


def test_robot_controller_state():
    """Test robot state management."""
    controller = RobotController()
    
    controller.update_state("moving", True)
    assert controller.state["moving"] is True
    
    state = controller.get_state()
    assert state["moving"] is True
