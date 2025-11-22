"""
This module defines the Player class, which represents the user-controlled
character in the game.
"""

import math

import pygame

from src.prefs import Constants
from src.prefs.paths import Player as player_assets
from src.systems.level_system import LevelSystem
from src.utils import load_frames


class Player(pygame.sprite.Sprite):
    """
    Represents the player character, handling movement, animations, and combat.

    This class manages the player's state, including health, stamina, position,
    and animations. It processes user input for movement and actions.

    Attributes
    ----------
    level_system : LevelSystem | None
        A reference to the game's level system for stat bonuses.
    scale : float
        The scaling factor for the player's sprite.
    anim : dict[str, list[pygame.Surface]]
        A dictionary mapping animation states to lists of frames.
    state : str
        The current animation state (e.g., "idle_down").
    image : pygame.Surface
        The current frame of the player's animation.
    rect : pygame.Rect
        The player's position and dimensions on the screen.
    speed : int
        The base movement speed of the player.
    radius : int
        The collision radius for circle-based collision detection.
    max_hp : int
        The maximum health points of the player.
    hp : int
        The current health points of the player.
    dead : bool
        True if the player's health has reached zero.
    """

    def __init__(self, level_system: LevelSystem | None = None):
        """
        Initializes the Player instance.

        Parameters
        ----------
        level_system : LevelSystem, optional
            A reference to the game's level system to apply stat bonuses.
            Defaults to None.
        """
        super().__init__()

        self.level_system = level_system

        # --- Animation Setup ---
        self.scale = 3.2
        self.anim = {}
        self._load_animations()

        # --- Initial State ---
        self.state = "idle_down"
        self.frame = 0.0
        self.frame_speed = 10.0
        self.image = self.anim[self.state][0]
        self.rect = self.image.get_rect(center=(100, 100))

        # --- Movement and Position ---
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 150
        self.radius = 12  # For collision detection
        self.hitbox = self.rect.inflate(-40, -30)

        # --- Combat and Health Stats ---
        self.max_hp = 100
        self.hp = self.max_hp
        self.invuln_timer = 0.0  # Invulnerability time after taking damage
        self.attack_cooldown = 0.0
        self.can_shoot_flag = True
        self.dead = False

        # --- Stamina for Running ---
        self.max_stamina = 250
        self.stamina = self.max_stamina
        self.stamina_regen_rate = 40
        self.stamina_drain_rate = 40
        self.running = False
        self.is_exhausted = False

        # --- Facing Direction ---
        self.facing = "down"
        self.flip_side = False  # For horizontal flipping of side-facing sprites

        # --- Timers ---
        self.hurt_timer = 0.0
        self.hurt_duration = 1.0

        # --- Healing ---
        self.healing_timer = 0.0
        self.healing_amount = 0.0

        # Buff/power-up system
        self.speed_boost_multiplier = 1.0
        self.speed_boost_timer = 0.0

        self.xp_multiplier = 1.0
        self.xp_multiplier_timer = 0.0

        self.damage_boost_multiplier = 1.0
        self.damage_boost_timer = 0.0

    def _load_animations(self):
        """Loads all player animation frames from sprite sheets."""
        actions = ["IDLE", "WALK", "RUN", "HURT", "DEATH"]
        directions = ["DOWN", "UP", "SIDE"]

        for action in actions:
            action_assets = getattr(player_assets, action)
            for direction in directions:
                key = f"{action.lower()}_{direction.lower()}"
                sheet_path = getattr(action_assets, direction)
                self.anim[key] = load_frames(sheet_path, int(self.scale))

    def get_effective_max_hp(self) -> int:
        """
        Calculates the player's maximum HP, including bonuses from the level system.

        Returns
        -------
        int
            The effective maximum HP.
        """
        if self.level_system:
            return self.max_hp + self.level_system.get_health_bonus()
        return self.max_hp

    def get_movement_speed(self) -> float:
        """
        Calculates the player's movement speed, including agility bonuses AND speed boost.

        Returns
        -------
        float
            The effective movement speed.
        """
        base_speed = self.speed
        if self.level_system:
            base_speed *= self.level_system.get_agility_multiplier()

        # Apply temporary speed boost
        return base_speed * self.speed_boost_multiplier

    def apply_knockback(self, enemy_center: tuple[int, int]):
        """
        Applies a knockback force to the player, pushing them away from an enemy.

        Parameters
        ----------
        enemy_center : tuple[int, int]
            The center coordinates of the enemy causing the knockback.
        """
        dx = self.rect.centerx - enemy_center[0]
        dy = self.rect.centery - enemy_center[1]
        dist = max(0.01, math.hypot(dx, dy))
        nx, ny = dx / dist, dy / dist
        knock_px = int(Constants.Attack.KNOCKBACK_FORCE * 0.02)
        self.rect.centerx += int(nx * knock_px)
        self.rect.centery += int(ny * knock_px)

    def take_damage(self, amount: int) -> bool:
        """
        Reduces the player's health by a given amount.

        Triggers invulnerability and the hurt animation. If health drops to zero,
        the player enters the 'dead' state.

        Parameters
        ----------
        amount : int
            The amount of damage to inflict.

        Returns
        -------
        bool
            True if damage was taken, False otherwise (e.g., if invulnerable).
        """
        if self.invuln_timer > 0 or self.dead:
            return False

        self.hp = max(0, self.hp - amount)
        self.invuln_timer = Constants.Attack.INVULN_TIME

        if self.hp <= 0:
            self.dead = True
            self.state = "death_" + self.facing
            self.frame = 0
            return True

        # Enter the hurt state
        self.hurt_timer = self.hurt_duration
        self.state = "hurt_" + self.facing
        self.frame = 0
        return True

    def start_healing(self, amount: int, duration: float):
        """
        Starts a heal-over-time effect.

        Parameters
        ----------
        amount : int
            The total amount of health to restore.
        duration : float
            The duration of the healing effect in seconds.
        """
        self.healing_amount = amount
        self.healing_timer = duration

    def update(self, dt: float):
        """
        Updates the player's state for the current frame.

        Handles input, movement, stamina, cooldowns, and animations.

        Parameters
        ----------
        dt : float
            The time elapsed since the last frame, in seconds.
        """
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            if self.attack_cooldown <= 0:
                self.attack_cooldown = 0
                self.can_shoot_flag = True

        # Handle death animation
        if self.dead:
            self._update_death_animation(dt)
            return

        # Handle healing over time
        if self.healing_timer > 0:
            heal_this_frame = (self.healing_amount / self.healing_timer) * dt
            self.hp = min(self.get_effective_max_hp(), self.hp + heal_this_frame)
            self.healing_timer -= dt

        # Update hurt timer
        if self.hurt_timer > 0:
            self.hurt_timer -= dt

        # Update buff timers
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= dt
            if self.speed_boost_timer <= 0:
                self.speed_boost_multiplier = 1.0
                self.speed_boost_timer = 0.0

        if self.xp_multiplier_timer > 0:
            self.xp_multiplier_timer -= dt
            if self.xp_multiplier_timer <= 0:
                self.xp_multiplier = 1.0
                self.xp_multiplier_timer = 0.0

        if self.damage_boost_timer > 0:
            self.damage_boost_timer -= dt
            if self.damage_boost_timer <= 0:
                self.damage_boost_multiplier = 1.0
                self.damage_boost_timer = 0.0

        # Process movement and stamina
        self._handle_input_and_movement(dt)

        # Update hitbox position
        self.hitbox = self.rect.inflate(-40, -30)

        # Update invulnerability timer
        self.invuln_timer = max(0.0, self.invuln_timer - dt)

        # Update animation based on current state
        self._update_animation(dt)

    def _handle_input_and_movement(self, dt: float):
        """Processes keyboard input to determine movement and running state."""
        keys = pygame.key.get_pressed()
        mx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (
            keys[pygame.K_a] or keys[pygame.K_LEFT]
        )
        my = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (
            keys[pygame.K_w] or keys[pygame.K_UP]
        )

        # --- Stamina and Running Logic ---
        wants_to_run = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        # Update exhausted state (prevents sprint-stuttering)
        if self.stamina <= 0:
            self.is_exhausted = True
        elif self.stamina >= self.max_stamina * 0.4:
            self.is_exhausted = False

        self.running = wants_to_run and not self.is_exhausted

        # --- Speed Calculation ---
        effective_speed = self.get_movement_speed()
        if self.running:
            speed_multiplier = Constants.Movement.SPRINT_SPEED
            self.stamina = max(0, self.stamina - self.stamina_drain_rate * dt)
        else:
            speed_multiplier = Constants.Movement.MOVEMENT_SPEED
            if self.is_exhausted:
                speed_multiplier *= 0.5  # Slow down when exhausted
            # Regenerate stamina when not running
            self.stamina = min(
                self.max_stamina, self.stamina + self.stamina_regen_rate * dt
            )

        # --- Apply Movement ---
        if mx != 0 or my != 0:
            # Normalize diagonal movement
            length = math.hypot(mx, my)
            self.vx = (mx / length) * effective_speed * speed_multiplier
            self.vy = (my / length) * effective_speed * speed_multiplier
        else:
            self.vx = self.vy = 0.0

    def _update_animation(self, dt: float):
        """Selects and advances the appropriate animation based on the player's state."""
        moving = abs(self.vx) > 1e-2 or abs(self.vy) > 1e-2
        is_running = moving and self.running and self.stamina > 0

        # Adjust animation speed based on state
        if self.is_exhausted and moving and not is_running:
            self.frame_speed = 9.0  # Faster walk/panting animation when exhausted
        elif is_running:
            self.frame_speed = 12.0
        else:
            self.frame_speed = 6.0

        # Determine animation prefix (idle, walk, run, hurt)
        if self.hurt_timer > 0:
            anim_prefix = "hurt"
        elif not moving:
            anim_prefix = "idle"
        elif is_running:
            anim_prefix = "run"
        else:
            anim_prefix = "walk"

        # Combine prefix with facing direction to get the animation key
        anim_key = f"{anim_prefix}_{self.facing}"
        frames = self.anim.get(anim_key, self.anim.get("idle_down", []))

        # Advance and loop the animation frame
        if frames:
            self.frame = (self.frame + self.frame_speed * dt) % len(frames)
            frame_img = frames[
                int(self.frame)
            ].copy()  # Use copy to avoid modifying original

            # Flip the image if facing left
            if self.facing == "side" and self.flip_side:
                frame_img = pygame.transform.flip(frame_img, True, False)

            self.image = frame_img

    def _update_death_animation(self, dt: float):
        """Handles the progression of the death animation."""
        anim_key = self.state
        frames = self.anim.get(anim_key, self.anim.get("death_down", []))

        if frames:
            # Advance the frame, but do not loop
            if self.frame < len(frames) - 1:
                self.frame += self.frame_speed * dt
                self.frame = min(self.frame, len(frames) - 1)

            img = frames[int(self.frame)]
            if self.facing == "side" and self.flip_side:
                img = pygame.transform.flip(img, True, False)
            self.image = img

    def can_shoot(self) -> bool:
        """
        Checks if the player is able to shoot.

        Returns
        -------
        bool
            True if the attack cooldown is finished, False otherwise.
        """
        return self.can_shoot_flag and self.attack_cooldown <= 0

    def draw(self, surf: pygame.Surface, camera=None):
        """
        Draws the player sprite on the given surface.

        Parameters
        ----------
        surf : pygame.Surface
            The surface to draw the player on.
        camera : Camera, optional
            The game camera, used to translate world coordinates to screen coordinates.
            If None, the player is drawn at its raw rect coordinates.
        """
        if camera:
            screen_rect = camera.apply(self.rect)
            surf.blit(self.image, screen_rect)
        else:
            surf.blit(self.image, self.rect)

    def death_animation_finished(self) -> bool:
        """
        Checks if the death animation has reached its final frame.

        Returns
        -------
        bool
            True if the animation is on its last frame, False otherwise.
        """
        anim_key = f"death_{self.facing}"
        frames = self.anim.get(anim_key, self.anim.get("death_down", []))
        if frames:
            return int(self.frame) >= len(frames) - 1
        return True

