"""
Menu scene for the RPG game.
"""
import math
import random
import pygame
from globals import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GRAY, BACKGROUND, YELLOW,
    SCENE_CREDITS, SCENE_GAME, SCENE_SETTINGS
)
from pos import Position


class MenuScene:
    """Main menu scene."""

    def __init__(self, title_font, menu_font, credit_font):
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font

        self.menu_items = ["Play Game", "Settings", "Credits"]
        self.selected_item = 0
        self.menu_item_rects = []
        self.hover_scale = [1.0 for _ in self.menu_items]
        self.selection_box_y = 0

        self.time_seconds = 0.0
        self.background_dots = []
        for _ in range(60):
            self.background_dots.append(
                {
                    "x": random.randint(0, SCREEN_WIDTH),
                    "y": random.randint(0, SCREEN_HEIGHT),
                    "radius": random.randint(1, 3),
                    "speed": random.uniform(0.3, 1.4),
                    "alpha": random.randint(40, 120),
                }
            )

    def handle_event(self, event):
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)
            elif event.key == pygame.K_DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._get_selected_action()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.menu_item_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_item = i
                    return self._get_selected_action()
        return None
    
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
        target_width = max(1, int(surface.get_width() * scale_factor))
        target_height = max(1, int(surface.get_height() * scale_factor))
        converted = surface.convert_alpha()
        return pygame.transform.smoothscale(converted, (target_width, target_height))

    def update(self, mouse_pos):
        """Update menu state."""
        self.time_seconds = pygame.time.get_ticks() / 1000.0

        # Move background dots down slowly to add depth.
        for dot in self.background_dots:
            dot["y"] += dot["speed"]
            if dot["y"] > SCREEN_HEIGHT + dot["radius"]:
                dot["y"] = -dot["radius"]
                dot["x"] = random.randint(0, SCREEN_WIDTH)

        # Check for mouse hover
        for i, rect in enumerate(self.menu_item_rects):
            if rect.collidepoint(mouse_pos):
                self.selected_item = i
                break

        # Update hover scales
        for i in range(len(self.menu_items)):
            if i == self.selected_item:
                self.hover_scale[i] = min(self.hover_scale[i] + 0.05, 1.10)
            else:
                self.hover_scale[i] = max(self.hover_scale[i] - 0.05, 1.0)

        # Smoothly move selection box toward selected item.
        target_y = 300 + self.selected_item * 100
        if self.selection_box_y == 0:
            self.selection_box_y = target_y
        self.selection_box_y += (target_y - self.selection_box_y) * 0.20

    def render(self, screen):
        """Render the menu scene."""
        screen.fill(BACKGROUND)

        # Draw a soft vertical gradient for better contrast.
        for y in range(0, SCREEN_HEIGHT, 4):
            shade = 30 + int((y / SCREEN_HEIGHT) * 20)
            pygame.draw.rect(screen, (shade, shade, shade + 8), (0, y, SCREEN_WIDTH, 4))

        # Draw moving background dots.
        dot_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for dot in self.background_dots:
            color = (255, 255, 255, dot["alpha"])
            pygame.draw.circle(dot_surface, color, (int(dot["x"]), int(dot["y"])), dot["radius"])
        screen.blit(dot_surface, (0, 0))

        screen_center = Position(SCREEN_WIDTH // 2, 0)

        # Draw title with subtle pulse.
        pulse = 1.0 + (math.sin(self.time_seconds * 2.2) * 0.02)
        title_text = self.title_font.render("RPG Placeholder Title", False, WHITE)
        title_text = self._safe_scale_text(title_text, pulse)
        title_pos = screen_center.add(Position(0, 115))
        title_rect = title_text.get_rect(center=title_pos.to_int_tuple())
        screen.blit(title_text, title_rect)

        # Draw subtitle
        madeby_text = self.credit_font.render(
            "Made by The Coding Conquerors of Destiny",
            False,
            (215, 215, 215)
        )
        madeby_pos = screen_center.add(Position(0, 225))
        madeby_rect = madeby_text.get_rect(center=madeby_pos.to_int_tuple())
        screen.blit(madeby_text, madeby_rect)

        # Draw selection highlight box.
        selection_rect = pygame.Rect(130, int(self.selection_box_y) - 8, 440, 76)
        box_surface = pygame.Surface((selection_rect.width, selection_rect.height), pygame.SRCALPHA)
        box_surface.fill((255, 255, 255, 22))
        screen.blit(box_surface, selection_rect.topleft)
        pygame.draw.rect(screen, (130, 130, 130), selection_rect, width=2, border_radius=8)

        # Draw menu items
        menu_start_pos = Position(150, 300)
        self.menu_item_rects = []
        for i, item in enumerate(self.menu_items):
            if i == self.selected_item:
                # Render ">" in yellow, item in white
                arrow_text = self.menu_font.render("> ", False, YELLOW)
                item_text = self.menu_font.render(item, False, WHITE)
                
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
                text = self.menu_font.render(item, False, color)
                
                # Apply hover scale
                if self.hover_scale[i] != 1.0:
                    text = self._safe_scale_text(text, self.hover_scale[i])
                
                item_pos = menu_start_pos.add(Position(0, i * 100))
                text_rect = text.get_rect(topleft=item_pos.to_int_tuple())
                self.menu_item_rects.append(text_rect)
                screen.blit(text, text_rect)

        controls_text = self.credit_font.render(
            "Use UP/DOWN or mouse to select, ENTER/SPACE to confirm",
            False,
            (190, 190, 190)
        )
        controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 45))
        screen.blit(controls_text, controls_rect)
