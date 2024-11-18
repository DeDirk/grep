import math
import random
from typing import Tuple

import pygame

from src.constants import COLORS, EFFECTS

class Particle:
    def __init__(self, x: float, y: float, color: Tuple[int, ...], 
                 speed: float, direction: float, lifetime: int, size: int = 2):
        self.x = x
        self.y = y
        self.color = color[:3]
        self.speed = speed
        self.direction = direction  # in radians
        self.lifetime = lifetime
        self.original_lifetime = lifetime
        self.size = size
        self.alpha = 255
        
    def update(self) -> bool:
        # Move particle
        self.x += math.cos(self.direction) * self.speed
        self.y += math.sin(self.direction) * self.speed
        
        # Update lifetime
        self.lifetime -= 1
        
        # Calculate alpha based on remaining lifetime
        self.alpha = int((self.lifetime / self.original_lifetime) * 255)
        
        # Return True if particle should be kept alive
        return self.lifetime > 0
        
    def draw(self, surface: pygame.Surface, camera_x: int = 0, camera_y: int = 0):
        if self.alpha <= 0:
            return
            
        # Create a surface with per-pixel alpha
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        # Create color with alpha
        color_with_alpha = (self.color[0], self.color[1], self.color[2], self.alpha)
        
        # Draw the particle
        pygame.draw.circle(particle_surface, color_with_alpha, 
                         (self.size, self.size), self.size)
        
        # Draw to main surface with camera offset
        surface.blit(particle_surface, 
                    (self.x - self.size - camera_x, 
                     self.y - self.size - camera_y)) 