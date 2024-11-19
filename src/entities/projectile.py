import math
import random

import pygame

from src.constants import WINDOW, COLORS

class Projectile:
    def __init__(self, pos, direction, config):
        """
        Initialize a projectile
        config: Dictionary containing projectile settings
        """
        self.radius = config['RADIUS']
        self.speed = config['SPEED']
        self.color = config['COLOR']
        self.from_enemy = False
        self.hits = 0
        self.max_hits = 1
        
        # Store damage and shrink settings if it's an enemy projectile
        if 'DAMAGE_PER_FRAME' in config:
            self.damage = config['DAMAGE_PER_FRAME']
            self.shrink_rate = config['SHRINK_RATE']
            self.min_size = config['MIN_SIZE']
        
        # Create rect and image
        self.rect = pygame.Rect(pos[0] - self.radius, pos[1] - self.radius, 
                             self.radius * 2, self.radius * 2)
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        
        # Calculate velocity
        self.velocity = (direction[0] * self.speed, direction[1] * self.speed)

    def move(self):
        self.rect.move_ip(self.velocity[0], self.velocity[1])

    def is_off_screen(self, camera):
        screen_pos = (
            self.rect.x - camera.x,
            self.rect.y - camera.y
        )
        return (screen_pos[0] > WINDOW['WIDTH'] or 
                screen_pos[0] + self.rect.width < 0 or 
                screen_pos[1] > WINDOW['HEIGHT'] or 
                screen_pos[1] + self.rect.height < 0)

    def update_rect_size(self):
        """Update rect size based on current projectile radius"""
        old_center = self.rect.center
        self.rect.size = (self.radius * 2, self.radius * 2)
        self.rect.center = old_center
        # Update image size
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)