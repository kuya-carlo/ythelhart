"""
This package contains all game entity classes.

Entities are dynamic game objects, such as the player, enemies, and
projectiles. This package makes them easily importable from a single
location.

The `__all__` variable is defined to specify which classes are part of
the public API of this package.
"""

from .enemy import Enemy
from .player import Player
from .projectile import Projectile

__all__ = ["Enemy", "Player", "Projectile"]
