from typing import List, Tuple, Callable
import pygame
from src.constants import WINDOW, COLORS
from src.controls import Controls

class Menu:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.options: List[Tuple[str, Callable]] = []
        self.selected_option = 0
        self.font_large = pygame.font.SysFont("Verdana", 60)
        self.font_small = pygame.font.SysFont("Verdana", 30)
        self.title = ""
        self.background_color = COLORS['WHITE']
        self.text_color = COLORS['BLACK']
        self.selected_color = COLORS['RED']
        self.controls = Controls()
        self.input_cooldown = 0
        self.cooldown_duration = 200
        
    def set_title(self, title: str):
        self.title = title
        
    def add_option(self, text: str, callback: Callable):
        self.options.append((text, callback))
        
    def handle_input(self):
        current_time = pygame.time.get_ticks()
        if current_time < self.input_cooldown:
            return

        # Handle keyboard input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.selected_option = (self.selected_option - 1) % len(self.options)
            self.input_cooldown = current_time + self.cooldown_duration
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.selected_option = (self.selected_option + 1) % len(self.options)
            self.input_cooldown = current_time + self.cooldown_duration
        elif keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
            self.options[self.selected_option][1]()  # Call the callback function
            self.input_cooldown = current_time + self.cooldown_duration
        
    def render(self):
        self.screen.fill(self.background_color)
        
        # Draw title
        title_surface = self.font_large.render(self.title, True, self.text_color)
        title_rect = title_surface.get_rect(center=(WINDOW['WIDTH'] // 2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # Draw options
        for i, (text, _) in enumerate(self.options):
            color = self.selected_color if i == self.selected_option else self.text_color
            text_surface = self.font_small.render(text, True, color)
            text_rect = text_surface.get_rect(
                center=(WINDOW['WIDTH'] // 2, 300 + i * 60)
            )
            self.screen.blit(text_surface, text_rect)
            
        pygame.display.update() 