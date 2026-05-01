"""
Settings scene for the RPG game.
"""
import pygame
from globals import BLACK, WHITE, SCENE_MENU


class SettingsScene:
    """Settings scene."""
    
    def __init__(self, title_font, menu_font, credit_font):
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font
    
    def handle_event(self, event):
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return SCENE_MENU
        return None
    
    def update(self, mouse_pos):
        """Update settings state."""
        pass
    
    def render(self, screen):
        """Render the settings scene."""
        screen.fill(BLACK)
        
        settings_text = self.title_font.render("Settings Coming Soon!", False, WHITE)
        settings_rect = settings_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(settings_text, settings_rect)
        
        esc_text = self.credit_font.render("Press ESC to return to menu", False, WHITE)
        esc_rect = esc_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 100))
        screen.blit(esc_text, esc_rect)
