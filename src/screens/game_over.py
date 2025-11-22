import pygame

from src.components.button import Button
from src.prefs import Constants, Style, Backgrounds
from src.screens.leaderboard import LeaderboardScreen
from src.screens.name_input import NameInputScreen

class GameOverScreen:
    def __init__(self, screen, wave):
        self.screen = screen
        self.wave = wave
        self.font = Style.Fonts(72).FONT
        self.small_font = Style.Fonts(48).FONT
        self.running = True
        self.action = None

        self.game_over_text = self.font.render("GAME OVER", True, (255, 50, 50))
        self.game_over_rect = self.game_over_text.get_rect(
            center=(
                Constants.Game.SCREEN_WIDTH // 2,
                Constants.Game.SCREEN_HEIGHT // 2 - 150,
            )
        )

        self.bg_image = pygame.image.load(str(Backgrounds.GAME_OVER)).convert()
        self.bg_image = pygame.transform.scale(
            self.bg_image,
            (Constants.Game.SCREEN_WIDTH, Constants.Game.SCREEN_HEIGHT),
        )
        self.dim_overlay = pygame.Surface(
            (Constants.Game.SCREEN_WIDTH, Constants.Game.SCREEN_HEIGHT)
        )
        self.dim_overlay.fill((0, 0, 0))
        self.dim_overlay.set_alpha(225) # 0 = fully transparent, 255 = fully opaque

        button_width = 300
        button_height = 60
        center_x = Constants.Game.SCREEN_WIDTH // 2
        start_y = Constants.Game.SCREEN_HEIGHT // 2

        self.restart_button = Button(
            "Restart",
            center_x - button_width // 2,
            start_y - 80,
            button_width,
            button_height,
            self._restart_action,
        )
        self.save_score_button = Button(
            "Save Score",
            center_x - button_width // 2,
            start_y,
            button_width,
            button_height,
            self._save_score_action,
        )
        self.main_menu_button = Button(
            "Main Menu",
            center_x - button_width // 2,
            start_y + 80,
            button_width,
            button_height,
            self._main_menu_action,
        )
        self.buttons = [
            self.restart_button,
            self.save_score_button,
            self.main_menu_button,
        ]

    def _restart_action(self):
        self.running = False
        self.action = "restart"

    def _save_score_action(self):
        name_input = NameInputScreen(self.screen, self.wave)
        name_input.run()
        leaderboard = LeaderboardScreen(self.screen)
        leaderboard.run()
        self.running = False
        self.action = "main_menu"

    def _main_menu_action(self):
        self.running = False
        self.action = "main_menu"

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
        return self.action

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.action = "quit"
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for button in self.buttons:
                    if button.hover:
                        button.callback()
                        break

    def draw(self):
        # Draw background first
        self.screen.blit(self.bg_image, (0, 0))
        self.screen.blit(self.dim_overlay, (0, 0))  # dims the background
        self.screen.blit(self.game_over_text, self.game_over_rect)
        for button in self.buttons:
            button.draw(self.screen, self.small_font)
        pygame.display.flip()
