"""
Menu scene for the RPG game.
"""
import pygame
from globals import (
    SCREEN_WIDTH,
    FPS,
    SCENE_CREDITS,
    SCENE_GAME,
    SCENE_SETTINGS,
    SCENE_TUTORIAL,
    FONT_ANTIALIAS,
    GAME_TITLE,
)
from pos import Position

from .aesthetic import (
    SharedBackground,
    draw_footer_hint,
    draw_gothic_title,
    draw_gothic_selection_box,
    draw_gothic_menu_item,
    safe_scale_surface,
    SUBTITLE_COLOR,
)


class MenuScene:
    """Main menu scene."""

    _MENU_START_Y = 285
    _MENU_ITEM_SPACING = 76
    _SELECTION_W = 440
    _SELECTION_H = 64
    _SELECTION_X = 130

    def __init__(self, title_font, menu_font, credit_font, sounds=None):
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font
        self.sounds = sounds or {}

        self.menu_items = ["Play Game", "Tutorial", "Settings", "Credits"]
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
        item = self.menu_items[self.selected_item]
        if item == "Play Game":
            return SCENE_GAME
        if item == "Tutorial":
            return SCENE_TUTORIAL
        if item == "Settings":
            return SCENE_SETTINGS
        if item == "Credits":
            return SCENE_CREDITS
        return None

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

        for i, rect in enumerate(self.menu_item_rects):
            if rect.collidepoint(mouse_pos):
                self.selected_item = i
                break
        if self.selected_item != self.last_selected_item:
            hover_sound = self.sounds.get("button_hover")
            if hover_sound:
                hover_sound.play()
            self.last_selected_item = self.selected_item

        for i in range(len(self.menu_items)):
            activation_bonus = 0.0
            if self.activation_item == i:
                activation_bonus = 0.10 * (1.0 - self.activation_progress)

            if i == self.selected_item:
                self.hover_scale[i] = min(self.hover_scale[i] + 0.05, 1.10 + activation_bonus)
            else:
                self.hover_scale[i] = max(self.hover_scale[i] - 0.05, 1.0)

        target_y = self._MENU_START_Y + self.selected_item * self._MENU_ITEM_SPACING
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

        draw_gothic_title(
            screen,
            self.title_font,
            GAME_TITLE,
            SCREEN_WIDTH // 2,
            100,
        )

        madeby_text = self.credit_font.render(
            "Made by The Coding Conquerors of Destiny™",
            FONT_ANTIALIAS,
            SUBTITLE_COLOR,
        )
        madeby_pos = screen_center.add(Position(0, 195))
        madeby_rect = madeby_text.get_rect(center=madeby_pos.to_int_tuple())
        screen.blit(madeby_text, madeby_rect)

        selection_rect = pygame.Rect(
            self._SELECTION_X,
            int(self.selection_box_y) - 6,
            self._SELECTION_W,
            self._SELECTION_H,
        )
        draw_gothic_selection_box(
            screen,
            selection_rect,
            activating=self.activation_item == self.selected_item,
            activation_progress=self.activation_progress,
        )

        menu_start_pos = Position(150, self._MENU_START_Y)
        self.menu_item_rects = []
        for i, item in enumerate(self.menu_items):
            item_pos = menu_start_pos.add(Position(0, i * self._MENU_ITEM_SPACING))
            rect = draw_gothic_menu_item(
                screen,
                self.menu_font,
                item,
                item_pos.to_int_tuple(),
                i == self.selected_item,
                self.hover_scale[i],
                safe_scale_surface,
            )
            self.menu_item_rects.append(rect)

        draw_footer_hint(
            screen,
            self.credit_font,
            "Use UP/DOWN or mouse to select, ENTER/SPACE to confirm",
        )
