"""This module centralizes all asset paths for the game."""

from pathlib import Path

# --- Asset Path Setup ---
# This setup assumes the script is in 'src/prefs', and assets are in 'assets'.
# It navigates up the directory tree to find the root 'assets' folder.
# This makes the path resolution independent of the current working directory.

# Get the absolute path to this file.
# Navigate three levels up to the project root, then into 'assets'.
ASSET_PATH = Path(__file__).resolve().parent.parent.parent / "assets"

# Define subdirectories within the main 'assets' folder.
IMAGE_PATH = ASSET_PATH / "images"
PICKUP_PATH = IMAGE_PATH / "pickups"
SPRITE_PATH = IMAGE_PATH / "sprites"
MAP_PATH = IMAGE_PATH / "map"
EXTRAS_PATH = IMAGE_PATH / "extras"
BACKGROUNDS_PATH = EXTRAS_PATH / "background"
FONT_PATH = ASSET_PATH / "fonts"
MUSIC_PATH = ASSET_PATH / "music"


class ActionAssets:
    """
    Stores paths for a specific character action's sprites.

    This class generates paths for 'Down', 'Side', and 'Up' facing sprites
    based on a base path and a common name.

    Parameters
    ----------
    base_path : Path
        The base directory containing the action sprites.
    name : str
        The base name for the sprite files (e.g., "Idle", "Run").
    """

    def __init__(self, base_path: Path, name: str):
        self.DOWN = base_path / f"Main_{name}.png"
        self.SIDE = base_path / f"MainSide_{name}.png"
        self.UP = base_path / f"MainUp_{name}.png"


class Player:
    """Contains asset paths for the main character, Stella."""

    MC_NAME = "Stella"
    BASE_PATH = SPRITE_PATH / MC_NAME

    # Define asset paths for each character action.
    DEATH = ActionAssets(BASE_PATH / "Death", "Death")
    HURT = ActionAssets(BASE_PATH / "Hurt", "Hurt")
    IDLE = ActionAssets(BASE_PATH / "Idle", "Idle")
    RUN = ActionAssets(BASE_PATH / "Run", "Run")
    WALK = ActionAssets(BASE_PATH / "Walk", "Walk")


class Enemies:
    """Contains asset paths for various enemy types."""

    # --- Orc Assets ---
    ORC_SHEET = SPRITE_PATH / "Orc" / "Orc.png"
    ORC_ATTACK = SPRITE_PATH / "Orc" / "OrcAttack.png"
    ORC_DEATH = SPRITE_PATH / "Orc" / "OrcDeath.png"
    ORC_HURT = SPRITE_PATH / "Orc" / "OrcHurt.png"

    # --- Rogue Assets ---
    ROGUE_SHEET = SPRITE_PATH / "Rogue" / "Rogue.png"
    ROGUE_ATTACK = SPRITE_PATH / "Rogue" / "RogueAttack.png"
    ROGUE_HURT = SPRITE_PATH / "Rogue" / "RogueHurt.png"
    ROGUE_DEATH = SPRITE_PATH / "Rogue" / "RogueDeath.png"

    # --- Tank Assets ---
    TANK_SHEET = SPRITE_PATH / "Tank" / "Tank.png"
    TANK_ATTACK = SPRITE_PATH / "Tank" / "TankAttack.png"
    TANK_HURT = SPRITE_PATH / "Tank" / "TankHurt.png"
    TANK_DEATH = SPRITE_PATH / "Tank" / "TankDeath.png"

    # --- Minotaur Assets ---
    MINO_IDLE = SPRITE_PATH / "Minotaur" / "MinoIdle.png"
    MINO_WALK = SPRITE_PATH / "Minotaur" / "MinoWalk.png"
    MINO_ATTACK = SPRITE_PATH / "Minotaur" / "MinoAttack.png"


class Projectiles:
    """Contains asset paths for projectiles."""

    ARROW = SPRITE_PATH / "Arrow" / "Arrow.png"


class UIAssets:
    """Contains asset paths for UI elements."""

    # --- Minotaur Health Bar ---
    MINO_HEALTH_OVER = SPRITE_PATH / "Minotaur" / "UI" / "mino_health_over.png"
    MINO_HEALTH_PROGRESS = SPRITE_PATH / "Minotaur" / "UI" / "mino_health_progress.png"
    MINO_HEALTH_UNDER = SPRITE_PATH / "Minotaur" / "UI" / "mino_health_under.png"


