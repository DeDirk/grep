from src.constants import COLORS  # Import COLORS from constants

class Settings:
    def __init__(self):
        self.dark_mode = False  # Default to light mode

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.apply_dark_mode()
        else:
            self.apply_light_mode()

    def apply_dark_mode(self):
        """Switch to dark mode by changing color values."""
        COLORS['WHITE'] = (0, 0, 0)  # Change white to grey
        COLORS['BLACK'] = (128, 128, 128) # Change black to grey
        COLORS['DARKGREY'] = (255, 255, 255)  # Change dark grey to white
        COLORS['GRAY'] = (255, 255, 255)  # Change grey to white
        

    def apply_light_mode(self):
        """Revert to light mode by changing color values back."""
        COLORS['WHITE'] = (255, 255, 255)  # Change black back to white
        COLORS['BLACK'] = (0, 0, 0)  # Change white back to black
        COLORS['DARKGREY'] = (64, 64, 64)  # Change dark grey back to dark grey
        COLORS['GRAY'] = (128, 128, 128)  # Change grey back to grey
