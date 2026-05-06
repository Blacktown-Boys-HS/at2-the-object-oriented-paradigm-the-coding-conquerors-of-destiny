"""
Placeholder game scene for the RPG game.
"""
import pygame
from pathlib import Path
from globals import SCREEN_WIDTH, SCREEN_HEIGHT, SCENE_MENU, FPS, FONT_ANTIALIAS, BLACK
from sprite_sheet import SpriteSheet
from camera import Camera
from player import Player

from .aesthetic import (
    SharedBackground,
    draw_pulsing_title,
    draw_subtitle_centered,
    draw_footer_hint,
)

class GameScene:
    """Game scene."""

    MOVE_SPEED = 200  # pixels per second

    def __init__(self, title_font, menu_font, credit_font, sounds=None):
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font
        self.sounds = sounds or {}
        self.time_seconds = 0.0
        self.player = Player()
        self.camera = Camera()
        self.keys_pressed = {"up": False, "down": False, "left": False, "right": False}

    def handle_event(self, event):
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return SCENE_MENU
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.keys_pressed["up"] = True
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.keys_pressed["down"] = True
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.keys_pressed["left"] = True
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.keys_pressed["right"] = True
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.keys_pressed["up"] = False
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.keys_pressed["down"] = False
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.keys_pressed["left"] = False
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.keys_pressed["right"] = False
        return None

    def update(self, mouse_pos):
        """Update game state."""
        self.time_seconds = pygame.time.get_ticks() / 1000.0
        dt = 1.0 / FPS

        dx = 0
        dy = 0
        if self.keys_pressed["up"]:
            dy -= 1
        if self.keys_pressed["down"]:
            dy += 1
        if self.keys_pressed["left"]:
            dx -= 1
        if self.keys_pressed["right"]:
            dx += 1

        moving = dx != 0 or dy != 0
        if moving:
            self.player.move(dx, dy, self.MOVE_SPEED * dt)
            if self.player.state != "run":
                self.player.set_state("run")
        else:
            if self.player.state != "idle":
                self.player.set_state("idle")

        self.player.update(dt)
        self.camera.update(
            self.player,
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        )

    def render(self, screen):
        """Render the game scene."""
        screen.fill(BLACK)
        self.player.render(screen, self.camera)

        # Movement hint
        hint = self.credit_font.render("WASD or Arrow Keys to move · ESC for menu", False, (200, 200, 200))
        screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)))
