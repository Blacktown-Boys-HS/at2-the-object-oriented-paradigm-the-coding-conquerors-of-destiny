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

    def handle_event(self, event):
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return SCENE_MENU
        return None

    def update(self, mouse_pos):
        """Update game state."""
        self.time_seconds = pygame.time.get_ticks() / 1000.0

    def render(self, screen):
        """Render the game scene."""
        screen.fill(BLACK)
        self.player.render(screen)
    
        # Draw knight sprite in top left
