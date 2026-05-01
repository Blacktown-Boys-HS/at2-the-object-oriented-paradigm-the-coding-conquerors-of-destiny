"""
Menu scene for the RPG game.
"""
import pygame
from globals import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GRAY, BLACK,
    SCENE_CREDITS, SCENE_GAME, SCENE_SETTINGS
)


class MenuScene:
    """Main menu scene."""
    
    def __init__(self, title_font, menu_font, credit_font):
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font
        
        self.menu_items = ["Play Game", "Settings", "Credits"]
        self.selected_item = 0
        self.menu_item_rects = []
        self.hover_scale = [1.0, 1.0, 1.0]
    
    def handle_event(self, event):
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)
            elif event.key == pygame.K_DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)
            elif event.key == pygame.K_RETURN:
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
            print("Starting game...")
            return SCENE_GAME
        elif self.menu_items[self.selected_item] == "Settings":
            print("Opening settings...")
            return SCENE_SETTINGS
        elif self.menu_items[self.selected_item] == "Credits":
            return SCENE_CREDITS
        return None
    
    def update(self, mouse_pos):
        """Update menu state."""
        # Check for mouse hover
        for i, rect in enumerate(self.menu_item_rects):
            if rect.collidepoint(mouse_pos):
                self.selected_item = i
                break
        
        # Update hover scales
        for i in range(len(self.menu_items)):
            if i == self.selected_item:
                self.hover_scale[i] = min(self.hover_scale[i] + 0.05, 1.15)
            else:
                self.hover_scale[i] = max(self.hover_scale[i] - 0.05, 1.0)
    
    def render(self, screen):
        """Render the menu scene."""
        screen.fill(BLACK)
        
        # Draw title
        title_text = self.title_font.render("RPG Placeholder Title", False, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        screen.blit(title_text, title_rect)
        
        # Draw subtitle
        madeby_text = self.credit_font.render("Made by The Coding Conquerors of Destiny™", False, WHITE)
        madeby_rect = madeby_text.get_rect(center=(SCREEN_WIDTH // 2, 240))
        screen.blit(madeby_text, madeby_rect)
        
        # Draw menu items
        menu_start_y = 300
        self.menu_item_rects = []
        for i, item in enumerate(self.menu_items):
            if i == self.selected_item:
                color = WHITE
                text = self.menu_font.render(f"> {item} <", False, color)
            else:
                color = GRAY
                text = self.menu_font.render(item, False, color)
            
            # Apply hover scale
            if self.hover_scale[i] != 1.0:
                scaled_width = int(text.get_width() * self.hover_scale[i])
                scaled_height = int(text.get_height() * self.hover_scale[i])
                text = pygame.transform.scale(text, (scaled_width, scaled_height))
            
            text_rect = text.get_rect(topleft=(150, menu_start_y + i * 100))
            self.menu_item_rects.append(text_rect)
            screen.blit(text, text_rect)
