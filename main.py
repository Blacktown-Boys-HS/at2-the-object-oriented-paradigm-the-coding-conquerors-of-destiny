"""
Main entry point for the RPG game.
"""

import asyncio

import pygame

from cursor import CustomCursor
from globals import BLUE, FPS, SCREEN_HEIGHT, SCREEN_WIDTH, load_fonts
from scene_manager import SceneManager
from sounds import SoundManager
from splash import SplashScreen
from transition import SceneTransition


def _render_debug_stats(screen, clock, scene_manager, debug_font):
    """Render debug information to the screen."""
    debug_y = 10
    fps_text = debug_font.render(f"FPS: {clock.get_fps():.0f}", False, BLUE)
    screen.blit(fps_text, (10, debug_y))

    debug_y += 40
    scene_text = debug_font.render(f"Scene: {scene_manager.current_scene}", False, BLUE)
    screen.blit(scene_text, (10, debug_y))


def _handle_events(scene_manager, cursor, splash, transition, sound_manager):
    """Handle all events for the frame. Returns False if QUIT event received."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        cursor.handle_event(event)

        if splash.active:
            if splash.handle_event(event):
                transition.start_fade_in()
                sound_manager.update_music_for_scene(scene_manager.current_scene)
            continue

        if not transition.active:
            scene_manager.handle_event(event, transition)

    return True


async def main():
    """Main game loop."""
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error:
        pass

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
        sound_manager.play_effect("game_start")

    # Initialize scenes
    scene_manager = SceneManager(title_font, menu_font, credit_font, sound_manager)

    running = True

    # Scene transition state
    transition = SceneTransition()

    if not splash.active:
        sound_manager.update_music_for_scene(scene_manager.current_scene)

    while running:
        clock.tick(FPS)

        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Handle events
        running = _handle_events(
            scene_manager, cursor, splash, transition, sound_manager
        )

        # Splash screen
        if splash.active:
            screen.fill((0, 0, 0))

            finished = splash.update()
            if finished:
                transition.start_fade_in()
                sound_manager.update_music_for_scene(scene_manager.current_scene)

            splash.draw(screen)
            cursor.draw(screen, mouse_pos)

            pygame.display.update()
            await asyncio.sleep(0)
            continue

        # Update current scene
        scene_manager.update(mouse_pos, transition)

        # Render current scene
        scene_manager.render(screen)

        # Scene transition
        transition_result = transition.update()

        if transition_result == "fade_out_done":
            scene_manager.finish_fade_out(transition)

        elif transition_result == "fade_in_done":
            # tell game it can start loading timer
            scene_manager.finish_fade_in()

        transition.draw(screen)

        # Display debug stats in top left
        _render_debug_stats(screen, clock, scene_manager, debug_font)

        cursor.draw(screen, mouse_pos)

        pygame.display.update()
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
