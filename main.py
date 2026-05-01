"""
Main entry point for the RPG game.
"""
from pathlib import Path
import pygame
import sys
from globals import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    SCENE_MENU, SCENE_CREDITS, SCENE_GAME, SCENE_SETTINGS,
    load_fonts
)
from scenes.menu import MenuScene
from scenes.credits import CreditsScene
from scenes.game import GameScene
from scenes.settings import SettingsScene
from sounds import SoundManager


def main():
    """Main game loop."""
    pygame.init()
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("RPG Game")
    
    clock = pygame.time.Clock()
    
    # Load fonts
    title_font, menu_font, credit_font = load_fonts()

    sound_manager = SoundManager()

    # Custom cursor setup (with click-scale effect)
    cursor_pressed = False
    cursor_scale = 1.0
    cursor_scale_default = 1.0
    cursor_scale_pressed = 0.85
    cursor_scale_speed = 0.35
    custom_cursor = None
    cursor_path = Path(__file__).resolve().parent / "assets" / "cursor" / "8_white.png"
    try:
        custom_cursor = pygame.image.load(str(cursor_path)).convert_alpha()
        pygame.mouse.set_visible(False)
    except (FileNotFoundError, pygame.error):
        pygame.mouse.set_visible(True)
    
    # Initialize scenes
    scenes = {
        SCENE_MENU: MenuScene(title_font, menu_font, credit_font, sound_manager.effects),
        SCENE_CREDITS: CreditsScene(title_font, menu_font, credit_font, sound_manager.effects),
        SCENE_GAME: GameScene(title_font, menu_font, credit_font, sound_manager.effects),
        SCENE_SETTINGS: SettingsScene(title_font, menu_font, credit_font, sound_manager.effects),
    }
    
    current_scene = SCENE_MENU
    running = True
    
    # Scene transition state (fade out -> switch scene -> fade in)
    transition_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    transition_surface.fill((0, 0, 0))
    transition_alpha = 255
    transition_speed = 12
    transition_direction = -1  # -1: fading in, 1: fading out
    is_transitioning = True
    pending_scene = None
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

            if event.type == pygame.MOUSEBUTTONDOWN:
                cursor_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP:
                cursor_pressed = False

            if not is_transitioning:
                next_scene = scenes[current_scene].handle_event(event)
                if next_scene and next_scene != current_scene:
                    pending_scene = next_scene
                    is_transitioning = True
                    transition_direction = 1
                    transition_alpha = 0
        
        # Update current scene
        scenes[current_scene].update(mouse_pos)
        deferred_next_scene = None
        if hasattr(scenes[current_scene], "consume_requested_scene"):
            deferred_next_scene = scenes[current_scene].consume_requested_scene()
        if (not is_transitioning) and deferred_next_scene and deferred_next_scene != current_scene:
            pending_scene = deferred_next_scene
            is_transitioning = True
            transition_direction = 1
            transition_alpha = 0
        
        # Render current scene
        scenes[current_scene].render(screen)
        
        if is_transitioning:
            if transition_direction == 1:
                transition_alpha = min(transition_alpha + transition_speed, 255)
                if transition_alpha >= 255:
                    if pending_scene:
                        current_scene = pending_scene
                        pending_scene = None
                        sound_manager.update_music_for_scene(current_scene)
                    transition_direction = -1
            elif transition_direction == -1:
                transition_alpha = max(transition_alpha - transition_speed, 0)
                if transition_alpha <= 0:
                    is_transitioning = False
            
            transition_surface.set_alpha(transition_alpha)
            screen.blit(transition_surface, (0, 0))

        if custom_cursor is not None:
            target_scale = cursor_scale_pressed if cursor_pressed else cursor_scale_default
            cursor_scale += (target_scale - cursor_scale) * cursor_scale_speed
            scaled_size = (
                max(1, int(custom_cursor.get_width() * cursor_scale)),
                max(1, int(custom_cursor.get_height() * cursor_scale)),
            )
            cursor_surface = pygame.transform.smoothscale(custom_cursor, scaled_size)
            cursor_rect = cursor_surface.get_rect(topleft=mouse_pos)
            screen.blit(cursor_surface, cursor_rect)
        
        pygame.display.update()
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
