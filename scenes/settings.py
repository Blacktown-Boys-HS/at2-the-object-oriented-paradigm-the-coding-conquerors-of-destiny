"""
Settings scene for the RPG game.
"""
import pygame
from globals import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SCENE_MENU,
    FPS,
    WHITE,
    GRAY,
    LIGHT_GRAY,
    YELLOW,
)

from .aesthetic import (
    SharedBackground,
    draw_pulsing_title,
    draw_footer_hint,
)


class SettingsScene:
    """Settings scene."""

    _TRACK_W = 420
    _TRACK_H = 10
    _THUMB_R = 12

    def __init__(self, title_font, menu_font, credit_font, sound_manager):
        self.title_font = title_font
        self.menu_font = menu_font
        self.credit_font = credit_font
        self.sound_manager = sound_manager
        self.bg = SharedBackground()
        self.time_seconds = 0.0
        self._drag_key = None

        cx = SCREEN_WIDTH // 2
        self._sliders = {
            "music": {
                "label": "Background music",
                "y": 300,
                "track": pygame.Rect(0, 0, self._TRACK_W, self._TRACK_H),
            },
            "sfx": {
                "label": "Sound effects",
                "y": 390,
                "track": pygame.Rect(0, 0, self._TRACK_W, self._TRACK_H),
            },
        }
        for spec in self._sliders.values():
            spec["track"].centerx = cx
            spec["track"].centery = spec["y"]

    def _value_for_key(self, key):
        if key == "music":
            return self.sound_manager.music_volume
        return self.sound_manager.sfx_volume

    def _set_value_from_x(self, key, x):
        track = self._sliders[key]["track"]
        t = (x - track.left) / track.width
        t = max(0.0, min(1.0, t))
        if key == "music":
            self.sound_manager.set_music_volume(t)
        else:
            self.sound_manager.set_sfx_volume(t)

    def _hit_slider(self, pos):
        for key, spec in self._sliders.items():
            track = spec["track"]
            expanded = track.inflate(24, 40)
            if expanded.collidepoint(pos):
                return key
        return None

    def handle_event(self, event):
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return SCENE_MENU

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            key = self._hit_slider(event.pos)
            if key:
                self._drag_key = key
                self._set_value_from_x(key, event.pos[0])
        elif event.type == pygame.MOUSEMOTION:
            if self._drag_key and event.buttons[0]:
                self._set_value_from_x(self._drag_key, event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._drag_key = None

        return None

    def update(self, mouse_pos):
        """Update settings state."""
        self.time_seconds = pygame.time.get_ticks() / 1000.0
        self.bg.update(1.0 / FPS)

    def render(self, screen):
        """Render the settings scene."""
        self.bg.draw(screen)

        draw_pulsing_title(
            screen,
            self.title_font,
            "Settings",
            SCREEN_WIDTH // 2,
            115,
            self.time_seconds,
        )

        for key, spec in self._sliders.items():
            label_surf = self.menu_font.render(spec["label"], False, WHITE)
            label_rect = label_surf.get_rect(
                center=(SCREEN_WIDTH // 2, spec["y"] - 42)
            )
            screen.blit(label_surf, label_rect)

            track = spec["track"]
            pygame.draw.rect(screen, GRAY, track, border_radius=5)
            val = self._value_for_key(key)
            fill_w = max(0, int(track.width * val))
            if fill_w > 0:
                fill_rect = pygame.Rect(track.left, track.top, fill_w, track.height)
                pygame.draw.rect(screen, LIGHT_GRAY, fill_rect, border_radius=5)

            thumb_cx = track.left + int(track.width * val)
            thumb_cy = track.centery
            pygame.draw.circle(screen, YELLOW, (thumb_cx, thumb_cy), self._THUMB_R)
            pygame.draw.circle(screen, WHITE, (thumb_cx, thumb_cy), self._THUMB_R, width=2)

            pct = int(round(val * 100))
            pct_surf = self.credit_font.render(f"{pct}%", False, (200, 200, 200))
            pct_rect = pct_surf.get_rect(midleft=(track.right + 20, track.centery))
            screen.blit(pct_surf, pct_rect)

        draw_footer_hint(
            screen,
            self.credit_font,
            "Drag sliders to adjust volume · ESC to return to menu",
        )
