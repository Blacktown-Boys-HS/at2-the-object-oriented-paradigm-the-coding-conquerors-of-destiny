"""
Shared visual style: gradient background, drifting dots, common typography helpers.
"""
import math
import random
import pygame

from globals import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND, WHITE

FOOTER_HINT_COLOR = (190, 190, 190)
SUBTITLE_COLOR = (215, 215, 215)
BODY_MUTED = (200, 200, 200)


def safe_scale_surface(surface, scale_factor):
    """Scale surfaces safely; prefer smooth scaling after convert_alpha."""
    target_width = max(1, int(surface.get_width() * scale_factor))
    target_height = max(1, int(surface.get_height() * scale_factor))
    converted = surface.convert_alpha()
    return pygame.transform.smoothscale(converted, (target_width, target_height))


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
        screen.fill(BACKGROUND)
        for y in range(0, self.height, 4):
            shade = 30 + int((y / self.height) * 20)
            pygame.draw.rect(screen, (shade, shade, shade + 8), (0, y, self.width, 4))

        dot_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for dot in self.dots:
            color = (255, 255, 255, dot["alpha"])
            pygame.draw.circle(
                dot_surface,
                color,
                (int(dot["x"]), int(dot["y"])),
                dot["radius"],
            )
        screen.blit(dot_surface, (0, 0))


def draw_pulsing_title(screen, font, text, center_x, center_y, time_seconds):
    pulse = 1.0 + (math.sin(time_seconds * 2.2) * 0.02)
    surf = font.render(text, False, WHITE)
    surf = safe_scale_surface(surf, pulse)
    rect = surf.get_rect(center=(center_x, center_y))
    screen.blit(surf, rect)


def draw_subtitle_centered(screen, font, text, center_x, center_y, color=SUBTITLE_COLOR):
    surf = font.render(text, False, color)
    rect = surf.get_rect(center=(center_x, center_y))
    screen.blit(surf, rect)


def draw_footer_hint(screen, font, text, margin_bottom=45, color=FOOTER_HINT_COLOR):
    surf = font.render(text, False, color)
    rect = surf.get_rect(
        center=(screen.get_width() // 2, screen.get_height() - margin_bottom)
    )
    screen.blit(surf, rect)
