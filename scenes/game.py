"""
Game scene for the RPG game.
"""
import math
import pygame
from pathlib import Path
from globals import SCREEN_WIDTH, SCREEN_HEIGHT, SCENE_MENU, SCENE_SETTINGS, FPS, FONT_ANTIALIAS, BLUE, GRAY, WHITE
from vignette import create_vignette
from camera import Camera
from player import Player

from .aesthetic import safe_scale_surface
from .dialogue import DialogueBox
from .hud import draw_player_health_bar, draw_debug_coords, draw_debug_collision, draw_door_prompt
from .game_over import GameOverMenu
from .pause_menu import PauseMenu
from .world import World
from .loading_screen import draw_loading_screen


class GameScene:
    """Game scene."""

    MOVE_SPEED = 75  # pixels per second

    def __init__(self, title_font, menu_font, credit_font, sounds=None):
        self._clock = pygame.time.Clock()
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font
        self.sounds = sounds or {}
        self.time_seconds = 0.0
        self.player = Player()
        self.camera = Camera(self.player.position.x, self.player.position.y)
        self.keys_pressed = {"up": False, "down": False, "left": False, "right": False}

        # Loading screen state
        self.loading = True
        self.loading_ready = False
        self.loading_time = 0.0
        self.loading_duration = 0.6
        self.loading_hints = [
            "Sharpening swords...",
            "Lighting torches...",
            "Spawning enemies...",
            "Polishing armour...",
            "Unlocking dungeon...",
        ]

        # First-time dialogue
        self.first_dialogue_shown = False
        font_path = None
        for candidate in [
            Path(__file__).resolve().parent.parent / "assets" / "fonts" / "Kenney Pixel.ttf",
            Path(__file__).resolve().parent.parent / "assets" / "font" / "Kenney Pixel.ttf",
        ]:
            if candidate.exists():
                font_path = str(candidate)
                break
        self.dialogue = DialogueBox(
            "Huh... Where am I? What is this place?",
            speed=30,
            font_path=font_path,
        )

        # Pause menu
        self.paused = False
        self.pause_pending_scene = None
        self.pause_menu = PauseMenu(title_font, menu_font, sounds)

        # Game over
        self.game_over = False
        self.game_over_menu = GameOverMenu(title_font, menu_font, credit_font, sounds)
        self.restart_on_enter = False

        # Map
        self.world = None
        self.near_door = None

        try:
            tmx_path = Path(__file__).resolve().parent.parent / "assets" / "maps" / "Tiled_files" / "Dungeon1.tmx"
            self.world = World(tmx_path, self.player, zoom=3.0, default_layer=8)
        except Exception as e:
            print(f"Warning: Could not load map : {e}")

        # Center player on map
        if self.world and self.world.map_layer:
            self.player.position.x = (27 * 16) / 2
            self.player.position.y = (37 * 16) / 2
        else:
            self.player.position.x = SCREEN_WIDTH / 2
            self.player.position.y = SCREEN_HEIGHT / 2

        self.spawn_x = self.player.position.x
        self.spawn_y = self.player.position.y
        self.camera.x = self.player.position.x
        self.camera.y = self.player.position.y

        # Camera zoom transition
        self.target_zoom = 3.0
        self.zoom_transition_speed = 1.2

    def handle_event(self, event):
        """Handle input events."""
        if self.loading:
            return None

        if self.game_over:
            self.game_over_menu.handle_event(event)
            return None

        if self.dialogue.active:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.dialogue.skip_or_dismiss()
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused
                if self.paused:
                    for k in self.keys_pressed:
                        self.keys_pressed[k] = False
                return None

            if self.paused:
                self.pause_menu.handle_event(event)
                return None

            if event.key == pygame.K_e:
                if self.near_door:
                    self.world.open_door(self.near_door)
                    open_sound = self.sounds.get("door_open")
                    if open_sound:
                        open_sound.play()
                return None

            if event.key in (pygame.K_UP, pygame.K_w):
                self.keys_pressed["up"] = True
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.keys_pressed["down"] = True
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.keys_pressed["left"] = True
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.keys_pressed["right"] = True

        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.keys_pressed["up"] = False
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.keys_pressed["down"] = False
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.keys_pressed["left"] = False
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.keys_pressed["right"] = False

        elif event.type == pygame.MOUSEBUTTONDOWN and self.paused:
            self.pause_menu.handle_event(event)

        return None

    def consume_requested_scene(self):
        """Return and clear a deferred scene transition request."""
        scene = self.pause_pending_scene
        self.pause_pending_scene = None
        return scene

    def on_enter(self):
        """Reset loading screen when transitioning into game scene."""
        self.loading = True
        self.loading_time = 0.0
        self.loading_ready = False
        self.paused = False

        if self.restart_on_enter:
            self._reset_player()
            self.restart_on_enter = False

        if self.world and self.world.map_layer:
            self.world.center(self.player.position.x, self.player.position.y)
            self.camera.x = self.player.position.x
            self.camera.y = self.player.position.y
            self.player.update(0)

    def _reset_player(self):
        """Respawn the player and reset gameplay state."""
        self.player.position.x = self.spawn_x
        self.player.position.y = self.spawn_y
        self.player.health = self.player.max_health
        self.player.damage_cooldown = 0.0
        self.player.set_state("idle")
        self.player.update(0)

        self.camera.x = self.player.position.x
        self.camera.y = self.player.position.y
        if self.world and self.world.map_layer:
            self.world.center(self.player.position.x, self.player.position.y)

        self.keys_pressed = {"up": False, "down": False, "left": False, "right": False}
        self.paused = False
        self.game_over = False
        self.near_door = None
        self.dialogue.active = False
        self.game_over_menu.reset()

        if self.world:
            self.world.reset_doors()

    def update(self, mouse_pos):
        """Update game state."""
        self.time_seconds = pygame.time.get_ticks() / 1000.0
        dt = self._clock.tick(FPS) / 1000.0

        # Loading screen
        if self.loading:
            if not self.loading_ready:
                return
            self.loading_time += dt
            if self.loading_time >= self.loading_duration:
                self.loading = False
                if not self.first_dialogue_shown:
                    self.dialogue.start()
            return

        # Dialogue
        if self.dialogue.active:
            self.dialogue.update(dt)
            if self.dialogue.is_finished():
                self.first_dialogue_shown = True
            elif not self.dialogue.closing:
                return

        # Game over
        if self.game_over:
            self.game_over_menu.update(dt, mouse_pos)
            action = self.game_over_menu.consume_action()
            if action == "Retry":
                self._reset_player()
            elif action == "Main Menu":
                self.restart_on_enter = True
                self.pause_pending_scene = SCENE_MENU
            return

        # Pause
        if self.paused:
            self.pause_menu.update(dt, mouse_pos, self.time_seconds)
            action = self.pause_menu.consume_action()
            if action == "Resume":
                self.paused = False
            elif action == "Settings":
                self.pause_pending_scene = SCENE_SETTINGS
            elif action == "Main Menu":
                self.paused = False
                self.pause_pending_scene = SCENE_MENU
            return

        # Player movement
        dx = 0
        dy = 0
        if self.keys_pressed["up"]:
            dy -= 1
        if self.keys_pressed["down"]:
            dy += 1
        if self.keys_pressed["left"]:
            dx -= 1
        if self.keys_pressed["right"]:
            dx += 1

        moving = dx != 0 or dy != 0


        if moving:
            # self.player.move(dx, dy, self.MOVE_SPEED * dt)
            if self.player.state not in ("run", "hit", "death"):
                self.player.set_state("run")
        else:
            if self.player.state not in ("idle", "hit", "death"):
                self.player.set_state("idle")

        # Collision detection
        old_x = self.player.position.x
        old_y = self.player.position.y

        # Move and check X axis only
        self.player.position.x += dx * self.MOVE_SPEED * dt
        player_rect = pygame.Rect(
            self.player.position.x - 4,
            self.player.position.y + 4,
            8, 4
        )
        if self.world:
            self.world.check_collision_x(player_rect, old_x, self.player)

        # Move and check Y axis only
        self.player.position.y += dy * self.MOVE_SPEED * dt
        player_rect = pygame.Rect(
            self.player.position.x - 4,
            self.player.position.y + 4,
            8, 4
        )
        if self.world:
            self.world.check_collision_y(player_rect, old_y, self.player)

        # Hazard detection
        if self.world and self.player.damage_cooldown <= 0:
            if self.world.check_hazard(player_rect, self.player):
                hit_sound = self.sounds.get("hit")
                if hit_sound:
                    hit_sound.play()
                if self.player.is_dead:
                    death_sound = self.sounds.get("death")
                    if death_sound:
                        death_sound.play()
                    self.game_over = True
                    self.paused = False
                    self.keys_pressed = {"up": False, "down": False, "left": False, "right": False}
                    self.player.set_state("death")

        # Door proximity check
        self.near_door = self.world.get_nearby_door(self.player) if self.world else None

        # Clamp to map bounds
        if self.world and self.world.map_width > 0 and self.world.map_height > 0:
            self.player.position.x = max(0, min(self.world.map_width, self.player.position.x))
            self.player.position.y = max(0, min(self.world.map_height, self.player.position.y))

        self.player.update(dt)

        # Change layer z index check
        if self.world:
            self.world.update_player_layer(self.player)

        self.camera.update(
            self.player,
            dt,
            self.world.map_width if self.world else 0,
            self.world.map_height if self.world else 0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            self.world.map_layer.zoom if self.world and self.world.map_layer else 1.0
        )

        # Zoom transition
        if self.world and self.world.map_layer and self.world.map_layer.zoom > self.target_zoom:
            self.world.map_layer.zoom = max(
                self.target_zoom,
                self.world.map_layer.zoom - self.zoom_transition_speed * dt
            )

    def render(self, screen):
        """Render the game scene."""

        # Loading screen
        if self.loading:
            draw_loading_screen(screen, self.loading_time, self.menu_font, self.credit_font, self.loading_hints)
            return
        
        # Map
        if self.world:
            self.world.draw(screen, self.camera.x, self.camera.y)
        zoom = self.world.map_layer.zoom if self.world and self.world.map_layer else 1.0

        # HUD
        draw_player_health_bar(screen, self.player, self.camera, zoom)

        # Door prompt
        if self.near_door:
            draw_door_prompt(screen, self.player, self.camera, zoom, self.credit_font)

        # Debug
        if self.world:
            draw_debug_collision(
                screen,
                self.world.collision_rects + self.world.hazard_rects,
                self.camera,
                zoom
            )
        draw_debug_coords(screen, self.player, self.credit_font)

        # Pause overlay
        if self.paused:
            self.pause_menu.render(screen, self.time_seconds)

        # Game over overlay
        if self.game_over:
            self.game_over_menu.render(screen, self.time_seconds)

        # Dialogue
        self.dialogue.render(screen, self.time_seconds)