"""
Main entry point for the RPG game.
"""
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


def main():
    """Main game loop."""
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("RPG Game")
    
    clock = pygame.time.Clock()
    
    # Load fonts
    title_font, menu_font, credit_font = load_fonts()
    
    # Initialize scenes
    scenes = {
        SCENE_MENU: MenuScene(title_font, menu_font, credit_font),
        SCENE_CREDITS: CreditsScene(title_font, menu_font, credit_font),
        SCENE_GAME: GameScene(title_font, menu_font, credit_font),
        SCENE_SETTINGS: SettingsScene(title_font, menu_font, credit_font),
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
    
    while running:
        clock.tick(FPS)
        
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif not is_transitioning:
                next_scene = scenes[current_scene].handle_event(event)
                if next_scene and next_scene != current_scene:
                    pending_scene = next_scene
                    is_transitioning = True
                    transition_direction = 1
                    transition_alpha = 0
        
        # Update current scene
        scenes[current_scene].update(mouse_pos)
        
        # Render current scene
        scenes[current_scene].render(screen)
        
        if is_transitioning:
            if transition_direction == 1:
                transition_alpha = min(transition_alpha + transition_speed, 255)
                if transition_alpha >= 255:
                    if pending_scene:
                        current_scene = pending_scene
                        pending_scene = None
                    transition_direction = -1
            elif transition_direction == -1:
                transition_alpha = max(transition_alpha - transition_speed, 0)
                if transition_alpha <= 0:
                    is_transitioning = False
            
            transition_surface.set_alpha(transition_alpha)
            screen.blit(transition_surface, (0, 0))
        
        pygame.display.update()
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
