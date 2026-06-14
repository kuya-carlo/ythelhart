"""
This module contains the main Game class, which orchestrates the entire game loop,
including player and enemy management, rendering, and level progression.
"""

import math
import random
from pathlib import Path
from typing import List, cast

import pygame
import pytmx

from src.core.camera import Camera
from src.entity import Enemy, Player, Projectile
from src.entity.minotaur import MinotaurBoss
from src.entity.pickup import spawn_random_pickup
from src.entity.rogue import Rogue
from src.entity.tank import Tank
from src.prefs import Constants, Map, Music, Style
from src.prefs.paths import MUSIC_PATH, PickupAssets, UIAssets
from src.screens.game_over import GameOverScreen
from src.systems.level_system import LevelSystem, LevelUpUI, XPManager

pygame.mixer.init()


class Game:
    """
    Main game controller that manages the game state, entities, and systems.

    This class initializes Pygame, loads the map, manages the player, enemies,
    and projectiles, and handles the main game loop, including updates,
    drawing, and event handling. It also integrates the level-up system.

    Attributes
    ----------
    screen : pygame.Surface
        The main display surface for the game.
    clock : pygame.time.Clock
        The clock to control the game's frame rate.
    font : pygame.font.Font
        The default font for rendering text.
    zoom_factor : float
        The scaling factor for the map and entities.
    map_data : pytmx.TiledMap | None
        The loaded Tiled map data.
    map_surface : pygame.Surface | None
        The rendered surface of the Tiled map.
    walls : list[pygame.Rect]
        A list of collision rectangles for the map walls.
    camera : Camera | None
        The camera object for scrolling the view.
    player : Player
        The player character instance.
    level_system : LevelSystem
        The system for managing player level, XP, and upgrades.
    levelup_ui : LevelUpUI
        The UI for displaying level-up options.
    enemies : pygame.sprite.Group
        A sprite group for all active enemies.
    projectiles : pygame.sprite.Group
        A sprite group for all active projectiles.
    minotaur_spawned : bool
        A flag indicating if the Minotaur boss has been spawned.
    minotaur : MinotaurBoss | None
        The Minotaur boss instance.
    last_click_world : tuple[int, int] | None
        The world coordinates of the last mouse click.
    wave : int
        The current enemy wave number.
    wave_timer : float
        A timer for the interval between waves.
    running : bool
        The main game loop flag.
    game_over : bool
        A flag indicating if the game is over.
    paused : bool
        A flag indicating if the game is paused.
    """

    def __init__(self, screen: pygame.Surface):
        """Initializes the main game controller and all related systems."""
        # Create the main game window
        self.screen = screen
        pygame.display.set_caption(Constants.Game.SCREEN_TITLE)

        self.clock = pygame.time.Clock()
        self.font = Style.Fonts(28).FONT  # In game text
        self.zoom_factor = Constants.Game.MAP_ZOOM

        # Setup map surfaces and collision data
        self.map_data = None
        self.map_surface = None
        self.walls = []
        self.camera = None
        self.load_map(Map.Main.MAP.PATH)

        assert (
            self.map_surface is not None
        ), "map_surface must be initialized by load_map"

        # Create the player instance
        self.player = Player()

        # Initialize the level-up system
        self.level_system = LevelSystem()
        self.levelup_ui = LevelUpUI(self.screen)

        # Position the player at the designated spawn point or map center
        self._initialize_player_position()

        # Initialize sprite groups
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.pickups = pygame.sprite.Group()
        self.minotaur_spawned = False
        self.minotaur = None

        # Track the last mouse click in world coordinates for aiming
        self.last_click_world = None

        # Initialize wave system variables
        self.wave = 0
        self.wave_timer = 0.0
        self.running = True
        self.action = None
        self.game_over = False
        self.game_over_screen_shown = False
        self.paused = False
        pygame.mixer.music.load(
            Music("GameBattleTheme.ogg", MUSIC_PATH / "SFX").MUSIC_PATH
        )
        pygame.mixer.music.set_volume(0.5)

        # Load sound effects
        self.sfx = {
            "player_hit": pygame.mixer.Sound(
                MUSIC_PATH / "SFX" / "NormalOrcAttack.ogg"
            ),
            "player_death": pygame.mixer.Sound(MUSIC_PATH / "SFX" / "GameOver.ogg"),
            "enemy_hit": pygame.mixer.Sound(
                MUSIC_PATH / "SFX" / "RoguePlayerAttack.ogg"
            ),
            "level_up": pygame.mixer.Sound(MUSIC_PATH / "SFX" / "LevelUp.ogg"),
            "tank_attack": pygame.mixer.Sound(MUSIC_PATH / "SFX" / "TankAttack.ogg"),
            "minotaur_attack": pygame.mixer.Sound(
                MUSIC_PATH / "SFX" / "MinotaurAttack.ogg"
            ),
        }
        self.sfx["player_death"].set_volume(0.75)

        # Start the first wave of enemies
        self.spawn_wave()

    def _initialize_player_position(self):
        """Finds the spawn point on the map and places the player there."""
        spawn = None
        try:
            # Look for a "spawn_point" layer in the Tiled map
            for name in getattr(self.map, "layernames", []):
                if name.lower() == "spawn_point":
                    spawn_layer = self.map.get_layer_by_name(name)
                    if spawn_layer is not None:
                        try:
                            for obj in spawn_layer:  # type: ignore
                                spawn = (
                                    int(obj.x * self.zoom_factor),
                                    int(obj.y * self.zoom_factor),
                                )
                                break
                        except TypeError:
                            pass
                    break
        except Exception:
            spawn = None

        # If no spawn point is found, place the player in the center of the map
        if spawn is None and self.map_surface is not None:
            self.player.rect.center = (
                self.map_surface.get_width() // 2,
                self.map_surface.get_height() // 2,
            )
        else:
            self.player.rect.center = spawn

        # Scale the player sprite according to the map's zoom factor
        self._scale_player()

    def _scale_player(self):
        """Scales the player's image and collision radius based on the map zoom."""
        if hasattr(self.player, "scale"):
            map_center = self.player.rect.center
            ratio = self.zoom_factor / self.player.scale
            self.player.image = pygame.transform.scale(
                self.player.image,
                (
                    max(1, int(self.player.image.get_width() * ratio)),
                    max(1, int(self.player.image.get_height() * ratio)),
                ),
            )
            self.player.rect = self.player.image.get_rect(center=map_center)
            self.player.radius = int(self.player.radius * ratio)
            self.player.scale = int(self.zoom_factor)

    def load_map(self, tmx_path: Path):
        """
        Loads a Tiled map file (.tmx), renders it to a surface, and extracts collision data.

        Parameters
        ----------
        tmx_path : Path
            The file path to the .tmx map file.

        Raises
        ------
        FileNotFoundError
            If the specified map file does not exist.
        """
        tmx_path = Path(tmx_path)
        if not tmx_path.exists():
            raise FileNotFoundError(f"[Error] Map file does not exist: {tmx_path}")

        self.debug_draw_colliders = False
        self.spawn_points = []

        # Load the map using pytmx
        self.map = pytmx.load_pygame(str(tmx_path))
        w = int(self.map.width * self.map.tilewidth * self.zoom_factor)
        h = int(self.map.height * self.map.tileheight * self.zoom_factor)
        self.map_surface = pygame.Surface((w, h))

        # Render all visible tile layers to the map surface
        for layer in self.map.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, image in layer.tiles():
                    if image:
                        # Scale tiles if a zoom factor is applied
                        if self.zoom_factor != 1.0:
                            image = pygame.transform.scale(
                                image,
                                (
                                    int(self.map.tilewidth * self.zoom_factor),
                                    int(self.map.tileheight * self.zoom_factor),
                                ),
                            )
                        self.map_surface.blit(
                            image,
                            (
                                x * self.map.tilewidth * self.zoom_factor,
                                y * self.map.tileheight * self.zoom_factor,
                            ),
                        )

        # Load wall objects from the "wall" object layer for collision
        self._load_walls()

        # Initialize the camera with the full map dimensions
        self.camera = Camera(
            self.map_surface.get_width(), self.map_surface.get_height()
        )

    def _load_walls(self):
        """Extracts wall collision rectangles from the Tiled map's 'wall' layer."""
        self.walls: List[pygame.Rect] = []
        wall_layer_name = None
        for name in getattr(self.map, "layernames", []):
            if name.lower() == "wall":
                wall_layer_name = name
                break
        if wall_layer_name is not None:
            layer = self.map.get_layer_by_name(wall_layer_name)
            if layer is not None:
                try:
                    # Inflate walls slightly to prevent clipping issues
                    per_side_x = 100
                    per_side_y = 150

                    for obj in layer:  # type: ignore
                        rect = pygame.Rect(
                            obj.x * self.zoom_factor,
                            obj.y * self.zoom_factor,
                            obj.width * self.zoom_factor,
                            obj.height * self.zoom_factor,
                        )

                        shrink_w = min(rect.width - 2, 2 * per_side_x)
                        shrink_h = min(rect.height - 2, 2 * per_side_y)

                        if shrink_w > 0 or shrink_h > 0:
                            rect.inflate_ip(-shrink_w, -shrink_h)

                        self.walls.append(rect)
                except TypeError:
                    pass

    def __get_enemy_spawns(self) -> list[tuple[float, float]]:
        """
        Collects all enemy spawn points from the 'enemy_spawn' layer in the map.

        Returns
        -------
        list[tuple[float, float]]
            A list of (x, y) coordinates for enemy spawn points.
        """
        spawns = []

        if self.map and "enemy_spawn" in self.map.layernames:
            layer = self.map.get_layer_by_name("enemy_spawn")
            if layer is not None:
                try:
                    for obj in layer:  # type: ignore
                        x = (obj.x + obj.width / 2) * self.zoom_factor
                        y = (obj.y + obj.height / 2) * self.zoom_factor
                        spawns.append((x, y))
                except TypeError:
                    pass

        self.spawn_points = spawns.copy()
        return spawns

    def spawn_enemy_at_edge(self):
        """
        Spawns a new enemy.

        The enemy is spawned at a random designated spawn point if available,
        otherwise at a random position just off-screen. The type of enemy
        spawned depends on the current wave number.
        """
        spawn_points = self.__get_enemy_spawns()
        if spawn_points:
            x, y = random.choice(spawn_points)
        else:
            # Fallback to spawning at screen edges if no spawn points are defined
            side = random.choice(["top", "bottom", "left", "right"])
            if side == "top":
                x, y = (
                    random.randint(0, Constants.Game.SCREEN_WIDTH),
                    -Constants.Enemy.ENEMY_SPAWN_BUFFER,
                )
            elif side == "bottom":
                x, y = (
                    random.randint(0, Constants.Game.SCREEN_WIDTH),
                    Constants.Game.SCREEN_HEIGHT + Constants.Enemy.ENEMY_SPAWN_BUFFER,
                )
            elif side == "left":
                x, y = (
                    -Constants.Enemy.ENEMY_SPAWN_BUFFER,
                    random.randint(0, Constants.Game.SCREEN_HEIGHT),
                )
            else:  # "right"
                x, y = (
                    Constants.Game.SCREEN_WIDTH + Constants.Enemy.ENEMY_SPAWN_BUFFER,
                    random.randint(0, Constants.Game.SCREEN_HEIGHT),
                )

        # Special case: Spawn the Minotaur boss on wave 5
        if self.wave == 5 and not self.minotaur_spawned:
            self.spawn_minotaur()
            self.minotaur_spawned = True
            return

        # Determine which type of enemy to spawn based on wave progression
        roll = random.random()
        if self.wave >= 3 and roll < 0.15:
            enemy = Tank(x, y)
        elif self.wave >= 2 and 0.15 <= roll < 0.45:
            enemy = Rogue(
                x,
                y,
                projectiles_group=self.projectiles,
                map_rect=(
                    cast(pygame.Surface, self.map_surface).get_rect()
                    if getattr(self, "map_surface", None) is not None
                    else None
                ),
                walls=self.walls,
                wave=self.wave,
            )
        else:
            enemy = Enemy(x, y)

        self.enemies.add(enemy)

    def spawn_wave(self):
        """Spawns a new wave of enemies with an increasing count."""
        self.wave += 1
        count = (
            Constants.Attack.WAVE_BASE_COUNT
            + (self.wave - 1) * Constants.Attack.WAVE_GROWTH
            + 3
        )
        for _ in range(count):
            self.spawn_enemy_at_edge()
        self.wave_timer = 0.0

    def spawn_minotaur(self, x: int | None = None, y: int | None = None):
        """
        Spawns the Minotaur boss at a specified location or the map center.

        Parameters
        ----------
        x : int | None, optional
            The x-coordinate for the spawn location. Defaults to the map center.
        y : int | None, optional
            The y-coordinate for the spawn location. Defaults to the map center.
        """
        if getattr(self, "map_surface", None) is None:
            return

        mx = (
            x
            if x is not None
            else cast(pygame.Surface, self.map_surface).get_width() // 2
        )
        my = (
            y
            if y is not None
            else cast(pygame.Surface, self.map_surface).get_height() // 2
        )

        self.minotaur = MinotaurBoss(mx, my)
        self.minotaur.camera = self.camera

        # Load and scale UI images for the boss health bar
        self._load_minotaur_ui()

        self.enemies.add(self.minotaur)

    def _load_minotaur_ui(self):
        """Loads and scales the UI assets for the Minotaur's health bar."""
        if not self.minotaur:
            return
        try:
            self.minotaur.ui_images = {
                "over": pygame.image.load(
                    str(UIAssets.MINO_HEALTH_OVER)
                ).convert_alpha(),
                "prog": pygame.image.load(
                    str(UIAssets.MINO_HEALTH_PROGRESS)
                ).convert_alpha(),
                "under": pygame.image.load(
                    str(UIAssets.MINO_HEALTH_UNDER)
                ).convert_alpha(),
            }
            UI_SCALE = 2

            def scale(img, s=UI_SCALE):
                return pygame.transform.scale(
                    img, (int(img.get_width() * s), int(img.get_height() * s))
                )

            self.minotaur.ui_images["over"] = scale(self.minotaur.ui_images["over"])
            self.minotaur.ui_images["prog"] = scale(self.minotaur.ui_images["prog"])
            self.minotaur.ui_images["under"] = scale(self.minotaur.ui_images["under"])
        except Exception:
            self.minotaur.ui_images = None

    def move_and_collide(self, sprite: pygame.sprite.Sprite, dt: float):
        """Move the sprite and handle collisions with walls."""
        sprite.rect.x += int(sprite.vx * dt)
        for wall in self.walls:
            if sprite.rect.colliderect(wall):
                if sprite.vx > 0:
                    sprite.rect.right = wall.left
                elif sprite.vx < 0:
                    sprite.rect.left = wall.right

        sprite.rect.y += int(sprite.vy * dt)
        for wall in self.walls:
            if sprite.rect.colliderect(wall):
                if sprite.vy > 0:
                    sprite.rect.bottom = wall.top
                elif sprite.vy < 0:
                    sprite.rect.top = wall.bottom

    def update(self, dt: float):
        """
        Updates the entire game state for the current frame.

        This includes updating the player, enemies, projectiles, handling collisions,
        and checking for game-over conditions.

        Parameters
        ----------
        dt : float
            The time elapsed since the last frame, in seconds.
        """
        # Halt all game actions for pause and level-up screens
        if self.paused or self.level_system.showing_levelup:
            return

        # Always update camera shake
        if self.camera:
            self.camera.update_shake(dt)

        # If the player is dead, handle the game-over sequence
        if self.player.dead:
            # On the first frame of death, trigger the audio and flag
            if not self.game_over:
                self.game_over = True
                pygame.mixer.stop()  # Stop all current SFX
                self.sfx["player_death"].play()
                pygame.mixer.music.fadeout(2000)  # Fade out music over 2 seconds

            # Continue updating the player to play the death animation
            self.player.update(dt)

            # Once the animation is finished, show the game over screen
            if (
                self.player.death_animation_finished()
                and not self.game_over_screen_shown
            ):
                self.game_over_screen_shown = True
                self.show_game_over_screen()
            return  # Stop further game logic

        # --- REGULAR GAMEPLAY (if player is alive) ---
        was_showing_levelup = self.level_system.showing_levelup

        # Update player facing direction and movement
        self._update_player_facing()
        self.player.update(dt)
        self.move_and_collide(self.player, dt)

        # Update other entities
        self._update_entities(dt)
        self._handle_collisions(dt)

        # Check for wave completion
        if len(self.enemies) == 0:
            self.wave_timer += dt
            if self.wave_timer >= Constants.Attack.WAVE_INTERVAL:
                self.spawn_wave()

        # Update camera to follow the player
        if self.camera:
            self.camera.update(self.player.rect)

        # Check for health upgrade
        if self.level_system.health_upgrade_pending:
            self.player.start_healing(20, 1.0)
            self.level_system.health_upgrade_pending = False

        # Play level up sound if the state just changed
        if self.level_system.showing_levelup and not was_showing_levelup:
            self.sfx["level_up"].play()

    def show_game_over_screen(self):
        """Displays the game over screen and handles the player's choice."""
        game_over_screen = GameOverScreen(self.screen, self.wave)
        action = game_over_screen.run()
        if action == "restart":
            self.restart()
        elif action == "main_menu":
            self.running = False  # End this game instance
        elif action == "quit":
            self.running = False
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _update_player_facing(self):
        """Updates the player's facing direction based on the mouse cursor's position."""
        mx, my = pygame.mouse.get_pos()
        if self.camera:
            world_mx, world_my = self.camera.screen_to_world((mx, my))
        else:
            world_mx, world_my = mx, my

        dx = world_mx - self.player.rect.centerx
        dy = world_my - self.player.rect.centery
        if abs(dx) > abs(dy):
            self.player.facing = "side"
            self.player.flip_side = dx < 0
        else:
            self.player.facing = "up" if dy < 0 else "down"
            self.player.flip_side = False

    def _update_entities(self, dt: float):
        """Updates all enemies and projectiles, and awards XP for kills."""
        # Store the alive state of enemies before updates
        # Before update
        enemy_states = {
            id(enemy): (enemy.alive, enemy.rect.center) for enemy in self.enemies
        }

        # Update enemies
        for enemy in list(self.enemies):
            try:
                enemy.update(dt, self.player, self.walls)
            except TypeError:
                enemy.update(dt, self.player)

        # Update projectiles
        self.projectiles.update(dt)
        self.pickups.update(dt)

        # Award XP for enemies that died this frame
        for enemy in list(self.enemies):
            if enemy_states.get(id(enemy), True) and not enemy.alive:
                if not getattr(enemy, "xp_given", False):
                    xp_reward = XPManager.get_xp_for_enemy(enemy)
                    self.level_system.add_xp(xp_reward)
                    enemy.xp_given = True

                    # Spawn pickup at enemy location
                    enemy_pos = enemy_states[id(enemy)][1]
                    if enemy_pos:
                        pickup = spawn_random_pickup(
                            enemy_pos[0], enemy_pos[1], drop_chance=0.3
                        )
                        if pickup:
                            print("Enemy died! Attempting pickup spawn.")
                            self.pickups.add(pickup)

        # Special handling for the Minotaur boss
        if self.minotaur:
            was_alive = self.minotaur.alive
            self.minotaur.update(dt, self.player, self.walls)
            if was_alive and not self.minotaur.alive:
                if not getattr(self.minotaur, "xp_given", False):
                    xp_reward = XPManager.get_xp_for_enemy(self.minotaur)
                    self.level_system.add_xp(xp_reward)
                    self.minotaur.xp_given = True

                    minotaur_pos = self.minotaur.rect.center
                    for _ in range(3):  # Drop 3 pickups
                        offset_x = random.randint(-30, 30)
                        offset_y = random.randint(-30, 30)
                        pickup = spawn_random_pickup(
                            minotaur_pos[0] + offset_x,
                            minotaur_pos[1] + offset_y,
                            drop_chance=1.0,  # Boss always drops
                        )
                        if pickup:
                            self.pickups.add(pickup)

            if not self.minotaur.alive and self.minotaur not in self.enemies:
                self.minotaur = None

    def _handle_collisions(self, dt: float):
        """Handles collisions between the player, enemies, and projectiles."""
        # Enemy projectiles hitting the player
        for proj in list(self.projectiles):
            if isinstance(proj.owner, Enemy):
                if not getattr(proj, "stuck", False) and proj.rect.colliderect(
                    self.player.rect
                ):
                    if self.player.take_damage(
                        getattr(proj, "damage", Constants.Player.PLAYER_DAMAGE)
                    ):
                        self.sfx["player_hit"].play()
                    self.player.apply_knockback(proj.owner.rect.center)
                    proj.stick(broken=True)

        # Player-enemy physical collisions
        for enemy in list(self.enemies):
            dx = self.player.rect.centerx - enemy.rect.centerx
            dy = self.player.rect.centery - enemy.rect.centery
            dist_sq = dx * dx + dy * dy
            min_dist = self.player.radius + enemy.radius
            if dist_sq <= min_dist * min_dist:
                # Apply damage if the enemy's attack is off cooldown
                if enemy.hit_cd <= 0:
                    # Calculate damage multiplier based on nearby enemies
                    nearby_radius = 80
                    nearby_count = sum(
                        1
                        for e in self.enemies
                        if (self.player.rect.centerx - e.rect.centerx) ** 2
                        + (self.player.rect.centery - e.rect.centery) ** 2
                        <= nearby_radius**2
                    )
                    damage_multiplier = max(1, min(nearby_count, 5))
                    damage = Constants.Enemy.ENEMY_DAMAGE * damage_multiplier

                    if self.player.take_damage(damage):
                        if isinstance(enemy, Tank):
                            self.sfx["tank_attack"].play()
                        elif isinstance(enemy, MinotaurBoss):
                            self.sfx["minotaur_attack"].play()
                        else:
                            self.sfx["player_hit"].play()
                        self.player.apply_knockback(enemy.rect.center)
                        enemy.hit_cd = Constants.Attack.INVULN_TIME

                # Resolve physical overlap by pushing entities apart
                dist = math.sqrt(dist_sq) if dist_sq > 0 else 0.0001
                overlap = min_dist - dist
                nx, ny = dx / dist, dy / dist
                self.player.rect.centerx += int(nx * overlap * 0.8)
                self.player.rect.centery += int(ny * overlap * 0.8)
                enemy.rect.centerx -= int(nx * overlap * 0.2)
                enemy.rect.centery -= int(ny * overlap * 0.2)
        for pickup in list(self.pickups):
            # Check collision with player
            dx = self.player.rect.centerx - pickup.rect.centerx
            dy = self.player.rect.centery - pickup.rect.centery
            dist_sq = dx * dx + dy * dy
            collection_radius = (
                self.player.radius + 15
            )  # Slightly larger collection range

            if dist_sq <= collection_radius * collection_radius:
                # Apply effect and show message
                message = pickup.apply_effect(self.player)
                print(message)  # TODO: Replace with on-screen notification
                pickup.kill()

    def draw(self):
        """Draws all game elements to the screen."""
        # Draw the map background
        self._draw_map()

        # Draw all entities
        for enemy in self.enemies:
            enemy.draw(self.screen, camera=self.camera)

        for pickup in self.pickups:
            pickup.draw(self.screen, camera=self.camera)

        for proj in self.projectiles:
            if self.camera:
                screen_rect = self.camera.apply_rect(proj.rect)
                self.screen.blit(proj.image, screen_rect)
            else:
                self.screen.blit(proj.image, proj.rect)
        self.player.draw(self.screen, camera=self.camera)

        # Optional debug overlays
        if getattr(self, "debug_draw_colliders", False):
            self._draw_debug_overlays()

        # Draw UI elements (only if not in the game over sequence)
        if not self.game_over:
            self.draw_enemy_pointers()
            self._draw_hud()
            self.draw_boss_health()

        # Draw overlays for game state (pause, level up)
        if self.paused:
            overlay = pygame.Surface(
                (Constants.Game.SCREEN_WIDTH, Constants.Game.SCREEN_HEIGHT),
                pygame.SRCALPHA,
            )
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            pause_font = Style.Fonts(72).FONT
            pause_txt = pause_font.render("PAUSED", True, (255, 255, 255))
            self.screen.blit(
                pause_txt,
                pause_txt.get_rect(
                    center=(
                        Constants.Game.SCREEN_WIDTH // 2,
                        Constants.Game.SCREEN_HEIGHT // 2 - 80,
                    )
                ),
            )
            # Instructions
            inst_font = Style.Fonts(36).FONT
            inst_txt = inst_font.render("Press ESC to Resume", True, (200, 200, 200))
            self.screen.blit(
                inst_txt,
                inst_txt.get_rect(
                    center=(
                        Constants.Game.SCREEN_WIDTH // 2,
                        Constants.Game.SCREEN_HEIGHT // 2 + 20,
                    )
                ),
            )
            quit_txt = inst_font.render("Press Q to Quit", True, (200, 100, 100))
            self.screen.blit(
                quit_txt,
                quit_txt.get_rect(
                    center=(
                        Constants.Game.SCREEN_WIDTH // 2,
                        Constants.Game.SCREEN_HEIGHT // 2 + 70,
                    )
                ),
            )
        elif self.level_system.showing_levelup:
            self.levelup_ui.draw(self.level_system)

        pygame.display.flip()

    def _draw_map(self):
        """Renders the visible portion of the map to the screen."""
        if self.map_surface and self.camera:
            cam_rect = pygame.Rect(
                int(self.camera.rect.x),
                int(self.camera.rect.y),
                Constants.Game.SCREEN_WIDTH,
                Constants.Game.SCREEN_HEIGHT,
            )
            map_rect = self.map_surface.get_rect()
            cam_rect.clamp_ip(map_rect)
            self.screen.blit(self.map_surface, (0, 0), cam_rect)
        else:
            self.screen.fill((40, 50, 60))

    def _draw_debug_overlays(self):
        """Draws debug information like collision boxes and spawn points."""
        if not self.camera:
            return
        s = pygame.Surface(
            (Constants.Game.SCREEN_WIDTH, Constants.Game.SCREEN_HEIGHT),
            pygame.SRCALPHA,
        )
        # Draw walls
        for wall in self.walls:
            r = self.camera.apply_rect(wall)
            pygame.draw.rect(s, (255, 0, 0, 80), r)
            pygame.draw.rect(s, (200, 0, 0, 140), r, 1)
        # Draw spawn points
        for sp in self.spawn_points:
            sx, sy = self.camera.world_to_screen(sp)
            pygame.draw.line(s, (0, 255, 0, 200), (sx - 6, sy), (sx + 6, sy), 2)
            pygame.draw.line(s, (0, 255, 0, 200), (sx, sy - 6), (sx, sy + 6), 2)
        # Draw player and enemy collision radii
        px, py = self.camera.world_to_screen(self.player.rect.center)
        pygame.draw.circle(
            s, (0, 150, 255, 150), (int(px), int(py)), self.player.radius, 2
        )
        for enemy in self.enemies:
            ex, ey = self.camera.world_to_screen(enemy.rect.center)
            pygame.draw.circle(
                s, (255, 255, 0, 150), (int(ex), int(ey)), enemy.radius, 2
            )
        self.screen.blit(s, (0, 0))

    def _draw_buff_icons(self):
        """
        Draws icons for active buffs/power-ups using the actual pickup images.

        Shows the pickup sprites with timers for each active buff.
        """
        icon_size = 40
        buff_padding = 8
        start_x = Constants.Game.SCREEN_WIDTH - icon_size - 20
        start_y = 20

        buffs = []

        # Check which buffs are active and load corresponding images
        if self.player.speed_boost_timer > 0:
            buffs.append(
                {
                    "image_path": PickupAssets.SPEED_BOOST,
                    "timer": self.player.speed_boost_timer,
                    "name": "Speed",
                }
            )

        if self.player.xp_multiplier_timer > 0:
            buffs.append(
                {
                    "image_path": PickupAssets.XP_MULTIPLIER,
                    "timer": self.player.xp_multiplier_timer,
                    "name": "XP",
                }
            )

        if self.player.damage_boost_timer > 0:
            buffs.append(
                {
                    "image_path": PickupAssets.DAMAGE_BOOST,
                    "timer": self.player.damage_boost_timer,
                    "name": "DMG",
                }
            )

        # Draw each active buff
        for i, buff in enumerate(buffs):
            y_pos = start_y + i * (icon_size + buff_padding)

            try:
                # Load and scale the pickup image
                icon_img = pygame.image.load(str(buff["image_path"])).convert_alpha()
                icon_img = pygame.transform.scale(icon_img, (icon_size, icon_size))

                # Draw semi-transparent dark background
                bg_rect = pygame.Rect(
                    start_x - 2, y_pos - 2, icon_size + 4, icon_size + 4
                )
                bg_surface = pygame.Surface(
                    (bg_rect.width, bg_rect.height), pygame.SRCALPHA
                )
                bg_surface.fill((0, 0, 0, 128))
                self.screen.blit(bg_surface, bg_rect)

                # Draw the icon
                self.screen.blit(icon_img, (start_x, y_pos))

                # Draw white border
                pygame.draw.rect(
                    self.screen,
                    (255, 255, 255),
                    (start_x, y_pos, icon_size, icon_size),
                    2,
                )

                # Draw timer below the icon
                timer_font = pygame.font.Font(None, 18)
                timer_text = timer_font.render(
                    f"{buff['timer']:.1f}s", True, (255, 255, 255)
                )
                timer_bg = pygame.Surface(
                    (timer_text.get_width() + 6, timer_text.get_height() + 2),
                    pygame.SRCALPHA,
                )
                timer_bg.fill((0, 0, 0, 180))

                timer_x = start_x + (icon_size - timer_text.get_width()) // 2 - 3
                timer_y = y_pos + icon_size + 2

                self.screen.blit(timer_bg, (timer_x, timer_y))
                self.screen.blit(timer_text, (timer_x + 3, timer_y + 1))

            except Exception:
                # Fallback to simple colored square if image loading fails
                pygame.draw.rect(
                    self.screen, (100, 100, 100), (start_x, y_pos, icon_size, icon_size)
                )
                pygame.draw.rect(
                    self.screen,
                    (255, 255, 255),
                    (start_x, y_pos, icon_size, icon_size),
                    2,
                )

    def _draw_hud(self):
        """Draws the Heads-Up Display (health, stamina, XP bars, wave count)."""
        bar_w, bar_h = 200, 18
        x, y = 20, 20

        # Health Bar
        max_hp_with_bonus = self.player.max_hp + self.level_system.get_health_bonus()
        hp_pct = max(0.0, self.player.hp / max_hp_with_bonus)
        pygame.draw.rect(self.screen, (60, 60, 60), (x, y, bar_w, bar_h))
        pygame.draw.rect(self.screen, (200, 50, 50), (x, y, int(bar_w * hp_pct), bar_h))
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_w, bar_h), 2)
        self.screen.blit(
            self.font.render("HP", True, (255, 255, 255)), (x + bar_w + 10, y - 2)
        )

        # Stamina Bar
        y += bar_h + 10
        stam_pct = max(0.0, self.player.stamina / self.player.max_stamina)
        pygame.draw.rect(self.screen, (60, 60, 60), (x, y, bar_w, bar_h))
        pygame.draw.rect(
            self.screen, (50, 180, 255), (x, y, int(bar_w * stam_pct), bar_h)
        )
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_w, bar_h), 2)
        self.screen.blit(
            self.font.render("STM", True, (255, 255, 255)), (x + bar_w + 10, y - 2)
        )

        # XP Bar
        y += bar_h + 10
        xp_pct = self.level_system.xp / self.level_system.xp_to_next_level
        pygame.draw.rect(self.screen, (60, 60, 60), (x, y, bar_w, bar_h))
        pygame.draw.rect(self.screen, (255, 215, 0), (x, y, int(bar_w * xp_pct), bar_h))
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_w, bar_h), 2)
        xp_text = f"LVL {self.level_system.level}"
        self.screen.blit(
            self.font.render(xp_text, True, (255, 255, 255)), (x + bar_w + 10, y - 2)
        )

        # Wave Counter
        self.screen.blit(
            self.font.render(f"Wave: {self.wave}", True, (255, 255, 255)),
            (20, y + bar_h + 10),
        )

        self._draw_buff_icons()

    def draw_enemy_pointers(self):
        """Draws arrows on the screen edges pointing towards off-screen enemies."""
        if not self.camera:
            return

        screen_rect = self.screen.get_rect()
        for enemy in self.enemies:
            ex, ey = enemy.rect.center
            sx, sy = self.camera.world_to_screen((ex, ey))

            # Skip enemies that are on-screen
            if screen_rect.collidepoint(sx, sy):
                continue

            # Calculate the angle and position for the pointer
            cx, cy = screen_rect.center
            angle = math.atan2(sy - cy, sx - cx)

            # Clamp the pointer to the screen edges with padding
            edge_padding = 40
            bound_x = screen_rect.width / 2 - edge_padding
            bound_y = screen_rect.height / 2 - edge_padding

            px = cx + math.cos(angle) * bound_x
            py = cy + math.sin(angle) * bound_y

            if px < edge_padding:
                px = edge_padding
            if px > screen_rect.width - edge_padding:
                px = screen_rect.width - edge_padding
            if py < edge_padding:
                py = edge_padding
            if py > screen_rect.height - edge_padding:
                py = screen_rect.height - edge_padding

            # Draw the triangular pointer
            size = 16
            points = [
                (px, py),
                (px - size * math.cos(angle - 0.5), py - size * math.sin(angle - 0.5)),
                (px - size * math.cos(angle + 0.5), py - size * math.sin(angle + 0.5)),
            ]
            pygame.draw.polygon(self.screen, (255, 80, 80), points)
            pygame.draw.polygon(self.screen, (0, 0, 0), points, 2)

    def draw_boss_health(self):
        """Draws the health bar for the Minotaur boss."""
        boss = self.minotaur
        if not boss or boss.hp <= 0:
            return

        # Use custom UI images if available, otherwise draw a simple bar
        if boss.ui_images:
            over = boss.ui_images["over"]
            prog = boss.ui_images["prog"]
            under = boss.ui_images["under"]
            x = (Constants.Game.SCREEN_WIDTH - over.get_width()) // 2
            y = 10
            self.screen.blit(under, (x, y))
            hp_ratio = max(0.0, min(1.0, boss.hp / boss.max_hp))
            cur_w = int(prog.get_width() * hp_ratio)
            if cur_w > 0:
                filled_portion = prog.subsurface(
                    pygame.Rect(0, 0, cur_w, prog.get_height())
                )
                self.screen.blit(filled_portion, (x, y))
            self.screen.blit(over, (x, y))
        else:
            bar_x, bar_y = 40, Constants.Game.SCREEN_HEIGHT - 80
            bar_w, bar_h = 400, 28
            pct = boss.hp / boss.max_hp
            pygame.draw.rect(self.screen, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(
                self.screen, (200, 50, 50), (bar_x, bar_y, int(bar_w * pct), bar_h)
            )
            pygame.draw.rect(
                self.screen, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 2
            )

    def shoot(self, target_pos: tuple[int, int] | None = None):
        """
        Creates a projectile aimed at a target position, respecting player cooldowns.

        Parameters
        ----------
        target_pos : tuple[int, int] | None, optional
            The screen or world coordinates to aim at. If None, uses the mouse position.
        """
        if not self.player.can_shoot():
            return

        if target_pos is None:
            screen_mouse = pygame.mouse.get_pos()
            target_pos = (
                self.camera.screen_to_world(screen_mouse)
                if self.camera
                else screen_mouse
            )

        self.last_click_world = target_pos

        map_rect = self.map_surface.get_rect() if self.map_surface else None

        # Apply damage bonus from the level system
        total_damage = self.player.get_current_damage()

        proj = Projectile(
            start=self.player.rect.center,
            target=target_pos,
            map_rect=map_rect,
            enemies=self.enemies,
            walls=self.walls,
            damage=total_damage,
        )
        self.projectiles.add(proj)
        self.sfx["enemy_hit"].play()

        # Apply attack speed bonus to the player's cooldown
        self.player.attack_cooldown = (
            0.5 * self.level_system.get_attack_speed_multiplier()
        )

    def restart(self):
        """Resets the game to its initial state for a new game."""
        self.player = Player()
        self.enemies.empty()
        self.projectiles.empty()
        self.pickups.empty()
        self.wave = 0
        self.wave_timer = 0
        self.game_over = False
        self.game_over_screen_shown = False
        self.minotaur_spawned = False
        self.minotaur = None
        self.level_system = LevelSystem()
        self.last_click_world = None

        self._initialize_player_position()

        if self.map_surface:
            self.camera = Camera(
                self.map_surface.get_width(),
                self.map_surface.get_height(),
            )
            self.camera.update(self.player.rect)
        self.spawn_wave()
        pygame.mixer.music.play(-1)

    def run(self):
        """The main game loop."""
        mouse_held = False
        pygame.mixer.music.play(-1)

        while self.running:
            dt = self.clock.tick(60) / 1000.0

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                    if event.key == pygame.K_q and self.paused:
                        self.running = False
                    if (
                        event.key == pygame.K_SPACE
                        and not self.paused
                        and not self.game_over
                    ):
                        self.shoot()
                    if event.key == pygame.K_F10:
                        self.debug_draw_colliders = not self.debug_draw_colliders
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.level_system.showing_levelup:
                        self.levelup_ui.handle_click(
                            pygame.mouse.get_pos(), self.level_system
                        )
                    elif not self.game_over:
                        mouse_held = True
                        self.shoot()
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    mouse_held = False

            # Continuous shooting if the mouse is held down
            if (
                mouse_held
                and not self.level_system.showing_levelup
                and not self.game_over
            ):
                self.shoot()

            # Update UI and game state
            if self.level_system.showing_levelup:
                self.levelup_ui.update(pygame.mouse.get_pos())

            self.update(dt)
            self.draw()
