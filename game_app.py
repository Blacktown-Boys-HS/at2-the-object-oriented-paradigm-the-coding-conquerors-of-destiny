"""
Application shell for the RPG game.
"""

import asyncio

import pygame

from cursor import CustomCursor
from globals import FPS, GAME_TITLE, SCREEN_HEIGHT, SCREEN_WIDTH, load_fonts
from scene_manager import SceneManager
from sounds import SoundManager
from splash import SplashScreen
from transition import SceneTransition


class GameApp:
    """Owns pygame setup, app-level events, and the main frame loop."""

    def __init__(self):
        pygame.init()
        self._init_mixer()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)

        self.clock = pygame.time.Clock()
        self.title_font, self.menu_font, self.credit_font, self.debug_font = load_fonts()

        self.sound_manager = SoundManager()
        self.cursor = CustomCursor()
        self.splash = SplashScreen()
        self.transition = SceneTransition()
        self.scene_manager = SceneManager(
            self.title_font,
            self.menu_font,
            self.credit_font,
            self.sound_manager,
        )

        if self.splash.active:
            self.sound_manager.play_effect("game_start")
        else:
            self.sound_manager.update_music_for_scene(self.scene_manager.current_scene)

    def _init_mixer(self):
        """Initialize mixer when available."""
        try:
            pygame.mixer.init()
        except pygame.error:
            pass

    async def run(self):
        """Run the main game loop."""
        running = True
        while running:
            self.clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()

            running = self._handle_events()
            if not running or self.scene_manager.quit_requested:
                break

            if self.splash.active:
                await self._render_splash(mouse_pos)
                continue

            self._update_scene(mouse_pos)
            if self.scene_manager.quit_requested:
                break

            self._render_scene(mouse_pos)

            pygame.display.update()
            await asyncio.sleep(0)

        pygame.quit()

    def _handle_events(self):
        """Handle app-level and scene-level events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            self.cursor.handle_event(event)

            if self.splash.active:
                if self.splash.handle_event(event):
                    self.transition.start_fade_in()
                    self.sound_manager.update_music_for_scene(
                        self.scene_manager.current_scene
                    )
                continue

            if not self.transition.active:
                self.scene_manager.handle_event(event, self.transition)

        return True

    async def _render_splash(self, mouse_pos):
        """Update and render the splash screen."""
        self.screen.fill((0, 0, 0))

        finished = self.splash.update()
        if finished:
            self.transition.start_fade_in()
            self.sound_manager.update_music_for_scene(self.scene_manager.current_scene)

        self.splash.draw(self.screen)
        self.cursor.draw(self.screen, mouse_pos)

        pygame.display.update()
        await asyncio.sleep(0)

    def _update_scene(self, mouse_pos):
        """Update active scene and transition state."""
        self.scene_manager.update(mouse_pos, self.transition)

        transition_result = self.transition.update()
        if transition_result == "fade_out_done":
            self.scene_manager.finish_fade_out(self.transition)
        elif transition_result == "fade_in_done":
            self.scene_manager.finish_fade_in()

    def _render_scene(self, mouse_pos):
        """Render active scene and app-level overlays."""
        self.scene_manager.render(self.screen)
        self.transition.draw(self.screen)
        self.cursor.draw(self.screen, mouse_pos)