class MapAsset:
    """
    Stores paths for a specific map asset.

    Links a map's image file (.png) with its tileset data file (.tsx).

    Parameters
    ----------
    base_path : Path
        The directory containing the map asset files.
    name : str
        The base name of the asset files (e.g., "TX Tileset Grass").
    """

    def __init__(self, base_path: Path, name: str):
        self.IMGPATH = base_path / f"{name}.png"
        self.PATH = base_path / f"{name}.tsx"


class MainMap:
    """
    Stores paths for a main map file.

    Links a map's image file (.png) with its Tiled map file (.tmx).

    Parameters
    ----------
    base_path : Path
        The directory containing the map files.
    name : str
        The base name of the map files.
    """

    def __init__(self, base_path: Path, name: str):
        self.IMGPATH = base_path / f"{name}.png"
        self.PATH = base_path / f"{name}.tmx"


class Map:
    """Contains nested classes for different map-related asset categories."""

    class Tileset:
        """Paths for map tilesets."""

        BASE_PATH = MAP_PATH / "base"
        GRASS_TILESET = MapAsset(BASE_PATH, "TX Tileset Grass")
        STONE_TILESET = MapAsset(BASE_PATH, "TX Tileset Stone Ground")
        WALL_TILESET = MapAsset(BASE_PATH, "TX Tileset Wall")

    class Main:
        """Paths for the main map files."""

        BASE_PATH = MAP_PATH / "main"
        MAP = MainMap(BASE_PATH, "map")

    class Props:
        """Paths for prop assets used in maps."""

        BASE_PATH = MAP_PATH / "props"
        MAIN = MapAsset(BASE_PATH, "TX Props")
        PROPS = MapAsset(BASE_PATH, "TX Props with Shadow")
        SHADOW = MapAsset(BASE_PATH, "TX_Shadow")

    class Plants:
        """Paths for plant assets used in maps."""

        BASE_PATH = MAP_PATH / "plants"
        PLANT_PATH = BASE_PATH / "TX Plant.png"
        PLANT = MapAsset(BASE_PATH, "TX Plant")
        SHADOWED_PLANT = MapAsset(BASE_PATH, "TX Plant with Shadow")

    class Structures:
        """Paths for structure assets used in maps."""

        BASE_PATH = MAP_PATH / "structures"
        MAIN = MapAsset(BASE_PATH, "TX Struct")

class PickupAssets:
    SIZE = 24
    SPEED_BOOST = PICKUP_PATH / "SpeedBoost.png"
    XP_MULTIPLIER = PICKUP_PATH / "ExpBoost.png"
    DAMAGE_BOOST = PICKUP_PATH / "AttackBoost.png"
    HEALTH_RESTORE = PICKUP_PATH / "HP.png"


class Extras:
    """Contains paths for miscellaneous extra assets."""

    LOGO = EXTRAS_PATH / "logo.png"
    MAP = EXTRAS_PATH / "map.png"
    BUTTON = EXTRAS_PATH / "button.png"


class Backgrounds:
    """Contains paths for background assets."""

    MAIN_MENU = BACKGROUNDS_PATH / "MainMenu.png"
    LOADING_SCREEN = BACKGROUNDS_PATH / "LoadingScreen.png"
    GAME_OVER = BACKGROUNDS_PATH / "GameOver.png"


class FontPath:
    """
    Constructs paths for different font weights of a given font family.

    Parameters
    ----------
    name : str
        The name of the font family (e.g., "PixelifySans").
    base_path : Path, optional
        The base directory for fonts, by default FONT_PATH.
    """

    def __init__(self, name: str, base_path: Path = FONT_PATH):
        font_dir = base_path / name
        self.FONTFILE = font_dir / f"{name}-Regular.ttf"
        self.BOLD_FONTFILE = font_dir / f"{name}-Bold.ttf"
        self.MEDIUM_FONTFILE = font_dir / f"{name}-Medium.ttf"
        self.SEMIBOLD_FONTFILE = font_dir / f"{name}-SemiBold.ttf"


class Music:
    """
    Constructs the path for a music file.

    Parameters
    ----------
    music_name : str
        The name of the music file (including extension).
    base_path : Path, optional
        The base directory for music, by default MUSIC_PATH.
    """

    def __init__(self, music_name: str, base_path: Path = MUSIC_PATH):
        self.MUSIC_PATH = base_path / music_name


if __name__ == "__main__":
    # This block is for testing purposes, e.g., to print all defined paths.
    print(dir())
