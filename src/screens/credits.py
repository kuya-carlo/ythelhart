"""
This module implements the credits screen.
"""

import pygame

from src.prefs import Constants
from src.prefs.style import Style
from src.utils.background import setup_background


class CreditsScreen:
    """A class to display the credits."""

    def __init__(self, screen: pygame.Surface):
        """
        Initializes the credits menu.

        Parameters
        ----------
        screen : pygame.Surface
            The main Pygame screen surface.
        """
        self.screen = screen
        self.bg_img = setup_background(self.screen)
        self.font_title = Style.Fonts(80).FONT
        self.font_text = Style.Fonts(30).FONT
        self.credits_text = self._load_credits()

    def _load_credits(self) -> list[str]:
        """Loads the credits from the credits.md file."""
        try:
            with open(Constants.Game.CREDITS_FILE, "r") as f:
                return f.readlines()
        except FileNotFoundError:
            return ["Credits file not found."]

    def run(self):
        """Runs the credits menu loop."""
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return

            self.screen.blit(self.bg_img, (0, 0))
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            title_surf = self.font_title.render("CREDITS", True, Style.Colors.WHITE)
            title_rect = title_surf.get_rect(
                center=(Constants.Game.SCREEN_WIDTH // 2, 100)
            )
            self.screen.blit(title_surf, title_rect)

            for i, line in enumerate(self.credits_text):
                line_surf = self.font_text.render(
                    line.strip(), True, Style.Colors.WHITE
                )
                line_rect = line_surf.get_rect(
                    center=(Constants.Game.SCREEN_WIDTH // 2, 200 + i * 40)
                )
                self.screen.blit(line_surf, line_rect)

            back_surf = self.font_text.render(
                "Press ESC to return", True, Style.Colors.WHITE
            )
            back_rect = back_surf.get_rect(
                center=(
                    Constants.Game.SCREEN_WIDTH // 2,
                    Constants.Game.SCREEN_HEIGHT - 100,
                )
            )
            self.screen.blit(back_surf, back_rect)

            pygame.display.flip()
            clock.tick(60)
