"""
Placeholder game scene for the RPG game.
"""
import pygame
from globals import SCREEN_WIDTH, SCREEN_HEIGHT, SCENE_MENU, FPS

from .aesthetic import (
    SharedBackground,
    draw_pulsing_title,
    draw_subtitle_centered,
    draw_footer_hint,
)


class GameScene:
    """Game scene."""

    def __init__(self, title_font, menu_font, credit_font):
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font
        self.bg = SharedBackground()
        self.time_seconds = 0.0

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

        coming = self.menu_font.render("Coming soon!", False, (230, 230, 230))
        coming_rect = coming.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)
        )
        screen.blit(coming, coming_rect)

        draw_footer_hint(screen, self.credit_font, "Press ESC to return to menu")
