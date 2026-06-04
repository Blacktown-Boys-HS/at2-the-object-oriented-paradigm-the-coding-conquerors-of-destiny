"""
Loading screen for the RPG game.
"""
import math
import pygame

from globals import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_ANTIALIAS, BLUE, GRAY
from .aesthetic import safe_scale_surface

def draw_loading_screen(screen, loading_time, menu_font, credit_font, hints):
    """Draw the loading screen overlay."""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    pulse = 1.0 + 0.08 * math.sin(loading_time * 10)
    loading_text = menu_font.render("Loading...", FONT_ANTIALIAS, BLUE)
    scaled = safe_scale_surface(loading_text, pulse)
    rect = scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(scaled, rect)

    hint_index = int(loading_time * 2) % len(hints)
    hint_text = credit_font.render(hints[hint_index], FONT_ANTIALIAS, GRAY)
    hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
    screen.blit(hint_text, hint_rect)