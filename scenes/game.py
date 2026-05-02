"""
Placeholder game scene for the RPG game.
"""
from pathlib import Path

import pygame
from globals import SCREEN_WIDTH, SCREEN_HEIGHT, SCENE_MENU, FPS, FONT_ANTIALIAS
from sprite_sheet import SpriteSheet

from .aesthetic import (
    SharedBackground,
    draw_pulsing_title,
    draw_subtitle_centered,
    draw_footer_hint,
)


class GameScene:
    """Game scene."""

    _KNIGHT_FRAME_WIDTH = 16
    _KNIGHT_FRAME_HEIGHT = 16
    _KNIGHT_DISPLAY_SCALE = 4  # 16×4 = 64 pixels

    def __init__(self, title_font, menu_font, credit_font, sounds=None):
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font
        self.sounds = sounds or {}
        self.bg = SharedBackground()
        self.time_seconds = 0.0
        self._knight_sheet = None
        knight_path = (
            Path(__file__).resolve().parent.parent
            / "assets"
            / "rpg_assets"
            / "sprites"
            / "knight.png"
        )
        try:
            self._knight_sheet = SpriteSheet(
                knight_path, self._KNIGHT_FRAME_WIDTH, self._KNIGHT_FRAME_HEIGHT
            )
        except (FileNotFoundError, pygame.error):
            self._knight_sheet = None

    def handle_event(self, event):
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return SCENE_MENU
        return None

    def update(self, mouse_pos):
        """Update game state."""
        self.time_seconds = pygame.time.get_ticks() / 1000.0
        self.bg.update(1.0 / FPS)

    def render(self, screen):
        """Render the game scene."""
        self.bg.draw(screen)

        draw_pulsing_title(
            screen,
            self.title_font,
            "Game",
            SCREEN_WIDTH // 2,
            115,
            self.time_seconds,
        )

        draw_subtitle_centered(
            screen,
            self.credit_font,
            "Placeholder — full adventure coming later",
            SCREEN_WIDTH // 2,
            200,
        )

        if self._knight_sheet:
            col = int(self.time_seconds * 8) % min(8, self._knight_sheet.cols)
            hero = self._knight_sheet.frame(col, 0)
            w = hero.get_width() * self._KNIGHT_DISPLAY_SCALE
            h = hero.get_height() * self._KNIGHT_DISPLAY_SCALE
            hero = pygame.transform.scale(hero, (max(1, w), max(1, h)))
            hero_rect = hero.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)
            )
            screen.blit(hero, hero_rect)

        coming = self.menu_font.render(
            "Coming soon!", FONT_ANTIALIAS, (230, 230, 230)
        )
        coming_rect = coming.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70)
        )
        screen.blit(coming, coming_rect)

        draw_footer_hint(screen, self.credit_font, "Press ESC to return to menu")
