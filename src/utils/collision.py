from typing import List, Dict, Tuple, Optional, Any
import math
import random

import pygame

def check_circle_collision(circle1: Dict, circle2: Dict) -> bool:
    """Check collision between two circles using their centers and radii"""
    dx = circle1['x'] - circle2['x']
    dy = circle1['y'] - circle2['y']
    distance = (dx * dx + dy * dy) ** 0.5
    return distance < (circle1['radius'] + circle2['radius'])

def check_wall_collisions(rect: pygame.Rect, walls: List[pygame.Rect]) -> Tuple[bool, str]:
    """
    Check if a rectangle collides with any walls and return collision direction
    Returns: (collision_occurred, collision_direction)
    collision_direction can be: 'vertical', 'horizontal', 'corner', or None
    """
    for wall in walls:
        if rect.colliderect(wall):
            # Calculate overlap on each axis
            dx = min(rect.right - wall.left, wall.right - rect.left)
            dy = min(rect.bottom - wall.top, wall.bottom - rect.top)
            
            # If overlap is smaller in one direction, that's the collision direction
            if dx < dy:
                return True, 'vertical'
            elif dy < dx:
                return True, 'horizontal'
            else:
                return True, 'corner'
                
    return False, None

def resolve_wall_collision(old_pos: pygame.Rect, new_pos: pygame.Rect, walls: List[pygame.Rect]) -> pygame.Rect:
    """Resolve collision with walls using continuous collision detection"""
    # First check if there's any collision at all
    if not any(new_pos.colliderect(wall) for wall in walls):
        return new_pos

    # Calculate movement vector
    movement_x = new_pos.x - old_pos.x
    movement_y = new_pos.y - old_pos.y

    # If no movement, return current position
    if movement_x == 0 and movement_y == 0:
        return old_pos

    # Try to find the furthest safe position using binary search
    steps = 8  # Number of binary search steps (increase for more precision)
    min_t = 0.0
    max_t = 1.0
    best_pos = old_pos.copy()

    for _ in range(steps):
        # Try a position halfway between min_t and max_t
        t = (min_t + max_t) / 2
        test_pos = old_pos.copy()
        test_pos.x = old_pos.x + movement_x * t
        test_pos.y = old_pos.y + movement_y * t

        # Check if this position is safe
        if any(test_pos.colliderect(wall) for wall in walls):
            max_t = t  # Position caused collision, try earlier
        else:
            min_t = t  # Position was safe, try later
            best_pos = test_pos.copy()

    # Now we have the furthest safe position
    result_pos = best_pos.copy()

    # Try to slide along walls if we hit them
    if min_t < 1.0:  # If we didn't reach the target position
        remaining_x = movement_x * (1 - min_t)
        remaining_y = movement_y * (1 - min_t)

        # Try horizontal movement
        test_pos = result_pos.copy()
        test_pos.x += remaining_x
        if not any(test_pos.colliderect(wall) for wall in walls):
            result_pos.x = test_pos.x

        # Try vertical movement
        test_pos = result_pos.copy()
        test_pos.y += remaining_y
        if not any(test_pos.colliderect(wall) for wall in walls):
            result_pos.y = test_pos.y

    return result_pos

def line_intersects_rect(start: Tuple[float, float], end: Tuple[float, float], 
                        rect: pygame.Rect) -> bool:
    """Check if a line segment intersects with a rectangle"""
    x1, y1 = start
    x2, y2 = end
    
    # Check if line is completely to one side of rectangle
    if (max(x1, x2) < rect.left or min(x1, x2) > rect.right or
        max(y1, y2) < rect.top or min(y1, y2) > rect.bottom):
        return False
        
    # Check if either endpoint is inside rectangle
    if (rect.left <= x1 <= rect.right and rect.top <= y1 <= rect.bottom) or \
       (rect.left <= x2 <= rect.right and rect.top <= y2 <= rect.bottom):
        return True
        
    # Check intersection with each edge of rectangle
    edges = [
        ((rect.left, rect.top), (rect.right, rect.top)),     # Top edge
        ((rect.left, rect.bottom), (rect.right, rect.bottom)), # Bottom edge
        ((rect.left, rect.top), (rect.left, rect.bottom)),   # Left edge
        ((rect.right, rect.top), (rect.right, rect.bottom))  # Right edge
    ]
    
    for edge_start, edge_end in edges:
        if line_segments_intersect((x1, y1), (x2, y2), edge_start, edge_end):
            return True
            
    return False

def line_segments_intersect(p1: Tuple[float, float], p2: Tuple[float, float],
                          p3: Tuple[float, float], p4: Tuple[float, float]) -> bool:
    """Check if two line segments intersect"""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    
    # Calculate denominators for intersection check
    denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    if denom == 0:  # Lines are parallel
        return False
        
    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
    ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
    
    # Check if intersection point lies within both line segments
    return (0 <= ua <= 1) and (0 <= ub <= 1)

