from pathlib import Path
import pygame

from globals import SCREEN_WIDTH, SCREEN_HEIGHT

SPLASH_IMAGE_NAME = "charlie_kirk_engine.png"
SPLASH_FADE_SPEED = 5
SPLASH_HOLD_FRAMES = 72
SPLASH_DISPLAY_SCALE = 0.50

class SplashScreen:
    """Opening splash screen with fade in, hold, and fade out."""
    def __init__(self):
        self.surface = None
        self.rect = None
        self.phase = "fade_in"
        self.alpha = 0 
        self.hold_left = SPLASH_HOLD_FRAMES
        self.active = False

        splash_path = Path(__file__).resolve().parent / "assets" / SPLASH_IMAGE_NAME

        try:
            self.surface = self._load_image(splash_path)
            if self.surface is not None:
                self.rect = self.surface.get_rect(
                        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

                )
                self.active = True
        except (FileNotFoundError, pygame.error, ValueError):
            self.surface = None
            self.rect = None
            self.active = False

    def _load_image(self, path):
        """Scale splash art to fit the window."""
        image = pygame.image.load(str(path)).convert_alpha()
        image_width, image_height = image.get_size()

        if image_width <= 0 or image_height <= 0:
            return None

        scale = min(
            SCREEN_WIDTH / image_width,
            SCREEN_HEIGHT, image_height
        ) * SPLASH_DISPLAY_SCALE

        new_width = max(1, int(image_width * scale))
        new_height = max(1, int(image_height * scale))

        return pygame.transform.smoothscale(image, (new_width, new_height))

    def handle_event(self, event):
        """Skip the splash screen when the player presses a key or clicks."""
        if not self.active:
            return False

        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self.skip()
            return True

        return False

    def skip(self):
        """Immediately end the splash screen."""
        self.active = False
        self.phase = "done"

    def update(self):
        """
        Update the splash animation.

        Returns True only on the frame where the splash finishes.
        """
        if not self.active:
            return False

        finished = False

        if self.phase == "fade_in":
            self.alpha = min(255, self.alpha + SPLASH_FADE_SPEED)
            if self.alpha >= 255:
                self.alpha = 255
                self.phase = "hold"

        elif self.phase == "hold":
            self.hold_left -= 1
            if self.hold_left <= 0:
                self.phase = "fade_out"

        elif self.phase == "fade_out":
            self.alpha = max(0, self.alpha - SPLASH_FADE_SPEED)
            if self.alpha <= 0:
                self.alpha = 0 
                self.active = False
                self.phase = "done"
                finished = True

        return finished

    def draw(self, screen):
        """Draw the splash image."""
        if self.surface is None or self.rect is None:
            return

        splash_copy = self.surface.copy()
        splash_copy.set_alpha(self.alpha)
        screen.blit(splash_copy, self.rect)

