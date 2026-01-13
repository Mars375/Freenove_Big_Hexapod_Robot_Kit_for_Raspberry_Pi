"""Unit tests for obstacle avoidance module."""
from features.autonomous.obstacle_avoidance import (
    AvoidanceAction,
    ObstacleAvoidance,
)


def test_obstacle_avoidance_critical():
    """Test critical distance detection."""
    avoidance = ObstacleAvoidance()
    action, reason = avoidance.analyze_distance(10.0)
    
    assert action == AvoidanceAction.STOP
    assert "Critical" in reason


def test_obstacle_avoidance_unsafe():
    """Test unsafe distance detection."""
    avoidance = ObstacleAvoidance()
    action, reason = avoidance.analyze_distance(25.0)
    
    assert action == AvoidanceAction.BACK_UP
    assert "too close" in reason


def test_obstacle_avoidance_warning():
    """Test warning distance detection."""
    avoidance = ObstacleAvoidance()
    action, reason = avoidance.analyze_distance(45.0)
    
    assert action == AvoidanceAction.TURN_LEFT


def test_obstacle_avoidance_safe():
    """Test safe distance."""
    avoidance = ObstacleAvoidance()
    action, reason = avoidance.analyze_distance(100.0)
    
    assert action == AvoidanceAction.CONTINUE
    assert "clear" in reason


def test_suggest_maneuver():
    """Test maneuver suggestion."""
    avoidance = ObstacleAvoidance()
    maneuver = avoidance.suggest_maneuver(20.0)
    
    assert "action" in maneuver
    assert "reason" in maneuver
    assert "distance" in maneuver
    assert maneuver["distance"] == 20.0
