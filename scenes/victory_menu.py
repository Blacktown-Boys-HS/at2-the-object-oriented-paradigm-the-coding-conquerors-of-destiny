"""
Victory overlay for the RPG game.
"""
import pygame

from globals import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_ANTIALIAS
from scenes.aesthetic import (
    draw_gothic_title,
    draw_gothic_selection_box,
    draw_gothic_menu_item,
    safe_scale_surface,
    SUBTITLE_COLOR,
    GOTHIC_GOLD,
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

        target_y = 405 + self.selected * 80
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
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 205))
        screen.blit(overlay, (0, 0))

        draw_gothic_title(
            screen,
            self.title_font,
            "YOU ESCAPED",
            SCREEN_WIDTH // 2,
            205,
            color=GOTHIC_GOLD,
        )

        pulse = 0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(time_seconds * 90).x
        subtitle_color = (
            min(255, int(SUBTITLE_COLOR[0] + 28 * pulse)),
            min(255, int(SUBTITLE_COLOR[1] + 20 * pulse)),
            min(255, int(SUBTITLE_COLOR[2] + 8 * pulse)),
        )
        subtitle = self.credit_font.render(
            "The orb burns through the final seal, and the dungeon lets you go.",
            FONT_ANTIALIAS,
            subtitle_color,
        )
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 305))
        screen.blit(subtitle, subtitle_rect)

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
        menu_start_y = 405
        self.item_rects = []
        for i, item in enumerate(self.ITEMS):
            item_pos = (menu_start_x, menu_start_y + i * 80)
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
