import pygame

# Initialize everything
pygame.init()
pygame.mixer.init()

from src.core import Game  # noqa: E402
from src.core.menu import MainMenu  # noqa: E402
from src.prefs import Constants  # noqa: E402


def main():
    """Setups the game window"""
    # Setup window
    screen = pygame.display.set_mode(
        (Constants.Game.SCREEN_WIDTH, Constants.Game.SCREEN_HEIGHT)
    )
    """Sets up the game screen"""
    pygame.display.set_caption(Constants.Game.SCREEN_TITLE)
    # show menu
    while True:
        menu = MainMenu(screen)
        menu.run()

        if menu.quit_requested:
            break
        menu.play_loading_screen()

        while True:  # Game session loop
            game = Game(screen)
            action = game.run()

            if action == "restart":
                continue  # Create a new game instance and restart the session
            else:
                break  # Exit to main menu or quit


if __name__ == "__main__":
    main()
