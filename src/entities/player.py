import math
import pygame
import random

from src.constants import (
    WINDOW,
    COLORS,
    PLAYER
)
from src.entities.projectile import Projectile
from src.camera import Camera
from src.controls import Controls
from src.utils.collision import resolve_wall_collision

class Player:
    def __init__(self, game):
        self.radius = PLAYER['RADIUS']
        self.image = pygame.Surface((PLAYER['RADIUS'] * 2, PLAYER['RADIUS'] * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, COLORS['BLUE'], (PLAYER['RADIUS'], PLAYER['RADIUS']), PLAYER['RADIUS'])
        self.rect = self.image.get_rect()
        self.rect.center = (600, 400)
        self.died = 0
        self.max_stamina = PLAYER['STAMINA']['MAX']
        self.current_stamina = self.max_stamina
        self.stamina_recovery_rate = PLAYER['STAMINA']['RECOVERY_RATE']
        self.is_exhausted = False
        self.stamina_bar_visible = 0
        self.stamina_bar_fade_time = PLAYER['STAMINA']['BAR']['FADE_TIME']
        
        # Add velocity attributes
        self.velocity_x = 0
        self.velocity_y = 0
        self.max_speed = PLAYER['MOVEMENT']['BASE_SPEED']
        self.acceleration = PLAYER['MOVEMENT']['ACCELERATION']
        self.deceleration = PLAYER['MOVEMENT']['DECELERATION']

        self.controls = Controls()

        # Add game reference
        self.game = game

        self.current_speed = PLAYER['MOVEMENT']['BASE_SPEED']

        self.max_health = PLAYER['HEALTH']['MAX']
        self.current_health = self.max_health

    def get_current_speed(self) -> float:
        """Calculate and return the player's current movement speed"""
        base_speed = PLAYER['MOVEMENT']['BASE_SPEED']
        
        if (self.controls.is_sprinting() and 
            not self.is_exhausted and 
            self.current_stamina > 0):
            return base_speed * PLAYER['MOVEMENT']['SPRINT_MULTIPLIER']
        
        return base_speed

    def move(self, visible_walls):
        # Decrease stamina bar visibility counter
        if self.stamina_bar_visible > 0:
            self.stamina_bar_visible -= 1

        x, y = self.controls.get_movement_vector()
        
        # Get current speed based on sprint state
        current_speed = self.get_current_speed()
        
        # Calculate velocities based on input and speed
        self.velocity_x = x * current_speed
        self.velocity_y = y * current_speed
        
        # Handle sprinting and stamina
        if self.controls.is_sprinting() and not self.is_exhausted and self.current_stamina > 0:
            self.current_stamina -= 1
            self.stamina_bar_visible = self.stamina_bar_fade_time
            if self.current_stamina <= 0:
                self.is_exhausted = True
            
            # Create boost effect when sprinting and actually moving
            if (x != 0 or y != 0):
                movement_angle = math.atan2(y, x)
                self.game.effect_manager.create_boost_effect(
                    self.rect.centerx,
                    self.rect.centery,
                    movement_angle
                )
        else:
            # Recover stamina when not sprinting
            old_stamina = self.current_stamina
            self.current_stamina = min(self.max_stamina, self.current_stamina + self.stamina_recovery_rate)
            if self.current_stamina != old_stamina:
                self.stamina_bar_visible = self.stamina_bar_fade_time
            if self.current_stamina >= self.max_stamina * PLAYER['STAMINA']['EXHAUSTION_THRESHOLD']:
                self.is_exhausted = False

        # Store old position for collision resolution
        old_pos = self.rect.copy()
        
        # Update position using velocities
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Check and resolve wall collisions
        if visible_walls:
            self.rect = resolve_wall_collision(old_pos, self.rect, visible_walls)

    def shoot(self, camera_pos):
        x, y, using_controller = self.controls.get_aim_vector()
        
        if using_controller:
            direction = (x, y)  # Controller input is already normalized
        else:
            screen_player_x = self.rect.centerx - camera_pos[0]
            screen_player_y = self.rect.centery - camera_pos[1]
            dx = x - screen_player_x
            dy = y - screen_player_y
            # Normalize the direction vector
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                direction = (dx / length, dy / length)
            else:
                direction = (1, 0)  # Default direction if length is 0

        # Add inaccuracy to direction
        angle = math.atan2(direction[1], direction[0])
        spread = random.uniform(-PLAYER['PROJECTILE']['INACCURACY'], PLAYER['PROJECTILE']['INACCURACY'])
        angle += spread
        direction = (math.cos(angle), math.sin(angle))
        
        # Create projectile config with speed variation
        projectile_config = PLAYER['PROJECTILE'].copy()
        speed_variation = random.uniform(
            1 - PLAYER['PROJECTILE']['VARIATION'],
            1 + PLAYER['PROJECTILE']['VARIATION']
        )
        projectile_config['SPEED'] *= speed_variation
        
        projectile = Projectile(
            self.rect.center, 
            direction,
            projectile_config
        )
        projectile.from_enemy = False
        projectile.using_controller = using_controller
        return projectile

    def die(self):
        self.died = 1
        
    def draw_stamina_bar(self, surface, camera):
        if self.stamina_bar_visible > 0:
            # Get screen position using camera
            screen_pos = camera.apply(self.rect)
            
            # Bar dimensions
            bar_width = PLAYER['STAMINA']['BAR']['WIDTH']
            bar_height = PLAYER['STAMINA']['BAR']['HEIGHT']
            bar_x = screen_pos.centerx - bar_width // 2
            bar_y = screen_pos.top - PLAYER['STAMINA']['BAR']['OFFSET_Y']  # Position above player

            # Background (empty) bar
            pygame.draw.rect(surface, COLORS['BLACK'], (bar_x, bar_y, bar_width, bar_height))
            
            # Filled portion of bar
            fill_width = int((self.current_stamina / self.max_stamina) * bar_width)
            if not self.is_exhausted:
                fill_color = COLORS['GREEN']
            else:
                fill_color = COLORS['RED']
            pygame.draw.rect(surface, fill_color, (bar_x, bar_y, fill_width, bar_height))

    def draw_health_bar(self, surface, camera):
        if self.current_health < self.max_health:
            # Bar dimensions
            bar_width = 50
            bar_height = 6
            bar_x = camera.apply(self.rect).centerx - bar_width // 2
            bar_y = camera.apply(self.rect).top - 20  # Position above stamina bar

            # Background (empty) bar
            pygame.draw.rect(surface, COLORS['BLACK'], (bar_x, bar_y, bar_width, bar_height))
            
            # Filled portion of bar
            fill_width = int((self.current_health / self.max_health) * bar_width)
            fill_color = COLORS['RED']
            pygame.draw.rect(surface, fill_color, (bar_x, bar_y, fill_width, bar_height))