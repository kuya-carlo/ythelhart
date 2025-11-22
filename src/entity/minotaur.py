"""
This module defines the MinotaurBoss class, a powerful boss enemy that
inherits from the base Enemy class.
"""

import math
from typing import Optional

import pygame

from src.core.camera import Camera
from src.entity.enemy import Enemy
from src.entity.player import Player
from src.prefs import Constants, Enemies
from src.prefs.paths import MUSIC_PATH
from src.utils import load_enemy_frames


class MinotaurBoss(Enemy):
    """
    A large, powerful boss enemy with unique animations and behaviors.

    The Minotaur has a large visual sprite but a smaller, fixed-size collision
    rectangle. It features distinct walk, idle, and attack animations, and can
    trigger screen shakes during its walk cycle. It also has an "enraged" phase
    at low health.

    Attributes
    ----------
    max_hp : int
        The maximum health points of the Minotaur.
    hp : int
        The current health points of the Minotaur.
    damage : int
        The damage dealt by the Minotaur's attack.
    speed : int
        The movement speed of the Minotaur.
    attack_range : int
        The range of the Minotaur's melee attack.
    enraged : bool
        A flag indicating if the Minotaur is in its enraged state.
    camera : Camera | None
        A reference to the game camera, used for screen shake effects.
    """

    FRAME_W = 288
    FRAME_H = 160
    SCALE = 3.5

    def __init__(self, x: int, y: int):
        """
        Initializes a new MinotaurBoss instance.

        Parameters
        ----------
        x : int
            The initial x-coordinate of the boss's center.
        y : int
            The initial y-coordinate of the boss's center.
        """
        super().__init__(x, y)

        # --- Animations ---
        self._load_minotaur_animations()
        self.current_animation = "idle"
        self.cur_frame = 0.0
        self.animation_speed = Constants.Game.ANIMATION_SPEED
        self.image = self.animations[self.current_animation][0]

        # --- Collision and Position ---
        # The Minotaur has a large sprite but a smaller, fixed-size collision box.
        self.rect = pygame.Rect(0, 0, 140, 140)
        self.rect.center = (x, y)
        self.radius = 20  # Collision radius for circle-based checks

        # --- Boss Stats ---
        self.max_hp = 5000
        self.hp = self.max_hp
        self.damage = 70
        self.speed = 120
        self.attack_range = 200
        self.attack_rate = 2.0
        self.attack_cooldown = 0.0
        self.attack_windup = 0.6
        self.attack_timer = 0.0
        self.attacking = False
        self.damage_done = False

        # --- Enrage Phase ---
        object.__setattr__(self, "alive", True)
        self.enraged = False
        self.enrage_threshold = 0.5

        # --- Screen Shake ---
        self.last_footstep_frame = -1
        self.camera: Optional[Camera] = None  # Set by the Game class upon spawning

        # --- Sound ---
        self.footstep_sfx = pygame.mixer.Sound(
            MUSIC_PATH / "SFX" / "Minotaur Footsteps.ogg"
        )

    def _load_minotaur_animations(self):
        """Loads all custom animation frames for the Minotaur."""
        try:
            self.animations = {
                "idle": load_enemy_frames(
                    Enemies.MINO_IDLE, self.FRAME_W, self.FRAME_H, 16, scale=self.SCALE
                ),
                "walk": load_enemy_frames(
                    Enemies.MINO_WALK, self.FRAME_W, self.FRAME_H, 12, scale=self.SCALE
                ),
                "death": load_enemy_frames(
                    Enemies.MINO_IDLE, self.FRAME_W, self.FRAME_H, 16, scale=self.SCALE
                ),  # Placeholder
                "attack": load_enemy_frames(
                    Enemies.MINO_ATTACK,
                    self.FRAME_W,
                    self.FRAME_H,
                    16,
                    scale=self.SCALE,
                ),
            }
        except (pygame.error, FileNotFoundError) as e:
            print(f"[Minotaur] Failed to load custom animations: {e}")

    def _advance_animation(self, dt: float):
        """
        Updates the animation frame, handling looping and screen shake triggers.
        Crucially, this method only updates the `image` attribute, not the `rect`.
        """
        frames = self.animations[self.current_animation]
        self.cur_frame += dt * self.animation_speed

        # Handle non-looping animations (attack, death)
        if self.current_animation in ["attack", "death"]:
            self.cur_frame = min(self.cur_frame, len(frames) - 1)
        # Handle looping animations (idle, walk)
        else:
            self.cur_frame %= len(frames)
            # Trigger screen shake on specific footstep frames during the walk cycle
            if self.current_animation == "walk" and self.camera:
                current_frame_index = int(self.cur_frame)
                footstep_frames = [3, 9]
                if (
                    current_frame_index in footstep_frames
                    and current_frame_index != self.last_footstep_frame
                ):
                    self.camera.add_shake(intensity=8, duration=0.2)
                    self.footstep_sfx.play()
                    self.last_footstep_frame = current_frame_index

        frame = frames[int(self.cur_frame)]

        # Flip the image based on facing direction (assuming sprites face left by default)
        if not getattr(self, "facing_left", False):
            frame = pygame.transform.flip(frame, True, False)

        # Only update the visual image, not the collision rectangle.
        self.image = frame

    def take_damage(self, amount: int, player: Player | None = None) -> bool:
        """
        Reduces the Minotaur's health and checks for enrage or death.

        Parameters
        ----------
        amount : int
            The amount of damage to inflict.
        player : Player, optional
            The player instance (for compatibility).

        Returns
        -------
        bool
            True if the Minotaur is still alive, False otherwise.
        """
        if not self.alive:
            return False

        alive_before = self.hp > 0
        self.hp = max(0, self.hp - amount)
        self.hurt = True
        self.hit_cd = 0.25

        just_died = alive_before and self.hp <= 0
        if just_died:
            object.__setattr__(self, "alive", False)
            self.current_animation = "death"
            death_len = len(self.animations.get("death", [1]))
            self.death_timer = death_len / Constants.Game.ANIMATION_SPEED + 0.2
            return False

        # Check for enrage transition
        if not self.enraged and self.hp <= self.max_hp * self.enrage_threshold:
            self.enraged = True
            self.speed *= 1.25
            self.attack_rate *= 0.85

        return True

    def update(self, dt: float, player: Player, walls: list[pygame.Rect] | None = None):
        """
        Updates the Minotaur's state, including AI, movement, and animations.

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
            self._handle_death_animation(dt)
            return

        # --- AI and Movement ---
        self._handle_ai(dt, player, walls)

        # --- Cooldowns ---
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        self.hit_cd = max(0.0, getattr(self, "hit_cd", 0.0) - dt)

        # --- Animation ---
        self._advance_animation(dt)

    def _handle_death_animation(self, dt: float):
        """Manages the death animation and fades out the sprite."""
        self._advance_animation(dt)
        self.death_timer -= dt
        if self.death_timer < 0.5:
            alpha = max(0, int((self.death_timer / 0.5) * 255))
            try:
                self.image.set_alpha(alpha)
            except pygame.error:
                pass
        if self.death_timer <= 0:
            self.kill()

    def _handle_ai(self, dt: float, player: Player, walls: list[pygame.Rect] | None):
        """Manages AI for movement and attacking."""
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy) or 0.0001
        nx, ny = dx / dist, dy / dist

        self.facing_left = nx < 0

        if self.attacking:
            self.attack_timer += dt
            frame_i = int(self.cur_frame)
            # Apply damage during the attack animation's damage window
            if 7 <= frame_i <= 10 and not self.damage_done:
                if dist <= self.attack_range:
                    player.take_damage(self.damage)
                self.damage_done = True
            # End the attack state when the animation finishes
            if frame_i >= len(self.animations["attack"]) - 1:
                self.attacking = False
                self.damage_done = False
                self.attack_timer = 0.0
                self.attack_cooldown = self.attack_rate
        else:
            # If in range and ready, start an attack
            if dist <= self.attack_range and self.attack_cooldown <= 0.0:
                self.attacking = True
                self.current_animation = "attack"
                self.cur_frame = 0.0
                self.attack_timer = 0.0
            # Otherwise, move towards the player
            elif dist > self.attack_range:
                self.current_animation = "walk"
                self._move_and_collide(dt, nx, ny, walls)
            else:
                self.current_animation = "idle"

    def _move_and_collide(
        self, dt: float, nx: float, ny: float, walls: list[pygame.Rect] | None
    ):
        """Handles movement and wall collision for the Minotaur."""
        move_x = int(nx * self.speed * dt)
        move_y = int(ny * self.speed * dt)

        self.rect.x += move_x
        if walls:
            for wall in walls:
                if self.rect.colliderect(wall):
                    if move_x > 0:
                        self.rect.right = wall.left
                    elif move_x < 0:
                        self.rect.left = wall.right
                    break
        self.rect.y += move_y
        if walls:
            for wall in walls:
                if self.rect.colliderect(wall):
                    if move_y > 0:
                        self.rect.bottom = wall.top
                    elif move_y < 0:
                        self.rect.top = wall.bottom
                    break

    def draw(self, surf: pygame.Surface, camera: Camera | None = None):
        """
        Draws the Minotaur's large sprite centered on its smaller collision rect.

        Parameters
        ----------
        surf : pygame.Surface
            The surface to draw on.
        camera : Camera | None, optional
            The game camera for coordinate translation.
        """
        draw_rect = camera.apply_rect(self.rect) if camera else self.rect
        # Center the large visual sprite on the smaller collision box's screen position
        image_rect = self.image.get_rect(center=draw_rect.center)
        surf.blit(self.image, image_rect)
