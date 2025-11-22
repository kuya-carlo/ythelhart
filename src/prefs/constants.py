"""This module defines a centralized set of constants for the game."""


class Constants:
    """A container for all game-related constants."""

    class Game:
        """
        Constants related to the game window and general mechanics.

        Attributes
        ----------
        SCREEN_WIDTH : int
            The width of the game screen in pixels.
        SCREEN_HEIGHT : int
            The height of the game screen in pixels.
        SCREEN_COORDS : tuple[int, int]
            A tuple containing the screen width and height.
        SCREEN_TITLE : str
            The title displayed on the game window.
        CREDITS_FILE : str
            The path to the file containing credits.
        FRAME_WIDTH : int
            The standard width of a single animation frame.
        FRAME_HEIGHT : int
            The standard height of a single animation frame.
        ANIMATION_SPEED : float
            The playback speed for animations (frames per second).
        MAP_ZOOM : float
            The zoom level applied to the game map.
        """

        SCREEN_WIDTH = 1280
        SCREEN_HEIGHT = 800
        SCREEN_COORDS = (SCREEN_WIDTH, SCREEN_HEIGHT)
        SCREEN_TITLE = "Ythelhart"
        CREDITS_FILE = "src/core/credits.txt"

        # Animation frame size, assuming square frames.
        FRAME_WIDTH = 64
        FRAME_HEIGHT = FRAME_WIDTH
        ANIMATION_SPEED = 6.0  # Frames per second
        MAP_ZOOM = 4.0

    class Player:
        """
        Constants related to the player character.

        Attributes
        ----------
        PLAYER_SPEED : int
            The base movement speed of the player in pixels per second.
        PLAYER_RUN_MULT : int
            The multiplier applied to the player's speed when running.
        PLAYER_MAX_HP : int
            The maximum health points of the player.
        PLAYER_DAMAGE : int
            The base damage dealt by the player's attacks.
        PLAYER_COOLDOWN : float
            The cooldown time in seconds between player attacks.
        """

        PLAYER_SPEED = 240
        PLAYER_RUN_MULT = 2  # Speed multiplier for sprinting
        PLAYER_MAX_HP = 100
        PLAYER_DAMAGE = 15
        PLAYER_COOLDOWN = 0  # Seconds

    class Enemy:
        """
        Constants related to enemy characters.

        Attributes
        ----------
        ENEMY_SPEED : int
            The base movement speed of enemies in pixels per second.
        ENEMY_DAMAGE : int
            The base damage dealt by enemy attacks.
        ENEMY_MAX_HP : int
            The maximum health points for a standard enemy.
        ENEMY_SPAWN_BUFFER : int
            The minimum distance from the player for enemies to spawn.
        """

        ENEMY_SPEED = 200
        ENEMY_DAMAGE = 10
        ENEMY_MAX_HP = 100
        ENEMY_SPAWN_BUFFER = 80  # Pixels

    class Attack:
        """
        Constants related to combat, attacks, and physics.

        Attributes
        ----------
        INVULN_TIME : float
            The duration in seconds a character is invulnerable after taking damage.
        PROJECTILE_SPEED : int
            The speed of projectiles in pixels per second.
        WAVE_INTERVAL : float
            The time in seconds between enemy spawn waves.
        WAVE_BASE_COUNT : int
            The initial number of enemies in the first wave.
        WAVE_GROWTH : int
            The number of additional enemies added to each subsequent wave.
        KNOCKBACK_FORCE : int
            The magnitude of the knockback effect when an entity is hit.
        """

        # Combat mechanics
        INVULN_TIME = 0.5  # Seconds
        PROJECTILE_SPEED = 800

        # Enemy wave mechanics
        WAVE_INTERVAL = 5.0  # Seconds
        WAVE_BASE_COUNT = 3
        WAVE_GROWTH = 2
        KNOCKBACK_FORCE = 5

    class Movement:
        """
        Constants related to character movement speeds.

        Attributes
        ----------
        SPRINT_SPEED : float
            The speed multiplier for sprinting.
        MOVEMENT_SPEED : float
            The base movement speed.
        """

        SPRINT_SPEED = 3.5
        MOVEMENT_SPEED = 2.0


if __name__ == "__main__":
    # This block is for testing purposes, e.g., to print all defined constants.
    print(dir())
