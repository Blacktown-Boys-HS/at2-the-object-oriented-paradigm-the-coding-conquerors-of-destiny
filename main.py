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
    
    while running:
        clock.tick(FPS)
        
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                next_scene = scenes[current_scene].handle_event(event)
                if next_scene:
                    current_scene = next_scene
        
        # Update current scene
        scenes[current_scene].update(mouse_pos)
        
        # Render current scene
        scenes[current_scene].render(screen)
        
        pygame.display.update()
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
