"""
This module provides a ProgressBar class for displaying a loading bar,
typically used for loading screens.
"""

import pygame

from src.prefs import Constants, Backgrounds
from src.prefs.paths import Extras
from src.utils.background import setup_background, draw_background


class ProgressBar:
    """
    A visual progress bar that fills over time.

    This class manages the state and rendering of a progress bar, which can be
    used to indicate loading progress. It also supports displaying optional
    decorative images and text.

    Attributes
    ----------
    screen : pygame.Surface
        The surface to draw the progress bar on.
    x : int
        The x-coordinate of the progress bar's top-left corner.
    y : int
        The y-coordinate of the progress bar's top-left corner.
    width : int
        The total width of the progress bar when full.
    height : int
        The height of the progress bar.
    speed : int
        The amount the progress bar fills per frame.
    progress : int
        The current fill width of the progress bar.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
        speed: int = 3,
    ):
        """
        Initializes a new ProgressBar instance.

        Parameters
        ----------
        screen : pygame.Surface
            The Pygame surface where the bar will be drawn.
        x : int
            The x-coordinate of the progress bar.
        y : int
            The y-coordinate of the progress bar.
        width : int
            The width of the progress bar.
        height : int
            The height of the progress bar.
        speed : int, optional
            The speed at which the progress bar fills. Defaults to 3.
        """
        self.screen = screen
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.speed = int(speed)
        # 'progress' tracks the current width of the filled portion of the bar.
        self.progress = 0
        self.bg_img = setup_background(self.screen, Backgrounds.LOADING_SCREEN)

        # Load optional decorative assets, failing silently if they are not found.
        self._load_assets()

    def _load_assets(self):
        """Loads optional title image for the loading screen."""
        try:
            self.title = pygame.image.load(Extras.LOGO).convert_alpha()
            self.title = pygame.transform.scale(self.title, (250, 200))
            self.title_rect = self.title.get_rect(
                center=(
                    Constants.Game.SCREEN_WIDTH / 2,
                    Constants.Game.SCREEN_HEIGHT / 2 - 100,
                )
            )
        except (pygame.error, FileNotFoundError):
            self.title = None
            self.title_rect = None

    @property
    def is_full(self) -> bool:
        """
        bool: True if the progress bar is completely full, False otherwise.
        """
        return self.progress >= self.width

    def update(self):
        """
        Updates the progress bar's fill status.

        Increments the progress by the defined speed until it is full.
        This should be called once per frame.
        """
        if self.progress < self.width:
            self.progress += self.speed
            # Clamp the progress to the maximum width.
            if self.progress > self.width:
                self.progress = self.width

    def draw(self):
        """
        Draws the progress bar and any associated assets to the screen.
        """
        draw_background(self.screen, self.bg_img)
        # Draw decorative assets if they were loaded successfully.
        if self.title and self.title_rect:
            self.screen.blit(self.title, self.title_rect)

        # Define rectangles for the bar's outline and filled portion.
        outline_rect = pygame.Rect(
            self.x - 1, self.y - 1, self.width + 2, self.height + 2
        )
        fill_rect = pygame.Rect(self.x, self.y, int(self.progress), self.height)

        # Draw the progress bar.
        try:
            # Draw the background/outline of the bar.
            pygame.draw.rect(self.screen, (60, 60, 60), outline_rect)
            # Draw the filled portion of the bar.
            pygame.draw.rect(self.screen, (166, 124, 0), fill_rect)
        except pygame.error:
            # Fails silently to prevent crashes if the display is not available.
            pass
