"""
Player character class for the RPG game.
"""
from pathlib import Path
import pygame
from sprite_sheet import SpriteSheet
from pos import Position


class Player:
    """Player character with sprite animation."""
    
    FRAME_WIDTH = 32
    FRAME_HEIGHT = 32
    DISPLAY_SCALE = 3  # 16×3 = 48 pixels
    
    def __init__(self, x=600, y=400):
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
                "run":  {"frames": self.sprite_sheet.get_animation(3, 0, 8), "speed": 8},
                "roll": {"frames": self.sprite_sheet.get_animation(5, 0, 8), "speed": 10},
                "hit":  {"frames": self.sprite_sheet.get_animation(6, 0, 4), "speed": 5},
                "death":{"frames": self.sprite_sheet.get_animation(7, 0, 4), "speed": 4},
            }

            self.state = "hit"
            self.current_frame = 0
            self.animation_time = 0.0

        except (FileNotFoundError, pygame.error):
            self.sprite_sheet = None
    
    def update(self, dt):
        if not self.sprite_sheet:
            return

        anim = self.animations[self.state]
        self.animation_time += dt

        frame_index = int(self.animation_time * anim["speed"])
        self.current_frame = frame_index % len(anim["frames"])
    
    def render(self, screen) -> None: 
        """Render the player sprite."""
        if self.sprite_sheet:
            # Try row 0 for the idle animation
            anim = self.animations[self.state]
            sprite = anim["frames"][self.current_frame]
            
            # Create a new surface to ensure clean rendering
            clean_sprite = pygame.Surface((sprite.get_width(), sprite.get_height()), pygame.SRCALPHA)
            clean_sprite.blit(sprite, (0, 0))
            
            # Scale the sprite
            scaled_width = int(clean_sprite.get_width() * self.DISPLAY_SCALE)
            scaled_height = int(clean_sprite.get_height() * self.DISPLAY_SCALE)
            scaled_sprite = pygame.transform.scale(clean_sprite, (max(1, scaled_width), max(1, scaled_height)))
            
            # Draw sprite
            x, y = self.position.to_int_tuple()
            sprite_rect = scaled_sprite.get_rect(center=(x, y))
            screen.blit(scaled_sprite, sprite_rect)

    def set_state(self, state):
        if state != self.state:
            self.state = state
            self.current_frame = 0
            self.animation_time = 0

    def set_position(self, x, y):
        """Set player position."""
        self.position = Position(x, y)
    
    def get_position(self):
        """Get player position."""
        return self.position
