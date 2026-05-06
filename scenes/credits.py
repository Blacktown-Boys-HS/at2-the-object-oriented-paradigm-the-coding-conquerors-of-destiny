"""
Credits scene for the RPG game.
"""
import pygame
from pathlib import Path
from globals import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, SCENE_MENU, FPS, FONT_ANTIALIAS, BLUE

from pos import Position

from .aesthetic import SharedBackground, draw_pulsing_title, draw_footer_hint
class CreditsScene:
    """Credits scene."""

    def __init__(self, title_font, menu_font, credit_font, sounds=None):
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font
        self.sounds = sounds or {}

        self.bg = SharedBackground()
        self.time_seconds = 0.0

        self.credits_items = [
            "Angadjot Dhaliwal",
            "Sri Hari Srinigganathan",
            "Shivesh Sundar",
        ]
        
        # Load group photo
        self.group_photo = None
        self.group_photo_rect = None
        photo_path = Path(__file__).resolve().parent.parent / "assets" / "group photo.jpg"
        try:
            photo = pygame.image.load(str(photo_path)).convert()
            # Scale photo to fit nicely (max 400px wide, maintain aspect ratio)
            photo_w, photo_h = photo.get_size()
            max_width = 400
            if photo_w > max_width:
                scale = max_width / photo_w
                new_size = (int(photo_w * scale), int(photo_h * scale))
                photo = pygame.transform.smoothscale(photo, new_size)
            
            self.group_photo = photo
            # Position in center of screen
            self.group_photo_rect = photo.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        except (FileNotFoundError, pygame.error):
            self.group_photo = None

    def handle_event(self, event):
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return SCENE_MENU
        return None

    def update(self, mouse_pos):
        """Update credits state."""
        self.time_seconds = pygame.time.get_ticks() / 1000.0
        self.bg.update(1.0 / FPS)

    def render(self, screen):
        """Render the credits scene."""
        self.bg.draw(screen)

        draw_pulsing_title(
            screen,
            self.title_font,
            "CREDITS",
            SCREEN_WIDTH // 2,
            115,
            self.time_seconds,
        )

        # Draw group photo with fancy border first
        if self.group_photo:
            # Draw outer glow border (BLUE/gold with pulsing effect)
            border_width = 8
            border_color_intensity = int(200 + 55 * (0.5 + 0.5 * __import__("math").sin(self.time_seconds * 3)))
            border_color = (min(255, border_color_intensity), min(255, border_color_intensity), 0)
            
            # Outer border rect with padding
            outer_rect = self.group_photo_rect.inflate(border_width * 2 + 4, border_width * 2 + 4)
            pygame.draw.rect(screen, border_color, outer_rect, border_width)
            
            # Inner shadow border (dark)
            inner_shadow_rect = self.group_photo_rect.inflate(4, 4)
            pygame.draw.rect(screen, (0, 0, 0), inner_shadow_rect, 2)
            
            # Draw the photo
            screen.blit(self.group_photo, self.group_photo_rect)

        # Draw names below the photo (horizontally centered)
        names_start_y = self.group_photo_rect.bottom + 60 if self.group_photo else 300
        names_text = " • ".join(self.credits_items)
        
        # Add pulsing glow effect around names
        glow_intensity = int(100 + 155 * (0.5 + 0.5 * __import__("math").sin(self.time_seconds * 2)))
        glow_color = (glow_intensity, glow_intensity // 2, 0)  # Orange/gold glow
        
        # Draw glow effect (multiple layers for depth)
        glow_font_size = int(self.credit_font.get_height() * 1.5)
        for offset in range(3, 0, -1):
            glow_alpha = int(100 * (1 - offset / 3))
            glow_surf = pygame.Surface((SCREEN_WIDTH, 100), pygame.SRCALPHA)
            temp_font = pygame.font.Font(None, self.credit_font.get_height())
            glow_text = temp_font.render(names_text, FONT_ANTIALIAS, (*glow_color, glow_alpha))
            glow_rect = glow_text.get_rect(center=(SCREEN_WIDTH // 2, names_start_y))
            glow_surf.blit(glow_text, glow_rect)
            screen.blit(glow_surf, (0, 0))
        
        # Draw main names text
        credits_text = self.credit_font.render(names_text, FONT_ANTIALIAS, WHITE)
        credits_rect = credits_text.get_rect(center=(SCREEN_WIDTH // 2, names_start_y))
        screen.blit(credits_text, credits_rect)
        
        # Draw decorative stars/sparkles around names
        import math
        star_radius = 200
        num_stars = 8
        for i in range(num_stars):
            angle = (self.time_seconds * 1.5 + (2 * math.pi * i / num_stars)) % (2 * math.pi)
            star_x = SCREEN_WIDTH // 2 + math.cos(angle) * star_radius
            star_y = names_start_y + math.sin(angle) * (star_radius // 2)
            star_size = int(3 + 2 * math.sin(self.time_seconds * 3 + i))
            pygame.draw.circle(screen, BLUE, (int(star_x), int(star_y)), max(1, star_size))

        draw_footer_hint(screen, self.credit_font, "Press ESC to return to menu")
