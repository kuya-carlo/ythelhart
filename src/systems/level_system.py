"""
This module implements the RPG-style level and experience system,
including stat progression and the level-up user interface.
"""

import pygame

from src.prefs import Constants, Music
from src.prefs.paths import MUSIC_PATH


class LevelSystem:
    """
    Manages the player's level, experience points (XP), and stat progression.

    This class tracks the player's current level, XP, and the stats they have
    invested points into. It handles leveling up and provides methods to get
    the effective bonuses from the allocated stats.

    Attributes
    ----------
    level : int
        The player's current level.
    xp : int
        The player's current experience points.
    xp_to_next_level : int
        The total XP required to reach the next level.
    stats : dict[str, int]
        A dictionary holding the number of points allocated to each stat.
    stat_points : int
        The number of unspent stat points available.
    showing_levelup : bool
        A flag indicating if the level-up UI should be displayed.
    """

    def __init__(self):
        """Initializes the level system to its default state."""
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100  # Base XP for level 2

        # Player stats store the number of points invested in each.
        self.stats = {
            "attack": 0,
            "attack_speed": 0,
            "agility": 0,
            "health": 0,
        }
        self.stat_points = 0
        self.showing_levelup = False
        self.health_upgrade_pending = False

    def add_xp(self, amount: int):
        """
        Adds experience points and checks for a level up.

        If the player's XP exceeds the amount required for the next level,
        the `level_up` method is called. This can happen multiple times if
        a large amount of XP is gained at once.

        Parameters
        ----------
        amount : int
            The amount of XP to add.
        """
        self.xp += amount
        while self.xp >= self.xp_to_next_level:
            self.level_up()

    def level_up(self):
        """
        Levels up the player, granting a stat point and increasing the XP requirement.
        """
        self.xp -= self.xp_to_next_level
        self.level += 1
        self.stat_points += 1

        # Increase the XP requirement for the next level using an exponential curve.
        self.xp_to_next_level = int(100 * (1.5 ** (self.level - 1)))

        # Trigger the level-up UI.
        self.showing_levelup = True

    def add_stat(self, stat_name: str) -> bool:
        """
        Allocates a stat point to a specified stat.

        Parameters
        ----------
        stat_name : str
            The name of the stat to increase (e.g., "attack", "health").

        Returns
        -------
        bool
            True if the stat point was successfully allocated, False otherwise.
        """
        if self.stat_points > 0 and stat_name in self.stats:
            self.stats[stat_name] += 1
            self.stat_points -= 1
            if stat_name == "health":
                self.health_upgrade_pending = True
            return True
        return False

    def get_attack_bonus(self) -> int:
        """Calculates the additional damage from the 'attack' stat."""
        return self.stats["attack"] * 5

    def get_attack_speed_multiplier(self) -> float:
        """Calculates the attack speed multiplier (lower is faster)."""
        return max(0.3, 1.0 - (self.stats["attack_speed"] * 0.1))

    def get_agility_multiplier(self) -> float:
        """Calculates the movement speed multiplier from the 'agility' stat."""
        return 1.0 + (self.stats["agility"] * 0.05)

    def get_health_bonus(self) -> int:
        """Calculates the additional max HP from the 'health' stat."""
        return self.stats["health"] * 20


