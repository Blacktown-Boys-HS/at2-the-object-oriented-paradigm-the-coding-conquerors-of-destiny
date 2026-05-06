"""
Menu scene for the RPG game.
"""
import math
import pygame
from globals import (
    SCREEN_WIDTH, WHITE, GRAY, BLUE, FPS,
    SCENE_CREDITS, SCENE_GAME, SCENE_SETTINGS, FONT_ANTIALIAS,
)
from pos import Position

from .aesthetic import SharedBackground, draw_footer_hint, safe_scale_surface

class MenuScene:
    """Main menu scene."""

    def __init__(self, title_font, menu_font, credit_font, sounds=None):
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font
        self.sounds = sounds or {}

        self.menu_items = ["Play Game", "Settings", "Credits"]
        self.selected_item = 0
        self.menu_item_rects = []
        self.hover_scale = [1.0 for _ in self.menu_items]
        self.selection_box_y = 0
        self.activation_item = None
        self.activation_progress = 0.0
        self.activation_duration = 0.18
        self.pending_scene = None
        self.last_selected_item = self.selected_item

        self.time_seconds = 0.0
        self.bg = SharedBackground()

    def handle_event(self, event):
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)
            elif event.key == pygame.K_DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._start_selection_activate()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.menu_item_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_item = i
                    self._start_selection_activate()
                    break
        return None

    def _start_selection_activate(self):
        """Play a short confirm animation before scene transition."""
        if self.activation_item is None:
            confirm_sound = self.sounds.get("confirm")
            if confirm_sound:
                confirm_sound.play()
            self.activation_item = self.selected_item
            self.activation_progress = 0.0
    
    def _get_selected_action(self):
        """Get the action for the selected menu item."""
        if self.menu_items[self.selected_item] == "Play Game":
            return SCENE_GAME
        if self.menu_items[self.selected_item] == "Settings":
            return SCENE_SETTINGS
        if self.menu_items[self.selected_item] == "Credits":
            return SCENE_CREDITS
        return None

    def _safe_scale_text(self, surface, scale_factor):
        """Scale text surfaces safely and prefer smooth scaling."""
        return safe_scale_surface(surface, scale_factor)

    def _draw_menu_title(self, screen, center_xy, pulse):
        """Styled main title: depth, outline, blue shimmer, accent rule."""
        title_str = "Pixel Warriors: Revenge of the Missing Semicolon"
        shimmer = 0.5 + 0.5 * math.sin(self.time_seconds * 2.8)
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

        for dx, dy in (
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (1, -1), (-1, 1), (1, 1),
        ):
            layer = self.title_font.render(title_str, FONT_ANTIALIAS, rim)
            composite.blit(layer, (ox + dx, oy + dy))

        composite.blit(
            self.title_font.render(title_str, FONT_ANTIALIAS, main_color),
            (ox, oy),
        )

        scaled = self._safe_scale_text(composite, pulse)
        rect = scaled.get_rect(center=center_xy)
        screen.blit(scaled, rect)

        bar_w = int(scaled.get_width() * 0.68)
        bar_y = rect.bottom + 8
        bar_x0 = center_xy[0] - bar_w // 2
        bar_x1 = center_xy[0] + bar_w // 2
        pygame.draw.line(
            screen,
            (80, 60, 120),
            (bar_x0, bar_y + 1),
            (bar_x1, bar_y + 1),
            3,
        )
        pygame.draw.line(
            screen,
            (126, 193, 245),
            (bar_x0, bar_y),
            (bar_x1, bar_y),
            2,
        )
        cx, mid_y = center_xy[0], bar_y + 12
        rh = 5 + int(2 * (0.5 + 0.5 * math.sin(self.time_seconds * 3.2)))
        pygame.draw.polygon(
            screen,
            (126, 193, 245),
            [
                (cx, mid_y - rh),
                (cx + rh, mid_y),
                (cx, mid_y + rh),
                (cx - rh, mid_y),
            ],
        )

    def consume_requested_scene(self):
        """Return and clear a deferred scene transition request."""
        scene = self.pending_scene
        self.pending_scene = None
        return scene

    def update(self, mouse_pos):
        """Update menu state."""
        self.time_seconds = pygame.time.get_ticks() / 1000.0
        dt = 1.0 / FPS

        self.bg.update(dt)

        # Check for mouse hover
        for i, rect in enumerate(self.menu_item_rects):
            if rect.collidepoint(mouse_pos):
                self.selected_item = i
                break
        if self.selected_item != self.last_selected_item:
            hover_sound = self.sounds.get("button_hover")
            if hover_sound:
                hover_sound.play()
            self.last_selected_item = self.selected_item

        # Update hover scales
        for i in range(len(self.menu_items)):
            # Selected item gets extra punch during confirm animation.
            activation_bonus = 0.0
            if self.activation_item == i:
                activation_bonus = 0.10 * (1.0 - self.activation_progress)

            if i == self.selected_item:
                self.hover_scale[i] = min(self.hover_scale[i] + 0.05, 1.10 + activation_bonus)
            else:
                self.hover_scale[i] = max(self.hover_scale[i] - 0.05, 1.0)

        # Smoothly move selection box toward selected item.
        target_y = 300 + self.selected_item * 100
        if self.selection_box_y == 0:
            self.selection_box_y = target_y
        self.selection_box_y += (target_y - self.selection_box_y) * 0.20

        if self.activation_item is not None:
            self.activation_progress += dt / self.activation_duration
            if self.activation_progress >= 1.0:
                self.pending_scene = self._get_selected_action()
                self.activation_item = None
                self.activation_progress = 0.0

    def render(self, screen):
        """Render the menu scene."""
        self.bg.draw(screen)

        screen_center = Position(SCREEN_WIDTH // 2, 0)

        # Draw title with subtle pulse.
        pulse = 1.0 + (math.sin(self.time_seconds * 2.2) * 0.02)
        title_pos = screen_center.add(Position(0, 115))
        self._draw_menu_title(screen, title_pos.to_int_tuple(), pulse)

        # Draw subtitle
        madeby_text = self.credit_font.render(
            "Made by The Coding Conquerors of Destiny™",
            FONT_ANTIALIAS,
            (215, 215, 215),
        )
        madeby_pos = screen_center.add(Position(0, 225))
        madeby_rect = madeby_text.get_rect(center=madeby_pos.to_int_tuple())
        screen.blit(madeby_text, madeby_rect)

        # Draw selection highlight box.
        selection_rect = pygame.Rect(130, int(self.selection_box_y) - 8, 440, 76)
        box_surface = pygame.Surface((selection_rect.width, selection_rect.height), pygame.SRCALPHA)
        box_alpha = 22
        if self.activation_item == self.selected_item:
            box_alpha = 22 + int(70 * (1.0 - self.activation_progress))
        box_surface.fill((255, 255, 255, box_alpha))
        screen.blit(box_surface, selection_rect.topleft)
        border_color = (130, 130, 130)
        if self.activation_item == self.selected_item:
            border_color = (220, 200, 120)
        pygame.draw.rect(screen, border_color, selection_rect, width=2, border_radius=8)

        # Draw menu items
        menu_start_pos = Position(150, 300)
        self.menu_item_rects = []
        for i, item in enumerate(self.menu_items):
            if i == self.selected_item:
                # Render ">" in Blue, item in white
                arrow_text = self.menu_font.render("> ", FONT_ANTIALIAS, BLUE)
                item_text = self.menu_font.render(item, FONT_ANTIALIAS, WHITE)
                
                item_pos = menu_start_pos.add(Position(0, i * 100))
                
                # Draw arrow
                arrow_rect = arrow_text.get_rect(topleft=item_pos.to_int_tuple())
                
                # Apply hover scale to both parts
                if self.hover_scale[i] != 1.0:
                    arrow_text = self._safe_scale_text(arrow_text, self.hover_scale[i])
                    item_text = self._safe_scale_text(item_text, self.hover_scale[i])
                
                arrow_rect = arrow_text.get_rect(topleft=item_pos.to_int_tuple())
                item_rect = item_text.get_rect(topleft=(arrow_rect.right, item_pos.y))
                
                self.menu_item_rects.append(arrow_rect.union(item_rect))
                screen.blit(arrow_text, arrow_rect)
                screen.blit(item_text, item_rect)
            else:
                color = GRAY
                text = self.menu_font.render(item, FONT_ANTIALIAS, color)
                
                # Apply hover scale
                if self.hover_scale[i] != 1.0:
                    text = self._safe_scale_text(text, self.hover_scale[i])
                
                item_pos = menu_start_pos.add(Position(0, i * 100))
                text_rect = text.get_rect(topleft=item_pos.to_int_tuple())
                self.menu_item_rects.append(text_rect)
                screen.blit(text, text_rect)

        draw_footer_hint(
            screen,
            self.credit_font,
            "Use UP/DOWN or mouse to select, ENTER/SPACE to confirm",
        )
