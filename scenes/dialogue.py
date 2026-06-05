"""Typewriter dialogue box with a closing animation."""
from pathlib import Path
import pygame
from globals import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FONT_ANTIALIAS,
    BLUE,
    GRAY,
    WHITE,
    get_gothic_font_path,
)


class DialogueBox:
    """Animated typewriter dialogue that fades/shrinks out when dismissed."""

    def __init__(self, text, speed=30, font_path=None):
        self.text = text
        self.speed = speed
        self.active = False
        self.chars_shown = 0
        self.timer = 0.0
        self.skipped = False

        # Build adaptive font: bigger for short text, smaller for long
        path = font_path
        if not path or not Path(path).exists():
            gothic = get_gothic_font_path()
            path = str(gothic) if gothic is not None else None
        if path and Path(path).exists():
            size = max(24, min(48, int(1400 / max(len(text), 1))))
            self.font = pygame.font.Font(path, size)
        else:
            self.font = pygame.font.SysFont("monospace", 32, bold=False)

        # Closing animation state
        self.closing = False
        self.close_timer = 0.0
        self.close_duration = 0.35  # seconds
        self.base_alpha = 230
        self.base_height = 100
        self.base_margin = 40

    def start(self):
        """Activate the dialogue and reset counters."""
        self.active = True
        self.chars_shown = 0
        self.timer = 0.0
        self.skipped = False
        self.closing = False
        self.close_timer = 0.0

    def skip_or_dismiss(self):
        """Advance: skip to end if typing, otherwise start close animation."""
        if self.chars_shown < len(self.text):
            self.chars_shown = len(self.text)
            self.skipped = True
        elif not self.closing:
            self.closing = True
            self.close_timer = 0.0

    def is_finished(self):
        """True when the box has fully closed."""
        return self.closing and self.close_timer >= self.close_duration

    def update(self, dt):
        """Advance typewriter and closing animation."""
        if not self.active:
            return
        if self.closing:
            self.close_timer = min(self.close_duration, self.close_timer + dt)
            if self.is_finished():
                self.active = False
            return
        if not self.skipped:
            self.timer += dt
            target = int(self.timer * self.speed)
            self.chars_shown = min(target, len(self.text))

    def render(self, screen, time_seconds):
        """Draw the dialogue box. Must be called every frame while active."""
        if not self.active:
            return

        progress = self.close_timer / self.close_duration if self.closing else 0.0
        alpha = int(self.base_alpha * (1.0 - progress))
        height = int(self.base_height * (1.0 - progress))
        if height <= 0:
            return

        margin = self.base_margin
        box_rect = pygame.Rect(
            margin,
            SCREEN_HEIGHT - height - 30,
            SCREEN_WIDTH - margin * 2,
            height,
        )
        box_surface = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        box_surface.fill((20, 20, 24, alpha))
        screen.blit(box_surface, box_rect.topleft)

        border_alpha = int(255 * (1.0 - progress))
        border_color = (100, 100, 110, border_alpha)
        pygame.draw.rect(screen, border_color[:3], box_rect, width=2, border_radius=6)

        # Typewriter text
        shown = self.text[: self.chars_shown]
        text_surface = self.font.render(shown, FONT_ANTIALIAS, WHITE)
        text_rect = text_surface.get_rect(
            midleft=(box_rect.left + 20, box_rect.centery)
        )
        screen.blit(text_surface, text_rect)

        # Blinking prompt when fully typed and not yet closing
        if self.chars_shown >= len(self.text) and not self.closing:
            if int(time_seconds * 3) % 2 == 0:
                prompt = self.font.render("▼", FONT_ANTIALIAS, BLUE)
                prompt_rect = prompt.get_rect(
                    midright=(box_rect.right - 20, box_rect.centery)
                )
                screen.blit(prompt, prompt_rect)
