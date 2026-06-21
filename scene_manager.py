from globals import (
    SCENE_CREDITS,
    SCENE_GAME,
    SCENE_MENU,
    SCENE_QUIT,
    SCENE_SETTINGS,
    SCENE_TUTORIAL,
)
from scenes.credits import CreditsScene
from scenes.game import GameScene
from scenes.menu import MenuScene
from scenes.settings import SettingsScene
from scenes.tutorial import TutorialScene


class SceneManager:
    """Creates scenes and handles scene transition requests."""

    def __init__(self, title_font, menu_font, credit_font, sound_manager):
        self.sound_manager = sound_manager

        self.scenes = {
            SCENE_MENU: MenuScene(
                title_font, menu_font, credit_font, sound_manager.effects
            ),
            SCENE_CREDITS: CreditsScene(
                title_font, menu_font, credit_font, sound_manager.effects
            ),
            SCENE_GAME: GameScene(
                title_font, menu_font, credit_font, sound_manager
            ),
            SCENE_SETTINGS: SettingsScene(
                title_font, menu_font, credit_font, sound_manager
            ),
            SCENE_TUTORIAL: TutorialScene(
                title_font, menu_font, credit_font, sound_manager.effects
            ),
        }
        self.current_scene = SCENE_MENU
        self.quit_requested = False

    def get_current_scene(self):
        """Return the active scene object."""
        return self.scenes[self.current_scene]

    def handle_event(self, event, transition):
        """Send events to the active scene and start transitions if needed."""
        if transition.active:
            return

        next_scene = self.get_current_scene().handle_event(event)
        self.request_scene(next_scene, transition)

    def update(self, mouse_pos, transition):
        """Update active scene and handle deferred scene requests."""
        self.get_current_scene().update(mouse_pos)

        if transition.active:
            return

        scene = self.get_current_scene()
        if hasattr(scene, "consume_requested_scene"):
            next_scene = scene.consume_requested_scene()
            self.request_scene(next_scene, transition)

    def render(self, screen):
        """Render the active scene"""
        self.get_current_scene().render(screen)

    def request_scene(self, next_scene, transition):
        """Start a fade transition to another scene."""
        if not next_scene:
            return

        if next_scene == SCENE_QUIT:
            self.quit_requested = True
            return

        if next_scene == self.current_scene:
            return

        if next_scene == SCENE_SETTINGS:
            self.scenes[SCENE_SETTINGS].previous_scene = self.current_scene

        transition.start_fade_out(next_scene)

    def finish_fade_out(self, transition):
        """Switch scene once the fade-out reaches black."""
        if transition.pending_scene:
            self.current_scene = transition.pending_scene
            transition.pending_scene = None

            self.sound_manager.update_music_for_scene(self.current_scene)

            scene = self.get_current_scene()
            if hasattr(scene, "on_enter"):
                scene.on_enter()

        transition.start_fade_in()

    def finish_fade_in(self):
        """Run logic after fading into the current scene."""
        if self.current_scene == SCENE_GAME:
            scene = self.get_current_scene()
            if hasattr(scene, "loading_ready"):
                scene.loading_ready = True
                print("loading_ready = True")
