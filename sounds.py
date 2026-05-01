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
        }
        self.menu_theme_path = self.sound_dir / "Main Menu Theme - Calm (E,80BPM).wav"
        self.music_scenes = {SCENE_MENU, SCENE_CREDITS, SCENE_SETTINGS}

    def update_music_for_scene(self, scene_name):
        """Play/stop looped background music based on active scene."""
        if scene_name in self.music_scenes:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(str(self.menu_theme_path))
                pygame.mixer.music.play(-1)
        else:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
