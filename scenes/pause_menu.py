"""
Pause menu for the RPG game.
"""

from matplotlib.font_manager import fontManager
from matplotlib.pyplot import box
import pygame
import math
from globals import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_ANTIALIAS, BLUE, GRAY, WHITE
from scenes.aesthetic import safe_scale_surface

class PauseMenu:
    """Handles pause menu rendering and state."""
    ITEMS = ["Resume", "Settings", "Main Menu"]

    def __init__(self, title_font, menu_font, sounds=None):
        self.title_font = title_font
        self.menu_font = menu_font
        self.sounds = sounds or {}

        self.selected = 0
        self.last_selected = 0
        self.item_rects = []
        self.hover_scale = [1.0 for _ in self.ITEMS]
        self.selection_y = 0

        self.activation_item = None
        self.activation_progress = 0.0
        self.activation_duration = 0.18
        self.pending_item = None

    def handle_event(self, event):
        """Handle keyboard and mouse input. Returns True if event was consumed."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.ITEMS)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.ITEMS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._start_activate()
            return True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected = i
                    self._start_activate()
                    break
            return True
        return False
    
    def _start_activate(self):
        if self.activation_item is None:
            confirm_sound = self.sounds.get("confirm")
            if confirm_sound:
                confirm_sound.play()
            self.activation_item = self.selected
            self.activation_progress = 0.0

    def update(self, dt, mouse_pos, time_seconds):
        """Update hover states and activation animation."""
        for i, rect in enumerate(self.item_rects):
            if rect.collidepoint(mouse_pos):
                self.selected = 1
                break

        if self.selected != self.last_selected:
            hover_sound = self.sounds.get("button_hover")
            if hover_sound:
                hover_sound.play()
            self.last_selected = 1

        for i in range(len(self.ITEMS)):
            activation_bonus = 0.0
            if self.activation_item == i:
                activation_bonus = 0.10 * (1.0 - self.activation_progress)
            
            if i == self.selected:
                self.hover_scale[i] = min(self.hover_scale[i] + 0.05, 1.10 + activation_bonus)
            else:
                self.hover_scale[i] = max(self.hover_scale[i] - 0.05, 1.0)

        target_y = 320 + self.selected * 80
        if self.selection_y == 0:
            self.selection_y = target_y
        self.selection_y += (target_y - self.selection_y) * 0.20

        if self.activation_item is not None:
            self.activation_progress += dt / self.activation_duration
            if self.activation_duration >= 1.0:
                self.pending_action = self.ITEMS[self.activation_item]
                self.activation_item = None
                self.activaton = 0.0
    
    def consume_action(self):
        """Return and clear the pending action."""
        action = self.pending_action
        self.pending_action = None
        return action
    
    def _draw_title(self, screen, time_seconds):
        title_str = "PAUSED"
        shimmer = 0.5 + 0.5 * math.sin(time_seconds * 2.8)
        main_color = (
            int(100 + 26 * shimmer),
            int(160 + 33 * shimmer),
            int(220 + 25 * shimmer),
        )
        shadow_deep = (14, 10, 32)
        rim = (72, 58, 120)

        base = self.title_font.render(title_str, FONT_ANTIALIAS, WHITE)
        w, h = base.get_width(), base.get_height()
        pad = 10
        composite = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
        ox, oy = pad, pad

        for d in (5, 4, 3, 2, 1):
            layer = self.title_font.render(title_str, FONT_ANTIALIAS, shadow_deep)
            composite.blit(layer, (ox + d, oy + d))
        
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
            layer = self.title_font.render(title_str, FONT_ANTIALIAS, rim)
            composite.blit(layer, (ox + dx, oy + dy))
        
        composite.blit(self.title_font.render(title_str, FONT_ANTIALIAS, main_color), (ox, oy))

        pulse = 1.0 + math.sin(time_seconds * 2.2) * 0.02
        scaled = safe_scale_surface(composite, pulse)
        rect = scaled.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(scaled, rect)
    
    def render(self, screen, time_seconds):
        """Render the full pause overlay."""
        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        self._draw_title(screen, time_seconds)

        # Selection highlight box
        selection_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, int(self.selection_y) - 8, 360, 60)
        box_surface = pygame.Surface((selection_rect.width, selection_rect.height), pygame.SRCALPHA)
        box_alpha = 22
        if self.activation_item == self.selected:
            box_alpha = 22 + int(70 * (1.0 - self.activation_progress))
        box_surface.fill((255, 255, 255, box_alpha))
        screen.blit(box_surface, selection_rect.topleft)
        border_color = (130, 130, 130)
        if self.activation_item == self.selected:
            border_color == (220, 200, 120)
        pygame.draw.rect(screen, border_color, selection_rect, width=2, border_radius=8)

        # Menu items
        menu_start_x = SCREEN_WIDTH // 2 - 120
        menu_start_y = 320
        self.item_rects = []
        for i, item in enumerate(self.ITEMS):
            if i == self.selected:
                arrow_text = self.menu_font.render("> ", FONT_ANTIALIAS, BLUE)
                item_text = self.menu_font.render(item, FONT_ANTIALIAS, WHITE)
                item_pos = (menu_start_x, menu_start_y + i * 80)
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
                item_pos = (menu_start_x, menu_start_y + i * 80)
                text_rect = text.get_rect(topleft=item_pos)
                self.item_rects.append(text_rect)
                screen.blit(text, text_rect)


