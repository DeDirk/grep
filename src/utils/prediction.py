import math
from typing import Tuple

def calculate_intercept_point(
    shooter_pos: Tuple[float, float],
    target_pos: Tuple[float, float],
    target_velocity: Tuple[float, float],
    projectile_speed: float
) -> Tuple[float, float]:
    """
    Calculate the intercept point for a projectile to hit a moving target.
    
    Args:
        shooter_pos: (x, y) position of the shooter
        target_pos: (x, y) position of the target
        target_velocity: (vx, vy) velocity of the target
        projectile_speed: Speed of the projectile
    
    Returns:
        Tuple[float, float]: Predicted intercept point (x, y), or None if no intercept is possible
    """
    # Get target speed
    target_speed = math.hypot(target_velocity[0], target_velocity[1])
    
    if target_speed > 0:  # Only predict if target is moving
        # Calculate vector from shooter to target
        dx = target_pos[0] - shooter_pos[0]
        dy = target_pos[1] - shooter_pos[1]
        distance = math.hypot(dx, dy)

        # Time for projectile to reach target if target were stationary
        base_time = distance / projectile_speed
        
        # First approximation of intercept point
        predicted_x = target_pos[0] + (target_velocity[0] * base_time)
        predicted_y = target_pos[1] + (target_velocity[1] * base_time)
        
        # Iterate a few times to refine the prediction
        for _ in range(3):
            # Calculate new distance to predicted point
            dx = predicted_x - shooter_pos[0]
            dy = predicted_y - shooter_pos[1]
            distance = math.hypot(dx, dy)
            
            # Calculate new time to reach this point
            time_to_target = distance / projectile_speed
            
            # Update prediction
            predicted_x = target_pos[0] + (target_velocity[0] * time_to_target)
            predicted_y = target_pos[1] + (target_velocity[1] * time_to_target)
        
        return (predicted_x, predicted_y)
    
    return None 