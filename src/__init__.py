"""
Game package - Core game implementation.
Private use only - This is not a library for external use.
"""

__version__ = '0.1.0'

# The only thing that needs to be exposed is the Game class
# since that's what main.py uses to start the game
from .game import Game

__all__ = ['Game'] 