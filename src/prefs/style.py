"""This module provides styling for the game."""

from pygame import font

from .paths import FontPath


class Style:
    """A class to manage the style of the game."""

    class Colors:
        """A class to manage the colors of the game."""

        WHITE = (255, 255, 255)
        GRAY = (80, 80, 80)
        YELLOW = (255, 210, 40)

    class Fonts:
        """
        A class to manage the fonts of the game.

        Parameters
        ----------
        size : int
            The size of the font.
        fontname : str, optional
            The name of the font, by default "PixelifySans"
        name : str, optional
            The style of the font, by default ""
        """

        def __init__(self, size: int, fontname="PixelifySans", name: str = ""):
            try:
                # Get the path of the font
                PATH = FontPath(fontname)
                self.font_path = None
                # Set the font style
                if name.lower() == "bold":
                    self.font_path = PATH.BOLD_FONTFILE
                elif name.lower() == "semibold":
                    self.font_path = PATH.SEMIBOLD_FONTFILE
                elif name.lower() == "medium":
                    self.font_path = PATH.MEDIUM_FONTFILE
                else:
                    self.font_path = PATH.FONTFILE
                # Set the font
                self.FONT = font.Font(self.font_path, size)
            except Exception:
                # Set the default font if the font is not found
                self.FONT = font.SysFont(None, size)


# Update: Font styling is centralized now
# will eat
