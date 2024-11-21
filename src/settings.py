from src.constants import COLORS, MENU  # Import COLORS from constants

class Settings:
    def __init__(self):
        self.dark_mode = False  # Default to light mode
        self.menu_colors = MENU['LIGHT_MODE']  # Initialize menu colors

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.apply_dark_mode()
        else:
            self.apply_light_mode()
        
        # Update any active menus
        from src.game import Game
        if hasattr(Game, 'instance') and Game.instance and Game.instance.menu:
            Game.instance.menu.update_colors()

    def apply_dark_mode(self):
        """Switch to dark mode by changing color values."""
        COLORS['WHITE'] = (0, 0, 0)  # Keep this as black (unused)
        COLORS['BLACK'] = (128, 128, 128)  # Change black to grey for walls
        COLORS['PROJECTILE'] = (255, 255, 255)  # New color: white for projectiles in dark mode
        COLORS['DARKGREY'] = (255, 255, 255)  # Change dark grey to white
        COLORS['GRAY'] = (255, 255, 255)  # Change grey to white
        self.menu_colors = MENU['DARK_MODE']  # Update menu colors

    def apply_light_mode(self):
        """Revert to light mode by changing color values back."""
        COLORS['WHITE'] = (255, 255, 255)  # Keep this as white (unused)
        COLORS['BLACK'] = (0, 0, 0)  # Change grey back to black for walls
        COLORS['PROJECTILE'] = (0, 0, 0)  # New color: black for projectiles in light mode
        COLORS['DARKGREY'] = (64, 64, 64)  # Change white back to dark grey
        COLORS['GRAY'] = (128, 128, 128)  # Change grey back to grey
        self.menu_colors = MENU['LIGHT_MODE']  # Update menu colors
