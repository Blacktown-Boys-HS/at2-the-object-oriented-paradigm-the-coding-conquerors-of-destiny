from pathlib import Path
import pygame

class CustomCursor:
    """Custom mouse cursor with a small click-scale effect."""

    def __init__(self):
        self.pressed = False
        self.scale = 1.25
        self.default_scale = 1.25
        self.presed_scale = 1.08
        self.scale_speed = 0.35
        self.image = None

        cusor_path = Path(__file__).resolve().parent / "assets" / "cursor" / "8_white.png"

        try:
            self.image = pygame.image.load(str(cusor_path)).convert()
            self.image.set_colorkey(self.image.get_at((0, 0)))
            pygame.mouse.set_visible(False)
        except (FileNotFoundError, pygame.error):
            pygame.mouse.set_visible(True)

    def handle_event(self, event):
        """Track whether the mouse button is pressed."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.pressed = False

    def draw(self, screen, mouse_pos):
        """Draw the custom cursor at the current mouse position."""
        if self.image is None:
            return

        target_scale = self.presed_scale if self.pressed else self.default_scale
        self.scale += (target_scale - self.scale) * self.scale_speed

        scaled_size = (
            max(1, int(self.image.get_width() * self.scale)),
            max(1, int(self.image.get_height() * self.scale)),
        )

        cursor_surface = pygame.transform.smoothscale(self.image, scaled_size)
        cursor_rect = cursor_surface.get_rect(topleft=mouse_pos)
        screen.blit(cursor_surface, cursor_rect)