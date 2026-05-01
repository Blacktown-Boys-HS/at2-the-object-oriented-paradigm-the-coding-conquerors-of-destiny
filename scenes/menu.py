"""
Menu scene for the RPG game.
"""
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
        self.hover_scale = [1.0, 1.0, 1.0]
        self.fade_alpha = 255
        self.is_fading = False
    
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
            self.is_fading = True
            return SCENE_GAME
        elif self.menu_items[self.selected_item] == "Settings":
            print("Opening settings...")
            self.is_fading = True
            return SCENE_SETTINGS
        elif self.menu_items[self.selected_item] == "Credits":
            self.is_fading = True
            return SCENE_CREDITS
        return None
    
    def update(self, mouse_pos):
        """Update menu state."""
        # Handle fade animation
        if self.is_fading:
            self.fade_alpha = max(self.fade_alpha - 8, 0)
            if self.fade_alpha == 0:
                self.is_fading = False
        
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
        screen.fill(BACKGROUND)
        
        # Create a surface for fade effect
        fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_surface.set_alpha(255 - self.fade_alpha)
        fade_surface.fill(BACKGROUND)
        
        screen_center = Position(SCREEN_WIDTH // 2, 0)
        
        # Draw title
        title_text = self.title_font.render("RPG Placeholder Title", False, WHITE)
        title_pos = screen_center.add(Position(0, 120))
        title_rect = title_text.get_rect(center=title_pos.to_int_tuple())
        screen.blit(title_text, title_rect)
        
        # Draw subtitle
        madeby_text = self.credit_font.render("Made by The Coding Conquerors of Destiny™", False, WHITE)
        madeby_pos = screen_center.add(Position(0, 240))
        madeby_rect = madeby_text.get_rect(center=madeby_pos.to_int_tuple())
        screen.blit(madeby_text, madeby_rect)
        
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
                    scaled_width_arrow = int(arrow_text.get_width() * self.hover_scale[i])
                    scaled_height_arrow = int(arrow_text.get_height() * self.hover_scale[i])
                    arrow_text = pygame.transform.scale(arrow_text, (scaled_width_arrow, scaled_height_arrow))
                    
                    scaled_width_item = int(item_text.get_width() * self.hover_scale[i])
                    scaled_height_item = int(item_text.get_height() * self.hover_scale[i])
                    item_text = pygame.transform.scale(item_text, (scaled_width_item, scaled_height_item))
                
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
                    scaled_width = int(text.get_width() * self.hover_scale[i])
                    scaled_height = int(text.get_height() * self.hover_scale[i])
                    text = pygame.transform.scale(text, (scaled_width, scaled_height))
                
                item_pos = menu_start_pos.add(Position(0, i * 100))
                text_rect = text.get_rect(topleft=item_pos.to_int_tuple())
                self.menu_item_rects.append(text_rect)
                screen.blit(text, text_rect)
        
        # Apply fade out overlay when transitioning
        if self.is_fading:
            screen.blit(fade_surface, (0, 0))
