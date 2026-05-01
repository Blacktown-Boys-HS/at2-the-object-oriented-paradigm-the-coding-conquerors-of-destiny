"""
Credits scene for the RPG game.
"""
import pygame
from globals import SCREEN_WIDTH, WHITE, SCENE_MENU, FPS, FONT_ANTIALIAS

from pos import Position

from .aesthetic import SharedBackground, draw_pulsing_title, draw_footer_hint
class CreditsScene:
    """Credits scene."""

    def __init__(self, title_font, menu_font, credit_font, sounds=None):
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font
        self.sounds = sounds or {}

        self.bg = SharedBackground()
        self.time_seconds = 0.0

        self.credits_items = [
            "> Software Assessment",
            "",
            "> Made by The Coding Conquerors of Destiny",
            "",
            "> Angadjot Dhaliwal and Sri Hari Srinigganathan",
            "",
            "> BLACKTOWN BOYS HIGH SCHOOL",
        ]

    def handle_event(self, event):
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return SCENE_MENU
        return None

    def update(self, mouse_pos):
        """Update credits state."""
        self.time_seconds = pygame.time.get_ticks() / 1000.0
        self.bg.update(1.0 / FPS)

    def render(self, screen):
        """Render the credits scene."""
        self.bg.draw(screen)

        draw_pulsing_title(
            screen,
            self.title_font,
            "CREDITS",
            SCREEN_WIDTH // 2,
            115,
            self.time_seconds,
        )

        credits_start_pos = Position(SCREEN_WIDTH // 2, 240)
        for i, item in enumerate(self.credits_items):
            if item:
                credits_text = self.credit_font.render(item, FONT_ANTIALIAS, WHITE)
                item_pos = credits_start_pos.add(Position(0, i * 60))
                credits_rect = credits_text.get_rect(center=item_pos.to_int_tuple())
                screen.blit(credits_text, credits_rect)

        draw_footer_hint(screen, self.credit_font, "Press ESC to return to menu")
