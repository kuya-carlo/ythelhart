import pygame

from src.components.button import Button
from src.prefs import Constants, Style


class MainMenuScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = Style.Fonts(72).FONT
        self.small_font = Style.Fonts(48).FONT
        self.running = True
        self.action = None

        self.title_text = self.font.render("Dungeon Crawler", True, Style.Colors.WHITE)
        self.title_rect = self.title_text.get_rect(
            center=(
                Constants.Game.SCREEN_WIDTH // 2,
                Constants.Game.SCREEN_HEIGHT // 2 - 150,
            )
        )

        button_width = 300
        button_height = 60
        center_x = Constants.Game.SCREEN_WIDTH // 2
        start_y = Constants.Game.SCREEN_HEIGHT // 2

        self.start_button = Button(
            "Start Game",
            center_x - button_width // 2,
            start_y - 40,
            button_width,
            button_height,
            self._start_action,
        )
        self.quit_button = Button(
            "Quit",
            center_x - button_width // 2,
            start_y + 40,
            button_width,
            button_height,
            self._quit_action,
        )
        self.buttons = [self.start_button, self.quit_button]

    def _start_action(self):
        self.running = False
        self.action = "start_game"

    def _quit_action(self):
        self.running = False
        self.action = "quit"

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
                self._quit_action()
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for button in self.buttons:
                    if button.hover:
                        button.callback()
                        break

    def draw(self):
        self.screen.fill((20, 20, 30))
        self.screen.blit(self.title_text, self.title_rect)
        for button in self.buttons:
            button.draw(self.screen, self.small_font)
        pygame.display.flip()
