"""
This module provides utility functions for common tasks in the game,
such as loading sprite sheets and drawing UI elements like health bars.
"""

import pygame

from src.prefs import Constants


def load_frames(sheet_path: str, scale: int = 3) -> list[pygame.Surface]:
    """
    Loads and splits a sprite sheet into a list of individual frames.

    This function assumes the sprite sheet is arranged in a grid, and each
    frame has the dimensions specified by `Constants.Game.FRAME_WIDTH` and
    `Constants.Game.FRAME_HEIGHT`.

    Parameters
    ----------
    sheet_path : str
        The file path to the sprite sheet image.
    scale : int, optional
        The factor by which to scale each frame. Defaults to 3.

    Returns
    -------
    list[pygame.Surface]
        A list of Pygame surfaces, where each surface is a single animation frame.
    """
    # Load the sprite sheet with transparency support.
    sheet = pygame.image.load(sheet_path).convert_alpha()
    sheet_w, sheet_h = sheet.get_size()

    frames = []

    # Iterate over the grid of frames in the sprite sheet.
    for y in range(0, sheet_h, Constants.Game.FRAME_HEIGHT):
        for x in range(0, sheet_w, Constants.Game.FRAME_WIDTH):
            # Extract a single frame from the sheet.
            frame = sheet.subsurface(
                (x, y, Constants.Game.FRAME_WIDTH, Constants.Game.FRAME_HEIGHT)
            )

            # Scale the frame to the desired size.
            frame = pygame.transform.scale(
                frame,
                (
                    Constants.Game.FRAME_WIDTH * scale,
                    Constants.Game.FRAME_HEIGHT * scale,
                ),
            )

            frames.append(frame)

    return frames


def load_enemy_frames(
    sheet_path: str,
    frame_width: int,
    frame_height: int,
    num_frames: int,
    scale: float = 1.0,
) -> list[pygame.Surface]:
    """
    Loads frames from a horizontal sprite sheet for an enemy.

    This function is designed for sprite sheets where frames are laid out
    in a single horizontal row.

    Parameters
    ----------
    sheet_path : str
        The file path to the sprite sheet image.
    frame_width : int
        The width of a single frame.
    frame_height : int
        The height of a single frame.
    num_frames : int
        The total number of frames in the sprite sheet.
    scale : float, optional
        The factor by which to scale each frame. Defaults to 1.0.

    Returns
    -------
    list[pygame.Surface]
        A list of Pygame surfaces, each representing a single frame.
    """
    sheet = pygame.image.load(sheet_path).convert_alpha()
    frames = []

    for i in range(num_frames):
        # Define the rectangle for the current frame in the horizontal strip.
        frame_rect = pygame.Rect(
            i * frame_width,  # The x-position is shifted for each frame.
            0,  # Assumes a single row of frames.
            frame_width,
            frame_height,
        )

        # Extract the frame from the sheet.
        frame = sheet.subsurface(frame_rect)

        # Scale the frame if a scaling factor is provided.
        if scale != 1.0:
            frame = pygame.transform.scale(
                frame, (int(frame_width * scale), int(frame_height * scale))
            )

        frames.append(frame)

    return frames


def load_arrow_frames(path: str) -> list[pygame.Surface]:
    """
    Loads and scales frames for an arrow projectile from a horizontal sprite sheet.

    This function assumes the sheet contains 5 frames arranged horizontally.

    Parameters
    ----------
    path : str
        The file path to the arrow sprite sheet.

    Returns
    -------
    list[pygame.Surface]
        A list of scaled Pygame surfaces for the arrow animation.
    """
    sheet = pygame.image.load(path).convert_alpha()
    sheet_w, sheet_h = sheet.get_size()

    frame_width = sheet_w // 5  # Assumes 5 frames in the sheet.
    frame_height = sheet_h

    frames = []
    for i in range(5):
        frame = sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
        # Scale the frame by a factor of 3.
        frame = pygame.transform.scale(frame, (frame_width * 3, frame_height * 3))
        frames.append(frame)

    return frames


def draw_bar(
    surface: pygame.Surface,
    x: int,
    y: int,
    w: int,
    h: int,
    pct: float,
    color: tuple[int, int, int],
):
    """
    Draws a generic percentage bar, such as a health or stamina bar.

    The bar consists of a background, a filled portion representing the
    percentage, and a border.

    Parameters
    ----------
    surface : pygame.Surface
        The surface to draw the bar on.
    x : int
        The x-coordinate of the top-left corner of the bar.
    y : int
        The y-coordinate of the top-left corner of the bar.
    w : int
        The total width of the bar.
    h : int
        The height of the bar.
    pct : float
        The percentage to fill the bar, from 0.0 to 1.0.
    color : tuple[int, int, int]
        The RGB color of the filled portion of the bar.
    """
    # Clamp the percentage between 0 and 1 to prevent drawing errors.
    pct = max(0.0, min(1.0, pct))

    # Draw the dark background of the bar.
    pygame.draw.rect(surface, (60, 60, 60), (x, y, w, h))

    # Draw the filled portion representing the current percentage.
    pygame.draw.rect(surface, color, (x, y, int(w * pct), h))

    # Draw a simple border around the bar.
    pygame.draw.rect(surface, (255, 255, 255), (x, y, w, h), 1)


if __name__ == "__main__":
    # This block can be used for testing the utility functions.
    print(dir())
