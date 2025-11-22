"""
This package centralizes the game's preferences, including constants, asset paths, and styling.

It exposes key classes and variables for easy access from other parts of the application.
By importing from `prefs`, other modules can access:
- `Constants`: A collection of game-wide numerical and string constants.
- `Style`: Classes for managing colors and fonts.
- Various path-related classes and variables for accessing game assets.

The `__all__` variable is defined to specify which names are exported when `from prefs import *`
is used, promoting a cleaner namespace.
"""

from .constants import Constants
from .paths import (
    IMAGE_PATH,
    MAP_PATH,
    SPRITE_PATH,
    ActionAssets,
    Backgrounds,
    Enemies,
    Extras,
    FontPath,
    MainMap,
    Map,
    MapAsset,
    Music,
    Player,
)
from .style import Style

# Defines the public API for this package.
__all__ = [
    "IMAGE_PATH",
    "Constants",
    "FontPath",
    "Music",
    "ActionAssets",
    "Backgrounds",
    "Enemies",
    "Extras",
    "MAP_PATH",
    "MainMap",
    "Map",
    "MapAsset",
    "Player",
    "SPRITE_PATH",
    "Style",
]
