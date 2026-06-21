"""
Game scene for the RPG game.
"""

import math
import random
from pathlib import Path

import pygame

from camera import Camera
from game_constants import *
from globals import (
    FPS,
    SCENE_MENU,
    SCENE_QUIT,
    SCENE_SETTINGS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    get_pixel_font_path,
)
from player import Player
from enemy import BossProjectile, BossSlimeEnemy, SlimeEnemy

from .dialogue import DialogueBox
from .debug_menu import DebugMenu
from .game_over import GameOverMenu
from .hud import (
    draw_attack_cooldown,
    draw_boss_health_bar,
    draw_debug_collision,
    draw_door_prompt,
    draw_exit_prompt,
    draw_key_prompt,
    draw_locked_door_prompt,
    draw_objective_arrow,
    draw_player_health_bar,
)
from .inventory_bar import InventoryBar
from .loading_screen import draw_loading_screen
from .pause_menu import PauseMenu
from .task_panel import TaskPanel
from .world import World


class PlayerFireball:
    """Fireball shot by the player toward the mouse."""

    def __init__(self, x, y, vx, vy):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.radius = 5
        self.damage = 35
        self.lifetime = 2.2
        self.age = 0.0
        self.active = True

    def update(self, dt):
        """Move the fireball and expire it."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt
        if self.age >= self.lifetime:
            self.active = False

    def get_rect(self):
        """Return the fireball hitbox."""
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def render(self, screen, camera, zoom, time_seconds=0.0):
        """Draw the fireball directly on the screen."""
        screen_x = int((self.x - camera.x) * zoom + SCREEN_WIDTH / 2)
        screen_y = int((self.y - camera.y) * zoom + SCREEN_HEIGHT / 2)
        draw_radius = max(4, int(self.radius * zoom))

        pulse = 0.5 + 0.5 * math.sin(time_seconds * 16 + self.age * 12)
        flame = (
            245,
            min(255, int(95 + 70 * pulse)),
            30,
        )
        glow = (110, 30, 12)

        pygame.draw.circle(screen, glow, (screen_x, screen_y), draw_radius + 4)
        pygame.draw.circle(screen, flame, (screen_x, screen_y), draw_radius)
        pygame.draw.circle(
            screen,
            (255, 225, 120),
            (screen_x - draw_radius // 3, screen_y - draw_radius // 3),
            max(2, draw_radius // 3),
        )


class HealthPotion:
    """Health potion spawned from Tiled potion spawn zones."""

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.radius = 6
        self.heal_amount = 35
        self.active = True

    def get_rect(self):
        """Return pickup hitbox."""
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def render(self, screen, camera, zoom, time_seconds=0.0):
        """Draw a glowing golden health orb."""
        bob = math.sin(time_seconds * 4.0) * 3
        screen_x = int((self.x - camera.x) * zoom + SCREEN_WIDTH / 2)
        screen_y = int((self.y + bob - camera.y) * zoom + SCREEN_HEIGHT / 2)
        radius = max(5, int(self.radius * zoom))

        pulse = 0.5 + 0.5 * math.sin(time_seconds * 8.0)
        glow_radius = radius + int(7 + 4 * pulse)
        core = (
            255,
            min(255, int(205 + 35 * pulse)),
            min(255, int(70 + 35 * pulse)),
        )
        inner = (255, 245, 165)
        rim = (125, 80, 18)

        pygame.draw.circle(screen, rim, (screen_x, screen_y), glow_radius)
        pygame.draw.circle(screen, (205, 140, 30), (screen_x, screen_y), radius + 4)
        pygame.draw.circle(screen, core, (screen_x, screen_y), radius)
        pygame.draw.circle(
            screen,
            inner,
            (screen_x - radius // 3, screen_y - radius // 3),
            max(2, radius // 3),
        )


class GameScene:
    """Game scene."""

    def __init__(self, title_font, menu_font, credit_font, sounds=None):
        self._init_core_objects(title_font, menu_font, credit_font, sounds)
        self._init_ui_elements(title_font, menu_font, credit_font, sounds)
        self._init_loading_state()
        self._init_dialogue()
        self._init_world()
        self._init_camera()

        self.attack_effect = 0.0
        self.attack_duration = 0.3
        self.boss_projectiles = []
        self.boss_shot_timer = 0.0
        self.boss_burst_timer = 1.2
        self.fireballs = []
        self.active_health_potion = None
        self.health_potion_spawn_timer = 2.0

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
        self.debug_menu = DebugMenu(title_font, menu_font, credit_font)
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
        font_path = get_pixel_font_path()
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
        self.enemies = []
        self.boss_enemy = None
        self.current_map_path = DEFAULT_MAP_PATH
        self.near_door = None
        self.near_key = None
        self.near_locked_door = None
        self.near_boss_room_trigger = None
        self.near_exit_trigger = None
        self.exit_trigger_active = False
        self.boss_room_started = False
        self.show_boss_arrow = False
        self.door_locked_message = False
        self.door_locked_time = 0.0

        self._load_world(DEFAULT_MAP_PATH, player_spawn=((27 * 16) / 2, (37 * 16) / 2))

    def _load_world(self, map_path, player_spawn=None):
        """Load a TMX world and rebuild enemies for it."""
        try:
            tmx_path = (
                Path(__file__).resolve().parent.parent
                / map_path
            )
            self.world = World(
                tmx_path,
                self.player,
                zoom=DEFAULT_CAMERA_ZOOM,
                default_layer=DEFAULT_LAYER,
            )
            self.current_map_path = map_path
            self.enemies = []
            self.boss_enemy = None
            self.boss_projectiles = []
            self.boss_shot_timer = 0.0
            self.boss_burst_timer = 1.2
            self.fireballs = []
            self.active_health_potion = None
            self.health_potion_spawn_timer = random.uniform(2.0, 5.0)

            if self.world:
                for x, y in self.world.enemy_spawns:
                    slime = SlimeEnemy(x, y)
                    self.world.group.add(slime)
                    self.enemies.append(slime)

                if self.world.boss_spawn:
                    boss_x, boss_y = self.world.boss_spawn
                    self.boss_enemy = BossSlimeEnemy(boss_x, boss_y)
                    self.world.group.add(self.boss_enemy)
                    self.enemies.append(self.boss_enemy)
        except Exception as e:
            print(f"Warning: Could not load map : {e}")

        if player_spawn is None and self.world and self.world.player_spawn:
            player_spawn = self.world.player_spawn

        if player_spawn is None and self.world:
            player_spawn = (self.world.map_width / 2, self.world.map_height - 96)

        if self.world and self.world.map_layer:
            self.player.position.x = float(player_spawn[0])
            self.player.position.y = float(player_spawn[1])
            self.world.center(self.player.position.x, self.player.position.y)
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

    def player_has_item(self, item_id):
        """Check if the player has a specific inventory item."""
        for item in self.inventory_bar.items:
            if item == item_id:
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
                self.task_panel.set_task_done("Find a key")
                self.task_panel.add_task("Find the boss door")
                self.show_boss_arrow = True
                self._play_sound("pickup")
            elif self.near_locked_door:
                required_key = self.near_locked_door.get("required_key_id")
                if required_key and not self.player_has_key(required_key):
                    self.door_locked_message = True
                    self.door_locked_time = 0.0
                else:
                    self.world.unlock_door(self.near_locked_door)
                    self._play_sound("door_open")
            elif self.near_exit_trigger:
                self._handle_exit_trigger(self.near_exit_trigger)
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
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
            self.debug_menu.toggle()
            return None

        if self.debug_menu.active:
            self.debug_menu.handle_event(event)
            return None

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

            if event.key == pygame.K_f:
                self._do_attack()
                return None

            if event.key == pygame.K_r:
                self._shoot_fireball(pygame.mouse.get_pos())
                return None

            self._handle_movement_input(event, is_keydown=True)

        elif event.type == pygame.KEYUP:
            self._handle_movement_input(event, is_keydown=False)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and not self.paused:
            self._shoot_fireball(event.pos)
            return None

        elif event.type == pygame.MOUSEBUTTONDOWN and self.paused:
            self.pause_menu.handle_event(event)

        return None

    def _do_attack(self):
        if self.player.state in ("death",):
            return
        if self.player.attack(self.enemies, self.world.group if self.world else None):
            self.attack_effect = self.attack_duration
            self._play_sound("attack")
            if self.player.last_attack_hit:
                self._play_sound("attack_hit")

    def _shoot_fireball(self, mouse_pos):
        """Shoot a fireball toward the mouse."""
        if not self.player.can_shoot_fireball():
            return

        zoom = self._get_zoom()
        target_x = (mouse_pos[0] - SCREEN_WIDTH / 2) / zoom + self.camera.x
        target_y = (mouse_pos[1] - SCREEN_HEIGHT / 2) / zoom + self.camera.y

        dx = target_x - self.player.position.x
        dy = target_y - self.player.position.y
        length = max(1.0, math.hypot(dx, dy))
        speed = 230

        self.player.start_fireball_cooldown()
        self.player.update_facing(dx)
        self.fireballs.append(
            PlayerFireball(
                self.player.position.x,
                self.player.position.y,
                dx / length * speed,
                dy / length * speed,
            )
        )
        self._play_sound("attack")

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
        reset_map_path = self.current_map_path
        reset_spawn = (self.spawn_x, self.spawn_y)

        # reload the current map so enemies and boss health reset on retry
        self._load_world(reset_map_path, player_spawn=reset_spawn)

        self.player.position.x = self.spawn_x
        self.player.position.y = self.spawn_y
        self.player.health = self.player.max_health
        self.player.damage_cooldown = 0.0
        self.player.attack_cooldown = 0.0
        self.player.fireball_cooldown = 0.0
        self.player.time_since_last_damage = 0.0
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
        self.near_boss_room_trigger = None
        self.near_exit_trigger = None
        self.exit_trigger_active = False
        self.boss_room_started = reset_map_path == BOSS_MAP_PATH
        self.show_boss_arrow = False
        self.boss_projectiles = []
        self.boss_shot_timer = 0.0
        self.boss_burst_timer = 1.2
        self.fireballs = []
        self.active_health_potion = None
        self.health_potion_spawn_timer = 2.0
        self.dialogue.active = False
        self.game_over_menu.reset()
        self.inventory_bar = InventoryBar(self.credit_font)
        self.door_locked_message = False

        if self.world:
            self.world.reset_doors()
            self.world.reset_keys()
            self.world.reset_locked_doors()
            self.world.reset_boss_room_triggers()
            self.world.reset_exit_triggers()

    def update(self, mouse_pos):
        """Update game state."""
        self.time_seconds = pygame.time.get_ticks() / 1000.0
        dt = self._clock.tick(FPS) / 1000.0

        # Update UI elements
        self.task_panel.update(dt)
        self.inventory_bar.update(dt)
        self.debug_menu.update(dt, mouse_pos)

        if self._check_debug_menu():
            return

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

        if self.attack_effect > 0:  
            self.attack_effect = max(0.0, self.attack_effect - dt)

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

    def _check_debug_menu(self):
        """Handle debug actions. Returns True if debug menu is open."""
        action = self.debug_menu.consume_action()
        if action == "Teleport to Boss Room":
            self._debug_teleport_to_boss_room()
        elif action == "Close":
            self.debug_menu.close()

        return self.debug_menu.active

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
            elif action == "Quit":
                self.paused = False
                self.pause_pending_scene = SCENE_QUIT
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

        # Update enemy events
        for enemy in self.enemies[:]:
            enemy.update(
                dt,
                self.player.position,
                self.world.get_collision_rects() if self.world else [],
            )
            enemy.check_contact_damage(self.player)
            if enemy.is_dead:
                if enemy is self.boss_enemy:
                    self._handle_boss_defeated()
                self.enemies.remove(enemy)
                self.world.group.remove(enemy)

        self._update_boss_projectiles(dt)
        self._update_fireballs(dt)
        self._update_health_potion(dt)

        # Check if slime killed the player
        if self.player.is_dead and not self.game_over:
            self.game_over = True
            self.paused = False
            self.keys_pressed = {"up": False, "down": False, "left": False, "right": False}
            self.player.set_state("death")

    def _update_boss_projectiles(self, dt):
        """Update boss projectile patterns and player hits."""
        if not self.boss_enemy or self.boss_enemy.is_dead:
            self.boss_projectiles = []
            return

        self.boss_shot_timer -= dt
        self.boss_burst_timer -= dt

        if self.boss_shot_timer <= 0:
            self._spawn_aimed_boss_projectile()
            self.boss_shot_timer = 0.75

        if self.boss_burst_timer <= 0:
            self._spawn_boss_burst()
            self.boss_burst_timer = 2.4

        player_rect = pygame.Rect(
            self.player.position.x - PLAYER_COLLISION_OFFSET_X,
            self.player.position.y + PLAYER_COLLISION_OFFSET_Y,
            PLAYER_COLLISION_WIDTH,
            PLAYER_COLLISION_HEIGHT,
        ).inflate(8, 8)

        for projectile in self.boss_projectiles[:]:
            projectile.update(dt)

            if self.world and (
                projectile.x < -32
                or projectile.y < -32
                or projectile.x > self.world.map_width + 32
                or projectile.y > self.world.map_height + 32
            ):
                projectile.active = False

            if projectile.active and projectile.get_rect().colliderect(player_rect):
                if self.player.damage_cooldown <= 0:
                    self.player.take_damage(projectile.damage)
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
                projectile.active = False

            if not projectile.active:
                self.boss_projectiles.remove(projectile)

    def _spawn_aimed_boss_projectile(self):
        """Shoot one projectile toward the player's current position."""
        dx = self.player.position.x - self.boss_enemy.position.x
        dy = self.player.position.y - self.boss_enemy.position.y
        length = max(1.0, (dx * dx + dy * dy) ** 0.5)
        speed = 115
        self.boss_projectiles.append(
            BossProjectile(
                self.boss_enemy.position.x,
                self.boss_enemy.position.y,
                dx / length * speed,
                dy / length * speed,
                radius=4,
                damage=10,
            )
        )

    def _spawn_boss_burst(self):
        """Shoot a rotating ring of projectiles from the boss."""
        amount = 10
        speed = 80
        offset = self.time_seconds * 0.8

        for i in range(amount):
            angle = offset + (i / amount) * 6.28318530718
            self.boss_projectiles.append(
                BossProjectile(
                    self.boss_enemy.position.x,
                    self.boss_enemy.position.y,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    radius=4,
                    damage=8,
                )
            )

    def _update_fireballs(self, dt):
        """Move player fireballs and damage enemies."""
        for fireball in self.fireballs[:]:
            fireball.update(dt)

            if self.world and (
                fireball.x < -32
                or fireball.y < -32
                or fireball.x > self.world.map_width + 32
                or fireball.y > self.world.map_height + 32
            ):
                fireball.active = False

            if (
                fireball.active
                and self.world
                and self.current_map_path != BOSS_MAP_PATH
            ):
                for rect in self.world.get_collision_rects():
                    if fireball.get_rect().colliderect(rect):
                        fireball.active = False
                        break

            if fireball.active:
                for enemy in self.enemies[:]:
                    if enemy.is_dead:
                        continue
                    enemy_rect = (
                        enemy.get_hit_rect()
                        if hasattr(enemy, "get_hit_rect")
                        else pygame.Rect(enemy.position.x - 8, enemy.position.y - 8, 16, 16)
                    )
                    if fireball.get_rect().colliderect(enemy_rect):
                        enemy.take_damage(fireball.damage)
                        self._play_sound("attack_hit")
                        fireball.active = False
                        break

            if not fireball.active:
                self.fireballs.remove(fireball)

    def _update_health_potion(self, dt):
        """Spawn and collect one health potion at a time."""
        if not self.world or not self.world.health_potion_spawns:
            self.active_health_potion = None
            return

        if self.active_health_potion:
            player_rect = pygame.Rect(
                self.player.position.x - PLAYER_COLLISION_OFFSET_X,
                self.player.position.y + PLAYER_COLLISION_OFFSET_Y,
                PLAYER_COLLISION_WIDTH,
                PLAYER_COLLISION_HEIGHT,
            ).inflate(14, 14)

            if player_rect.colliderect(self.active_health_potion.get_rect()):
                if self.player.health < self.player.max_health:
                    self.player.heal(self.active_health_potion.heal_amount)
                    self._play_sound("pickup")
                    self.active_health_potion = None
                    self.health_potion_spawn_timer = random.uniform(6.0, 11.0)
            return

        self.health_potion_spawn_timer -= dt
        if self.health_potion_spawn_timer <= 0:
            spawn_rect = random.choice(self.world.health_potion_spawns)
            if spawn_rect.width > 0 and spawn_rect.height > 0:
                x = random.uniform(spawn_rect.left, spawn_rect.right)
                y = random.uniform(spawn_rect.top, spawn_rect.bottom)
            else:
                x, y = spawn_rect.center

            self.active_health_potion = HealthPotion(x, y)

    def _handle_boss_defeated(self):
        """Reward the player after defeating the boss."""
        self.task_panel.set_task_done("Defeat the boss")
        self.task_panel.add_task("Escape the dungeon")
        self.inventory_bar.set_slot(1, "magic_rune")
        self.boss_projectiles = []
        self.fireballs = []
        self.boss_enemy = None
        self.boss_room_started = False
        self._play_sound("pickup")

    def _update_world_state(self, dt):
        """Update world state: door/key proximity, player layer, and camera."""
        # Check proximity to interactive objects
        self.near_door = self.world.get_nearby_door(self.player) if self.world else None
        self.near_key = self.world.get_nearby_key(self.player) if self.world else None
        self.near_locked_door = (
            self.world.get_nearby_locked_door(self.player) if self.world else None
        )
        self.near_boss_room_trigger = (
            self.world.get_boss_room_trigger(self.player) if self.world else None
        )
        self.near_exit_trigger = (
            self.world.get_exit_trigger(self.player) if self.world else None
        )

        if self.near_boss_room_trigger and not self.boss_room_started:
            self._handle_boss_room_trigger(self.near_boss_room_trigger)

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

    def _handle_boss_room_trigger(self, trigger):
        """Enter the boss room if the player has the required key."""
        required_key = trigger.get("required_key_id")
        if required_key and not self.player_has_key(required_key):
            self.door_locked_message = True
            self.door_locked_time = 0.0
            return

        self._enter_boss_room(trigger)

    def _debug_teleport_to_boss_room(self):
        """Debug shortcut for jumping straight to the boss room."""
        self.debug_menu.close()
        self.loading = False
        self.paused = False
        self.game_over = False
        self.dialogue.active = False
        self.keys_pressed = {"up": False, "down": False, "left": False, "right": False}

        self.boss_room_started = True
        self.show_boss_arrow = False
        self.door_locked_message = False
        self.task_panel.add_task("Defeat the boss")

        self._load_world(BOSS_MAP_PATH)
        self.spawn_x = self.player.position.x
        self.spawn_y = self.player.position.y
        self.camera.x = self.player.position.x
        self.camera.y = self.player.position.y
        self.player.update(0)

        if self.world and self.world.map_layer:
            self.world.center(self.player.position.x, self.player.position.y)

    def _enter_boss_room(self, trigger):
        """Start the boss room encounter."""
        trigger["used"] = True
        self.boss_room_started = True
        self.show_boss_arrow = False
        self.door_locked_message = False
        self.task_panel.set_task_done("Find the boss door")
        self.task_panel.add_task("Defeat the boss")

        target_x = trigger.get("target_x")
        target_y = trigger.get("target_y")
        player_spawn = None
        if target_x is not None and target_y is not None:
            player_spawn = (float(target_x), float(target_y))

        self._load_world(BOSS_MAP_PATH, player_spawn=player_spawn)
        self.spawn_x = self.player.position.x
        self.spawn_y = self.player.position.y
        self.camera.x = self.player.position.x
        self.camera.y = self.player.position.y
        self.player.update(0)

        if self.world and self.world.map_layer:
            self.world.center(self.player.position.x, self.player.position.y)

    def _handle_exit_trigger(self, trigger):
        """Handle exit trigger gate based on boss reward item."""
        required_item = trigger.get("required_item", "magic_rune")
        if required_item and not self.player_has_item(required_item):
            self.dialogue.set_text_and_start(
                trigger.get("message", "You need to beat the boss first.")
            )
            return

        self._exit_dungeon(trigger)

    def _exit_dungeon(self, trigger):
        """Placeholder for leaving the dungeon after the boss reward."""
        trigger["used"] = True
        self.dialogue.set_text_and_start("The rune opens the way forward.")

    def render(self, screen):
        """Render the game scene."""
        if self.loading:
            self._render_loading(screen)
            return

        zoom = self._get_zoom()

        self._render_world(screen)
        self._render_effects(screen, zoom)
        self._render_hud(screen)
        self._render_prompts(screen, zoom)
        self._render_debug(screen, zoom)
        self._render_ui(screen)
        self._render_overlays(screen)
        self._render_enemy_health_bars(screen, zoom)

    def _render_loading(self, screen):
        """Render the loading screen."""
        draw_loading_screen(
            screen,
            self.loading_time,
            self.menu_font,
            self.credit_font,
            self.loading_hints,
        )

    def _get_zoom(self):
        """Get the current map zoom."""
        if self.world and self.world.map_layer:
            return self.world.map_layer.zoom
        return 1.0

    def _render_world(self, screen):
        """Render the map and sprites."""
        if self.world:
            self.world.draw(screen, self.camera.x, self.camera.y)

    def _render_hud(self, screen):
        """Render player HUD elements."""
        draw_player_health_bar(screen, self.player, self.credit_font, self.time_seconds)
        draw_attack_cooldown(screen, self.player, self.credit_font, self.time_seconds)
        draw_boss_health_bar(
            screen,
            self.boss_enemy,
            self.credit_font,
            self.time_seconds,
        )

    def _render_effects(self, screen, zoom):
        """Render gameplay effects."""
        if self.active_health_potion:
            self.active_health_potion.render(
                screen,
                self.camera,
                zoom,
                self.time_seconds,
            )

        for fireball in self.fireballs:
            fireball.render(screen, self.camera, zoom, self.time_seconds)

        for projectile in self.boss_projectiles:
            projectile.render(screen, self.camera, zoom, self.time_seconds)

        self.player.render_attack_effect(
            screen,
            self.camera,
            zoom,
            self.attack_effect,
            self.attack_duration,
        )

    def _render_prompts(self, screen, zoom):
        """Render interaction prompts and direction helpers."""
        if self.show_boss_arrow and self.world:
            boss_trigger = self.world.get_active_boss_room_trigger()
            if boss_trigger:
                draw_objective_arrow(
                    screen,
                    self.player,
                    boss_trigger["rect"],
                    self.camera,
                    zoom,
                    self.credit_font,
                    self.time_seconds,
                )

        if self.near_door:
            draw_door_prompt(screen, self.player, self.camera, zoom, self.credit_font)

        if self.near_key:
            draw_key_prompt(screen, self.player, self.camera, zoom, self.credit_font)

        if self.near_exit_trigger:
            draw_exit_prompt(screen, self.player, self.camera, zoom, self.credit_font)

        if self.near_locked_door:
            draw_door_prompt(screen, self.player, self.camera, zoom, self.credit_font)

        if self.door_locked_message:
            draw_locked_door_prompt(
                screen, self.player, self.camera, zoom, self.credit_font
            )

    def _render_debug(self, screen, zoom):
        """Render debug overlays."""
        if self.world:
            draw_debug_collision(
                screen,
                (
                    self.world.collision_rects
                    + self.world.hazard_rects
                    + [t["rect"] for t in self.world.boss_room_triggers]
                    + [t["rect"] for t in self.world.exit_triggers]
                    + self.world.health_potion_spawns
                ),
                self.camera,
                zoom,
            )
        # draw_debug_coords(screen, self.player, self.credit_font)

    def _render_ui(self, screen):
        """Render normal gameplay UI."""
        self.task_panel.render(screen, self.time_seconds)
        if self.current_map_path != BOSS_MAP_PATH:
            self.inventory_bar.render(screen)

    def _render_overlays(self, screen):
        """Render overlays that sit above the gameplay UI."""
        if self.paused:
            self.pause_menu.render(screen, self.time_seconds)

        if self.game_over:
            self.game_over_menu.render(screen, self.time_seconds)

        self.dialogue.render(screen, self.time_seconds)
        self.debug_menu.render(screen)

    def _render_enemy_health_bars(self, screen, zoom):
        """Render enemy health bars."""
        for enemy in self.enemies:
            if enemy is self.boss_enemy:
                continue
            enemy.render_health_bar(screen, self.camera, zoom)
