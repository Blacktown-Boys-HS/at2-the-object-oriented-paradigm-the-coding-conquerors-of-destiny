"""
Centralized sound and music setup.
"""

from pathlib import Path

import pygame

from globals import (
    SCENE_CREDITS,
    SCENE_GAME,
    SCENE_MENU,
    SCENE_SETTINGS,
    SCENE_TUTORIAL,
)


class SoundManager:
    """Loads sound effects and controls background music by scene."""

    def __init__(self):
        base_dir = Path(__file__).resolve().parent
        self.sound_dir = base_dir / "assets" / "sound"
        self.audio_enabled = pygame.mixer.get_init() is not None

        self.effects = {}
        self._load_effects()
        self.menu_theme_path = self.sound_dir / "Main Menu Theme - Calm (E,80BPM).ogg"
        self.game_theme_path = (
            base_dir / "assets" / "rpg_assets" / "music" / "time_for_adventure.ogg"
        )
        self.boss_theme_path = (
            base_dir / "assets" / "rpg_assets" / "music" / "boss.ogg"
        )
        self.music_scenes = {
            SCENE_MENU,
            SCENE_CREDITS,
            SCENE_SETTINGS,
            SCENE_TUTORIAL,
        }
        self._music_volume = 1.0
        self._sfx_volume = 1.0
        self.current_music_path = None
        self.apply_volumes()

    def _load_effects(self):
        """Load effects if the mixer is available."""
        effect_files = {
            "button_hover": "Button Hover_1.ogg",
            "cancel_back": "Cancel  Back.ogg",
            "confirm": "Confirm_1.ogg",
            "hit": "hurt.ogg",
            "death": "death.ogg",
            "attack": "power_up.ogg",
            "attack_hit": "explosion.ogg",
            "game_start": "Game Start Sound FX.ogg",
        }

        for key, filename in effect_files.items():
            sound = self._load_effect(filename)
            if sound:
                self.effects[key] = sound

    def _load_effect(self, filename):
        """Return a sound effect, or None if audio is unavailable."""
        if not self.audio_enabled:
            return None

        try:
            return pygame.mixer.Sound(str(self.sound_dir / filename))
        except (FileNotFoundError, pygame.error):
            return None

    @property
    def music_volume(self):
        return self._music_volume

    @property
    def sfx_volume(self):
        return self._sfx_volume

    def set_music_volume(self, volume):
        """Background music volume 0.0–1.0."""
        self._music_volume = max(0.0, min(1.0, float(volume)))
        if self.audio_enabled:
            pygame.mixer.music.set_volume(self._music_volume)

    def set_sfx_volume(self, volume):
        """Sound effects volume 0.0–1.0."""
        self._sfx_volume = max(0.0, min(1.0, float(volume)))
        for sound in self.effects.values():
            sound.set_volume(self._sfx_volume)

    def apply_volumes(self):
        """Re-apply stored volumes (e.g. after mixer re-init)."""
        if self.audio_enabled:
            pygame.mixer.music.set_volume(self._music_volume)
        for sound in self.effects.values():
            sound.set_volume(self._sfx_volume)

    def play_effect(self, effect_key):
        """Safely play a sound effect if it exists."""
        sound = self.effects.get(effect_key)
        if sound:
            sound.play()

    def _play_music_path(self, music_path):
        """Play a looped music file if it is not already playing."""
        if not self.audio_enabled:
            return

        if getattr(self, "current_music_path", None) == music_path:
            return

        try:
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.play(-1)
            self.current_music_path = music_path
        except (FileNotFoundError, pygame.error):
            self.current_music_path = None

    def play_game_music(self):
        """Play the main dungeon music."""
        self._play_music_path(self.game_theme_path)

    def play_boss_music(self):
        """Play the boss arena music."""
        self._play_music_path(self.boss_theme_path)

    def update_music_for_scene(self, scene_name):
        """Play/stop looped background music based on active scene."""
        if not self.audio_enabled:
            return

        music_path = None
        if scene_name == SCENE_GAME:
            music_path = self.game_theme_path
        elif scene_name in self.music_scenes:
            music_path = self.menu_theme_path

        if music_path is None:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            self.current_music_path = None
            return

        self._play_music_path(music_path)
