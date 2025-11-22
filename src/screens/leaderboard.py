"""
This module implements the leaderboard screen.
"""

import pygame

from src.prefs import Constants
from src.prefs.style import Style
from src.systems.leaderboard import load_scores
from src.utils.background import setup_background


class LeaderboardScreen:
    """A class to display the leaderboard."""

    def __init__(self, screen: pygame.Surface):
        """
        Initializes the leaderboard menu.

        Parameters
        ----------
        screen : pygame.Surface
            The main Pygame screen surface.
        """
        self.screen = screen
        self.bg_img = setup_background(self.screen)
        self.font_title = Style.Fonts(80).FONT
        self.font_score = Style.Fonts(40).FONT
        self.scores = load_scores()

    def run(self):
        """Runs the leaderboard menu loop."""
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

            title_surf = self.font_title.render("LEADERBOARD", True, Style.Colors.WHITE)
            title_rect = title_surf.get_rect(
                center=(Constants.Game.SCREEN_WIDTH // 2, 100)
            )
            self.screen.blit(title_surf, title_rect)

            if not self.scores:
                no_scores_surf = self.font_score.render(
                    "No scores yet!", True, Style.Colors.WHITE
                )
                no_scores_rect = no_scores_surf.get_rect(
                    center=(Constants.Game.SCREEN_WIDTH // 2, 200)
                )
                self.screen.blit(no_scores_surf, no_scores_rect)
            else:
                for i, score in enumerate(self.scores):
                    score_surf = self.font_score.render(
                        f"{i + 1}. {score.get('name', 'Anonymous')} - Wave {score.get('wave', 0)}",
                        True,
                        Style.Colors.WHITE,
                    )
                    score_rect = score_surf.get_rect(
                        center=(Constants.Game.SCREEN_WIDTH // 2, 200 + i * 50)
                    )
                    self.screen.blit(score_surf, score_rect)

            back_surf = self.font_score.render(
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
