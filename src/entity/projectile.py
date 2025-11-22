"""
This module defines the Projectile class, used for arrows fired by both
the player and enemies like the Rogue.
"""

import math

import pygame

from src.entity.player import Player
from src.prefs import Constants
from src.prefs.paths import Projectiles


class Projectile(pygame.sprite.Sprite):
    """
    A projectile that moves in a straight line and detects collisions.

    This class manages the movement, rotation, and collision of projectiles.
    It can be owned by either the player or an enemy, determining what it
    can collide with and damage.

    Attributes
    ----------
    speed : int
        The speed of the projectile in pixels per second.
    damage : int
        The amount of damage the projectile inflicts upon collision.
    owner : str
        The owner of the projectile ("player" or "rogue").
    image : pygame.Surface
        The current visual representation of the projectile.
    rect : pygame.Rect
        The collision rectangle of the projectile.
    stuck : bool
        A flag indicating if the projectile is stuck in a wall or entity.
    """

    def __init__(
        self,
        start: tuple[int, int],
        target: tuple[int, int],
        map_rect: pygame.Rect | None = None,
        enemies: pygame.sprite.Group | None = None,
        walls: list[pygame.Rect] | None = None,
        speed: int = Constants.Attack.PROJECTILE_SPEED,
        damage: int = Constants.Player.PLAYER_DAMAGE,
        owner: str = "player",
        player_ref: Player | None = None,
    ):
        """
        Initializes a new Projectile instance.

        Parameters
        ----------
        start : tuple[int, int]
            The starting (x, y) coordinates.
        target : tuple[int, int]
            The target (x, y) coordinates to aim at.
        map_rect : pygame.Rect | None, optional
            The rectangle defining the map boundaries. Defaults to None.
        enemies : pygame.sprite.Group | None, optional
            A sprite group of enemies for collision detection. Defaults to None.
        walls : list[pygame.Rect] | None, optional
            A list of wall rectangles for collision. Defaults to None.
        speed : int, optional
            The speed of the projectile. Defaults to `Constants.Attack.PROJECTILE_SPEED`.
        damage : int, optional
            The damage dealt by the projectile. Defaults to `Constants.Player.PLAYER_DAMAGE`.
        owner : str, optional
            The owner of the projectile ("player" or "rogue"). Defaults to "player".
        player_ref : Player | None, optional
            A reference to the player sprite, for enemy projectiles. Defaults to None.
        """
        super().__init__()
        self.speed = speed
        self.damage = damage
        self.owner = owner
        self.player_ref = player_ref
        self.enemies = enemies
        self.walls = walls
        self.map_rect = map_rect

        # --- Sprite and Rotation Setup ---
        self._load_and_rotate_assets(start, target)

        # --- Position and Velocity ---
        self._pos_x = float(self.rect.centerx)
        self._pos_y = float(self.rect.centery)
        self._calculate_velocity(start, target)

        # --- State ---
        self.stuck = False
        self.decay_timer = 0.0

    def _load_and_rotate_assets(self, start: tuple[int, int], target: tuple[int, int]):
        """Loads projectile images, scales them, and rotates them to face the target."""
        sheet = pygame.image.load(Projectiles.ARROW).convert_alpha()
        frame_w, frame_h = sheet.get_width() // 5, sheet.get_height()

        # Extract base images for full and broken arrows
        full_arrow = sheet.subsurface((0, 0, frame_w, frame_h))
        broken_arrow = sheet.subsurface((frame_w * 4, 0, frame_w, frame_h))

        # Scale images
        scale = 2.2
        self.full_image_clean = pygame.transform.scale(
            full_arrow, (int(frame_w * scale), int(frame_h * scale))
        )
        self.broken_image_clean = pygame.transform.scale(
            broken_arrow, (int(frame_w * scale), int(frame_h * scale))
        )

        # Calculate rotation angle
        dx, dy = target[0] - start[0], target[1] - start[1]
        angle = math.degrees(math.atan2(-dy, dx))

        # Rotate images
        self.full_image = pygame.transform.rotate(self.full_image_clean, angle)
        self.broken_image = pygame.transform.rotate(self.broken_image_clean, angle)

        self.image = self.full_image
        self.rect = self.image.get_rect(center=start)

    def _calculate_velocity(self, start: tuple[int, int], target: tuple[int, int]):
        """Calculates the velocity vector based on start and target positions."""
        dx, dy = target[0] - start[0], target[1] - start[1]
        dist = math.hypot(dx, dy) or 1.0
        self.vx = (dx / dist) * self.speed
        self.vy = (dy / dist) * self.speed

    def stick(self, broken: bool = False):
        """
        Stops the projectile's movement and starts its decay timer.

        Parameters
        ----------
        broken : bool, optional
            If True, the projectile's image is changed to the broken state.
            Defaults to False.
        """
        self.stuck = True
        self.vx = 0
        self.vy = 0
        self.decay_timer = 5.0  # 5 seconds until it disappears

        self.image = self.broken_image if broken else self.full_image
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self, dt: float):
        """
        Updates the projectile's position and checks for collisions.

        Parameters
        ----------
        dt : float
            The time elapsed since the last frame, in seconds.
        """
        if self.stuck:
            self.decay_timer -= dt
            if self.decay_timer <= 0:
                self.kill()
            return

        # --- Movement ---
        self._pos_x += self.vx * dt
        self._pos_y += self.vy * dt
        self.rect.center = (int(self._pos_x), int(self._pos_y))

        # --- Collision Detection ---
        # Check for wall collisions
        if self.walls and self.rect.collidelist(self.walls) != -1:
            self.stick(broken=True)
            return
        # Check for out-of-bounds
        if self.map_rect and not self.map_rect.colliderect(self.rect):
            self.stick(broken=True)
            return

        # --- Target-specific Collision ---
        if self.owner == "player" and self.enemies:
            self._check_enemy_collision()
        elif self.owner == "rogue" and self.player_ref:
            self._check_player_collision()

    def _check_enemy_collision(self):
        """Checks for and handles collisions with enemies."""
        if self.enemies:
            hit_enemy = pygame.sprite.spritecollideany(self, self.enemies)
            if hit_enemy and hit_enemy.alive:
                hit_enemy.take_damage(self.damage, player=self.player_ref)
                self.stick(broken=True)

    def _check_player_collision(self):
        """Checks for and handles collisions with the player."""
        if self.player_ref:
            # Use a smaller hitbox for more accurate player collision
            player_hitbox = self.player_ref.rect.inflate(
                -self.player_ref.rect.width * 0.5, -self.player_ref.rect.height * 0.5
            )
            if self.rect.colliderect(player_hitbox):
                self.player_ref.take_damage(self.damage)
                self.stick(broken=True)
