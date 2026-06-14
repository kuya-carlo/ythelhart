from collections.abc import Callable

import pygame

from src.prefs import Extras, Style


class Button:
    """
    A clickable UI button with text and a callback function.

    Attributes
    ----------
    image : pygame.Surface
        The visual representation of the button.
    rect : pygame.Rect
        The position and dimensions of the button.
    callback : Callable
        The function to execute when the button is clicked.
    text : str
        The text label displayed on the button.
    hover : bool
        True if the mouse cursor is over the button.
    selected : bool
        True if the button is selected via keyboard navigation.
    """

    def __init__(
        self, text: str, x: int, y: int, width: int, height: int, callback: Callable
    ):
        """
        Initializes a new Button instance.

        Parameters
        ----------
        text : str
            The text to display on the button.
        x : int
            The x-coordinate of the top-left corner.
        y : int
            The y-coordinate of the top-left corner.
        width : int
            The width of the button.
        height : int
            The height of the button.
        callback : callable
            The function to call when the button is activated.
        """
        # Load and scale the button's background image
        self.image = pygame.image.load(Extras.BUTTON).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))

        self.callback = callback
        self.text = text
        self.hover = False
        self.selected = False

    def draw(self, surf: pygame.Surface, font: pygame.font.Font):
        """
        Draws the button on a given surface.

        A tint is applied if the button is hovered over or selected.

        Parameters
        ----------
        surf : pygame.Surface
            The surface to draw the button on.
        font : pygame.font.Font
            The font used to render the button's text.
        """
        # Show a visual effect when the button is hovered or selected
        if self.hover or self.selected:
            surf.blit(self.image, self.rect.topleft)

        # Render the text centered on the button
        label = font.render(self.text, True, Style.Colors.WHITE)
        surf.blit(label, label.get_rect(center=self.rect.center))

    def update_hover(self, mouse_pos: tuple[int, int]):
        """
        Updates the button's hover state based on the mouse position.

        Parameters
        ----------
        mouse_pos : tuple[int, int]
            The current (x, y) position of the mouse cursor.
        """
        self.hover = self.rect.collidepoint(mouse_pos)
