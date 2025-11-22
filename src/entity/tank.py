"""
This module defines the Tank enemy class, a slow but powerful melee attacker
that inherits from the base Enemy class.
"""

import math

import pygame

from src.entity.enemy import Enemy
from src.entity.player import Player
from src.prefs import Constants, Enemies
from src.utils import load_enemy_frames


class Tank(Enemy):
    """
    A slow, high-health melee enemy.

    The Tank moves slowly towards the player and performs a powerful melee
    attack when in range. It has a higher health pool than other enemies.

    Attributes
    ----------
    xp_reward : int
        The amount of XP awarded for defeating the Tank.
    hp : int
        The current health points of the Tank.
    max_hp : int
        The maximum health points of the Tank.
    attack_range : int
        The range of the Tank's melee attack in pixels.
    damage : int
        The amount of damage dealt by the Tank's attack.
    """

    def __init__(self, x: int, y: int):
        """
        Initializes a new Tank instance.

        Parameters
        ----------
        x : int
            The initial x-coordinate.
        y : int
            The initial y-coordinate.
        """
        super().__init__(x, y)
        self.xp_reward = 40

        # --- Stats ---
        self.hp = 250
        self.max_hp = 250
        self.damage = 50
        self.attack_range = 95

        # --- Attack Timers and State ---
        self.attack_anim_timer = 0.0
        self.attack_anim_duration = 10.0 / (8.0 * 0.7)  # ~1.79 seconds
        self.attack_cooldown = 0.0
        self.attack_rate = 2.0  # Cooldown between attacks
        self.attacking = False
        self.damage_applied = False  # Ensures damage is applied only once per attack

        # --- Hurt State ---
        self.hurt = False
        self.hurt_timer = 0.0

        # --- Animation ---
        self.prev_animation = "idle"
        self._load_tank_animations()
        self.current_animation = "idle"
        self.cur_frame = 0.0

        # Update sprite and rect for Tank size
        try:
            self.image = self.animations["idle"][0]
            self.rect = self.image.get_rect(center=(x, y))
            self.rect.inflate_ip(-38, -38)
        except (KeyError, IndexError):
            # Fallback if animations failed to load
            pass

    def _load_tank_animations(self):
        """Loads all animation frames for the Tank from sprite sheets."""
        try:
            self.animations = {
                "idle": load_enemy_frames(Enemies.TANK_SHEET, 64, 64, 6, scale=3),
                "attack": load_enemy_frames(Enemies.TANK_ATTACK, 64, 64, 10, scale=3),
                "hurt": load_enemy_frames(Enemies.TANK_HURT, 64, 64, 4, scale=3),
                "death": load_enemy_frames(Enemies.TANK_DEATH, 64, 64, 6, scale=3),
            }
        except (pygame.error, FileNotFoundError):
            # Retain parent's animations as a fallback
            pass

    def die(self):
        """Handles the transition to the death state."""
        if not self.alive:
            return
        object.__setattr__(self, "alive", False)
        self.current_animation = "death"
        self.cur_frame = 0.0
        # Calculate death timer based on animation length
        death_len = len(self.animations.get("death", [1]))
        speed = getattr(Constants.Game, "ANIMATION_SPEED", 8.0)
        self.death_timer = death_len / speed + 0.2

    def take_damage(self, amount: int, player: Player | None = None) -> bool:
        """
        Reduces the Tank's health and handles the death state.

        Parameters
        ----------
        amount : int
            The amount of damage to inflict.
        player : Player, optional
            The player instance (for compatibility with parent).

        Returns
        -------
        bool
            True if the Tank died as a result of this damage, False otherwise.
        """
        if not self.alive:
            return False

        old_hp = self.hp
        self.hp -= amount
        self.hurt = True
        self.hurt_timer = 0.25
        self.cur_frame = 0.0

        just_died = old_hp > 0 and self.hp <= 0
        if just_died:
            self.die()
            return True
        return False

    def update(self, dt: float, player: Player, walls: list[pygame.Rect] | None = None):
        """
        Updates the Tank's state, including AI, movement, and animations.

        Parameters
        ----------
        dt : float
            The time elapsed since the last frame, in seconds.
        player : Player
            The player sprite, used as the target.
        walls : list[pygame.Rect] | None, optional
            A list of wall rectangles for collision detection. Defaults to None.
        """
        if self.hurt:
            self.hurt_timer -= dt
            if self.hurt_timer <= 0:
                self.hurt = False

        if not self.alive:
            self._handle_death_animation(dt)
            return

        # --- AI, Movement, and Attack Logic ---
        self._handle_ai(dt, player)

        # --- Wall Collision ---
        if walls:
            self._handle_wall_collision(walls)

        # --- Cooldowns ---
        self.attack_cooldown = max(0, self.attack_cooldown - dt)

        # --- Animation ---
        self._update_animation(dt, player)

    def _handle_death_animation(self, dt: float):
        """Manages the death animation and fades out the sprite."""
        self.current_animation = "death"
        frames = self.animations[self.current_animation]
        self.cur_frame += dt * 8.0
        self.cur_frame = min(self.cur_frame, len(frames) - 1)

        frame = frames[int(self.cur_frame)]
        if self.facing_left:
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame

        # Fade out before removal
        self.death_timer -= dt
        if self.death_timer < 0.5:
            alpha = max(0, int((self.death_timer / 0.5) * 255))
            self.image.set_alpha(alpha)
        if self.death_timer <= 0:
            self.kill()

    def _handle_ai(self, dt: float, player: Player):
        """Manages AI for movement and attacking."""
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy) or 0.0001
        nx, ny = dx / dist, dy / dist

        self.facing_left = nx < 0

        # Move towards player if not in attack range
        if dist > self.attack_range:
            move_speed = Constants.Enemy.ENEMY_SPEED * 0.75
            self.rect.x += int(nx * move_speed * dt)
            self.rect.y += int(ny * move_speed * dt)
        # Attack if in range and not on cooldown
        elif self.attack_cooldown <= 0.0 and not self.attacking:
            self.attacking = True
            self.attack_anim_timer = self.attack_anim_duration
            self.attack_cooldown = self.attack_rate
            self.damage_applied = False

    def _handle_wall_collision(self, walls: list[pygame.Rect]):
        """Corrects the Tank's position after colliding with a wall."""
        for wall in walls:
            if self.rect.colliderect(wall):
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

    def _update_animation(self, dt: float, player: Player):
        """Selects and advances the appropriate animation."""
        # Determine current animation state
        if self.hurt:
            new_animation = "hurt"
        elif self.attacking:
            new_animation = "attack"
        else:
            new_animation = "idle"

        # Reset frame index if animation state changes
        if new_animation != self.prev_animation:
            self.cur_frame = 0.0
            self.current_animation = new_animation
            self.prev_animation = new_animation
        else:
            self.current_animation = new_animation

        # Advance animation frame
        frames = self.animations[self.current_animation]
        speed_multiplier = {"attack": 0.6, "hurt": 0.8, "idle": 0.5}.get(
            self.current_animation, 0.5
        )
        self.cur_frame += dt * 8.0 * speed_multiplier

        # Handle animation looping and attack logic
        if self.current_animation == "attack":
            if self.cur_frame >= len(frames):
                self.cur_frame = len(frames) - 1
                if self.attacking:
                    self.attacking = False
            # Apply damage at the midpoint of the attack animation
            elif not self.damage_applied and int(self.cur_frame) >= len(frames) // 2:
                dist_to_player = math.hypot(
                    player.rect.centerx - self.rect.centerx,
                    player.rect.centery - self.rect.centery,
                )
                if dist_to_player <= self.attack_range + 20:
                    player.take_damage(self.damage)
                self.damage_applied = True
        elif self.cur_frame >= len(frames):
            self.cur_frame = 0.0

        # Set the final image
        frame_idx = min(int(self.cur_frame), len(frames) - 1)
        frame = frames[frame_idx]
        if self.facing_left:
            frame = pygame.transform.flip(frame, True, False)

        center = self.rect.center
        self.image = frame
        self.rect = self.image.get_rect(center=center)
        self.rect.inflate_ip(-38, -38)
