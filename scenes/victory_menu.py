"""
Victory overlay for the RPG game.
"""
import math

import pygame

from globals import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_ANTIALIAS
from scenes.aesthetic import (
    draw_gothic_title,
    draw_gothic_selection_box,
    draw_gothic_menu_item,
    safe_scale_surface,
    SUBTITLE_COLOR,
    GOTHIC_GOLD,
    GOTHIC_GOLD_DIM,
    GOTHIC_PANEL_INNER,
    GOTHIC_STONE,
)


class VictoryMenu:
    """Handles victory rendering and menu state."""

    ITEMS = ["Main Menu", "Quit"]

    def __init__(self, title_font, menu_font, credit_font, sounds=None):
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font
        self.sounds = sounds or {}

        self.selected = 0
        self.last_selected = 0
        self.item_rects = []
        self.hover_scale = [1.0 for _ in self.ITEMS]
        self.selection_y = 0

        self.activation_item = None
        self.activation_progress = 0.0
        self.activation_duration = 0.18
        self.pending_action = None

    def reset(self):
        """Reset menu animation state."""
        self.selected = 0
        self.last_selected = 0
        self.hover_scale = [1.0 for _ in self.ITEMS]
        self.selection_y = 0
        self.activation_item = None
        self.activation_progress = 0.0
        self.pending_action = None

    def handle_event(self, event):
        """Handle keyboard and mouse input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.ITEMS)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.ITEMS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._start_activate()
            return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected = i
                    self._start_activate()
                    break
            return True

        return False

    def _start_activate(self):
        """Play a short confirm animation before victory action."""
        if self.activation_item is None:
            confirm_sound = self.sounds.get("confirm")
            if confirm_sound:
                confirm_sound.play()
            self.activation_item = self.selected
            self.activation_progress = 0.0

    def update(self, dt, mouse_pos):
        """Update hover states and activation animation."""
        for i, rect in enumerate(self.item_rects):
            if rect.collidepoint(mouse_pos):
                self.selected = i
                break

        if self.selected != self.last_selected:
            hover_sound = self.sounds.get("button_hover")
            if hover_sound:
                hover_sound.play()
            self.last_selected = self.selected

        for i in range(len(self.ITEMS)):
            activation_bonus = 0.0
            if self.activation_item == i:
                activation_bonus = 0.10 * (1.0 - self.activation_progress)

            if i == self.selected:
                self.hover_scale[i] = min(
                    self.hover_scale[i] + 0.05,
                    1.10 + activation_bonus,
                )
            else:
                self.hover_scale[i] = max(self.hover_scale[i] - 0.05, 1.0)

        target_y = 565 + self.selected * 72
        if self.selection_y == 0:
            self.selection_y = target_y
        self.selection_y += (target_y - self.selection_y) * 0.20

        if self.activation_item is not None:
            self.activation_progress += dt / self.activation_duration
            if self.activation_progress >= 1.0:
                self.pending_action = self.ITEMS[self.activation_item]
                self.activation_item = None
                self.activation_progress = 0.0

    def consume_action(self):
        """Return and clear the pending action."""
        action = self.pending_action
        self.pending_action = None
        return action

    def render(self, screen, time_seconds):
        """Render the full victory overlay."""
        screen.fill(GOTHIC_STONE)

        for y in range(0, SCREEN_HEIGHT, 4):
            shade = 8 + int((y / SCREEN_HEIGHT) * 20)
            pygame.draw.rect(
                screen,
                (shade, max(0, shade - 2), shade + 8),
                (0, y, SCREEN_WIDTH, 4),
            )

        frame = pygame.Rect(70, 58, SCREEN_WIDTH - 140, SCREEN_HEIGHT - 116)
        pygame.draw.rect(screen, GOTHIC_GOLD_DIM, frame, width=3, border_radius=14)
        pygame.draw.rect(
            screen,
            GOTHIC_GOLD,
            frame.inflate(-12, -12),
            width=2,
            border_radius=10,
        )

        panel = pygame.Rect(SCREEN_WIDTH // 2 - 360, 255, 720, 210)
        panel_surface = pygame.Surface(panel.size, pygame.SRCALPHA)
        pygame.draw.rect(
            panel_surface,
            (GOTHIC_GOLD[0], GOTHIC_GOLD[1], GOTHIC_GOLD[2], 230),
            panel_surface.get_rect(),
            border_radius=12,
        )
        pygame.draw.rect(
            panel_surface,
            (*GOTHIC_PANEL_INNER, 255),
            panel_surface.get_rect().inflate(-6, -6),
            border_radius=9,
        )
        screen.blit(panel_surface, panel.topleft)

        draw_gothic_title(
            screen,
            self.title_font,
            "YOU ESCAPED",
            SCREEN_WIDTH // 2,
            175,
            color=GOTHIC_GOLD,
        )

        pulse = 0.5 + 0.5 * math.sin(time_seconds * 4.0)
        orb_x = SCREEN_WIDTH // 2
        orb_y = 315
        glow_radius = int(48 + 8 * pulse)
        pygame.draw.circle(screen, (42, 16, 62), (orb_x, orb_y), glow_radius)
        pygame.draw.circle(screen, (90, 32, 130), (orb_x, orb_y), 38)
        pygame.draw.circle(screen, (170, 76, 230), (orb_x, orb_y), 28)
        pygame.draw.circle(screen, (238, 190, 255), (orb_x - 10, orb_y - 10), 9)
        pygame.draw.circle(screen, (255, 235, 255), (orb_x - 13, orb_y - 13), 4)

        subtitle_color = (
            min(255, int(SUBTITLE_COLOR[0] + 28 * pulse)),
            min(255, int(SUBTITLE_COLOR[1] + 20 * pulse)),
            min(255, int(SUBTITLE_COLOR[2] + 8 * pulse)),
        )

        lines = [
            "The Violet Slime King has fallen.",
            "The purple orb breaks the final seal,",
            "and the dungeon finally lets you go.",
        ]
        text_y = 375
        for line in lines:
            text = self.credit_font.render(line, FONT_ANTIALIAS, subtitle_color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, text_y))
            screen.blit(text, text_rect)
            text_y += 30

        selection_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 190,
            int(self.selection_y) - 6,
            380,
            60,
        )
        draw_gothic_selection_box(
            screen,
            selection_rect,
            activating=self.activation_item == self.selected,
            activation_progress=self.activation_progress,
        )

        menu_start_x = SCREEN_WIDTH // 2 - 130
        menu_start_y = 565
        self.item_rects = []
        for i, item in enumerate(self.ITEMS):
            item_pos = (menu_start_x, menu_start_y + i * 72)
            rect = draw_gothic_menu_item(
                screen,
                self.menu_font,
                item,
                item_pos,
                i == self.selected,
                self.hover_scale[i],
                safe_scale_surface,
            )
            self.item_rects.append(rect)
