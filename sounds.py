"""
Centralized sound and music setup.
"""
from pathlib import Path
import pygame

from globals import SCENE_CREDITS, SCENE_MENU, SCENE_SETTINGS


class SoundManager:
    """Loads sound effects and controls background music by scene."""

    def __init__(self):
        base_dir = Path(__file__).resolve().parent
        self.sound_dir = base_dir / "assets" / "sound"

        self.effects = {
            "button_hover": pygame.mixer.Sound(str(self.sound_dir / "Button Hover_1.wav")),
            "cancel_back": pygame.mixer.Sound(str(self.sound_dir / "Cancel  Back.wav")),
            "confirm": pygame.mixer.Sound(str(self.sound_dir / "Confirm_1.wav")),
            "hit": pygame.mixer.Sound(str(self.sound_dir / "hurt.mp3")),
            "death" : pygame.mixer.Sound(str(self.sound_dir / "death.mp3"))
        }
        game_start_path = self.sound_dir / "Game Start Sound FX.mp3"
        try:
            self.effects["game_start"] = pygame.mixer.Sound(str(game_start_path))
        except pygame.error:
            pass
        self.menu_theme_path = self.sound_dir / "Main Menu Theme - Calm (E,80BPM).wav"
        self.music_scenes = {SCENE_MENU, SCENE_CREDITS, SCENE_SETTINGS}
        self._music_volume = 1.0
        self._sfx_volume = 1.0
        self.apply_volumes()

    @property
    def music_volume(self):
        return self._music_volume

    @property
    def sfx_volume(self):
        return self._sfx_volume

    def set_music_volume(self, volume):
        """Background music volume 0.0–1.0."""
        self._music_volume = max(0.0, min(1.0, float(volume)))
        pygame.mixer.music.set_volume(self._music_volume)

    def set_sfx_volume(self, volume):
        """Sound effects volume 0.0–1.0."""
        self._sfx_volume = max(0.0, min(1.0, float(volume)))
        for sound in self.effects.values():
            sound.set_volume(self._sfx_volume)

    def apply_volumes(self):
        """Re-apply stored volumes (e.g. after mixer re-init)."""
        pygame.mixer.music.set_volume(self._music_volume)
        for sound in self.effects.values():
            sound.set_volume(self._sfx_volume)

    def update_music_for_scene(self, scene_name):
        """Play/stop looped background music based on active scene."""
        if scene_name in self.music_scenes:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(str(self.menu_theme_path))
                pygame.mixer.music.play(-1)
        else:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
