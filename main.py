"""
Main entry point for the RPG game.
"""
from pathlib import Path
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

SPLASH_IMAGE_NAME = "charlie_kirk_engine.png"
SPLASH_FADE_SPEED = 5
SPLASH_HOLD_FRAMES = 72  # ~1.2s at 60 FPS
# Relative to “fit entire window” size (0.75 = 25% smaller, still centered)
SPLASH_DISPLAY_SCALE = 0.50


def _load_splash_image(path):
    """Scale splash art to fit the window; letterbox on black."""
    img = pygame.image.load(str(path)).convert_alpha()
    iw, ih = img.get_size()
    if iw <= 0 or ih <= 0:
        return None
    scale = min(SCREEN_WIDTH / iw, SCREEN_HEIGHT / ih) * SPLASH_DISPLAY_SCALE
    nw = max(1, int(iw * scale))
    nh = max(1, int(ih * scale))
    return pygame.transform.smoothscale(img, (nw, nh))


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

    # Custom cursor setup (with click-scale effect)
    cursor_pressed = False
    cursor_scale = 1.25
    cursor_scale_default = 1.25
    cursor_scale_pressed = 1.08
    cursor_scale_speed = 0.35
    custom_cursor = None
    cursor_path = Path(__file__).resolve().parent / "assets" / "cursor" / "8_white.png"
    try:
        custom_cursor = pygame.image.load(str(cursor_path)).convert()
        custom_cursor.set_colorkey(custom_cursor.get_at((0, 0)))
        pygame.mouse.set_visible(False)
    except (FileNotFoundError, pygame.error):
        pygame.mouse.set_visible(True)

    splash_surface = None
    splash_rect = None
    splash_path = Path(__file__).resolve().parent / "assets" / SPLASH_IMAGE_NAME
    try:
        splash_surface = _load_splash_image(splash_path)
        if splash_surface is not None:
            splash_rect = splash_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    except (FileNotFoundError, pygame.error, ValueError):
        splash_surface = None
        splash_rect = None

    showing_splash = splash_surface is not None
    splash_phase = "fade_in"
    splash_alpha = 0
    splash_hold_left = SPLASH_HOLD_FRAMES
    if showing_splash:
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
    
    # Scene transition state (fade out -> switch scene -> fade in)
    transition_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    transition_surface.fill((0, 0, 0))
    transition_alpha = 255
    transition_speed = 12
    transition_direction = -1  # -1: fading in, 1: fading out
    is_transitioning = True
    pending_scene = None
    if not showing_splash:
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

            if showing_splash:
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    showing_splash = False
                    splash_phase = "done"
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
        
        if showing_splash:
            screen.fill((0, 0, 0))
            if splash_phase == "fade_in":
                splash_alpha = min(255, splash_alpha + SPLASH_FADE_SPEED)
                if splash_alpha >= 255:
                    splash_alpha = 255
                    splash_phase = "hold"
            elif splash_phase == "hold":
                splash_hold_left -= 1
                if splash_hold_left <= 0:
                    splash_phase = "fade_out"
            elif splash_phase == "fade_out":
                splash_alpha = max(0, splash_alpha - SPLASH_FADE_SPEED)
                if splash_alpha <= 0:
                    showing_splash = False
                    splash_phase = "done"
                    is_transitioning = True
                    transition_direction = -1
                    transition_alpha = 255
                    sound_manager.update_music_for_scene(current_scene)

            splash_copy = splash_surface.copy()
            splash_copy.set_alpha(splash_alpha)
            screen.blit(splash_copy, splash_rect)

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
        
        # Display debug stats in top left
        debug_y = 10
        fps_text = debug_font.render(f"FPS: {clock.get_fps():.0f}", False, BLUE)
        screen.blit(fps_text, (10, debug_y))
        
        debug_y += 40
        scene_text = debug_font.render(f"Scene: {current_scene}", False, BLUE)
        screen.blit(scene_text, (10, debug_y))
        
        pygame.display.update()
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
