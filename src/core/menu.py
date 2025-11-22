"""
This module implements the main menu and related UI components for the game,
including interactive buttons and a loading screen.
"""

import pygame

from src.components import Button
from src.prefs import Constants, Extras, Music, Style
from src.screens import CreditsScreen, LeaderboardScreen
from src.utils.background import setup_background, draw_background

from .progressbar import ProgressBar


class MainMenu:
    """
    The main menu screen, handling user interaction and navigation.

    This class manages the background, music, logo, and buttons for the main menu.
    It runs a loop to handle events and draw the menu until the user starts the
    game or exits.

    Attributes
    ----------
    screen : pygame.Surface
        The main display surface to draw the menu on.
    start_requested : bool
        Set to True when the user chooses to start the game.
    quit_requested : bool
        Set to True when the user chooses to exit the game.
    """

    def __init__(self, screen: pygame.Surface):
        """
        Sets up the main menu screen.

        Parameters
        ----------
        screen : pygame.Surface
            The main Pygame screen surface.
        """
        self.screen = screen
        # Initialize and play background music
        pygame.mixer.music.load(Music("Hardware Haven Theme Music.ogg").MUSIC_PATH)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)  # Loop indefinitely

        # Setup fonts for titles and buttons
        self.font_big = Style.Fonts(80).FONT
        self.font_small = Style.Fonts(40).FONT

        # Setup UI widgets
        self._setup_widgets()

        # Load and prepare the background image
        self.bg_img = setup_background(self.screen)

        # Menu state flags
        self.start_requested = False
        self.quit_requested = False
        self.show_leaderboard = False
        self.show_credits = False

        # Set up keyboard navigation, starting with the first button selected
        self.selected_index = 0
        self.buttons[self.selected_index].selected = True

    def _setup_widgets(self):
        """Initializes and positions the logo and buttons on the screen."""
        sw, sh = Constants.Game.SCREEN_COORDS

        # Load, scale, and position the game logo
        raw_logo = pygame.image.load(Extras.LOGO).convert_alpha()
        lw, lh = raw_logo.get_size()
        scale = 500 / lh  # Scale logo to a height of 500px
        self.logo = pygame.transform.smoothscale(raw_logo, (int(lw * scale), 500))
        self.logo_rect = self.logo.get_rect(midleft=(50, 550))

        # Define button dimensions and positioning
        btn_w, btn_h = 300, 100
        padding = 10
        offset = 50
        btn_x = sw - padding - btn_w - 30
        btn4_y = sh - padding - btn_h - offset
        btn3_y = btn4_y - btn_h - padding
        btn2_y = btn3_y - btn_h - padding
        btn1_y = btn2_y - btn_h - padding

        # Create button instances
        self.buttons = [
            Button("PLAY", btn_x, btn1_y, btn_w, btn_h, self.start_game),
            Button("Leaderboard", btn_x, btn2_y, btn_w, btn_h, self.toggle_leaderboard),
            Button("Credits", btn_x, btn3_y, btn_w, btn_h, self.toggle_credits),
            Button("EXIT", btn_x, btn4_y, btn_w, btn_h, self.exit_game),
        ]

    def start_game(self):
        """Callback function to signal that the game should start."""
        self.start_requested = True

    def exit_game(self):
        """Callback function to signal that the application should exit."""
        self.quit_requested = True

    def toggle_leaderboard(self):
        """Toggles the leaderboard display."""
        self.show_leaderboard = not self.show_leaderboard

    def toggle_credits(self):
        """Toggles the credits display."""
        self.show_credits = not self.show_credits

    def run(self):
        """
        Runs the main menu loop.

        Handles user input for mouse and keyboard, updates button states,
        and draws all menu elements to the screen. The loop terminates when
        the user decides to start or quit the game.
        """
        leaderboard_menu = LeaderboardScreen(self.screen)
        credits_menu = CreditsScreen(self.screen)
        clock = pygame.time.Clock()
        while not self.start_requested and not self.quit_requested:
            mouse_pos = pygame.mouse.get_pos()

            if self.show_leaderboard:
                leaderboard_menu.run()
                self.show_leaderboard = False

            if self.show_credits:
                credits_menu.run()
                self.show_credits = False

            # Update hover state for all buttons
            for i, btn in enumerate(self.buttons):
                btn.update_hover(mouse_pos)
                if btn.hover and self.selected_index != i:
                    self.buttons[self.selected_index].selected = False
                    self.selected_index = i
                    btn.selected = True

            # --- Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_requested = True
                elif event.type == pygame.KEYDOWN:
                    self._handle_key_event(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_mouse_click(mouse_pos)

                if self.start_requested or self.quit_requested:
                    return

            # --- Drawing ---

            draw_background(self.screen, self.bg_img)
            # Draw UI elements
            self.screen.blit(self.logo, self.logo_rect)
            for btn in self.buttons:
                btn.draw(self.screen, self.font_small)

            pygame.display.flip()
            clock.tick(60)

    def _handle_key_event(self, key: int):
        """Handles keyboard input for menu navigation and selection."""
        if key in [pygame.K_DOWN, pygame.K_s]:
            # Move selection down
            self.buttons[self.selected_index].selected = False
            self.selected_index = (self.selected_index + 1) % len(self.buttons)
            self.buttons[self.selected_index].selected = True
        elif key in [pygame.K_UP, pygame.K_w]:
            # Move selection up
            self.buttons[self.selected_index].selected = False
            self.selected_index = (self.selected_index - 1 + len(self.buttons)) % len(
                self.buttons
            )
            self.buttons[self.selected_index].selected = True
        elif key == pygame.K_RETURN:
            # Activate the currently selected button
            self.buttons[self.selected_index].callback()

    def _handle_mouse_click(self, mouse_pos: tuple[int, int]):
        """Handles mouse clicks on buttons."""
        for i, btn in enumerate(self.buttons):
            if btn.rect.collidepoint(mouse_pos):
                btn.callback()
                # Update selection to the clicked button
                self.buttons[self.selected_index].selected = False
                self.selected_index = i
                btn.selected = True
                break

    def play_loading_screen(self):
        """
        Displays a simple loading screen with a progress bar.

        This method runs a loop that updates and draws a progress bar until it is full.
        It also stops the menu music upon completion.
        """
        progress_bar = ProgressBar(
            self.screen,
            Constants.Game.SCREEN_WIDTH - 350,
            Constants.Game.SCREEN_HEIGHT - 50,
            300,
            20,
            3,
        )
        # TODO: add a overlay
        draw_background(progress_bar.screen, progress_bar.bg_img, True)
        clock = pygame.time.Clock()
        while not progress_bar.is_full:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_requested = True
                    return

            progress_bar.update()
            progress_bar.draw()

            pygame.display.flip()
            clock.tick(60)

        # Stop the menu music after the loading screen finishes
        pygame.mixer.music.stop()
