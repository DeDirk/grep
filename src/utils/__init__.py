"""
Utility functions for collision detection and physics.
"""

from .collision import (
    check_circle_collision,
    check_wall_collisions,
    resolve_wall_collision,
    line_intersects_rect,
    push_out_of_walls,
    line_segments_intersect,
    handle_projectile_enemy_collision,
    handle_projectile_player_collision,
    handle_player_enemy_collision,
    handle_projectile_projectile_collision,
    handle_item_player_collision,
    handle_projectile_wall_collision
)

__all__ = [
    'check_circle_collision',
    'check_wall_collisions',
    'resolve_wall_collision',
    'line_intersects_rect',
    'push_out_of_walls',
    'line_segments_intersect',
    'handle_projectile_enemy_collision',
    'handle_projectile_player_collision',
    'handle_player_enemy_collision',
    'handle_projectile_projectile_collision',
    'handle_item_player_collision',
    'handle_projectile_wall_collision'
] 