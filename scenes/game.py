"""
Placeholder game scene for the RPG game.
"""
import math
from pydantic import InstanceOf
import pygame
from pathlib import Path
from globals import SCREEN_WIDTH, SCREEN_HEIGHT, SCENE_MENU, SCENE_SETTINGS, FPS, FONT_ANTIALIAS, BLACK, BACKGROUND, BLUE, GRAY, WHITE
import scenes
from sprite_sheet import SpriteSheet
from vignette import create_vignette
from camera import Camera
from player import Player
import pytmx
import pyscroll

from .aesthetic import (
    SharedBackground,
    draw_pulsing_title,
    draw_subtitle_centered,
    draw_footer_hint,
    safe_scale_surface,
)
from .dialogue import DialogueBox

class GameScene:
    """Game scene."""

    MOVE_SPEED = 100  # pixels per second

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

        # Pause menu state
        self.paused = False
        self.pause_items = ["Resume", "Settings", "Main Menu"]
        self.pause_selected = 0
        self.pause_item_rects = []
        self.pause_hover_scale = [1.0 for _ in self.pause_items]
        self.pause_selection_y = 0
        self.pause_activation_item = None
        self.pause_activation_progress = 0.0
        self.pause_activation_duration = 0.18
        self.pause_pending_scene = None
        self.pause_last_selected = self.pause_selected

        #load tmx file
        self.map_layer = None
        self.map_width = 0
        self.map_height = 0
        try:
            tmx_path = Path(__file__).resolve().parent.parent / "assets" / "maps" / "Tiled_files" / "Dungeon1.tmx"

            tmx_data = pytmx.load_pygame(
                str(tmx_path),
                pixelalpha=True
            )

            map_data = pyscroll.data.TiledMapData(tmx_data)
            self.map_layer = pyscroll.orthographic.BufferedRenderer(
                map_data,
                (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
            self.map_layer.zoom = 3.5
            self.map_width = tmx_data.width * tmx_data.tilewidth
            self.map_height = tmx_data.height * tmx_data.tileheight

            self.collision_rects = []

            # Find walls above layer index
            self.above_layer_index = 0
            for i, layer in enumerate(tmx_data.layers):
                if layer.name == "Walls":
                    self.above_layer_index = i + 1
                    break
            
            print(f"above_layer_index: {self.above_layer_index}")
            
            # create pyscroll group
            self.group = pyscroll.PyscrollGroup(
                map_layer=self.map_layer,
                default_layer=8 
            )
            self.group.add((self.player))

            # Collisions
            for obj in tmx_data.objects:
                if obj.x is not None:
                    try:
                        self.collision_rects.append(
                            pygame.Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height))
                    )
                    except Exception:
                        pass
        except Exception as e:
            print(f"Warning: Could not load map: {e}")

        #check map width and height
        print(f"map_width={self.map_width} map_height={self.map_height} tile_width={tmx_data.tilewidth} tile_height={tmx_data.tileheight}") 

        #check map layers
        for layer in tmx_data.layers:
            print(f"layer: {layer.name}, type: {type(layer).__name__}")
        
        for obj in tmx_data.objects:
            print(f"object: {obj.name}, type: {type(obj.type)}, x: {obj.x}, y: {obj.y}")

        # Center player on map
        if self.map_layer:
            self.player.position.x = (27 * 16) / 2
            self.player.position.y = (37 * 16) / 2
            self.camera.x = self.player.position.x
            self.camera.y = self.player.position.y
        else:
            self.player.position.x = SCREEN_WIDTH / 2
            self.player.position.y = SCREEN_HEIGHT / 2

        # Camera zoom transition (starts zoomed in, pulls back to normal)
        self.target_zoom = 3.0
        self.zoom_transition_speed = 1.2  # zoom units per second

        # Vignette effect
        self.vignette = create_vignette(SCREEN_WIDTH, SCREEN_HEIGHT, strength=120)

    def handle_event(self, event):
        """Handle input events."""
        if self.loading:
            return None
        if self.dialogue.active:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.dialogue.skip_or_dismiss()
            return None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused
                # Clear movement keys when pausing
                if self.paused:
                    for k in self.keys_pressed:
                        self.keys_pressed[k] = False
                return None

            if self.paused:
                if event.key == pygame.K_UP:
                    self.pause_selected = (self.pause_selected - 1) % len(self.pause_items)
                elif event.key == pygame.K_DOWN:
                    self.pause_selected = (self.pause_selected + 1) % len(self.pause_items)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._start_pause_activate()
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
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.pause_item_rects):
                if rect.collidepoint(mouse_pos):
                    self.pause_selected = i
                    self._start_pause_activate()
                    break
        return None

    def _start_pause_activate(self):
        """Play a short confirm animation before pause menu action."""
        if self.pause_activation_item is None:
            confirm_sound = self.sounds.get("confirm")
            if confirm_sound:
                confirm_sound.play()
            self.pause_activation_item = self.pause_selected
            self.pause_activation_progress = 0.0

    def _get_pause_action(self):
        """Get the action for the selected pause item."""
        item = self.pause_items[self.pause_selected]
        if item == "Resume":
            self.paused = False
            return None
        if item == "Settings":
            return SCENE_SETTINGS
        if item == "Main Menu":
            self.paused = False
            return SCENE_MENU
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

        if self.map_layer:
            self.map_layer.center((self.player.position.x, self.player.position.y))
            self.camera.x = self.player.position.x
            self.camera.y = self.player.position.y

    def update(self, mouse_pos):
        """Update game state."""
        self.time_seconds = pygame.time.get_ticks() / 1000.0
        dt = self._clock.tick(FPS) / 1000.0

        # Loading screen timer
        if self.loading:
            if not self.loading_ready:
                return
            self.loading_time += dt
            if self.loading_time >= self.loading_duration:
                self.loading = False
                if not self.first_dialogue_shown:
                    self.dialogue.start()

        # Update dialogue (typewriter + close animation); block movement while open
        if self.dialogue.active:
            self.dialogue.update(dt)
            if self.dialogue.is_finished():
                self.first_dialogue_shown = True
            elif not self.dialogue.closing:
                return

        # Check for mouse hover on pause items
        if self.paused:
            for i, rect in enumerate(self.pause_item_rects):
                if rect.collidepoint(mouse_pos):
                    self.pause_selected = i
                    break
            if self.pause_selected != self.pause_last_selected:
                hover_sound = self.sounds.get("button_hover")
                if hover_sound:
                    hover_sound.play()
                self.pause_last_selected = self.pause_selected

            # Update hover scales
            for i in range(len(self.pause_items)):
                activation_bonus = 0.0
                if self.pause_activation_item == i:
                    activation_bonus = 0.10 * (1.0 - self.pause_activation_progress)
                if i == self.pause_selected:
                    self.pause_hover_scale[i] = min(self.pause_hover_scale[i] + 0.05, 1.10 + activation_bonus)
                else:
                    self.pause_hover_scale[i] = max(self.pause_hover_scale[i] - 0.05, 1.0)

            # Smoothly move selection box
            target_y = 320 + self.pause_selected * 80
            if self.pause_selection_y == 0:
                self.pause_selection_y = target_y
            self.pause_selection_y += (target_y - self.pause_selection_y) * 0.20

            if self.pause_activation_item is not None:
                self.pause_activation_progress += dt / self.pause_activation_duration
                if self.pause_activation_progress >= 1.0:
                    self.pause_pending_scene = self._get_pause_action()
                    self.pause_activation_item = None
                    self.pause_activation_progress = 0.0

        # Only update player movement / camera when not paused and not in dialogue
        if not self.paused and not self.dialogue.active:
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

            old_x = self.player.position.x
            old_y = self.player.position.y

            if moving:
                self.player.move(dx, dy, self.MOVE_SPEED * dt)
                if self.player.state != "run":
                    self.player.set_state("run")
            else:
                if self.player.state != "idle":
                    self.player.set_state("idle")

            # Collision detection
            player_rect = pygame.Rect(
                self.player.position.x - 4,
                self.player.position.y + 4,
                8, 4
            )

            for rect in self.collision_rects:
                if player_rect.colliderect(rect):
                    self.player.position.x = old_x
                    self.player.position.y = old_y

            # Clamp player to camera viewport so they never walk past where
            # the camera can follow (prevents drifting off-screen at edges)
            if self.map_width > 0 and self.map_height > 0:
                self.player.position.x = max(0, min(self.map_width, self.player.position.x))
                self.player.position.y = max(0, min(self.map_height, self.player.position.y))

            self.player.update(dt)
            self.camera.update(
                self.player,
                dt,
                self.map_width,
                self.map_height,
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
                self.map_layer.zoom if self.map_layer else 1.0
            )

        # Zoom transition (starts zoomed in, pulls back to normal)
        if self.map_layer and self.map_layer.zoom > self.target_zoom:
            self.map_layer.zoom = max(self.target_zoom, self.map_layer.zoom - self.zoom_transition_speed * dt)

    def _safe_scale_text(self, surface, scale_factor):
        """Scale text surfaces safely."""
        return safe_scale_surface(surface, scale_factor)

    def _draw_pause_title(self, screen, center_xy, pulse):
        """Draw paused title with blue shimmer."""
        title_str = "PAUSED"
        shimmer = 0.5 + 0.5 * math.sin(self.time_seconds * 2.8)
        main_color = (
            int(100 + 26 * shimmer),
            int(160 + 33 * shimmer),
            int(220 + 25 * shimmer),
        )
        shadow_deep = (14, 10, 32)
        rim = (72, 58, 120)

        base = self.title_font.render(title_str, FONT_ANTIALIAS, WHITE)
        w, h = base.get_width(), base.get_height()
        pad = 10
        composite = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
        ox, oy = pad, pad

        for d in (5, 4, 3, 2, 1):
            layer = self.title_font.render(title_str, FONT_ANTIALIAS, shadow_deep)
            composite.blit(layer, (ox + d, oy + d))

        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
            layer = self.title_font.render(title_str, FONT_ANTIALIAS, rim)
            composite.blit(layer, (ox + dx, oy + dy))

        composite.blit(
            self.title_font.render(title_str, FONT_ANTIALIAS, main_color),
            (ox, oy),
        )

        scaled = self._safe_scale_text(composite, pulse)
        rect = scaled.get_rect(center=center_xy)
        screen.blit(scaled, rect)

    def render(self, screen):
        """Render the game scene."""

        # Loading screen — cover the game until map is fully buffered
        if self.loading:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            screen.blit(overlay, (0, 0))

            pulse = 1.0 + 0.08 * math.sin(self.loading_time * 10)
            loading_text = self.menu_font.render("Loading...", FONT_ANTIALIAS, BLUE)
            scaled = self._safe_scale_text(loading_text, pulse)
            rect = scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(scaled, rect)

            # Rotating hint at bottom
            hint_index = int(self.loading_time * 2) % len(self.loading_hints)
            hint_text = self.credit_font.render(self.loading_hints[hint_index], False, GRAY)
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            screen.blit(hint_text, hint_rect)
            return

        if self.map_layer:
            self.group.center(pygame.math.Vector2(self.camera.x, self.camera.y))
            self.group.draw(screen)
        zoom = self.map_layer.zoom if self.map_width else 1.0

        # Draw health bar above player
        screen_x = (self.player.position.x - self.camera.x) * zoom + SCREEN_WIDTH / 2
        screen_y = (self.player.position.y - self.camera.y) * zoom + SCREEN_HEIGHT / 2

        bar_width = 40
        bar_height = 10
        bar_x = int(screen_x - bar_width / 2)
        bar_y = int(screen_y - 40) # so that it is above the player

        # Background
        pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        # Health fill
        fill_width = int(bar_width * (self.player.health / self.player.max_health))
        pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, fill_width, bar_height))
        # Border
        pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 1)

        # debugging tiles
        for rect in self.collision_rects:
            screen_x = (rect.x - self.camera.x) * zoom + SCREEN_WIDTH / 2 
            screen_y = (rect.y - self.camera.y) * zoom + SCREEN_HEIGHT / 2
            debug_rect = pygame.Rect(screen_x, screen_y, rect.width * zoom, rect.height * zoom)
            pygame.draw.rect(screen, (255, 0, 0), debug_rect, 1)

        # PAUSE OVERLAY 
        if self.paused:
            # Darken the game behind
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            # Pause title with blue shimmer
            pulse = 1.0 + (math.sin(self.time_seconds * 2.2) * 0.02)
            self._draw_pause_title(screen, (SCREEN_WIDTH // 2, 200), pulse)

            # Selection highlight box
            selection_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, int(self.pause_selection_y) - 8, 360, 60)
            box_surface = pygame.Surface((selection_rect.width, selection_rect.height), pygame.SRCALPHA)
            box_alpha = 22
            if self.pause_activation_item == self.pause_selected:
                box_alpha = 22 + int(70 * (1.0 - self.pause_activation_progress))
            box_surface.fill((255, 255, 255, box_alpha))
            screen.blit(box_surface, selection_rect.topleft)
            border_color = (130, 130, 130)
            if self.pause_activation_item == self.pause_selected:
                border_color = (220, 200, 120)
            pygame.draw.rect(screen, border_color, selection_rect, width=2, border_radius=8)

            # Pause menu items
            menu_start_x = SCREEN_WIDTH // 2 - 120
            menu_start_y = 320
            self.pause_item_rects = []
            for i, item in enumerate(self.pause_items):
                if i == self.pause_selected:
                    arrow_text = self.menu_font.render("> ", FONT_ANTIALIAS, BLUE)
                    item_text = self.menu_font.render(item, FONT_ANTIALIAS, WHITE)
                    item_pos = (menu_start_x, menu_start_y + i * 80)
                    if self.pause_hover_scale[i] != 1.0:
                        arrow_text = self._safe_scale_text(arrow_text, self.pause_hover_scale[i])
                        item_text = self._safe_scale_text(item_text, self.pause_hover_scale[i])
                    arrow_rect = arrow_text.get_rect(topleft=item_pos)
                    item_rect = item_text.get_rect(topleft=(arrow_rect.right, item_pos[1]))
                    self.pause_item_rects.append(arrow_rect.union(item_rect))
                    screen.blit(arrow_text, arrow_rect)
                    screen.blit(item_text, item_rect)
                else:
                    color = GRAY
                    text = self.menu_font.render(item, FONT_ANTIALIAS, color)
                    if self.pause_hover_scale[i] != 1.0:
                        text = self._safe_scale_text(text, self.pause_hover_scale[i])
                    item_pos = (menu_start_x, menu_start_y + i * 80)
                    text_rect = text.get_rect(topleft=item_pos)
                    self.pause_item_rects.append(text_rect)
                    screen.blit(text, text_rect)
            
        # Vignette effect
        #screen.blit(self.vignette, (0, 0))

        # First-time dialogue overlay
        self.dialogue.render(screen, self.time_seconds)

        # Debug: player coordinates (drawn last so it stays on top)
        coord_text = self.credit_font.render(
            f"x:{self.player.position.x:.1f}  y:{self.player.position.y:.1f}",
            FONT_ANTIALIAS,
            (255, 255, 0),
        )
        screen.blit(coord_text, (10, 90))
