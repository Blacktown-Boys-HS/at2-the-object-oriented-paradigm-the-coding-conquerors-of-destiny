"""
Credits scene for the RPG game.
"""
import pygame
from globals import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GRAY, BLACK,
    SCENE_MENU
)


class CreditsScene:
    """Credits scene."""
    
    def __init__(self, title_font, menu_font, credit_font):
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font
        
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
                return SCENE_MENU
        return None
    
    def update(self, mouse_pos):
        """Update credits state."""
        pass
    
    def render(self, screen):
        """Render the credits scene."""
        screen.fill(BLACK)
        
        # Draw title
        credits_title = self.title_font.render("CREDITS", False, WHITE)
        credits_title_rect = credits_title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(credits_title, credits_title_rect)
        
        # Draw credits items
        credits_start_y = 200
        for i, item in enumerate(self.credits_items):
            if item:  # Only render non-empty lines
                credits_text = self.credit_font.render(item, False, WHITE)
                credits_rect = credits_text.get_rect(center=(SCREEN_WIDTH // 2, credits_start_y + i * 60))
                screen.blit(credits_text, credits_rect)
        
        # Draw "Press ESC to return" hint
        esc_text = self.credit_font.render("Press ESC to return to menu", False, GRAY)
        esc_rect = esc_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(esc_text, esc_rect)