#---NEW---

    def add_speed_boost(self, multiplier: float, duration: float):
        """
        Adds a temporary speed boost to the player.

        Parameters
        ----------
        multiplier : float
            The speed multiplier (e.g., 1.5 for 50% faster).
        duration : float
            How long the boost lasts in seconds.
        """
        self.speed_boost_multiplier = multiplier
        self.speed_boost_timer = duration

    def add_xp_multiplier(self, multiplier: float, duration: float):
        """
        Adds a temporary XP multiplier to the player.

        Parameters
        ----------
        multiplier : float
            The XP multiplier (e.g., 2.0 for double XP).
        duration : float
            How long the multiplier lasts in seconds.
        """
        self.xp_multiplier = multiplier
        self.xp_multiplier_timer = duration

    def add_damage_boost(self, multiplier: float, duration: float):
        """
        Adds a temporary damage boost to the player.

        Parameters
        ----------
        multiplier : float
            The damage multiplier (e.g., 2.0 for double damage).
        duration : float
            How long the boost lasts in seconds.
        """
        self.damage_boost_multiplier = multiplier
        self.damage_boost_timer = duration

    def get_current_damage(self) -> int:
        """
        Gets the player's current damage including temporary boosts.

        Returns
        -------
        int
            The total damage value.
        """
        from src.prefs import Constants

        base_damage = Constants.Player.PLAYER_DAMAGE
        if self.level_system:
            base_damage += self.level_system.get_attack_bonus()

        return int(base_damage * self.damage_boost_multiplier)

    def get_current_xp_multiplier(self) -> float:
        """
        Gets the player's current XP multiplier.

        Returns
        -------
        float
            The XP multiplier value.
        """
        return self.xp_multiplier