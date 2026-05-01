"""
Placeholder game scene for the RPG game.
"""
import pygame
from globals import BACKGROUND, WHITE, SCENE_MENU
from pos import Position


class GameScene:
    """Game scene."""
    
    def __init__(self, title_font, menu_font, credit_font):
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font
        self.fade_alpha = 255
        self.is_fading = False
    
    def handle_event(self, event):
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.is_fading = True
                return SCENE_MENU
        return None
    
    def update(self, mouse_pos):
        """Update game state."""
        if self.is_fading:
            self.fade_alpha = max(self.fade_alpha - 8, 0)
            if self.fade_alpha == 0:
                self.is_fading = False
    
    def render(self, screen):
        """Render the game scene."""
        screen.fill((150, 150, 150))
        
        # Create fade surface
        fade_surface = pygame.Surface((screen.get_width(), screen.get_height()))
        fade_surface.set_alpha(255 - self.fade_alpha)
        fade_surface.fill(BACKGROUND)
        
        screen_pos = Position(screen.get_width() // 2, screen.get_height() // 2)
        
        game_text = self.title_font.render("Game Coming Soon!", False, (50, 50, 50))
        game_pos = screen_pos
        game_rect = game_text.get_rect(center=game_pos.to_int_tuple())
        screen.blit(game_text, game_rect)
        
        esc_text = self.credit_font.render("Press ESC to return to menu", False, (50, 50, 50))
        esc_pos = screen_pos.add(Position(0, 100))
        esc_rect = esc_text.get_rect(center=esc_pos.to_int_tuple())
        screen.blit(esc_text, esc_rect)
        
        # Apply fade overlay
        if self.is_fading:
            screen.blit(fade_surface, (0, 0))
