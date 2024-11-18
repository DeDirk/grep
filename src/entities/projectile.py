import math
import random

import pygame

from src.constants import WINDOW, COLORS, SIZES, MOVEMENT

class Projectile:
    def __init__(self, position, direction, radius=SIZES['PROJECTILE']['RADIUS'], 
                 speed=None, color=COLORS['BLACK']) -> None:
        self.radius = radius
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (self.radius, self.radius), self.radius)
        
        self.rect = self.image.get_rect()
        self.rect.center = position

        inaccuracy = MOVEMENT['PROJECTILE']['INACCURACY']
        direction = (
            direction[0] + random.uniform(-inaccuracy, inaccuracy),
            direction[1] + random.uniform(-inaccuracy, inaccuracy)
        )

        magnitude = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
        self.direction = (direction[0] / magnitude, direction[1] / magnitude)
        
        if speed is None:
            self.speed = random.uniform(
                MOVEMENT['PROJECTILE']['ENEMY_SPEED']['MIN'],
                MOVEMENT['PROJECTILE']['ENEMY_SPEED']['MAX']
            )
        else:
            variation = MOVEMENT['PROJECTILE']['PLAYER_SPEED']['VARIATION']
            self.speed = speed * (1 + random.uniform(-variation, variation))
        
        # Store velocity components
        self.velocity = (self.direction[0] * self.speed, self.direction[1] * self.speed)
            
        self.from_enemy = True
        self.hits = 0
        self.max_hits = 25

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