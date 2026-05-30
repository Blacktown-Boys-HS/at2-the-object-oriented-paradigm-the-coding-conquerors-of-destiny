"""
Player character class for the RPG game.
"""
from pathlib import Path
import pygame
from sprite_sheet import SpriteSheet
from pos import Position


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

            #load animations
            self.animations = {
                "idle": {"frames": self.sprite_sheet.get_animation(0, 0, 4), "speed": 5},
                "run":  {"frames": self.sprite_sheet.get_animation(2, 0, 8) + self.sprite_sheet.get_animation(3, 0, 8), "speed": 8},
                "roll": {"frames": self.sprite_sheet.get_animation(5, 0, 8), "speed": 10},
                "hit":  {"frames": self.sprite_sheet.get_animation(6, 0, 4), "speed": 5},
                "death":{"frames": self.sprite_sheet.get_animation(7, 0, 4), "speed": 4},
            }

            self.state = "idle"
            self.facing_right = True
            self.current_frame = 0
            self.animation_time = 0.0

        except (FileNotFoundError, pygame.error):
            self.sprite_sheet = None

        # for pyscroll
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA) # Placeholder
        self.rect = pygame.Rect(x, y, 16, 16)

        self.max_health = 100
        self.health = 100
        self.damage_cooldown = 0.0
    
    def update(self, dt):
        if not self.sprite_sheet:
            return
        
        # Tick down the invincibility
        if self.damage_cooldown > 0:
            self.damage_cooldown = max(0.0, self.damage_cooldown - dt)

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
        scaled = pygame.transform.scale(sprite, (
            int(sprite.get_width() * self.DISPLAY_SCALE),
            int(sprite.get_height() * self.DISPLAY_SCALE)
        ))
        if not self.facing_right:
            scaled = pygame.transform.flip(scaled, True, False)
        self.image = scaled
        self.rect = self.image.get_rect(center=(int(self.position.x), int(self.position.y)))

        

    def render(self, screen, camera, zoom=1) -> None:
        """Render the player sprite relative to the camera."""
        if self.sprite_sheet:
            anim = self.animations[self.state]
            sprite = anim["frames"][self.current_frame]

            scaled_width = int(sprite.get_width() * self.DISPLAY_SCALE)
            scaled_height = int(sprite.get_height() * self.DISPLAY_SCALE)

            scaled_sprite = pygame.transform.scale(
                sprite,
                (scaled_width, scaled_height)
            )

            # Flip if facing left
            if not self.facing_right:
                scaled_sprite = pygame.transform.flip(scaled_sprite, True, False)

            # Convert world position to screen position using camera center and zoom
            from globals import SCREEN_WIDTH, SCREEN_HEIGHT
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
        import math
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
        # Switch to hit animation if not already dying
        if self.health > 0 and self.state != "death":
            self.set_state("hit")

    @property
    def is_dead(self):
        return self.health <= 0
