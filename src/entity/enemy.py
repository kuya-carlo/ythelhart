"""
This module defines the base Enemy class for the game, providing common
functionality for all enemy types, such as movement, animation, and health.
"""

import math

import pygame

from src.entity.player import Player
from src.prefs import Constants, Enemies
from src.utils import load_enemy_frames


class Enemy(pygame.sprite.Sprite):
    """
    A base class for enemy characters.

    This class handles basic enemy behavior, including chasing the player,
    managing health and damage, and playing animations. It is intended to be
    subclassed for specific enemy types.

    Attributes
    ----------
    xp_given : bool
        A flag to ensure XP is awarded only once upon death.
    xp_reward : int
        The amount of XP awarded for defeating this enemy.
    animations : dict[str, list[pygame.Surface]]
        A dictionary containing lists of frames for different animation states.
    state : str
        The current animation state (e.g., "idle", "attack").
    image : pygame.Surface
        The current frame of the enemy's animation.
    rect : pygame.Rect
        The enemy's collision and position rectangle.
    alive : bool
        A flag indicating if the enemy is alive.
    hp : int
        The current health points of the enemy.
    max_hp : int
        The maximum health points of the enemy.
    radius : int
        The collision radius for circle-based collision detection.
    """

    def __init__(self, x: int, y: int):
        """
        Initializes a new Enemy instance.

        Parameters
        ----------
        x : int
            The initial x-coordinate of the enemy.
        y : int
            The initial y-coordinate of the enemy.
        """
        super().__init__()
        self.xp_given = False
        self.xp_reward = 20

        # --- Animation Setup ---
        self._load_animations()
        self.state = "idle"
        self.frame_index = 0
        self.animation_speed = 8.0
        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect(center=(x, y))
        self.rect.inflate_ip(-48, -48)  # Shrink rect for more precise collisions

        # --- State and Control Flags ---
        object.__setattr__(
            self, "alive", True
        )  # Use object.__setattr__ to bypass potential setters
        self.attacking = False
        self.hurt = False
        self.facing_left = False

        # --- Timers ---
        self.death_timer = 0.0
        self.hit_cd = 0.0  # Cooldown after being hit
        self.flash = 0.0  # Timer for the white flash effect when damaged

        # --- Combat Stats ---
        self.hp = Constants.Enemy.ENEMY_MAX_HP
        self.max_hp = Constants.Enemy.ENEMY_MAX_HP
        self.radius = 6  # For circle-based collision checks

        # --- Movement ---
        self.vx = 0
        self.vy = 0

    def _load_animations(self):
        """Loads all animation frames for the Orc enemy from sprite sheets."""
        self.animations = {
            "idle": load_enemy_frames(Enemies.ORC_SHEET, 64, 64, 6, scale=3),
            "attack": load_enemy_frames(Enemies.ORC_ATTACK, 64, 64, 8, scale=3),
            "hurt": load_enemy_frames(Enemies.ORC_HURT, 64, 64, 4, scale=3),
            "death": load_enemy_frames(Enemies.ORC_DEATH, 64, 64, 8, scale=3),
        }

    def set_state(self, new_state: str):
        """
        Safely changes the enemy's animation state.

        If the new state is different from the current one, it resets the
        animation frame index to 0.

        Parameters
        ----------
        new_state : str
            The new animation state to set (e.g., "attack", "death").
        """
        if new_state != self.state:
            self.state = new_state
            self.frame_index = 0

    def take_damage(self, amount: int, player: Player | None = None) -> bool:
        """
        Reduces the enemy's health and handles the death state.

        Parameters
        ----------
        amount : int
            The amount of damage to inflict.
        player : Player, optional
            The player instance, for potential future use (e.g., aggro).

        Returns
        -------
        bool
            True if the enemy died as a result of this damage, False otherwise.
        """
        if not self.alive:
            return False

        old_hp = self.hp
        self.hp = max(0, self.hp - amount)
        self.hit_cd = 0.25
        self.flash = 0.12
        self.hurt = True

        just_died = old_hp > 0 and self.hp <= 0
        if just_died:
            object.__setattr__(self, "alive", False)
            death_anim_len = len(self.animations["death"])
            self.death_timer = death_anim_len / Constants.Game.ANIMATION_SPEED + 0.2
            self.set_state("death")
            return True

        return False

    def update(self, dt: float, player: Player, walls: list[pygame.Rect] | None = None):
        """
        Updates the enemy's state, including movement, AI, and animations.

        Parameters
        ----------
        dt : float
            The time elapsed since the last frame, in seconds.
        player : Player
            The player sprite, used as the target for movement.
        walls : list[pygame.Rect] | None, optional
            A list of wall rectangles for collision detection. Defaults to None.
        """
        if not self.alive:
            self._handle_death(dt)
            return

        # --- Cooldowns ---
        self.hit_cd = max(0.0, self.hit_cd - dt)
        self.flash = max(0.0, self.flash - dt)
        if self.hurt and self.hit_cd <= 0.0:
            self.hurt = False

        # --- Movement and AI ---
        self._handle_movement(dt, player, walls)

        # --- Animation ---
        self._update_animation_state(player)
        self._advance_animation(dt)

    def _handle_death(self, dt: float):
        """Manages the death animation and removal of the sprite."""
        self._advance_animation(dt)
        self.death_timer -= dt

        # Fade out the sprite before removing it
        fade_time = 0.5
        if self.death_timer < fade_time:
            alpha = max(0, int((self.death_timer / fade_time) * 255))
            self.image.set_alpha(alpha)

        if self.death_timer <= 0:
            self.kill()  # Remove sprite from all groups

    def move_and_collide(self, dt: float, walls: list[pygame.Rect] | None):
        """Move the sprite and handle collisions with walls."""
        self.rect.x += int(self.vx * dt)
        if walls:
            for wall in walls:
                if self.rect.colliderect(wall):
                    if self.vx > 0:
                        self.rect.right = wall.left
                    elif self.vx < 0:
                        self.rect.left = wall.right

        self.rect.y += int(self.vy * dt)
        if walls:
            for wall in walls:
                if self.rect.colliderect(wall):
                    if self.vy > 0:
                        self.rect.bottom = wall.top
                    elif self.vy < 0:
                        self.rect.top = wall.bottom

    def _handle_movement(
        self, dt: float, player: Player, walls: list[pygame.Rect] | None
    ):
        """Moves the enemy towards the player and handles wall collisions."""
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        # Only move if not already at the player's position
        if dist > self.radius + getattr(player, "radius", 20):
            if dist > 0.0001:
                nx, ny = dx / dist, dy / dist
                self.vx = nx * Constants.Enemy.ENEMY_SPEED
                self.vy = ny * Constants.Enemy.ENEMY_SPEED
            else:
                self.vx = 0
                self.vy = 0
        else:
            self.vx = 0
            self.vy = 0

        self.move_and_collide(dt, walls)
        self.facing_left = dx < 0

    def _update_animation_state(self, player: Player):
        """Determines the correct animation state based on the enemy's actions."""
        # Simple distance check for attacking
        # Note: A more robust implementation might use a state machine
        dist_to_player = math.hypot(
            self.rect.centerx - player.rect.centerx,
            self.rect.centery - player.rect.centery,
        )
        attack_range = self.radius + getattr(player, "radius", 20) + 10

        if self.hurt:
            self.set_state("hurt")
        elif dist_to_player <= attack_range:
            self.set_state("attack")
        else:
            self.set_state("idle")

    def _advance_animation(self, dt: float):
        """Advances the current animation frame."""
        frames = self.animations[self.state]

        # Adjust animation speed for different actions
        speed_multiplier = 0.35 if self.state == "attack" else 1.0
        self.frame_index += dt * Constants.Game.ANIMATION_SPEED * speed_multiplier

        # Loop or clamp the frame index
        if self.frame_index >= len(frames):
            if self.state == "death":
                self.frame_index = len(frames) - 1  # Stay on the last frame
            else:
                self.frame_index %= len(frames)  # Loop animation

        frame = frames[int(self.frame_index)]

        # Flip image based on facing direction
        if self.facing_left:
            frame = pygame.transform.flip(frame, True, False)

        center = self.rect.center
        self.image = frame
        self.rect = self.image.get_rect(center=center)
        self.rect.inflate_ip(-40, -40)

    def draw(self, surf: pygame.Surface, camera: pygame.sprite.Sprite | None = None):
        """
        Draws the enemy and its health bar on the given surface.

        Parameters
        ----------
        surf : pygame.Surface
            The surface to draw on.
        camera : pygame.sprite.Sprite | None, optional
            The game camera, used to convert world coordinates to screen coordinates.
        """
        draw_rect = camera.apply_rect(self.rect) if camera else self.rect
        surf.blit(self.image, draw_rect)

        # Draw HP bar above the enemy
        bar_w = max(24, int(draw_rect.width * 0.9))
        bar_h = 6
        bar_x = draw_rect.centerx - (bar_w // 2)
        bar_y = draw_rect.top - (bar_h + 6)

        pct = max(0.0, min(1.0, self.hp / self.max_hp)) if self.max_hp > 0 else 0.0

        pygame.draw.rect(surf, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(surf, (0, 200, 0), (bar_x, bar_y, int(bar_w * pct), bar_h))
        pygame.draw.rect(surf, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 1)
