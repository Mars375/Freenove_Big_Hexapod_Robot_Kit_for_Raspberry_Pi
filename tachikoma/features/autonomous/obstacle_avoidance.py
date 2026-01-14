"""
Obstacle avoidance module.
Uses ultrasonic sensor to detect and avoid obstacles.
"""
from enum import Enum

from tachikoma.core.logger import get_logger

logger = get_logger(__name__)


class AvoidanceAction(str, Enum):
    """Actions for obstacle avoidance."""
    CONTINUE = "continue"
    STOP = "stop"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    BACK_UP = "back_up"


class ObstacleAvoidance:
    """
    Obstacle avoidance system using ultrasonic sensor.
    
    Provides automatic obstacle detection and avoidance strategies.
    """
    
    def __init__(self, 
                 safe_distance: float = 30.0,
                 warning_distance: float = 50.0,
                 critical_distance: float = 15.0):
        """
        Initialize obstacle avoidance.
        
        Args:
            safe_distance: Distance considered safe (cm)
            warning_distance: Distance to start warning (cm)
            critical_distance: Distance for emergency stop (cm)
        """
        self.safe_distance = safe_distance
        self.warning_distance = warning_distance
        self.critical_distance = critical_distance
        
        logger.info(
            "obstacle_avoidance.initialized",
            safe=safe_distance,
            warning=warning_distance,
            critical=critical_distance
        )
    
    def analyze_distance(self, distance: float) -> tuple[AvoidanceAction, str]:
        """
        Analyze distance and determine action.
        
        Args:
            distance: Distance from ultrasonic sensor (cm)
            
        Returns:
            Tuple of (action, reason)
        """
        if distance < self.critical_distance:
            logger.warning("obstacle_avoidance.critical", distance=distance)
            return AvoidanceAction.STOP, f"Critical obstacle at {distance:.1f}cm"
        
        elif distance < self.safe_distance:
            logger.info("obstacle_avoidance.unsafe", distance=distance)
            return AvoidanceAction.BACK_UP, f"Obstacle too close at {distance:.1f}cm"
        
        elif distance < self.warning_distance:
            logger.debug("obstacle_avoidance.warning", distance=distance)
            return AvoidanceAction.TURN_LEFT, f"Warning: obstacle at {distance:.1f}cm"
        
        else:
            return AvoidanceAction.CONTINUE, "Path clear"
    
    def suggest_maneuver(self, distance: float, prefer_right: bool = False) -> dict:
        """
        Suggest complete maneuver based on distance.
        
        Args:
            distance: Distance from sensor
            prefer_right: Prefer turning right over left
            
        Returns:
            Maneuver dictionary with action and parameters
        """
        action, reason = self.analyze_distance(distance)
        
        maneuver = {
            "action": action.value,
            "reason": reason,
            "distance": distance,
            "is_safe": distance >= self.safe_distance
        }
        
        if action == AvoidanceAction.TURN_LEFT and prefer_right:
            maneuver["action"] = AvoidanceAction.TURN_RIGHT.value
        
        if action == AvoidanceAction.BACK_UP:
            maneuver["parameters"] = {"speed": 3, "steps": 10}
        elif action in [AvoidanceAction.TURN_LEFT, AvoidanceAction.TURN_RIGHT]:
            maneuver["parameters"] = {"angle": 45, "speed": 4}
        
        return maneuver


# Global instance
_avoidance: ObstacleAvoidance | None = None


def get_obstacle_avoidance() -> ObstacleAvoidance:
    """Get or create obstacle avoidance singleton."""
    global _avoidance
    if _avoidance is None:
        _avoidance = ObstacleAvoidance()
    return _avoidance
