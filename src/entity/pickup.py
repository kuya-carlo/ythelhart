"""
This module implements the pickup/drop system for power-ups and bonuses.

Pickups are dropped by enemies when defeated and provide temporary or
permanent bonuses to the player such as speed boosts, XP multipliers,
damage boosts, and health restoration.
"""

import random
from enum import Enum
from src.prefs.paths import PickupAssets

import pygame


class PickupType(Enum):
    """
    Enumeration of available pickup types.

    Each pickup provides a different bonus to the player.
    """
    SPEED_BOOST = "speed"  # Temporary movement speed increase
    XP_MULTIPLIER = "xp"  # Temporary 2x XP gain
    DAMAGE_BOOST = "damage"  # Temporary 2x damage
    HEALTH_RESTORE = "health"  # Instant health restoration


class Pickup(pygame.sprite.Sprite):
    """
    A collectible pickup that provides bonuses to the player.

    Pickups are spawned when enemies die and float/bounce on the ground.
    When the player collides with them, they apply their effect and disappear.

    Attributes
    ----------
    pickup_type : PickupType
        The type of bonus this pickup provides.
    x : float
        The x-coordinate of the pickup in world space.
    y : float
        The y-coordinate of the pickup in world space.
    image : pygame.Surface
        The visual representation of the pickup.
    rect : pygame.Rect
        The collision rectangle for the pickup.
    lifetime : float
        Time in seconds before the pickup disappears (default 15 seconds).
    bounce_timer : float
        Timer for the bounce animation effect.
    """

    # Pickup visual properties
    SIZE = 40
    COLORS = {
        PickupType.SPEED_BOOST: (100, 200, 255),  # Light blue
        PickupType.XP_MULTIPLIER: (255, 215, 0),  # Gold
        PickupType.DAMAGE_BOOST: (255, 100, 100),  # Red
        PickupType.HEALTH_RESTORE: (100, 255, 100),  # Green
    }

    # Effect durations (in seconds)
    DURATION = {
        PickupType.SPEED_BOOST: 10.0,
        PickupType.XP_MULTIPLIER: 15.0,
        PickupType.DAMAGE_BOOST: 10.0,
        PickupType.HEALTH_RESTORE: 0.0,  # Instant effect
    }

    # Effect values
    VALUES = {
        PickupType.SPEED_BOOST: 1.5,  # 50% speed increase
        PickupType.XP_MULTIPLIER: 2.0,  # 2x XP
        PickupType.DAMAGE_BOOST: 2.0,  # 2x damage
        PickupType.HEALTH_RESTORE: 50,  # 50 HP restored
    }

    def __init__(self, x: float, y: float, pickup_type: PickupType):
        """
        Initializes a new Pickup instance.

        Parameters
        ----------
        x : float
            The x-coordinate in world space.
        y : float
            The y-coordinate in world space.
        pickup_type : PickupType
            The type of pickup to create.
        """
        super().__init__()

        self.pickup_type = pickup_type
        self.x = x
        self.y = y

        # Create the visual representation
        self.image = self._create_image()
        self.rect = self.image.get_rect(center=(int(x), int(y)))

        # Pickup behavior
        self.lifetime = 15.0  # Disappears after 15 seconds
        self.bounce_timer = 0.0
        self.alpha = 255  # For fade-out effect

    def _create_image(self) -> pygame.Surface:
        """
        Creates the visual representation of the pickup.

        Returns
        -------
        pygame.Surface
            The rendered pickup sprite.
        """
        if self.pickup_type == PickupType.SPEED_BOOST:
            path = PickupAssets.SPEED_BOOST
        elif self.pickup_type == PickupType.XP_MULTIPLIER:
            path = PickupAssets.XP_MULTIPLIER
        elif self.pickup_type == PickupType.DAMAGE_BOOST:
            path = PickupAssets.DAMAGE_BOOST
        elif self.pickup_type == PickupType.HEALTH_RESTORE:
            path = PickupAssets.HEALTH_RESTORE

        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, (self.SIZE, self.SIZE))
        return image

    def update(self, dt: float):
        """
        Updates the pickup's state and animations.

        Parameters
        ----------
        dt : float
            Time elapsed since last frame in seconds.
        """
        # Update lifetime
        self.lifetime -= dt

        # Fade out in last 3 seconds
        if self.lifetime < 3.0:
            self.alpha = int((self.lifetime / 3.0) * 255)
            self.image.set_alpha(self.alpha)

        # Remove if expired
        if self.lifetime <= 0:
            self.kill()

        # Bounce animation
        self.bounce_timer += dt * 5
        bounce_offset = int(abs(pygame.math.Vector2(0, 1).rotate(self.bounce_timer * 180).y) * 5)
        self.rect.centery = int(self.y) - bounce_offset

    def draw(self, surface: pygame.Surface, camera=None):
        """
        Draws the pickup on the screen.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to draw on.
        camera : Camera, optional
            The game camera for coordinate translation.
        """
        if camera:
            screen_rect = camera.apply_rect(self.rect)
            surface.blit(self.image, screen_rect)
        else:
            surface.blit(self.image, self.rect)

    def apply_effect(self, player) -> str:
        """
        Applies the pickup's effect to the player.

        Parameters
        ----------
        player : Player
            The player to apply the effect to.

        Returns
        -------
        str
            A message describing the effect applied.
        """
        if self.pickup_type == PickupType.SPEED_BOOST:
            player.add_speed_boost(self.VALUES[PickupType.SPEED_BOOST], self.DURATION[PickupType.SPEED_BOOST])
            return f"Speed Boost! +{int((self.VALUES[PickupType.SPEED_BOOST] - 1) * 100)}% speed for {self.DURATION[PickupType.SPEED_BOOST]}s"

        elif self.pickup_type == PickupType.XP_MULTIPLIER:
            player.add_xp_multiplier(self.VALUES[PickupType.XP_MULTIPLIER], self.DURATION[PickupType.XP_MULTIPLIER])
            return f"XP Multiplier! {self.VALUES[PickupType.XP_MULTIPLIER]}x XP for {self.DURATION[PickupType.XP_MULTIPLIER]}s"

        elif self.pickup_type == PickupType.DAMAGE_BOOST:
            player.add_damage_boost(self.VALUES[PickupType.DAMAGE_BOOST], self.DURATION[PickupType.DAMAGE_BOOST])
            return f"Damage Boost! {self.VALUES[PickupType.DAMAGE_BOOST]}x damage for {self.DURATION[PickupType.DAMAGE_BOOST]}s"

        elif self.pickup_type == PickupType.HEALTH_RESTORE:
            max_hp = player.get_effective_max_hp()
            if player.hp >= max_hp:
                return "Health full! Pickup ignored."
            heal_amount = min(self.VALUES[PickupType.HEALTH_RESTORE], max_hp - player.hp)
            player.hp += heal_amount
            return f"Health Restored! +{int(heal_amount)} HP"

        return "Pickup collected!"


def spawn_random_pickup(x: float, y: float, drop_chance: float = 0.3) -> Pickup | None:
    """
    Spawns a random pickup at the given location with a certain probability.

    Parameters
    ----------
    x : float
        The x-coordinate in world space.
    y : float
        The y-coordinate in world space.
    drop_chance : float, optional
        The probability (0.0 to 1.0) that a pickup will spawn. Defaults to 0.3 (30%).

    Returns
    -------
    Pickup | None
        A new Pickup instance if one is spawned, otherwise None.
    """
    if random.random() > drop_chance:
        return None

    # Weighted random selection (health is more common)
    pickup_types = [
        PickupType.HEALTH_RESTORE,  # 40% chance
        PickupType.HEALTH_RESTORE,
        PickupType.SPEED_BOOST,  # 20% chance
        PickupType.XP_MULTIPLIER,  # 20% chance
        PickupType.DAMAGE_BOOST,  # 20% chance
    ]

    pickup_type = random.choice(pickup_types)
    return Pickup(x, y, pickup_type)