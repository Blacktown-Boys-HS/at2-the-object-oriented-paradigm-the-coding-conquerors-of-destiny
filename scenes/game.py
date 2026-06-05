"""
Game scene for the RPG game.
"""

from pathlib import Path

import pygame

from camera import Camera
from game_constants import *
from globals import (
    FPS,
    SCENE_MENU,
    SCENE_SETTINGS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    get_gothic_font_path,
)
from player import Player

from .dialogue import DialogueBox
from .game_over import GameOverMenu
from .hud import (
    draw_debug_collision,
    draw_debug_coords,
    draw_door_prompt,
    draw_key_prompt,
    draw_locked_door_prompt,
    draw_player_health_bar,
)
from .inventory_bar import InventoryBar
from .loading_screen import draw_loading_screen
from .pause_menu import PauseMenu
from .task_panel import TaskPanel
from .world import World


class GameScene:
    """Game scene."""

    def __init__(self, title_font, menu_font, credit_font, sounds=None):
        self._init_core_objects(title_font, menu_font, credit_font, sounds)
        self._init_ui_elements(title_font, menu_font, credit_font, sounds)
        self._init_loading_state()
        self._init_dialogue()
        self._init_world()
        self._init_camera()

    def _init_core_objects(self, title_font, menu_font, credit_font, sounds):
        """Initialize core objects: clock, fonts, sounds, player, camera, keys."""
        self._clock = pygame.time.Clock()
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font
        self.sounds = sounds or {}
        self.time_seconds = 0.0
        self.player = Player()
        self.camera = Camera(self.player.position.x, self.player.position.y)
        self.keys_pressed = {"up": False, "down": False, "left": False, "right": False}

    def _init_ui_elements(self, title_font, menu_font, credit_font, sounds):
        """Initialize UI elements: task panel, inventory bar, pause menu, game over menu."""
        self.task_panel = TaskPanel(credit_font)
        self.inventory_bar = InventoryBar(credit_font)
        self.paused = False
        self.pause_pending_scene = None
        self.pause_menu = PauseMenu(title_font, menu_font, sounds)
        self.game_over = False
        self.game_over_menu = GameOverMenu(title_font, menu_font, credit_font, sounds)
        self.restart_on_enter = False

    def _init_loading_state(self):
        """Initialize loading screen state and hints."""
        self.loading = True
        self.loading_ready = False
        self.loading_time = 0.0
        self.loading_duration = LOADING_SCREEN_DURATION
        self.loading_hints = [
            "Sharpening swords...",
            "Lighting torches...",
            "Spawning enemies...",
            "Polishing armour...",
            "Unlocking dungeon...",
        ]

    def _init_dialogue(self):
        """Initialize dialogue box and first dialogue state."""
        self.first_dialogue_shown = False
        font_path = get_gothic_font_path()
        if font_path is not None:
            font_path = str(font_path)
        self.dialogue = DialogueBox(
            "Huh... Where am I? What is this place?",
            speed=30,
            font_path=font_path,
        )

    def _init_world(self):
        """Initialize world map and proximity detection state."""
        self.world = None
        self.near_door = None
        self.near_key = None
        self.near_locked_door = None
        self.door_locked_message = False
        self.door_locked_time = 0.0

        try:
            tmx_path = (
                Path(__file__).resolve().parent.parent
                / "assets"
                / "maps"
                / "Tiled_files"
                / "Dungeon1.tmx"
            )
            self.world = World(
                tmx_path,
                self.player,
                zoom=DEFAULT_CAMERA_ZOOM,
                default_layer=DEFAULT_LAYER,
            )
        except Exception as e:
            print(f"Warning: Could not load map : {e}")

        # Center player on map
        if self.world and self.world.map_layer:
            self.player.position.x = (27 * 16) / 2
            self.player.position.y = (37 * 16) / 2
        else:
            self.player.position.x = SCREEN_WIDTH / 2
            self.player.position.y = SCREEN_HEIGHT / 2

    def _init_camera(self):
        """Initialize camera position and zoom transition settings."""
        self.spawn_x = self.player.position.x
        self.spawn_y = self.player.position.y
        self.camera.x = self.player.position.x
        self.camera.y = self.player.position.y
        self.target_zoom = DEFAULT_CAMERA_ZOOM
        self.zoom_transition_speed = CAMERA_ZOOM_TRANSITION_SPEED

    def player_has_key(self, key_id):
        """Check if the player has a specific key in their inventory."""
        for item in self.inventory_bar.items:
            if item == key_id:
                return True
        return False

    def _play_sound(self, sound_key):
        """Play a sound effect safely, handling both SoundManager and dict types."""
        if hasattr(self.sounds, "play_effect"):
            self.sounds.play_effect(sound_key)
        else:
            sound = self.sounds.get(sound_key)
            if sound:
                sound.play()

    def _handle_pause(self, event):
        """Handle pause key press."""
        if event.key == pygame.K_ESCAPE:
            self.paused = not self.paused
            if self.paused:
                for k in self.keys_pressed:
                    self.keys_pressed[k] = False
            return True
        return False

    def _handle_interaction(self, event):
        """Handle interaction (E key) with doors and keys."""
        if event.key == pygame.K_e:
            if self.near_door:
                required_key = self.near_door.get("required_key_id")
                if required_key and not self.player_has_key(required_key):
                    self.door_locked_message = True
                    self.door_locked_time = 0.0
                else:
                    self.world.open_door(self.near_door)
                    self._play_sound("door_open")
            elif self.near_key:
                self.world.collect_key(self.near_key)
                self.inventory_bar.set_slot(0, self.near_key["id"])
                self._play_sound("pickup")
            elif self.near_locked_door:
                required_key = self.near_locked_door.get("required_key_id")
                if required_key and not self.player_has_key(required_key):
                    self.door_locked_message = True
                    self.door_locked_time = 0.0
                else:
                    self.world.unlock_door(self.near_locked_door)
                    self._play_sound("door_open")
            return True
        return False

    def _handle_movement_input(self, event, is_keydown):
        """Handle movement key input (WASD/arrows)."""
        key = event.key
        if key in (pygame.K_UP, pygame.K_w):
            self.keys_pressed["up"] = is_keydown
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.keys_pressed["down"] = is_keydown
        elif key in (pygame.K_LEFT, pygame.K_a):
            self.keys_pressed["left"] = is_keydown
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.keys_pressed["right"] = is_keydown

    def handle_event(self, event):
        """Handle input events."""
        if self.loading:
            return None

        if self.game_over:
            self.game_over_menu.handle_event(event)
            return None

        self.task_panel.handle_event(event)
        self.inventory_bar.handle_event(event)

        if self.dialogue.active:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.dialogue.skip_or_dismiss()
            return None

        if event.type == pygame.KEYDOWN:
            if self._handle_pause(event):
                return None

            if self.paused:
                self.pause_menu.handle_event(event)
                return None

            if self._handle_interaction(event):
                return None

            self._handle_movement_input(event, is_keydown=True)

        elif event.type == pygame.KEYUP:
            self._handle_movement_input(event, is_keydown=False)

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
        self.near_key = None
        self.near_locked_door = None
        self.dialogue.active = False
        self.game_over_menu.reset()
        self.inventory_bar = InventoryBar(self.credit_font)
        self.door_locked_message = False

        if self.world:
            self.world.reset_doors()
            self.world.reset_keys()
            self.world.reset_locked_doors()

    def update(self, mouse_pos):
        """Update game state."""
        self.time_seconds = pygame.time.get_ticks() / 1000.0
        dt = self._clock.tick(FPS) / 1000.0

        # Update UI elements
        self.task_panel.update(dt)
        self.inventory_bar.update(dt)

        # Update timers
        self._update_timers(dt)

        # Check for early returns (loading, dialogue, game over, pause)
        if self._check_loading_screen(dt):
            return

        if self._check_dialogue(dt):
            return

        if self._check_game_over(dt, mouse_pos):
            return

        if self._check_pause(dt, mouse_pos):
            return

        # Update player movement and state
        self._update_player_movement(dt)

        # Update player collision and hazards
        self._update_player_collision(dt)

        # Update world state
        self._update_world_state(dt)

    def _update_timers(self, dt):
        """Update door locked message timer."""
        if self.door_locked_message:
            self.door_locked_time += dt
            if self.door_locked_time >= DOOR_LOCKED_MESSAGE_DURATION:
                self.door_locked_message = False

    def _check_loading_screen(self, dt):
        """Check and handle loading screen. Returns True if still loading."""
        if self.loading:
            if not self.loading_ready:
                return True
            self.loading_time += dt
            if self.loading_time >= self.loading_duration:
                self.loading = False
                if not self.first_dialogue_shown:
                    self.dialogue.start()
            return True
        return False

    def _check_dialogue(self, dt):
        """Check and handle dialogue. Returns True if dialogue is active."""
        if self.dialogue.active:
            self.dialogue.update(dt)
            if self.dialogue.is_finished():
                self.first_dialogue_shown = True
            elif not self.dialogue.closing:
                return True
        return False

    def _check_game_over(self, dt, mouse_pos):
        """Check and handle game over state. Returns True if game over."""
        if self.game_over:
            self.game_over_menu.update(dt, mouse_pos)
            action = self.game_over_menu.consume_action()
            if action == "Retry":
                self._reset_player()
            elif action == "Main Menu":
                self.restart_on_enter = True
                self.pause_pending_scene = SCENE_MENU
            return True
        return False

    def _check_pause(self, dt, mouse_pos):
        """Check and handle pause state. Returns True if paused."""
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
            return True
        return False

    def _update_player_movement(self, dt):
        """Update player movement and facing direction."""
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

        # Update player facing direction
        self.player.update_facing(dx)

        # Update player state based on movement
        if moving:
            if self.player.state not in ("run", "hit", "death"):
                self.player.set_state("run")
        else:
            if self.player.state not in ("idle", "hit", "death"):
                self.player.set_state("idle")

        # Store movement values for collision detection
        self._current_dx = dx
        self._current_dy = dy

    def _update_player_collision(self, dt):
        """Update player collision detection and handle hazards."""
        dx = self._current_dx
        dy = self._current_dy

        # Store old position for collision reversion
        old_x = self.player.position.x
        old_y = self.player.position.y

        # Move and check X axis only
        self.player.position.x += dx * PLAYER_MOVE_SPEED * dt
        player_rect = pygame.Rect(
            self.player.position.x - PLAYER_COLLISION_OFFSET_X,
            self.player.position.y + PLAYER_COLLISION_OFFSET_Y,
            PLAYER_COLLISION_WIDTH,
            PLAYER_COLLISION_HEIGHT,
        )
        if self.world:
            self.world.check_collision_x(player_rect, old_x, self.player)

        # Move and check Y axis only
        self.player.position.y += dy * PLAYER_MOVE_SPEED * dt
        player_rect = pygame.Rect(
            self.player.position.x - PLAYER_COLLISION_OFFSET_X,
            self.player.position.y + PLAYER_COLLISION_OFFSET_Y,
            PLAYER_COLLISION_WIDTH,
            PLAYER_COLLISION_HEIGHT,
        )
        if self.world:
            self.world.check_collision_y(player_rect, old_y, self.player)

        # Hazard detection
        if self.world and self.player.damage_cooldown <= 0:
            if self.world.check_hazard(player_rect, self.player):
                self._play_sound("hit")
                if self.player.is_dead:
                    self._play_sound("death")
                    self.game_over = True
                    self.paused = False
                    self.keys_pressed = {
                        "up": False,
                        "down": False,
                        "left": False,
                        "right": False,
                    }
                    self.player.set_state("death")

        # Clamp player to map bounds
        if self.world and self.world.map_width > 0 and self.world.map_height > 0:
            self.player.position.x = max(
                0, min(self.world.map_width, self.player.position.x)
            )
            self.player.position.y = max(
                0, min(self.world.map_height, self.player.position.y)
            )

        # Update player sprite and animation
        self.player.update(dt)

    def _update_world_state(self, dt):
        """Update world state: door/key proximity, player layer, and camera."""
        # Check proximity to interactive objects
        self.near_door = self.world.get_nearby_door(self.player) if self.world else None
        self.near_key = self.world.get_nearby_key(self.player) if self.world else None
        self.near_locked_door = (
            self.world.get_nearby_locked_door(self.player) if self.world else None
        )

        # Update player layer based on above zones
        if self.world:
            self.world.update_player_layer(self.player)

        # Update camera position
        self.camera.update(
            self.player,
            dt,
            self.world.map_width if self.world else 0,
            self.world.map_height if self.world else 0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            self.world.map_layer.zoom if self.world and self.world.map_layer else 1.0,
        )

        # Handle zoom transition
        if (
            self.world
            and self.world.map_layer
            and self.world.map_layer.zoom > self.target_zoom
        ):
            self.world.map_layer.zoom = max(
                self.target_zoom,
                self.world.map_layer.zoom - self.zoom_transition_speed * dt,
            )

    def render(self, screen):
        """Render the game scene."""

        # Loading screen
        if self.loading:
            draw_loading_screen(
                screen,
                self.loading_time,
                self.menu_font,
                self.credit_font,
                self.loading_hints,
            )
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

        # Key prompt
        if self.near_key:
            draw_key_prompt(screen, self.player, self.camera, zoom, self.credit_font)

        # Locked door prompt
        if self.near_locked_door:
            draw_door_prompt(screen, self.player, self.camera, zoom, self.credit_font)

        # Locked door message
        if self.door_locked_message:
            draw_locked_door_prompt(
                screen, self.player, self.camera, zoom, self.credit_font
            )

        # Debug
        if self.world:
            draw_debug_collision(
                screen,
                self.world.collision_rects + self.world.hazard_rects,
                self.camera,
                zoom,
            )
        draw_debug_coords(screen, self.player, self.credit_font)

        # Task panel
        self.task_panel.render(screen, self.time_seconds)

        # Inventory bar
        self.inventory_bar.render(screen)

        # Pause overlay
        if self.paused:
            self.pause_menu.render(screen, self.time_seconds)

        # Game over overlay
        if self.game_over:
            self.game_over_menu.render(screen, self.time_seconds)

        # Dialogue
        self.dialogue.render(screen, self.time_seconds)