class SimpleLevelUpUI:
    """
    A simple, placeholder UI for the level-up screen.

    This class is designed to be easily customizable. To change its appearance,
    modify the `draw` method.
    """

    def __init__(self, screen: pygame.Surface):
        """
        Initializes the level-up UI.

        Parameters
        ----------
        screen : pygame.Surface
            The main screen surface to draw the UI on.
        """
        self.screen = screen
        self.font_title = pygame.font.SysFont(None, 72)
        self.font_normal = pygame.font.SysFont(None, 32)
        self.font_small = pygame.font.SysFont(None, 24)
        self.buttons = []
        self.setup_buttons()
        pygame.mixer.music.load(Music("LevelUp.ogg", MUSIC_PATH / "SFX").MUSIC_PATH)

    def setup_buttons(self):
        """Creates and positions the stat selection buttons."""
        screen_w, screen_h = Constants.Game.SCREEN_WIDTH, Constants.Game.SCREEN_HEIGHT
        button_w, button_h, spacing = 400, 60, 20
        start_y = screen_h // 2 - 100

        stats_info = [
            ("attack", "1. ATTACK (+5 damage)"),
            ("attack_speed", "2. ATTACK SPEED (-10% cooldown)"),
            ("agility", "3. AGILITY (+5% speed)"),
            ("health", "4. HEALTH (+20 max HP)"),
        ]

        self.buttons = []
        for i, (stat_id, text) in enumerate(stats_info):
            rect = pygame.Rect(
                (screen_w - button_w) // 2,
                start_y + i * (button_h + spacing),
                button_w,
                button_h,
            )
            self.buttons.append(
                {
                    "stat": stat_id,
                    "text": text,
                    "key": i + 1,
                    "rect": rect,
                    "hover": False,
                }
            )

    def update(self, mouse_pos: tuple[int, int]):
        """Updates the hover state of the buttons based on mouse position."""
        for btn in self.buttons:
            btn["hover"] = btn["rect"].collidepoint(mouse_pos)

    def handle_click(
        self, mouse_pos: tuple[int, int], level_system: LevelSystem
    ) -> bool:
        """
        Handles mouse clicks on the stat buttons.

        Parameters
        ----------
        mouse_pos : tuple[int, int]
            The position of the mouse click.
        level_system : LevelSystem
            The instance of the level system to apply the stat change to.

        Returns
        -------
        bool
            True if a button was successfully clicked and a stat allocated.
        """
        for btn in self.buttons:
            if btn["rect"].collidepoint(mouse_pos):
                if level_system.add_stat(btn["stat"]):
                    if level_system.stat_points <= 0:
                        level_system.showing_levelup = False
                    return True
        return False

    def handle_key(self, key: int, level_system: LevelSystem) -> bool:
        """
        Handles keyboard shortcuts (1-4) for allocating stat points.

        Parameters
        ----------
        key : int
            The Pygame key constant that was pressed.
        level_system : LevelSystem
            The instance of the level system.

        Returns
        -------
        bool
            True if a valid key was pressed and a stat allocated.
        """
        key_map = {
            pygame.K_1: "attack",
            pygame.K_2: "attack_speed",
            pygame.K_3: "agility",
            pygame.K_4: "health",
        }
        if key in key_map:
            stat = key_map[key]
            if level_system.add_stat(stat):
                if level_system.stat_points <= 0:
                    level_system.showing_levelup = False
                return True
        return False

    def draw(self, level_system: LevelSystem):
        """
        Draws the level-up interface. This method is intended for customization.
        """
        screen_w, screen_h = Constants.Game.SCREEN_WIDTH, Constants.Game.SCREEN_HEIGHT

        # Draw a semi-transparent overlay to dim the background.
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Draw title and subtitle.
        title = self.font_title.render(
            f"LEVEL {level_system.level}!", True, (255, 215, 0)
        )
        self.screen.blit(title, title.get_rect(center=(screen_w // 2, 120)))
        points_text = f"{level_system.stat_points} STAT POINT{'S' if level_system.stat_points != 1 else ''} AVAILABLE"
        subtitle = self.font_normal.render(points_text, True, (255, 255, 255))
        self.screen.blit(subtitle, subtitle.get_rect(center=(screen_w // 2, 180)))

        # Draw buttons.
        for btn in self.buttons:
            color = (80, 80, 120) if btn["hover"] else (40, 40, 60)
            pygame.draw.rect(self.screen, color, btn["rect"], border_radius=8)
            border_color = (255, 215, 0) if btn["hover"] else (150, 150, 150)
            pygame.draw.rect(self.screen, border_color, btn["rect"], 3, border_radius=8)
            text_surf = self.font_normal.render(btn["text"], True, (255, 255, 255))
            self.screen.blit(text_surf, text_surf.get_rect(center=btn["rect"].center))

            # Display current stat level.
            stat_surf = self.font_small.render(
                f"[{level_system.stats[btn['stat']]}]", True, (180, 180, 180)
            )
            self.screen.blit(
                stat_surf,
                stat_surf.get_rect(
                    bottomright=(btn["rect"].right - 10, btn["rect"].bottom - 10)
                ),
            )

        # Draw instruction text.
        instruction = self.font_small.render(
            "Click a button or press 1-4 to choose", True, (200, 200, 200)
        )
        self.screen.blit(
            instruction, instruction.get_rect(center=(screen_w // 2, screen_h - 80))
        )


# Alias for backward compatibility.
LevelUpUI = SimpleLevelUpUI


class XPManager:
    """
    A static class to manage XP reward values for different enemy types.
    """

    XP_VALUES = {
        "Enemy": 25,
        "Rogue": 35,
        "Tank": 50,
        "MinotaurBoss": 500,
    }

    @staticmethod
    def get_xp_for_enemy(enemy: pygame.sprite.Sprite) -> int:
        """
        Gets the XP reward for defeating a specific enemy.

        Parameters
        ----------
        enemy : pygame.sprite.Sprite
            The enemy instance that was defeated.

        Returns
        -------
        int
            The XP value for the given enemy type.
        """
        enemy_type = type(enemy).__name__
        return XPManager.XP_VALUES.get(
            enemy_type, 10
        )  # Default to 10 XP if type not found
