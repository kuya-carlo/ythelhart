"""
This module defines the Rogue enemy class, a ranged attacker that inherits
from the base Enemy class.
"""

import math

import pygame

from src.entity.enemy import Enemy
from src.entity.player import Player
from src.entity.projectile import Projectile
from src.prefs import Constants, Enemies
from src.utils import load_enemy_frames


class Rogue(Enemy):
    """
    A ranged enemy that shoots projectiles at the player.

    The Rogue maintains a certain distance from the player, backing away if
    too close and approaching if too far. It fires projectiles when the
    player is within its shooting range.

    Attributes
    ----------
    xp_reward : int
        The amount of XP awarded for defeating the Rogue.
    attack_rate : float
        The time in seconds between each shot.
    shoot_range : int
        The maximum distance in pixels from which the Rogue can shoot.
    min_keep_distance : int
        The minimum distance the Rogue tries to maintain from the player.
    projectiles_group : pygame.sprite.Group | None
        The sprite group to which new projectiles will be added.
    """

    def __init__(
        self,
        x: int,
        y: int,
        projectiles_group: pygame.sprite.Group | None = None,
        map_rect: pygame.Rect | None = None,
        walls: list[pygame.Rect] | None = None,
        wave: int = 1,
    ):
        """
        Initializes a new Rogue instance.

        Parameters
        ----------
        x : int
            The initial x-coordinate.
        y : int
            The initial y-coordinate.
        projectiles_group : pygame.sprite.Group | None, optional
            The group to add fired projectiles to. Defaults to None.
        map_rect : pygame.Rect | None, optional
            The rectangle defining the map boundaries, for projectile cleanup.
            Defaults to None.
        walls : list[pygame.Rect] | None, optional
            A list of wall rectangles for collision detection. Defaults to None.
        wave : int, optional
            The wave number this enemy spawns in, for potential scaling.
            Defaults to 1.
        """
        super().__init__(x, y)
        self.xp_reward = 30
        self.wave = wave
        self.attack_anim_timer = 0.0
        self.attack_anim_duration = 0.4  # Animation duration in seconds

        # --- Stat Adjustments ---
        # Rogues have less health than standard enemies.
        self.hp = max(1, int(Constants.Enemy.ENEMY_MAX_HP * 0.6))
        self.max_hp = self.hp

        # --- Animations ---
        # Load Rogue-specific animations, falling back to the parent's if they fail.
        self._load_rogue_animations()

        # --- Ranged Combat AI ---
        self.attack_cooldown = 0.0
        self.attack_rate = 1.4  # Seconds between shots
        self.shoot_range = 700
        self.min_keep_distance = 120
        self.projectiles_group = projectiles_group
        self.map_rect = map_rect
        self.walls = walls

        # Rogues have a smaller collision radius.
        self.radius = max(6, self.rect.width // 6)

    def _load_rogue_animations(self):
        """Loads all animation frames for the Rogue from sprite sheets."""
        try:
            self.animations = {
                "idle": load_enemy_frames(Enemies.ROGUE_SHEET, 64, 64, 6, scale=3),
                "attack": load_enemy_frames(Enemies.ROGUE_ATTACK, 64, 64, 8, scale=3),
                "hurt": load_enemy_frames(Enemies.ROGUE_HURT, 64, 64, 4, scale=3),
                "death": load_enemy_frames(Enemies.ROGUE_DEATH, 64, 64, 6, scale=3),
            }
        except (pygame.error, FileNotFoundError):
            # If loading fails, the animations from the parent Enemy class are retained.
            pass

    def can_shoot(self) -> bool:
        """
        Checks if the Rogue is able to shoot.

        Returns
        -------
        bool
            True if the attack cooldown is finished, False otherwise.
        """
        return self.attack_cooldown <= 0.0

    def do_shoot(self, target_pos: tuple[int, int], player_ref: Player):
        """
        Creates and fires a projectile towards a target.

        Parameters
        ----------
        target_pos : tuple[int, int]
            The (x, y) coordinates of the target.
        player_ref : Player
            A reference to the player sprite, for collision checking.
        """
        if self.projectiles_group is None:
            return

        proj = Projectile(
            start=self.rect.center,
            target=target_pos,
            map_rect=self.map_rect,
            enemies=None,  # Rogue projectiles don't hit other enemies
            walls=self.walls,
            speed=400,  # Slower than player projectiles
            damage=5,
            owner="rogue",  # Set the owner to this Rogue instance
            player_ref=player_ref,
        )

        self.projectiles_group.add(proj)
        self.attack_cooldown = self.attack_rate

    def update(self, dt: float, player: Player, walls: list[pygame.Rect] | None = None):
        """
        Updates the Rogue's state, including AI, movement, and animations.

        Parameters
        ----------
        dt : float
            The time elapsed since the last frame, in seconds.
        player : Player
            The player sprite, used as the target.
        walls : list[pygame.Rect] | None, optional
            A list of wall rectangles for collision detection. Defaults to None.
        """
        if not self.alive:
            super().update(dt, player, walls)  # Let parent handle death animation
            return

        # --- AI and Movement ---
        self._handle_ai_movement(dt, player, walls)

        # --- Cooldowns and Timers ---
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        if self.attack_anim_timer > 0:
            self.attack_anim_timer -= dt
            self.attacking = True
        else:
            self.attacking = False

        # --- Animation ---
        self._update_animation_state()
        self._advance_animation(dt)

    def _handle_ai_movement(
        self, dt: float, player: Player, walls: list[pygame.Rect] | None
    ):
        """Manages the Rogue's movement based on its distance to the player."""
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy) if (dx != 0 or dy != 0) else 0.0001
        nx, ny = (dx / dist, dy / dist) if dist else (0, 0)

        self.facing_left = nx < 0

        # AI decision-making: back away, shoot, or approach.
        if dist < self.min_keep_distance:
            # Too close, back away from the player.
            move_speed = Constants.Enemy.ENEMY_SPEED * 0.6
            self.rect.x -= int(nx * move_speed * dt)
            self.rect.y -= int(ny * move_speed * dt)
        elif dist <= self.shoot_range and self.can_shoot():
            # In range and ready to shoot, so stop and attack.
            self.attacking = True
            self.attack_anim_timer = self.attack_anim_duration
            self.do_shoot(player.rect.center, player_ref=player)
        else:
            # Out of range or on cooldown, so approach the player.
            move_speed = Constants.Enemy.ENEMY_SPEED * 0.9
            self.rect.x += int(nx * move_speed * dt)
            self.rect.y += int(ny * move_speed * dt)

        # Handle wall collisions after movement.
        if walls:
            self._handle_wall_collision(walls)

    def _handle_wall_collision(self, walls: list[pygame.Rect]):
        """Corrects the Rogue's position after colliding with a wall."""
        for wall in walls:
            if self.rect.colliderect(wall):
                # A simple push-out correction.
                if abs(self.rect.centerx - wall.centerx) > abs(
                    self.rect.centery - wall.centery
                ):
                    if self.rect.centerx > wall.centerx:
                        self.rect.left = wall.right
                    else:
                        self.rect.right = wall.left
                else:
                    if self.rect.centery > wall.centery:
                        self.rect.top = wall.bottom
                    else:
                        self.rect.bottom = wall.top

    def _update_animation_state(self):
        """Sets the current animation based on the Rogue's state."""
        if self.hurt:
            self.set_state("hurt")
        elif self.attacking:
            self.set_state("attack")
        else:
            self.set_state("idle")
