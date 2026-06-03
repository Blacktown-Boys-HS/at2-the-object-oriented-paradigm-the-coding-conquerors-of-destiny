"""
Main entry point for the RPG game.
"""
import pygame
import asyncio

from globals import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, load_fonts, BLUE
)
from scene_manager import SceneManager

from sounds import SoundManager
from cursor import CustomCursor
from splash import SplashScreen
from transition import SceneTransition

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
        game_start_fx = sound_manager.effects.get("game_start")
        if game_start_fx:
            game_start_fx.play()

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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            cursor.handle_event(event)

            if splash.active:
                if splash.handle_event(event):
                    transition.start_fade_in()
                    sound_manager.update_music_for_scene(scene_manager.current_scene)
                continue
                
            if not transition.active:
                scene_manager.handle_event(event, transition)
                
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
        debug_y = 10
        fps_text = debug_font.render(f"FPS: {clock.get_fps():.0f}", False, BLUE)
        screen.blit(fps_text, (10, debug_y))

        debug_y += 40
        scene_text = debug_font.render(f"Scene: {scene_manager.current_scene}", False, BLUE)
        screen.blit(scene_text, (10, debug_y))

        cursor.draw(screen, mouse_pos)

        pygame.display.update()
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
