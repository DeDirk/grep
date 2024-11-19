import math
import random
from typing import Tuple, List

import pygame

from src.entities.projectile import Projectile
from src.constants import (
    WINDOW,
    ENEMY,
    COLORS
)
from src.utils.prediction import calculate_intercept_point

class Enemy:
    def __init__(self, game):
        # Basic setup
        self.radius = ENEMY['RADIUS']
        self.image = None
        self.rect = None
        self.update_image()
        
        # Add velocity attributes
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = ENEMY['MOVEMENT']['ACCELERATION']
        self.deceleration = ENEMY['MOVEMENT']['DECELERATION']
        
        # Phase management
        self.current_phase = 1
        self.max_phases = 3
        self.phase_health = {
            1: ENEMY['HEALTH']['PHASE_1'],
            2: ENEMY['HEALTH']['PHASE_2'],
            3: ENEMY['HEALTH']['PHASE_3']
        }
        self.current_health = self.phase_health[1]
        
        # State management
        self.state = "move_towards_player"
        self.last_state_change = pygame.time.get_ticks()
        self.next_state_change = random.randint(3000, 8000)
        
        # Phase states mapping
        self.phase_states = {
            1: ["move_towards_player", "sweep_towards_player", "dash_toward_player"],
            2: ["middle_shoot", "movement_5", "movement_6"],
            3: ["movement_7", "movement_8", "movement_9"]
        }

        # Movement-specific variables
        self._init_movement_variables()

        
        # Add game reference
        self.game = game

        # Add a flag to track if the dash indicator has been shown
        self.dash_indicator_shown = False

    def _init_movement_variables(self) -> None:
        """Initialize all movement-related variables"""
        # Wall slowdown factor (movement 1)	
        self.wall_slowdown_factor = ENEMY['WALL_INTERACTION']['SLOWDOWN_FACTOR']

        # Base speed (movement 1)
        self.base_speed = ENEMY['MOVEMENT']['BASE_SPEED']

        # Sweep variables (movement 2)
        self.sweep_offset = 0
        self.sweep_direction = 1
        self.sweep_frame_counter = 0
        self.sweep_frequency = ENEMY['MOVEMENT']['SWEEP']['FREQUENCY']
        self.sweep_speed = ENEMY['MOVEMENT']['SWEEP']['SPEED']

        # Dash variables (movement 3)   
        self.dashing = True
        self.last_dash_time = pygame.time.get_ticks()
        self.dash_angle = 0
        self.dash_speed = ENEMY['MOVEMENT']['DASH']['SPEED']
        self.dash_duration = ENEMY['MOVEMENT']['DASH']['DURATION']
        self.dash_pause_duration = ENEMY['MOVEMENT']['DASH']['PAUSE_DURATION']

        # Middle shoot variables (movement 4)
        self.next_shot_interval = random.randint(800, 1200)
        self.initial_angle = 0
        self.circle_start_time = 0
        self.last_shot_time = 0

        # Movement 5 variables

        # Movement 6 variables
        

    def take_damage(self, damage):
        self.current_health -= damage
        
        if self.current_health <= 0 and self.current_phase < self.max_phases:
            self.transition_to_next_phase()
            return False  # Enemy not fully defeated yet
        
        return self.current_health <= 0 and self.current_phase >= self.max_phases

    def transition_to_next_phase(self):
        self.current_phase += 1
        if self.current_phase <= self.max_phases:
            self.current_health = self.phase_health[self.current_phase]
            self.state = self.phase_states[self.current_phase][0]
            
            # Create phase change effect
            self.game.effect_manager.create_phase_change_effect(
                self.rect.centerx,
                self.rect.centery
            )
            
            # Add transition variables
            self.phase_transition_start = pygame.time.get_ticks()
            self.phase_transition_duration = 1500  # 1.5 seconds pause
            self.in_phase_transition = True
            self.transition_color = COLORS['RED']  # Starting color

    def update_state(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_state_change >= self.next_state_change:
            old_state = self.state
            self.state = random.choice(self.phase_states[self.current_phase])
            if old_state != self.state:
                # Create movement change effect
                self.game.effect_manager.create_movement_change_effect(
                    self.rect.centerx,
                    self.rect.centery
                )
            self.last_state_change = current_time
            self.next_state_change = random.randint(3000, 8000)

    def move(self, player_position, walls=None):
        # Check if we're in a phase transition
        if hasattr(self, 'in_phase_transition') and self.in_phase_transition:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.phase_transition_start
            
            if elapsed >= self.phase_transition_duration:
                self.in_phase_transition = False
            else:
                # Calculate transition progress (0 to 1)
                progress = elapsed / self.phase_transition_duration
                # Interpolate between red and purple
                transition_color = self.interpolate_color(
                    COLORS['RED'],
                    COLORS['PURPLE'],
                    progress
                )
                self.update_image(transition_color)
            return []  # Return empty list since we're not shooting during transition
        
        self.update_state()
        new_projectiles = []
        
        # Phase 1 movements
        if self.state == "move_towards_player":
            self.move_towards_player(player_position, walls)
        elif self.state == "sweep_towards_player":
            self.sweep_towards_player(player_position, walls)
        elif self.state == "dash_toward_player":
            self.dash_toward_player(player_position, walls)
            
        # Phase 2 movements
        elif self.state == "middle_shoot":
            new_projectiles = self.middle_shoot(player_position)
        elif self.state == "movement_5":
            new_projectiles = self.movement_5(player_position)
        elif self.state == "movement_6":
            new_projectiles = self.movement_6(player_position)
            
        # Phase 3 movements
        elif self.state == "movement_7":
            self.movement_7(player_position)
        elif self.state == "movement_8":
            self.movement_8(player_position)
        elif self.state == "movement_9":
            self.movement_9(player_position)
        
        return new_projectiles
    
    def orbit_around_point(self, center_point, orbit_radius=300, rotation_speed=0.05):
        """
        Makes the enemy orbit around a given point.
        Returns the enemy's current orbit angle.
        
        Args:
            center_point (tuple): (x, y) point to orbit around
            orbit_radius (int): Distance from center point
            rotation_speed (float): Speed of rotation
        """
        if not hasattr(self, 'orbit_angle'):
            dx = self.rect.centerx - center_point[0]
            dy = self.rect.centery - center_point[1]
            self.orbit_angle = math.atan2(dy, dx)
        
        self.orbit_angle += rotation_speed
        
        # Calculate target position on circle
        target_x = center_point[0] + orbit_radius * math.cos(self.orbit_angle)
        target_y = center_point[1] + orbit_radius * math.sin(self.orbit_angle)
        
        # Move towards target position
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            # Smoothly adjust speed based on distance
            speed_factor = min(dist / 100, 1.5)
            move_speed = ENEMY['MOVEMENT']['DASH']['SPEED'] * speed_factor
            
            # Add slight prediction to movement
            prediction_factor = 0.2
            predicted_x = target_x + (target_x - self.rect.centerx) * prediction_factor
            predicted_y = target_y + (target_y - self.rect.centery) * prediction_factor
            
            # Calculate direction to predicted position
            dx = predicted_x - self.rect.centerx
            dy = predicted_y - self.rect.centery
            dist = math.hypot(dx, dy)
            
            if dist > 0:
                self.rect.centerx += (dx / dist) * move_speed
                self.rect.centery += (dy / dist) * move_speed
        
        return self.orbit_angle

    def middle_shoot(self, player_position):
        current_time = pygame.time.get_ticks()
        new_projectiles = []
        
        orbit_angle = self.orbit_around_point(player_position)
        
        if current_time - self.last_shot_time >= self.next_shot_interval:
            for i in range(8):
                shot_angle = (i * math.pi / 4) + orbit_angle
                projectile = self.shoot(shot_angle, 'PHASE_TWO')
                new_projectiles.append(projectile)
                
            self.last_shot_time = current_time
            self.next_shot_interval = random.randint(500, 1500)
        
        return new_projectiles

    def movement_5(self, player_position):
        # Initialize shooting variables if they don't exist
        if not hasattr(self, 'last_triple_shot_time'):
            self.last_triple_shot_time = pygame.time.get_ticks()
            self.triple_shot_interval = random.randint(1000, 2000)  # Time between triple shots

        current_time = pygame.time.get_ticks()
        new_projectiles = []
        
        # Use orbital movement
        orbit_angle = self.orbit_around_point(player_position, orbit_radius=250, rotation_speed=0.03)
        
        # Handle shooting
        if current_time - self.last_triple_shot_time >= self.triple_shot_interval:
            # Calculate angle to player
            dx = player_position[0] - self.rect.centerx
            dy = player_position[1] - self.rect.centery
            base_angle = math.atan2(dy, dx)
            
            # Shoot three projectiles with slight spread
            for i in range(3):
                spread = (i - 1) * 0.2  # This creates a spread of -0.2, 0, and 0.2 radians
                shot_angle = base_angle + spread
                new_projectiles.append(self.shoot(shot_angle, 'PHASE_THREE'))
                
            self.last_triple_shot_time = current_time
            self.triple_shot_interval = random.randint(500, 1000)  # Randomize next interval
        
        return new_projectiles

    def movement_6(self, player_position):
        if not hasattr(self, 'last_predictive_shot_time'):
            self.last_predictive_shot_time = pygame.time.get_ticks()
            self.predictive_shot_interval = random.randint(800, 1500)

        current_time = pygame.time.get_ticks()
        new_projectiles = []
        
        # Use orbital movement similar to movement_5
        orbit_angle = self.orbit_around_point(player_position, orbit_radius=300, rotation_speed=0.02)
        
        # Handle shooting with prediction
        if current_time - self.last_predictive_shot_time >= self.predictive_shot_interval:
            # Get player velocity
            player_velocity = (self.game.player.velocity_x, self.game.player.velocity_y)
            projectile_speed = ENEMY['PROJECTILE']['PREDICTIVE']['SPEED']
            
            # Calculate intercept point
            predicted_pos = calculate_intercept_point(
                (self.rect.centerx, self.rect.centery),
                player_position,
                player_velocity,
                projectile_speed
            )
            
            if predicted_pos:
                # Calculate angle to predicted position
                dx = predicted_pos[0] - self.rect.centerx
                dy = predicted_pos[1] - self.rect.centery
                angle = math.atan2(dy, dx)
                
                # Create predictive shot
                new_projectiles.append(self.shoot(angle, 'PHASE_THREE'))
            else:
                # If no intercept possible, shoot directly at player
                dx = player_position[0] - self.rect.centerx
                dy = player_position[1] - self.rect.centery
                angle = math.atan2(dy, dx)
                new_projectiles.append(self.shoot(angle, 'PHASE_THREE'))
            
            self.last_predictive_shot_time = current_time
            self.predictive_shot_interval = random.randint(800, 1500)
        
        return new_projectiles

    # Phase 3 movement methods
    def movement_7(self, player_position):
        pass  # Add your seventh movement pattern here

    def movement_8(self, player_position):
        pass  # Add your eighth movement pattern here

    def movement_9(self, player_position):
        pass  # Add your ninth movement pattern here
    
    def shoot(self, angle, projectile_type='BASIC'):
        """
        Create a projectile with the specified configuration
        """
        direction = (math.cos(angle), math.sin(angle))
        projectile = Projectile(
            self.rect.center,
            direction,
            ENEMY['PROJECTILE']['PREDICTIVE']
        )
        projectile.from_enemy = True
        return projectile

    def update_image(self, color=None):
        """Update the surface and redraw the circle."""
        if color is None:
            color = COLORS['RED']
        
        # Ensure radius is at least 1 pixel
        self.radius = max(1, self.radius)
        
        try:
            self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, color, (self.radius, self.radius), self.radius)
            self.rect = self.image.get_rect(center=self.rect.center if self.rect else (0, 0))
        except pygame.error as e:
            print(f"Error in update_image: radius = {self.radius}")
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=self.rect.center if self.rect else (0, 0))
        
    def move_towards_player(self, player_position, walls=None):
        # Get speed multiplier considering both distance and walls
        speed_multiplier = self.calculate_speed_multiplier(player_position, walls)
        
        dx = player_position[0] - self.rect.centerx
        dy = player_position[1] - self.rect.centery
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            # Apply combined speed multiplier
            direction_x = dx / distance
            direction_y = dy / distance
            
            self.velocity_x += direction_x * self.acceleration * speed_multiplier
            self.velocity_y += direction_y * self.acceleration * speed_multiplier
            
            # Calculate current speed
            current_speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
            
            # Clamp to max speed (affected by multiplier)
            max_speed = self.base_speed * (speed_multiplier + 0.1)
            if current_speed > max_speed:
                scale = max_speed / current_speed
                self.velocity_x *= scale
                self.velocity_y *= scale
        
        # Update position using velocity
        self.rect.centerx += int(self.velocity_x)
        self.rect.centery += int(self.velocity_y)
    
    def sweep_towards_player(self, player_position, walls=None):
        current_time = pygame.time.get_ticks()
        
        # Get speed multiplier based on distance
        speed_multiplier = self.calculate_speed_multiplier(player_position, walls)
        
        # Update sweep direction every few seconds
        if not hasattr(self, 'last_sweep_change'):
            self.last_sweep_change = current_time
            self.sweep_direction = 1
        
        if current_time - self.last_sweep_change > 2000:
            self.sweep_direction *= -1
            self.last_sweep_change = current_time
        
        # Calculate angle to player
        dx = player_position[0] - self.rect.centerx
        dy = player_position[1] - self.rect.centery
        angle_to_player = math.atan2(dy, dx)
        
        # Calculate sweep offset
        sweep_offset = ENEMY['MOVEMENT']['SWEEP']['AMPLITUDE'] * self.sweep_direction
        
        # Calculate desired movement direction with distance-based speed
        base_speed = ENEMY['MOVEMENT']['BASE_SPEED'] * 1 * (speed_multiplier) # Apply multiplier to base speed
        
        # Calculate perpendicular sweep movement
        sweep_x = -math.sin(angle_to_player) * sweep_offset * speed_multiplier  # Apply multiplier to sweep
        sweep_y = math.cos(angle_to_player) * sweep_offset * speed_multiplier
        
        # Calculate target velocities combining forward and sweep movement
        target_velocity_x = math.cos(angle_to_player) * base_speed + sweep_x
        target_velocity_y = math.sin(angle_to_player) * base_speed + sweep_y
        
        # Apply acceleration towards target velocity
        self.velocity_x += (target_velocity_x - self.velocity_x) * 0.15
        self.velocity_y += (target_velocity_y - self.velocity_y) * 0.15
        
        # Update position using velocity
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
    
    def dash_toward_player(self, player_position, walls=None):
        current_time = pygame.time.get_ticks()
        
        # Get speed multiplier based on distance
        speed_multiplier = self.calculate_speed_multiplier(player_position, walls)
        
        if self.dashing:
            # Reset radius to normal when dashing
            if hasattr(self, 'original_radius'):
                self.radius = self.original_radius
                self.update_image()
                delattr(self, 'original_radius')
            
            # Calculate direction to player
            dx = player_position[0] - self.rect.centerx
            dy = player_position[1] - self.rect.centery
            distance = math.hypot(dx, dy)
            target_angle = math.atan2(dy, dx)
            
            if distance > 0:
                # Initialize current_angle if it doesn't exist
                if not hasattr(self, 'current_angle'):
                    self.current_angle = target_angle
                
                # During dash: limit turning
                angle_diff = (target_angle - self.current_angle + math.pi) % (2 * math.pi) - math.pi
                max_turn_rate = math.pi / 128
                clamped_diff = max(min(angle_diff, max_turn_rate), -max_turn_rate)
                self.current_angle = (self.current_angle + clamped_diff) % (2 * math.pi)
                
                # Use current_angle for movement
                direction_x = math.cos(self.current_angle)
                direction_y = math.sin(self.current_angle)
                
                # Apply stronger acceleration during dash with distance multiplier
                dash_acceleration = self.acceleration * 3 * speed_multiplier
                self.velocity_x += direction_x * dash_acceleration
                self.velocity_y += direction_y * dash_acceleration
                
                # Clamp to dash speed (also affected by distance)
                max_dash_speed = ENEMY['MOVEMENT']['DASH']['SPEED']
                current_speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
                if current_speed > max_dash_speed:
                    scale = max_dash_speed / current_speed
                    self.velocity_x *= scale
                    self.velocity_y *= scale
            
            if current_time - self.last_dash_time >= ENEMY['MOVEMENT']['DASH']['DURATION']:
                self.dashing = False
                self.last_dash_time = current_time
                self.dash_indicator_shown = False
        else:
            # During pause: face directly towards player (no turn limit)
            dx = player_position[0] - self.rect.centerx
            dy = player_position[1] - self.rect.centery
            distance = math.hypot(dx, dy)
            
            if distance > 0:
                self.current_angle = math.atan2(dy, dx)  # Freely update angle during pause
            
            # Check if the dash indicator has been shown
            if not self.dash_indicator_shown:
                # Show dash indicator (e.g., change color or size)
                if not hasattr(self, 'original_radius'):
                    self.original_radius = self.radius
                self.radius *= 1.5  # Example: increase size for the indicator
                self.update_image()
                self.dash_indicator_shown = True  # Set the flag to indicate the indicator has been shown
            
            # Calculate progress through pause duration (0 to 1)
            progress = (current_time - self.last_dash_time) / ENEMY['MOVEMENT']['DASH']['PAUSE_DURATION']
            
            # Define size multiplier based on progress:
            # 0.0-0.3: original to small (1.0 to 0.9)
            # 0.3-0.7: small to big (0.9 to 1.1)
            # 0.7-1.0: big to original (1.1 to 1.0)
            if progress < 0.3:
                # Original to small
                t = progress / 0.3  # normalize to 0-1
                size_mult = 1.0 + (-0.1 * t)  # 1.0 to 0.9
            elif progress < 0.7:
                # Small to big
                t = (progress - 0.3) / 0.4  # normalize to 0-1
                size_mult = 0.9 + (0.2 * t)  # 0.9 to 1.1
            else:
                # Big to original
                t = (progress - 0.7) / 0.3  # normalize to 0-1
                size_mult = 1.5 + (-0.5 * t)  # 1.1 to 1.0
            
            # Update radius
            new_radius = self.original_radius * size_mult
            if self.radius != new_radius:
                self.radius = new_radius
                self.update_image()
            
            # Slow down movement after dash (deceleration also affected by distance)
            decel = self.deceleration * 2 * speed_multiplier
            if self.velocity_x > 0:
                self.velocity_x = max(0, self.velocity_x - decel)
            elif self.velocity_x < 0:
                self.velocity_x = min(0, self.velocity_x + decel)
            
            if self.velocity_y > 0:
                self.velocity_y = max(0, self.velocity_y - decel)
            elif self.velocity_y < 0:
                self.velocity_y = min(0, self.velocity_y + decel)
            
            # Switch back to dashing after pause duration
            if current_time - self.last_dash_time >= ENEMY['MOVEMENT']['DASH']['PAUSE_DURATION']:
                self.dashing = True
                self.last_dash_time = current_time
        
        # Update position using velocity
        self.rect.centerx += int(self.velocity_x)
        self.rect.centery += int(self.velocity_y)

    def shrink(self, amount):
            """Shrink the enemy by a given amount."""
            self.radius -= amount
            if self.radius > 0:
                self.update_image()  # Update image and rect after shrinking
            else:
                # Handle enemy destruction if the radius becomes too small
                self.radius = 0
                # Optionally set a flag to indicate the enemy is destroyed

    def calculate_wall_overlap(self, walls: List[pygame.Rect]) -> float:
        """
        Calculate how much of the enemy is overlapping with walls.
        Returns a value between 0 (no overlap) and 1 (full overlap).
        """
        # Create a rect that encompasses the enemy circle
        enemy_rect = pygame.Rect(
            self.rect.centerx - self.radius,
            self.rect.centery - self.radius,
            self.radius * 2,
            self.radius * 2
        )
        
        max_overlap_area = math.pi * self.radius * self.radius  # Total circle area
        total_overlap = 0
        
        for wall in walls:
            if enemy_rect.colliderect(wall):
                # Calculate overlap rectangle
                overlap_rect = enemy_rect.clip(wall)
                
                # For simplicity, we'll use the rectangle overlap area
                # This is an approximation since we're actually a circle
                overlap_area = overlap_rect.width * overlap_rect.height
                total_overlap += overlap_area
        
        # Return ratio of overlap (capped at 1.0)
        return min(total_overlap / max_overlap_area, 1.0)

    def calculate_speed_multiplier(self, player_position, walls: List[pygame.Rect] = None):
        """
        Calculate speed multiplier based on distance to player and wall overlap.
        """
        # Calculate base distance multiplier
        dx = player_position[0] - self.rect.centerx
        dy = player_position[1] - self.rect.centery
        distance = math.hypot(dx, dy)
        distance_multiplier = 1.0  # Default multiplier
        
        # If no walls provided, just return distance multiplier
        if not walls:
            return distance_multiplier
            
        # Calculate wall overlap
        wall_overlap = self.calculate_wall_overlap(walls)
        
        # Amplify small wall_overlap values (e.g., ^0.5 makes 0.2 become ~0.447)
        wall_overlap = pow(wall_overlap, 0.5)  # Square root makes small values larger
        # Calculate wall slowdown (lerp between 1.0 and wall_slowdown_factor)
        wall_multiplier = 1.0 - (wall_overlap * (1.0 - self.wall_slowdown_factor))

        # Combine multipliers
        return distance_multiplier * wall_multiplier

    def interpolate_color(self, color1, color2, factor):
        """Interpolate between two colors based on a factor (0-1)"""
        return tuple(int(color1[i] + (color2[i] - color1[i]) * factor) for i in range(3))

