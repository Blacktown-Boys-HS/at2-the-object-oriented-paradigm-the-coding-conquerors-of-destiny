"""
Tutorial scene — how to play, pulled from game_data objectives and controls.
"""
import pygame

from game_data import tutorial_sections
from globals import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SCENE_MENU,
    FPS,
    WHITE,
    FONT_ANTIALIAS,
)

from .aesthetic import (
    SharedBackground,
    draw_gothic_title,
    draw_gothic_panel,
    draw_footer_hint,
    GOTHIC_GOLD,
    GOTHIC_TEXT_MUTED,
)


class TutorialScene:
    """Scrollable tutorial with gothic styling."""

    _PANEL = pygame.Rect(0, 0, 760, 460)
    _LINE_HEIGHT = 30
    _SECTION_GAP = 18

    def __init__(self, title_font, menu_font, credit_font, sounds=None):
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font
        self.sounds = sounds or {}
        self.bg = SharedBackground()
        self.time_seconds = 0.0
        self.sections = tutorial_sections()
        self.scroll_y = 0
        self._content_height = self._measure_content_height()
        self._panel = self._PANEL.copy()
        self._panel.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)

    def _measure_content_height(self):
        height = 0
        for section in self.sections:
            height += self._LINE_HEIGHT + 8
            height += len(section["lines"]) * self._LINE_HEIGHT
            height += self._SECTION_GAP
        return height

    def _max_scroll(self):
        view_h = self._panel.height - 48
        return max(0, self._content_height - view_h)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return SCENE_MENU
            if event.key == pygame.K_UP:
                self.scroll_y = max(0, self.scroll_y - 36)
            elif event.key == pygame.K_DOWN:
                self.scroll_y = min(self._max_scroll(), self.scroll_y + 36)
        elif event.type == pygame.MOUSEWHEEL:
            self.scroll_y = max(
                0, min(self._max_scroll(), self.scroll_y - event.y * 36)
            )
        return None

    def update(self, mouse_pos):
        self.time_seconds = pygame.time.get_ticks() / 1000.0
        self.bg.update(1.0 / FPS)

    def render(self, screen):
        self.bg.draw(screen)

        draw_gothic_title(
            screen, self.title_font, "Tutorial", SCREEN_WIDTH // 2, 100
        )

        draw_gothic_panel(screen, self._panel)

        clip = self._panel.inflate(-28, -28)
        content = pygame.Surface((clip.width, clip.height), pygame.SRCALPHA)
        y = 8 - self.scroll_y
        for section in self.sections:
            heading = self.menu_font.render(
                section["title"], FONT_ANTIALIAS, GOTHIC_GOLD
            )
            content.blit(heading, (0, y))
            y += self._LINE_HEIGHT + 8
            for line in section["lines"]:
                wrapped = self._wrap_line(line, clip.width)
                for part in wrapped:
                    text = self.credit_font.render(
                        part, FONT_ANTIALIAS, WHITE
                    )
                    content.blit(text, (12, y))
                    y += self._LINE_HEIGHT
            y += self._SECTION_GAP

        screen.set_clip(clip)
        screen.blit(content, clip.topleft)
        screen.set_clip(None)

        hint = self.credit_font.render(
            "UP/DOWN or scroll to read", FONT_ANTIALIAS, GOTHIC_TEXT_MUTED
        )
        hint_rect = hint.get_rect(midbottom=(SCREEN_WIDTH // 2, self._panel.bottom + 28))
        screen.blit(hint, hint_rect)

        draw_footer_hint(
            screen, self.credit_font, "Press ESC to return to menu"
        )

    def _wrap_line(self, text, max_width):
        words = text.split()
        if not words:
            return [""]
        lines = []
        current = words[0]
        for word in words[1:]:
            trial = f"{current} {word}"
            if self.credit_font.size(trial)[0] <= max_width - 12:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines
