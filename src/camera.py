import pygame
from src.constants import WINDOW, MOVEMENT

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.lerp_speed = MOVEMENT['CAMERA']['LERP_SPEED']
        self.deadzone = MOVEMENT['CAMERA']['DEADZONE']
        
    def update(self, player_rect):
        screen_x = player_rect.centerx - self.x
        screen_y = player_rect.centery - self.y
        
        dx = screen_x - (WINDOW['WIDTH'] // 2)
        dy = screen_y - (WINDOW['HEIGHT'] // 2)
        
        if abs(dx) > self.deadzone:
            if dx > 0:
                self.x += (dx - self.deadzone) * self.lerp_speed
            else:
                self.x += (dx + self.deadzone) * self.lerp_speed
                
        if abs(dy) > self.deadzone:
            if dy > 0:
                self.y += (dy - self.deadzone) * self.lerp_speed
            else:
                self.y += (dy + self.deadzone) * self.lerp_speed
        
    def apply(self, rect):
        return pygame.Rect(
            rect.x - int(self.x),
            rect.y - int(self.y),
            rect.width,
            rect.height
        ) 