from globals import (
    SCENE_MENU,
    SCENE_CREDITS,
    SCENE_GAME,
    SCENE_SETTINGS
)
from scenes.menu import MenuScene
from scenes.credits import CreditsScene
from scenes.game import GameScene
from scenes.settings import SettingsScene

class SceneManager:
    """Creates scenes and handles scene transition requests."""

    def __init__(self, title_font, menu_font, credit_font, sound_manager):
        self.sound_manager = sound_manager

        self.scenes = {
            SCENE_MENU: MenuScene(title_font, menu_font, credit_font, sound_manager.effects),
            SCENE_CREDITS: CreditsScene(title_font, menu_font, credit_font, sound_manager.effects),
            SCENE_GAME: GameScene(title_font, menu_font, credit_font, sound_manager.effects),
            SCENE_SETTINGS: SettingsScene(title_font, menu_font, credit_font, sound_manager.effects),
        }
        self.current_scene = SCENE_MENU

    def get_current_scene(self):
        """Return the active scene object."""
        return self.scenes[self.current_scene]
    
    def handle_event(self, event, transition):
        """Send events to the active scene and start transitions if needed."""
        if transition.active:
            return
        
        next_scene = self.get_current_scene().handle_event(event)
        self.request_scene(next_scene, transition)