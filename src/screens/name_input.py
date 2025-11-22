"""
This module implements the name input screen.
"""

import pygame

from src.prefs import Constants
from src.prefs.style import Style
from src.systems.leaderboard import save_score
from src.utils.background import setup_background


class NameInputScreen:
    """A class to handle name input."""

    def __init__(self, screen: pygame.Surface, wave: int):
        """
        Initializes the name input screen.

        Parameters
        ----------
        screen : pygame.Surface
            The main Pygame screen surface.
        wave : int
            The wave number to save.
        """
        self.screen = screen
        self.bg_img = setup_background(self.screen)
        self.wave = wave
        self.font_title = Style.Fonts(80).FONT
        self.font_input = Style.Fonts(40).FONT
        self.name = ""
        self.input_rect = pygame.Rect(
            Constants.Game.SCREEN_WIDTH // 2 - 200, 200, 400, 50
        )

    def run(self):
        """Runs the name input loop."""
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        save_score(self.name, self.wave)
                        return
                    elif event.key == pygame.K_BACKSPACE:
                        self.name = self.name[:-1]
                    else:
                        self.name += event.unicode

            self.screen.blit(self.bg_img, (0, 0))
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            title_surf = self.font_title.render(
                "Enter Your Name", True, Style.Colors.WHITE
            )
            title_rect = title_surf.get_rect(
                center=(Constants.Game.SCREEN_WIDTH // 2, 100)
            )
            self.screen.blit(title_surf, title_rect)

            pygame.draw.rect(self.screen, Style.Colors.WHITE, self.input_rect, 2)
            name_surf = self.font_input.render(self.name, True, Style.Colors.WHITE)
            self.screen.blit(name_surf, (self.input_rect.x + 5, self.input_rect.y + 5))

            pygame.display.flip()
            clock.tick(60)