def push_out_of_walls(rect: pygame.Rect, walls: List[pygame.Rect]) -> pygame.Rect:
    """Push an entity out of any walls it's stuck in"""
    for wall in walls:
        if rect.colliderect(wall):
            # Calculate overlap on each axis
            left_overlap = wall.right - rect.left
            right_overlap = rect.right - wall.left
            top_overlap = wall.bottom - rect.top
            bottom_overlap = rect.bottom - wall.top
            
            # Find the smallest overlap
            min_overlap = min(left_overlap, right_overlap, top_overlap, bottom_overlap)
            
            # Push in direction of smallest overlap
            if min_overlap == left_overlap:
                rect.left = wall.right
            elif min_overlap == right_overlap:
                rect.right = wall.left
            elif min_overlap == top_overlap:
                rect.top = wall.bottom
            else:  # bottom_overlap
                rect.bottom = wall.top
    
    return rect

def check_projectile_collision(projectile_circle: Dict, target_circle: Dict) -> bool:
    """Generic function to check collision between a projectile and a circular target"""
    return check_circle_collision(projectile_circle, target_circle)

def create_circle_dict(entity: Any) -> Dict:
    """Helper function to create a circle dictionary from an entity with rect and radius"""
    return {
        'x': entity.rect.centerx,
        'y': entity.rect.centery,
        'radius': entity.radius
    }

def handle_projectile_enemy_collision(projectile: Any, enemy: Any, effect_manager: Any) -> bool:
    """Handle collision between projectile and enemy"""
    if check_projectile_collision(create_circle_dict(projectile), create_circle_dict(enemy)):
        enemy.take_damage(1)  # You can pass damage amount as parameter if needed
        effect_manager.create_wall_hit_effect(
            projectile.rect.centerx,
            projectile.rect.centery,
            random.uniform(0, 2 * math.pi)  # Random direction for enemy hits
        )
        return True
    return False

def handle_projectile_player_collision(projectile: Any, player: Any) -> bool:
    """Handle collision between projectile and player"""
    if check_projectile_collision(create_circle_dict(projectile), create_circle_dict(player)):
        player.die()
        return True
    return False

def handle_player_enemy_collision(player: Any, enemy: Any) -> bool:
    """Handle collision between player and enemy"""
    return check_circle_collision(create_circle_dict(player), create_circle_dict(enemy))

def handle_projectile_projectile_collision(projectile1: Any, projectile2: Any) -> bool:
    """Handle collision between two projectiles"""
    return check_circle_collision(create_circle_dict(projectile1), create_circle_dict(projectile2))

def handle_item_player_collision(item: Any, player: Any) -> bool:
    """Check if the player collects an item"""
    item_circle = {
        'x': item.rect.centerx,
        'y': item.rect.centery,
        'radius': item.size
    }
    return check_circle_collision(create_circle_dict(player), item_circle)

def handle_projectile_wall_collision(projectile, wall, game_state) -> bool:
    """Handle collision between projectile and wall"""
    if projectile.rect.colliderect(wall):
        # Calculate which side of the wall was hit using velocity
        proj_center_x = projectile.rect.centerx
        proj_center_y = projectile.rect.centery
        
        # Calculate previous position using velocity
        prev_x = proj_center_x - projectile.velocity[0]
        prev_y = proj_center_y - projectile.velocity[1]
        
        # Determine which side was hit
        if prev_x < wall.left and proj_center_x >= wall.left:  # Hit from left
            wall_normal = math.pi
            spawn_x = wall.left
            spawn_y = proj_center_y
        elif prev_x > wall.right and proj_center_x <= wall.right:  # Hit from right
            wall_normal = 0
            spawn_x = wall.right
            spawn_y = proj_center_y
        elif prev_y < wall.top and proj_center_y >= wall.top:  # Hit from top
            wall_normal = 3*math.pi/2
            spawn_x = proj_center_x
            spawn_y = wall.top
        elif prev_y > wall.bottom and proj_center_y <= wall.bottom:  # Hit from bottom
            wall_normal = math.pi/2
            spawn_x = proj_center_x
            spawn_y = wall.bottom
        else:
            # Fallback for edge cases
            wall_normal = 0
            spawn_x = proj_center_x
            spawn_y = proj_center_y
        
        # Create effect at the collision point
        game_state.effect_manager.create_wall_hit_effect(
            spawn_x,
            spawn_y,
            wall_normal
        )
        
        # Remove the projectile
        if projectile in game_state.projectiles:
            game_state.projectiles.remove(projectile)
        
        return True
    return False