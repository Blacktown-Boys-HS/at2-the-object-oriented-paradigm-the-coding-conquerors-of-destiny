"""
Small debug menu for testing game shortcuts.
"""

import pygame

from globals import FONT_ANTIALIAS, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE
from scenes.aesthetic import (
    GOTHIC_GOLD,
    GOTHIC_PANEL_INNER,
    GOTHIC_TEXT_MUTED,
    draw_gothic_menu_item,
    draw_gothic_panel,
    safe_scale_surface,
)


class DebugMenu:
    """Developer-only menu for quick testing."""

    ITEMS = ["Teleport to Boss Room", "Close"]

    def __init__(self, title_font, menu_font, credit_font):
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font

        self.active = False
        self.selected = 0
        self.last_selected = 0
        self.item_rects = []
        self.pending_action = None
        self.hover_scale = [1.0 for _ in self.ITEMS]

    def toggle(self):
        """Open or close the debug menu."""
        self.active = not self.active
        self.pending_action = None

    def close(self):
        """Close the debug menu."""
        self.active = False
        self.pending_action = None

    def handle_event(self, event):
        """Handle keyboard and mouse input."""
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
            elif event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.ITEMS)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.ITEMS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.pending_action = self.ITEMS[self.selected]
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(event.pos):
                    self.selected = i
                    self.pending_action = self.ITEMS[self.selected]
                    break
            return True

        return False

    def update(self, dt, mouse_pos):
        """Update hover animation."""
        if not self.active:
            return

        for i, rect in enumerate(self.item_rects):
            if rect.collidepoint(mouse_pos):
                self.selected = i
                break

        for i in range(len(self.ITEMS)):
            target = 1.08 if i == self.selected else 1.0
            self.hover_scale[i] += (target - self.hover_scale[i]) * min(1, dt * 12)

    def consume_action(self):
        """Return and clear the selected debug action."""
        action = self.pending_action
        self.pending_action = None
        return action

    def render(self, screen):
        """Draw the debug menu overlay."""
        if not self.active:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 145))
        screen.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(340, 190, 520, 320)
        draw_gothic_panel(screen, panel_rect, border_radius=10)

        title = self.title_font.render("DEBUG", FONT_ANTIALIAS, WHITE)
        title_rect = title.get_rect(center=(panel_rect.centerx, panel_rect.top + 58))
        screen.blit(title, title_rect)

        hint = self.credit_font.render("F3 toggles this menu", FONT_ANTIALIAS, GOTHIC_TEXT_MUTED)
        hint_rect = hint.get_rect(center=(panel_rect.centerx, panel_rect.top + 104))
        screen.blit(hint, hint_rect)

        self.item_rects = []
        start_x = panel_rect.left + 92
        start_y = panel_rect.top + 155
        for i, item in enumerate(self.ITEMS):
            rect = draw_gothic_menu_item(
                screen,
                self.menu_font,
                item,
                (start_x, start_y + i * 72),
                i == self.selected,
                self.hover_scale[i],
                safe_scale_surface,
            )
            self.item_rects.append(rect)

        border = pygame.Rect(panel_rect.left + 28, panel_rect.top + 132, panel_rect.width - 56, 150)
        pygame.draw.rect(screen, GOTHIC_GOLD, border, width=1, border_radius=8)
