"""
Placeholder game scene for the RPG game.
"""
import pygame
from pathlib import Path
from globals import SCREEN_WIDTH, SCREEN_HEIGHT, SCENE_MENU, FPS, FONT_ANTIALIAS, BLACK
from sprite_sheet import SpriteSheet
from player import Player

from .aesthetic import (
    SharedBackground,
    draw_pulsing_title,
    draw_subtitle_centered,
    draw_footer_hint,
)

class GameScene:
    """Game scene."""

    def __init__(self, title_font, menu_font, credit_font, sounds=None):
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font
        self.sounds = sounds or {}
        self.time_seconds = 0.0
        self.player = Player()
        
        # Create animation preview players for each state
        self.animations = {}
        if self.player.sprite_sheet:
            for state_name in self.player.animations.keys():
                preview = Player()
                preview.set_state(state_name)
                preview.set_position(0, 0)
                self.animations[state_name] = preview

    def handle_event(self, event):
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return SCENE_MENU
        return None

    def update(self, mouse_pos):
        """Update game state."""
        self.time_seconds = pygame.time.get_ticks() / 1000.0
        dt = 1.0 / FPS
        self.player.update(dt)
        
        # Update all animation previews
        for preview in self.animations.values():
            preview.update(dt)

    def render(self, screen):
        """Render the game scene."""
        screen.fill(BLACK)
        
        # Draw all animations horizontally across the screen
        if self.animations:
            spacing = SCREEN_WIDTH // (len(self.animations) + 1)
            y_pos = SCREEN_HEIGHT // 2
            
            for i, (state_name, preview) in enumerate(self.animations.items()):
                x_pos = spacing * (i + 1)
                preview.set_position(x_pos, y_pos)
                preview.render(screen)
                
                # Draw state name label below each animation
                label = self.credit_font.render(state_name.upper(), False, (255, 255, 255))
                label_rect = label.get_rect(center=(x_pos, y_pos + 80))
                screen.blit(label, label_rect)
        else:
            self.player.render(screen)
