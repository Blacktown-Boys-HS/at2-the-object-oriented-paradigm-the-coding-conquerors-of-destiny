"""
Credits scene for the RPG game.
"""
import pygame
from pathlib import Path
from globals import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SCENE_MENU,
    FPS,
    FONT_ANTIALIAS,
    WHITE,
)

from .aesthetic import (
    SharedBackground,
    draw_gothic_title,
    draw_footer_hint,
    GOTHIC_GOLD,
    GOTHIC_GOLD_DIM,
    SUBTITLE_COLOR,
)


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
            "Sri Hari Sriranganathan",
            "Shivesh Sundar",
        ]

        self.group_photo = None
        self.group_photo_rect = None
        photo_path = Path(__file__).resolve().parent.parent / "assets" / "group photo.jpg"
        try:
            photo = pygame.image.load(str(photo_path)).convert()
            photo_w, photo_h = photo.get_size()
            max_width = 400
            if photo_w > max_width:
                scale = max_width / photo_w
                new_size = (int(photo_w * scale), int(photo_h * scale))
                photo = pygame.transform.smoothscale(photo, new_size)

            self.group_photo = photo
            self.group_photo_rect = photo.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )
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

        draw_gothic_title(
            screen,
            self.title_font,
            "CREDITS",
            SCREEN_WIDTH // 2,
            100,
        )

        if self.group_photo:
            outer_rect = self.group_photo_rect.inflate(20, 20)
            pygame.draw.rect(screen, GOTHIC_GOLD_DIM, outer_rect, width=4, border_radius=4)
            pygame.draw.rect(screen, GOTHIC_GOLD, self.group_photo_rect.inflate(8, 8), width=2)
            screen.blit(self.group_photo, self.group_photo_rect)

        names_start_y = self.group_photo_rect.bottom + 60 if self.group_photo else 300
        names_text = " • ".join(self.credits_items)
        credits_text = self.credit_font.render(names_text, FONT_ANTIALIAS, WHITE)
        credits_rect = credits_text.get_rect(center=(SCREEN_WIDTH // 2, names_start_y))
        screen.blit(credits_text, credits_rect)

        team = self.credit_font.render(
            "The Coding Conquerors of Destiny",
            FONT_ANTIALIAS,
            SUBTITLE_COLOR,
        )
        team_rect = team.get_rect(center=(SCREEN_WIDTH // 2, names_start_y + 36))
        screen.blit(team, team_rect)

        draw_footer_hint(screen, self.credit_font, "Press ESC to return to menu")
