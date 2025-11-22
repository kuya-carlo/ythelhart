"""
This package contains the core components of the game engine.

It includes the main game loop, menu systems, and other fundamental
modules that orchestrate the overall game flow and user experience.

The `__all__` variable is defined to specify which names are exported
when `from src.core import *` is used, providing a clear public API.
"""

from .game import Game
from .menu import MainMenu
from .progressbar import ProgressBar

__all__ = ["Game", "MainMenu", "ProgressBar"]
