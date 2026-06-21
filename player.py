"""
Player character class for the RPG game.
"""

import math
from pathlib import Path

import pygame

from pos import Position
from sprite_sheet import SpriteSheet


class Player(pygame.sprite.Sprite):
    """Player character with sprite animation."""

    FRAME_WIDTH = 32
    FRAME_HEIGHT = 32
    DISPLAY_SCALE = 1

    def __init__(self, x=600, y=400):
        super().__init__()
        self.position = Position(x, y)
        self.sprite_sheet = None
        self.current_frame = 0
        self.animation_time = 0.0
        self.attack_cooldown = 0.0
        self.attack_cooldown_duration = 0.8
        self.last_attack_hit = False

        # Load sprite sheet
        knight_path = (
            Path(__file__).resolve().parent
            / "assets"
            / "rpg_assets"
            / "sprites"
            / "knight.png"
        )
        try:
            self.sprite_sheet = SpriteSheet(
                knight_path, self.FRAME_WIDTH, self.FRAME_HEIGHT
            )

            # load animations
            self.animations = {
                "idle": {
                    "frames": self.sprite_sheet.get_animation(0, 0, 4),
                    "speed": 5,
                },
                "run": {
                    "frames": self.sprite_sheet.get_animation(2, 0, 8)
                    + self.sprite_sheet.get_animation(3, 0, 8),
                    "speed": 8,
                },
                "roll": {
                    "frames": self.sprite_sheet.get_animation(5, 0, 8),
                    "speed": 10,
                },
                "hit": {"frames": self.sprite_sheet.get_animation(6, 0, 4), "speed": 5},
                "death": {
                    "frames": self.sprite_sheet.get_animation(7, 0, 4),
                    "speed": 4,
                },
            }

            self.state = "idle"
            self.facing_right = True
            self.current_frame = 0
            self.animation_time = 0.0

        except (FileNotFoundError, pygame.error):
            self.sprite_sheet = None

        # for pyscroll
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)  # Placeholder
        self.rect = pygame.Rect(x, y, 16, 16)

        self.max_health = 100
        self.health = 100
        self.damage_cooldown = 0.0
        self.time_since_last_damage = 0.0
        self.REGEN_DELAY = 5.0
        self.REGEN_RATE = 8.0  # HP per second after delay

    @property
    def is_regenerating(self):
        return (
            0 < self.health < self.max_health
            and self.time_since_last_damage >= self.REGEN_DELAY
        )

    def update(self, dt):
        if self.damage_cooldown > 0:
            self.damage_cooldown = max(0.0, self.damage_cooldown - dt)

        if self.health > 0:
            self.time_since_last_damage += dt
            if self.is_regenerating:
                self.health = min(
                    self.max_health, self.health + self.REGEN_RATE * dt
                )

        if not self.sprite_sheet:
            return

        anim = self.animations[self.state]
        self.animation_time += dt
        frame_index = int(self.animation_time * anim["speed"])

        # Return to idle after animation finishes
        if self.state == "hit":
            if frame_index >= len(anim["frames"]):
                self.set_state("idle")
                return

        self.current_frame = frame_index % len(anim["frames"])

        sprite = anim["frames"][self.current_frame]
        scaled = pygame.transform.scale(
            sprite,
            (
                int(sprite.get_width() * self.DISPLAY_SCALE),
                int(sprite.get_height() * self.DISPLAY_SCALE),
            ),
        )
        if not self.facing_right:
            scaled = pygame.transform.flip(scaled, True, False)
        self.image = scaled
        self.rect = self.image.get_rect(
            center=(int(self.position.x), int(self.position.y))
        )

        if self.attack_cooldown > 0:
            self.attack_cooldown = max(0.0, self.attack_cooldown - dt)

    def render(self, screen, camera, zoom=1) -> None:
        """Render the player sprite relative to the camera."""
        if self.sprite_sheet:
            anim = self.animations[self.state]
            sprite = anim["frames"][self.current_frame]

            scaled_width = int(sprite.get_width() * self.DISPLAY_SCALE)
            scaled_height = int(sprite.get_height() * self.DISPLAY_SCALE)

            scaled_sprite = pygame.transform.scale(
                sprite, (scaled_width, scaled_height)
            )

            # Flip if facing left
            if not self.facing_right:
                scaled_sprite = pygame.transform.flip(scaled_sprite, True, False)

            # Convert world position to screen position using camera center and zoom
            from globals import SCREEN_HEIGHT, SCREEN_WIDTH

            screen_x = (self.position.x - camera.x) * zoom + SCREEN_WIDTH / 2
            screen_y = (self.position.y - camera.y) * zoom + SCREEN_HEIGHT / 2

            sprite_rect = scaled_sprite.get_rect(
                center=(round(screen_x), round(screen_y))
            )
            screen.blit(scaled_sprite, sprite_rect)

    def set_state(self, state):
        if state != self.state:
            self.state = state
            self.current_frame = 0
            self.animation_time = 0

    def move(self, dx, dy, speed):
        """Move the player by (dx, dy) direction with given speed."""

        if dx != 0 or dy != 0:
            length = math.sqrt(dx * dx + dy * dy)
            dx /= length
            dy /= length
        self.position.x += dx * speed
        self.position.y += dy * speed

        # Update facing direction
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False

    def set_position(self, x, y):
        """Set player position."""
        self.position = Position(x, y)

    def get_position(self):
        """Get player position."""
        return self.position

    def take_damage(self, amount):
        """Take damage. Caller must check damage_cooldown <= 0 before calling.
        Sets a 0.5s invincibility window after each hit."""
        self.health = max(0, self.health - amount)
        self.damage_cooldown = 0.5  # seconds of invincibility after a hit
        self.time_since_last_damage = 0.0
        # Switch to hit animation if not already dying
        if self.health > 0 and self.state != "death":
            self.set_state("hit")

    def attack(self, enemies, group):
        self.last_attack_hit = False
        if self.attack_cooldown > 0:
            return False  # on cooldown
        self.attack_cooldown = self.attack_cooldown_duration
        attack_rect = pygame.Rect(
            self.position.x - 40,
            self.position.y - 40,
            80, 80
        )
        for enemy in enemies[:]:
            if hasattr(enemy, "get_hit_rect"):
                enemy_rect = enemy.get_hit_rect()
            else:
                enemy_rect = pygame.Rect(enemy.position.x - 8, enemy.position.y - 8, 16, 16)
            if attack_rect.colliderect(enemy_rect):
                enemy.take_damage(20)
                self.last_attack_hit = True
        return True

    def render_attack_effect(self, screen, camera, zoom, attack_effect, attack_duration):
        if attack_effect <= 0:
            return
        from globals import SCREEN_WIDTH, SCREEN_HEIGHT
        progress = 1.0 - (attack_effect / attack_duration)
        radius = int(40 + progress * 40)  
        thickness = max(2, int(5 * (1.0 - progress))) 
        screen_x = int((self.position.x - camera.x) * zoom + SCREEN_WIDTH / 2)
        screen_y = int((self.position.y - camera.y) * zoom + SCREEN_HEIGHT / 2)
        pygame.draw.circle(screen, (100, 200, 255), (screen_x, screen_y), radius, thickness)
        # Inner ring for extra impact
        if progress < 0.5:
            inner_radius = int(20 + progress * 30)
            pygame.draw.circle(screen, (180, 230, 255), (screen_x, screen_y), inner_radius, max(1, thickness - 1))

    def update_facing(self, dx):
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False

    @property
    def is_dead(self):
        return self.health <= 0
