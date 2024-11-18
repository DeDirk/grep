import math
import random

import pygame

from src.constants import (
    WINDOW,
    COLORS,
    ITEMS,
    PLAYER
)

class Item:
    def __init__(self, position, item_type="stamina", size=20):
        """
        Initialize an item
        
        Args:
            position (tuple): (x, y) coordinates for item spawn
            item_type (str): Type of item ("stamina", etc.)
            size (int): Radius of the item
        """
        self.item_type = item_type
        self.size = size
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = ITEMS['LIFETIME']
        self.occupied_space = ITEMS['SPAWN']['MIN_DISTANCE']
        self.color = COLORS['GREEN']
        
        # Create the item's surface and rectangle
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (size, size), size)
        
        # Add a pulsing effect
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.original_size = size
        self.pulse_counter = random.random() * math.pi * 2  # Random start phase
        self.pulse_speed = 0.1
        
    def update(self):
        """Update the item's visual effects"""
        # Create a pulsing effect
        self.pulse_counter += self.pulse_speed
        scale_factor = 1 + math.sin(self.pulse_counter) * 0.1  # 10% size variation
        
        current_size = int(self.original_size * scale_factor)
        self.image = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (current_size, current_size), current_size)
        
        # Keep the center position while updating the rect size
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center
        
    def apply_effect(self, player):
        """Apply the item's effect to the player"""
        if self.item_type == "stamina":
            restore_amount = player.max_stamina * ITEMS['STAMINA_RESTORE']
            player.current_stamina = min(player.max_stamina, 
                                       player.current_stamina + restore_amount)
            player.is_exhausted = False
            player.stamina_bar_visible = PLAYER['STAMINA']['BAR']['FADE_TIME']
        
    def should_despawn(self, camera):
        """Check if item should despawn based on lifetime and visibility"""
        current_time = pygame.time.get_ticks()
        time_alive = current_time - self.spawn_time
        
        # If item has existed for more than lifetime
        if time_alive > self.lifetime:
            # Check if item is visible on screen
            item_screen_pos = camera.apply(self.rect)
            screen_rect = pygame.Rect(0, 0, WINDOW['WIDTH'], WINDOW['HEIGHT'])
            
            # Only despawn if item is off screen
            return not screen_rect.colliderect(item_screen_pos)
            
        return False