"""
This module defines the Camera class, which manages the game's viewpoint,
including following the player and implementing a screen shake effect.
"""

import random
from typing import Tuple

import pygame

from src.prefs import Constants


class Camera:
    """
    Manages the game's camera, following a target and handling screen shake.

    The camera's position is defined by the top-left corner of the viewport
    in world coordinates. It ensures the viewport does not go beyond the map
    boundaries.

    Attributes
    ----------
    screen_w : int
        The width of the screen in pixels.
    screen_h : int
        The height of the screen in pixels.
    map_w : int
        The width of the game map in pixels.
    map_h : int
        The height of the game map in pixels.
    rect : pygame.Rect
        The camera's viewport, where (x, y) is the top-left offset in world coordinates.
    shake_amount : float
        The current intensity of the screen shake.
    shake_duration : float
        The remaining duration of the screen shake in seconds.
    shake_offset_x : int
        The current horizontal offset caused by screen shake.
    shake_offset_y : int
        The current vertical offset caused by screen shake.
    """

    def __init__(
        self,
        map_width: int,
        map_height: int,
        screen_width: int = Constants.Game.SCREEN_WIDTH,
        screen_height: int = Constants.Game.SCREEN_HEIGHT,
    ):
        """
        Initializes the camera.

        Parameters
        ----------
        map_width : int
            The width of the map in pixels.
        map_height : int
            The height of the map in pixels.
        screen_width : int, optional
            The width of the screen. Defaults to `Constants.Game.SCREEN_WIDTH`.
        screen_height : int, optional
            The height of the screen. Defaults to `Constants.Game.SCREEN_HEIGHT`.
        """
        self.screen_w = screen_width
        self.screen_h = screen_height
        self.map_w = map_width
        self.map_h = map_height

        # The camera's rect stores the top-left offset of the viewport in world coordinates.
        self.rect = pygame.Rect(0, 0, self.map_w, self.map_h)

        # Initialize screen shake parameters
        self.shake_amount = 0.0
        self.shake_duration = 0.0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

    def add_shake(self, intensity: float, duration: float = 0.3):
        """
        Triggers a screen shake effect.

        Parameters
        ----------
        intensity : float
            The maximum displacement of the shake in pixels.
        duration : float, optional
            The duration of the shake effect in seconds. Defaults to 0.3.
        """
        self.shake_amount = intensity
        self.shake_duration = duration

    def update(self, player_rect: pygame.Rect):
        """
        Updates the camera's position to center on the player.

        The camera's movement is clamped to the map boundaries to prevent
        showing areas outside the map.

        Parameters
        ----------
        player_rect : pygame.Rect
            The rectangle representing the player's position and size.
        """
        # Center the camera on the player
        x = player_rect.centerx - self.screen_w // 2
        y = player_rect.centery - self.screen_h // 2

        # Clamp the camera's position to the map boundaries
        x = max(0, min(x, max(0, self.map_w - self.screen_w)))
        y = max(0, min(y, max(0, self.map_h - self.screen_h)))

        # Store the calculated top-left offset
        self.rect.topleft = (x, y)

    def update_shake(self, dt: float):
        """
        Updates the screen shake effect over time.

        This method should be called every frame. It decreases the shake duration
        and intensity, creating a decaying effect.

        Parameters
        ----------
        dt : float
            The time elapsed since the last frame, in seconds.
        """
        if self.shake_duration > 0:
            self.shake_duration -= dt

            # Generate a random offset for the shake
            self.shake_offset_x = random.randint(
                -int(self.shake_amount), int(self.shake_amount)
            )
            self.shake_offset_y = random.randint(
                -int(self.shake_amount), int(self.shake_amount)
            )

            # Reduce the shake intensity over time for a smooth decay
            self.shake_amount *= 0.9
        else:
            # Reset shake parameters when the effect ends
            self.shake_offset_x = 0
            self.shake_offset_y = 0
            self.shake_amount = 0.0

    def apply(self, entity_rect: pygame.Rect) -> pygame.Rect:
        """
        Adjusts an entity's rectangle for rendering.

        Translates world coordinates to screen coordinates by applying the camera's
        offset and the current screen shake.

        Parameters
        ----------
        entity_rect : pygame.Rect
            The rectangle of the entity in world coordinates.

        Returns
        -------
        pygame.Rect
            The adjusted rectangle in screen coordinates.
        """
        return entity_rect.move(
            -self.rect.x + self.shake_offset_x, -self.rect.y + self.shake_offset_y
        )

    def apply_rect(self, rect: pygame.Rect) -> pygame.Rect:
        """
        Adjusts any rectangle for rendering (alias for `apply`).

        Parameters
        ----------
        rect : pygame.Rect
            The rectangle in world coordinates.

        Returns
        -------
        pygame.Rect
            The adjusted rectangle in screen coordinates.
        """
        return rect.move(
            -self.rect.x + self.shake_offset_x, -self.rect.y + self.shake_offset_y
        )

    def world_to_screen(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """
        Converts world coordinates to screen coordinates.

        Parameters
        ----------
        pos : Tuple[int, int]
            A tuple (x, y) representing a position in world coordinates.

        Returns
        -------
        Tuple[int, int]
            The corresponding position in screen coordinates.
        """
        return (
            pos[0] - self.rect.x + self.shake_offset_x,
            pos[1] - self.rect.y + self.shake_offset_y,
        )

    def screen_to_world(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """
        Converts screen coordinates to world coordinates.

        Parameters
        ----------
        pos : Tuple[int, int]
            A tuple (x, y) representing a position on the screen.

        Returns
        -------
        Tuple[int, int]
            The corresponding position in world coordinates.
        """
        return (
            pos[0] + self.rect.x - self.shake_offset_x,
            pos[1] + self.rect.y - self.shake_offset_y,
        )
