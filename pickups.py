"""
Pickup item classes for the RPG game.
"""

import math

import pygame

from globals import SCREEN_HEIGHT, SCREEN_WIDTH


class HealthPotion:
    """Health potion spawned from Tiled potion spawn zones."""

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.radius = 6
        self.heal_amount = 35
        self.active = True

    def get_rect(self):
        """Return pickup hitbox."""
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def render(self, screen, camera, zoom, time_seconds=0.0):
        """Draw a glowing golden health orb."""
        bob = math.sin(time_seconds * 4.0) * 3
        screen_x = int((self.x - camera.x) * zoom + SCREEN_WIDTH / 2)
        screen_y = int((self.y + bob - camera.y) * zoom + SCREEN_HEIGHT / 2)
        radius = max(5, int(self.radius * zoom))

        pulse = 0.5 + 0.5 * math.sin(time_seconds * 8.0)
        glow_radius = radius + int(7 + 4 * pulse)
        core = (
            255,
            min(255, int(205 + 35 * pulse)),
            min(255, int(70 + 35 * pulse)),
        )
        inner = (255, 245, 165)
        rim = (125, 80, 18)

        pygame.draw.circle(screen, rim, (screen_x, screen_y), glow_radius)
        pygame.draw.circle(screen, (205, 140, 30), (screen_x, screen_y), radius + 4)
        pygame.draw.circle(screen, core, (screen_x, screen_y), radius)
        pygame.draw.circle(
            screen,
            inner,
            (screen_x - radius // 3, screen_y - radius // 3),
            max(2, radius // 3),
        )
