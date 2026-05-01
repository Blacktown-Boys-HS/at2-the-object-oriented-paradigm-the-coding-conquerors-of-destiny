"""
Credits scene for the RPG game.
"""
import pygame
from globals import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GRAY, BACKGROUND,
    SCENE_MENU
)
from pos import Position

class CreditsScene:
    """Credits scene."""
    
    def __init__(self, title_font, menu_font, credit_font):
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font
        
        self.fade_alpha = 255
        self.is_fading = False
        
        self.credits_items = [
            "Software Assessment",
            "",
            "Made by The Coding Conquerors of Destiny™",
            "",
            "Blacktown Boys High School"
        ]
    
    def handle_event(self, event):
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.is_fading = True
                return SCENE_MENU
        return None
    
    def update(self, mouse_pos):
        """Update credits state."""
        if self.is_fading:
            self.fade_alpha = max(self.fade_alpha - 8, 0)
            if self.fade_alpha == 0:
                self.is_fading = False
    
    def render(self, screen):
        """Render the credits scene."""
        screen.fill(BACKGROUND)
        
        # Create fade surface
        fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_surface.set_alpha(255 - self.fade_alpha)
        fade_surface.fill(BACKGROUND)
        
        screen_center = Position(SCREEN_WIDTH // 2, 0)
        
        # Draw title
        credits_title = self.title_font.render("CREDITS", False, WHITE)
        title_pos = screen_center.add(Position(0, 80))
        credits_title_rect = credits_title.get_rect(center=title_pos.to_int_tuple())
        screen.blit(credits_title, credits_title_rect)
        
        # Draw credits items
        credits_start_pos = Position(SCREEN_WIDTH // 2, 200)
        for i, item in enumerate(self.credits_items):
            if item:
                credits_text = self.credit_font.render(item, False, WHITE)
                item_pos = credits_start_pos.add(Position(0, i * 60))
                credits_rect = credits_text.get_rect(center=item_pos.to_int_tuple())
                screen.blit(credits_text, credits_rect)
        
        # Draw "Press ESC to return" hint
        esc_text = self.credit_font.render("Press ESC to return to menu", False, GRAY)
        esc_pos = Position(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        esc_rect = esc_text.get_rect(center=esc_pos.to_int_tuple())
        screen.blit(esc_text, esc_rect)
        
        # Apply fade overlay
        if self.is_fading:
            screen.blit(fade_surface, (0, 0))
