"""
Main entry point for the RPG game.
"""
import pygame
import sys

from globals import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    SCENE_MENU, SCENE_CREDITS, SCENE_GAME, SCENE_SETTINGS,
    load_fonts, BLUE
)
from scenes.menu import MenuScene
from scenes.credits import CreditsScene
from scenes.game import GameScene
from scenes.settings import SettingsScene
from sounds import SoundManager
from cursor import CustomCursor
from splash import SplashScreen


def main():
    """Main game loop."""
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("RPG Game")

    clock = pygame.time.Clock()

    # Load fonts
    title_font, menu_font, credit_font, debug_font = load_fonts()

    sound_manager = SoundManager()

    # Custom cursor setup
    cursor = CustomCursor()

    # Splash screen setup
    splash = SplashScreen()
    if splash.active:
        game_start_fx = sound_manager.effects.get("game_start")
        if game_start_fx:
            game_start_fx.play()

    # Initialize scenes
    scenes = {
        SCENE_MENU: MenuScene(title_font, menu_font, credit_font, sound_manager.effects),
        SCENE_CREDITS: CreditsScene(title_font, menu_font, credit_font, sound_manager.effects),
        SCENE_GAME: GameScene(title_font, menu_font, credit_font, sound_manager.effects),
        SCENE_SETTINGS: SettingsScene(title_font, menu_font, credit_font, sound_manager),
    }

    current_scene = SCENE_MENU
    running = True

    # Scene transition state
    transition_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    transition_surface.fill((0, 0, 0))
    transition_alpha = 255
    transition_speed = 12
    transition_direction = -1
    is_transitioning = True
    pending_scene = None

    if not splash.active:
        sound_manager.update_music_for_scene(current_scene)

    while running:
        clock.tick(FPS)

        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            cursor.handle_event(event)

            if splash.active:
                if splash.handle_event(event):
                    is_transitioning = True
                    transition_direction = -1
                    transition_alpha = 255
                    sound_manager.update_music_for_scene(current_scene)
                continue

            if not is_transitioning:
                next_scene = scenes[current_scene].handle_event(event)
                if next_scene and next_scene != current_scene:
                    # Track where we came from before entering settings
                    if next_scene == SCENE_SETTINGS:
                        scenes[SCENE_SETTINGS].previous_scene = current_scene
                    pending_scene = next_scene
                    is_transitioning = True
                    transition_direction = 1
                    transition_alpha = 0

        # Splash screen
        if splash.active:
            screen.fill((0, 0, 0))

            finished = splash.update()
            if finished:
                is_transitioning = True
                transition_direction = -1
                transition_alpha = 255
                sound_manager.update_music_for_scene(current_scene)

            splash.draw(screen)
            cursor.draw(screen, mouse_pos)

            pygame.display.update()
            continue

        # Update current scene
        scenes[current_scene].update(mouse_pos)

        deferred_next_scene = None
        if hasattr(scenes[current_scene], "consume_requested_scene"):
            deferred_next_scene = scenes[current_scene].consume_requested_scene()

        if (not is_transitioning) and deferred_next_scene and deferred_next_scene != current_scene:
            # Track where we came from before entering settings
            if deferred_next_scene == SCENE_SETTINGS:
                scenes[SCENE_SETTINGS].previous_scene = current_scene
            pending_scene = deferred_next_scene
            is_transitioning = True
            transition_direction = 1
            transition_alpha = 0

        # Render current scene
        scenes[current_scene].render(screen)

        # Scene transition
        if is_transitioning:
            if transition_direction == 1:
                transition_alpha = min(transition_alpha + transition_speed, 255)
                if transition_alpha >= 255:
                    if pending_scene:
                        current_scene = pending_scene
                        pending_scene = None
                        sound_manager.update_music_for_scene(current_scene)
                        if hasattr(scenes[current_scene], "on_enter"):
                            scenes[current_scene].on_enter()
                    transition_direction = -1

            elif transition_direction == -1:
                transition_alpha = max(transition_alpha - transition_speed, 0)
                if transition_alpha <= 0:
                    is_transitioning = False

                    # tell game it can start loading timer
                    if current_scene == SCENE_GAME and hasattr(scenes[current_scene], "loading_ready"):
                        scenes[current_scene].loading_ready = True
                        print("loading_ready set to True")

            transition_surface.set_alpha(transition_alpha)
            screen.blit(transition_surface, (0, 0))

        # Display debug stats in top left
        debug_y = 10
        fps_text = debug_font.render(f"FPS: {clock.get_fps():.0f}", False, BLUE)
        screen.blit(fps_text, (10, debug_y))

        debug_y += 40
        scene_text = debug_font.render(f"Scene: {current_scene}", False, BLUE)
        screen.blit(scene_text, (10, debug_y))

        cursor.draw(screen, mouse_pos)

        pygame.display.update()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
