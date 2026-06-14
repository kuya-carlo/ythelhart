# Ythelhart ⚔️

Ythelhart is a 2D action-RPG built in Python using **Pygame** and **PyTMX**. Explore maps, defeat enemies, level up your character, and battle the mighty Minotaur boss to claim your spot on the leaderboard!

---

## 🎮 Features

### Gameplay Mechanics
- **Specialized Character Classes**: Play and fight against distinct classes including **Rogue**, **Tank**, and the final **Minotaur Boss**.
- **Pickups & Buffs**: Collect dynamic items spawning from defeated enemies (such as Speed Boosts, Damage Boosts, XP Multipliers, and HP restores).
- **Stamina & Combat**: Sprint, attack, dodge, and manage your stats during combat.

### Systems
- **Tiled Map Loader**: Seamless integration with `.tmx` maps. The game loads layers, colliders, and spawn points directly from Tiled files.
- **Dynamic Camera System**: A smooth, centered camera that follows the player and constrains itself to map boundaries.
- **Level-Up & Progression**: Dynamic XP management and custom Level-Up UI overlays to upgrade player stats.
- **Leaderboard & Name Input**: High scores are tracked locally in `leaderboard.json` and presented in-game.
- **Audio Manager**: Immersive sound effects and theme music using high-quality `.ogg` audio files.

---

## 🛠️ Tech Stack

- **Core**: Python >= 3.12
- **Framework**: Pygame (2D Game Library)
- **Map Parsing**: PyTMX (Tiled Map Editor support)
- **Dependency Management**: [uv](https://github.com/astral-sh/uv) (Fast Python package manager)
- **Build Tool**: PyInstaller (for standalone binaries)

---

## 📂 Project Structure

```
OOP Project/
├── assets/                  # Game Assets
│   ├── fonts/               # Font files (PixelifySans)
│   ├── images/              # Map tilesets, sprites (Stella, Lazarus, Minotaur, etc.)
│   └── music/               # BGM and SFX (.ogg)
├── src/                     # Source Code
│   ├── components/          # Reusable UI components (buttons, etc.)
│   ├── core/                # Game engine, loop, camera, and menus
│   ├── entity/              # Entities (player, enemies, boss, projectiles, pickups)
│   ├── prefs/               # Constants, asset paths, and styles
│   ├── screens/             # Menu, Leaderboard, Name Input, Credits, and Game Over screens
│   ├── systems/             # Leaderboard storage and XP/Level systems
│   ├── utils/               # Frame and background helpers
│   └── main.py              # Main entry point
├── .github/workflows/       # CI/CD Workflows
│   ├── ci.yml               # Linting (Black, Isort, Ruff, Basedpyright) and testing
│   └── build.yml            # Converged Windows and Linux executable builder
├── main.spec                # PyInstaller specification file
├── pyproject.toml           # Project metadata and dependencies
└── uv.lock                  # UV lockfile
```

---

## 🚀 Getting Started

### Prerequisites
Make sure you have [uv](https://github.com/astral-sh/uv) installed on your system.

### Running the Game
1. Clone the repository and navigate to the project directory.
2. Run the entry point directly using `uv`:
   ```bash
   uv run python3 src/main.py
   ```
   *Note: UV will automatically create a virtual environment, install dependencies from `pyproject.toml`, and run the game.*

### Building Executables Locally
To build a standalone executable for your operating system:
```bash
uv run pyinstaller main.spec
```
The compiled binary will be generated inside the `dist/` directory.

---

## 🤖 CI/CD Integration

The project has two pre-configured GitHub Actions pipelines:
1. **CI Pipeline (`ci.yml`)**: Automatically triggers on pushes and pull requests to run format checks (Black, Isort), linter checks (Ruff), and static type-checks (Basedpyright).
2. **Build Pipeline (`build.yml`)**: Builds executables for Linux (`ubuntu-latest`) and Windows (`windows-latest`) using a strategy matrix. Once compiled, it:
   - Uploads build artifacts to the run.
   - Automatically posts direct artifact download links as comments on the triggering commit.
   - Attaches the binaries to draft releases for tags matching `v*`.
