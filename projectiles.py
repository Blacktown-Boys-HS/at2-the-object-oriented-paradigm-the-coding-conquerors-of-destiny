"""
Projectile classes for the RPG game.
"""

import math

import pygame

from globals import SCREEN_HEIGHT, SCREEN_WIDTH


class PlayerFireball:
    """Fireball shot by the player toward the mouse."""

    def __init__(self, x, y, vx, vy, damage=35):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.radius = 4
        self.damage = damage
        self.lifetime = 2.2
        self.age = 0.0
        self.active = True

    def update(self, dt):
        """Move the fireball and expire it."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt
        if self.age >= self.lifetime:
            self.active = False

    def get_rect(self):
        """Return the fireball hitbox."""
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def render(self, screen, camera, zoom, time_seconds=0.0):
        """Draw the fireball directly on the screen."""
        screen_x = int((self.x - camera.x) * zoom + SCREEN_WIDTH / 2)
        screen_y = int((self.y - camera.y) * zoom + SCREEN_HEIGHT / 2)
        draw_radius = max(3, int(self.radius * zoom))

        pulse = 0.5 + 0.5 * math.sin(time_seconds * 16 + self.age * 12)
        flame = (
            245,
            min(255, int(95 + 70 * pulse)),
            30,
        )
        glow = (110, 30, 12)

        pygame.draw.circle(screen, glow, (screen_x, screen_y), draw_radius + 4)
        pygame.draw.circle(screen, flame, (screen_x, screen_y), draw_radius)
        pygame.draw.circle(
            screen,
            (255, 225, 120),
            (screen_x - draw_radius // 3, screen_y - draw_radius // 3),
            max(2, draw_radius // 3),
        )


class BossProjectile:
    """Projectile fired by the boss in the arena."""

    def __init__(self, x, y, vx, vy, radius=5, damage=15, lifetime=4.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.radius = radius
        self.damage = damage
        self.lifetime = lifetime
        self.age = 0.0
        self.active = True

    def update(self, dt):
        """Move the projectile and expire it after its lifetime."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt
        if self.age >= self.lifetime:
            self.active = False

    def get_rect(self):
        """Return collision rect for hitting the player."""
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def render(self, screen, camera, zoom, time_seconds=0.0):
        """Draw projectile directly on the screen."""
        screen_x = int((self.x - camera.x) * zoom + SCREEN_WIDTH / 2)
        screen_y = int((self.y - camera.y) * zoom + SCREEN_HEIGHT / 2)
        draw_radius = max(3, int(self.radius * zoom))

        pulse = 0.5 + 0.5 * math.sin(time_seconds * 10 + self.age * 8)
        core = (
            min(255, int(180 + 45 * pulse)),
            min(255, int(80 + 30 * pulse)),
            255,
        )
        rim = (70, 20, 100)

        pygame.draw.circle(screen, rim, (screen_x, screen_y), draw_radius + 2)
        pygame.draw.circle(screen, core, (screen_x, screen_y), draw_radius)
        pygame.draw.circle(
            screen,
            (245, 210, 255),
            (screen_x - draw_radius // 3, screen_y - draw_radius // 3),
            max(1, draw_radius // 3),
        )
