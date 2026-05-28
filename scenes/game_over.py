"""
Game over overlay for the RPG game.
"""
import math
import pygame

from globals import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_ANTIALIAS, BLUE, GRAY, WHITE
from scenes.aesthetic import safe_scale_surface


class GameOverMenu:
    """Handles game over rendering and menu state."""

    ITEMS = ["Retry", "Main Menu"]

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
        """Play a short confirm animation before game over action."""
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
                self.hover_scale[i] = min(self.hover_scale[i] + 0.05, 1.10 + activation_bonus)
            else:
                self.hover_scale[i] = max(self.hover_scale[i] - 0.05, 1.0)

        target_y = 385 + self.selected * 80
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

    def _draw_title(self, screen, time_seconds):
        title_str = "GAME OVER"
        shimmer = 0.5 + 0.5 * math.sin(time_seconds * 2.8)
        main_color = (
            int(170 + 45 * shimmer),
            int(70 + 25 * shimmer),
            int(90 + 20 * shimmer),
        )
        shadow_deep = (18, 8, 20)
        rim = (90, 44, 70)

        base = self.title_font.render(title_str, FONT_ANTIALIAS, WHITE)
        w, h = base.get_width(), base.get_height()
        pad = 10
        composite = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
        ox, oy = pad, pad

        for d in (5, 4, 3, 2, 1):
            layer = self.title_font.render(title_str, FONT_ANTIALIAS, shadow_deep)
            composite.blit(layer, (ox + d, oy + d))

        for dx, dy in (
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (1, -1), (-1, 1), (1, 1),
        ):
            layer = self.title_font.render(title_str, FONT_ANTIALIAS, rim)
            composite.blit(layer, (ox + dx, oy + dy))

        composite.blit(self.title_font.render(title_str, FONT_ANTIALIAS, main_color), (ox, oy))

        pulse = 1.0 + math.sin(time_seconds * 2.2) * 0.02
        scaled = safe_scale_surface(composite, pulse)
        rect = scaled.get_rect(center=(SCREEN_WIDTH // 2, 220))
        screen.blit(scaled, rect)

    def render(self, screen, time_seconds):
        """Render the full game over overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 205))
        screen.blit(overlay, (0, 0))

        self._draw_title(screen, time_seconds)

        subtitle = self.credit_font.render("You fell in the dungeon.", FONT_ANTIALIAS, (210, 210, 210))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 310))
        screen.blit(subtitle, subtitle_rect)

        selection_rect = pygame.Rect(SCREEN_WIDTH // 2 - 190, int(self.selection_y) - 8, 380, 60)
        box_surface = pygame.Surface((selection_rect.width, selection_rect.height), pygame.SRCALPHA)
        box_alpha = 24
        if self.activation_item == self.selected:
            box_alpha = 24 + int(70 * (1.0 - self.activation_progress))
        box_surface.fill((255, 255, 255, box_alpha))
        screen.blit(box_surface, selection_rect.topleft)

        border_color = (130, 130, 130)
        if self.activation_item == self.selected:
            border_color = (220, 200, 120)
        pygame.draw.rect(screen, border_color, selection_rect, width=2, border_radius=8)

        menu_start_x = SCREEN_WIDTH // 2 - 130
        menu_start_y = 385
        self.item_rects = []
        for i, item in enumerate(self.ITEMS):
            item_pos = (menu_start_x, menu_start_y + i * 80)
            if i == self.selected:
                arrow_text = self.menu_font.render("> ", FONT_ANTIALIAS, BLUE)
                item_text = self.menu_font.render(item, FONT_ANTIALIAS, WHITE)
                if self.hover_scale[i] != 1.0:
                    arrow_text = safe_scale_surface(arrow_text, self.hover_scale[i])
                    item_text = safe_scale_surface(item_text, self.hover_scale[i])
                arrow_rect = arrow_text.get_rect(topleft=item_pos)
                item_rect = item_text.get_rect(topleft=(arrow_rect.right, item_pos[1]))
                self.item_rects.append(arrow_rect.union(item_rect))
                screen.blit(arrow_text, arrow_rect)
                screen.blit(item_text, item_rect)
            else:
                text = self.menu_font.render(item, FONT_ANTIALIAS, GRAY)
                if self.hover_scale[i] != 1.0:
                    text = safe_scale_surface(text, self.hover_scale[i])
                text_rect = text.get_rect(topleft=item_pos)
                self.item_rects.append(text_rect)
                screen.blit(text, text_rect)
