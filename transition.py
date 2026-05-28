import pygame

from globals import SCREEN_WIDTH, SCREEN_HEIGHT

class SceneTransition:
    def __init__(self):
        """Handles fade transitions between scenes."""
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.surface.fill((0, 0, 0))

        self.alpha = 255
        self.speed = 12
        self.direction = -1
        self.active = True
        self.pending_scene = None

    def start_fade_out(self, next_scene):
        """Fade to black before switching scene."""
        self.pending_scene = next_scene
        self.active = True
        self.direction = 1
        self.alpha = 0

    def start_fade_in(self):
        """Fade from black into the current scene."""
        self.active = True
        self.direction = -1
        self.alpha = 255

    def update(self):
        """
        Update the fade.

        Returns:
        - "fade_out_done" when screen is fully black
        - "fade_in_done" when fade-in is finished
        - None while still fading
        """
        if not self.active:
            return None

        if self.direction == 1:
            self.alpha = min(self.alpha + self.speed, 255)

            if self.alpha >= 255:
                return "fade_out_done"
            
        elif self.direction == -1:
            self.alpha = max(self.alpha - self.speed, 0)

            if self.alpha <= 0:
                self.active = False
                return "fade_in_done"

        return None

    def draw(self, screen):
        """Draw the fade overlay."""
        if not self.active:
            return

        self.surface.set_alpha(self.alpha)
        screen.blit(self.surface, (0,0))
