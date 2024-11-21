from typing import List, Tuple, Callable
import pygame
from src.constants import WINDOW, COLORS
from src.controls import Controls

class Menu:
    def __init__(self, screen: pygame.Surface, settings=None):
        self.screen = screen
        self.options: List[Tuple[str, Callable]] = []
        self.selected_option = 0
        self.font_large = pygame.font.SysFont("Verdana", 60)
        self.font_small = pygame.font.SysFont("Verdana", 30)
        self.title = ""
        self.settings = settings
        self.controls = Controls()
        self.input_cooldown = 0
        self.cooldown_duration = 200
        
        # Add color properties
        if self.settings:
            self.text_color = self.settings.menu_colors['TEXT_COLOR']
            self.selected_color = self.settings.menu_colors['SELECTED_COLOR']
            self.bg_color = self.settings.menu_colors['MENU_BG']
        else:
            self.text_color = COLORS['BLACK']
            self.selected_color = COLORS['GRAY']
            self.bg_color = COLORS['WHITE']

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
        if keys[pygame.K_l]:  # Add L key check for dark mode toggle
            if self.settings:
                self.settings.toggle_dark_mode()
                self.input_cooldown = current_time + self.cooldown_duration
            
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
        """Render the menu"""
        # Use colors from settings if available, otherwise use defaults
        if self.settings:
            bg_color = self.settings.menu_colors['MENU_BG']
            text_color = self.settings.menu_colors['TEXT_COLOR']
            selected_color = self.settings.menu_colors['SELECTED_COLOR']
        else:
            bg_color = COLORS['WHITE']
            text_color = COLORS['BLACK']
            selected_color = COLORS['GRAY']
            
        self.screen.fill(bg_color)
        
        # Render title
        title_surface = self.font_large.render(self.title, True, text_color)
        title_rect = title_surface.get_rect(center=(WINDOW['WIDTH'] // 2, 200))
        self.screen.blit(title_surface, title_rect)
        
        # Render options
        for i, (text, _) in enumerate(self.options):
            color = selected_color if i == self.selected_option else text_color
            text_surface = self.font_small.render(text, True, color)
            text_rect = text_surface.get_rect(center=(WINDOW['WIDTH'] // 2, 300 + i * 60))
            self.screen.blit(text_surface, text_rect)
        
        pygame.display.update() 

    def update_colors(self):
        """Update colors when dark mode is toggled"""
        if self.settings:
            self.text_color = self.settings.menu_colors['TEXT_COLOR']
            self.selected_color = self.settings.menu_colors['SELECTED_COLOR']
            self.bg_color = self.settings.menu_colors['MENU_BG']
        