"""
Shared visual style: gradient background, drifting dots, common typography helpers.
"""
import math
import random
import pygame

from globals import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BACKGROUND,
    WHITE,
    FONT_ANTIALIAS,
)

FOOTER_HINT_COLOR = (190, 190, 190)
SUBTITLE_COLOR = (215, 215, 215)
BODY_MUTED = (200, 200, 200)

def safe_scale_surface(surface, scale_factor):
    """Scale surfaces with nearest neighbor so text stays crisp (no smooth blur)."""
    target_width = max(1, int(surface.get_width() * scale_factor))
    target_height = max(1, int(surface.get_height() * scale_factor))
    converted = surface.convert_alpha()
    return pygame.transform.scale(converted, (target_width, target_height))


class SharedBackground:
    """Gradient + subtle falling dots (same look as the main menu)."""

    def __init__(self, width=None, height=None, dot_count=60):
        self.width = width or SCREEN_WIDTH
        self.height = height or SCREEN_HEIGHT
        self.dots = []
        for _ in range(dot_count):
            self.dots.append(
                {
                    "x": random.randint(0, self.width),
                    "y": random.randint(0, self.height),
                    "radius": random.randint(1, 3),
                    "speed": random.uniform(0.3, 1.4),
                    "alpha": random.randint(40, 120),
                }
            )

    def update(self, dt):
        for dot in self.dots:
            dot["y"] += dot["speed"]
            if dot["y"] > self.height + dot["radius"]:
                dot["y"] = -dot["radius"]
                dot["x"] = random.randint(0, self.width)

    def draw(self, screen):
        screen.fill((30, 30, 30))


def draw_pulsing_title(screen, font, text, center_x, center_y, time_seconds):
    pulse = 1.0 + (math.sin(time_seconds * 2.2) * 0.02)
    surf = font.render(text, FONT_ANTIALIAS, WHITE)
    surf = safe_scale_surface(surf, pulse)
    rect = surf.get_rect(center=(center_x, center_y))
    screen.blit(surf, rect)


def draw_subtitle_centered(screen, font, text, center_x, center_y, color=SUBTITLE_COLOR):
    surf = font.render(text, FONT_ANTIALIAS, color)
    rect = surf.get_rect(center=(center_x, center_y))
    screen.blit(surf, rect)


def draw_footer_hint(screen, font, text, margin_bottom=45, color=FOOTER_HINT_COLOR):
    surf = font.render(text, FONT_ANTIALIAS, color)
    rect = surf.get_rect(
        center=(screen.get_width() // 2, screen.get_height() - margin_bottom)
    )
    screen.blit(surf, rect)
