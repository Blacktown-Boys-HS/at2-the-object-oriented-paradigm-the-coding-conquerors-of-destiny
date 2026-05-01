"""
Global variables and constants for the RPG game.
"""
import pygame

# Screen setup
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
LIGHT_GRAY = (180, 180, 180)
HOVER_COLOR = (200, 200, 200)

# Clock and FPS
FPS = 60

# Scenes
SCENE_MENU = "menu"
SCENE_CREDITS = "credits"
SCENE_GAME = "game"
SCENE_SETTINGS = "settings"

# Font sizes
TITLE_FONT_SIZE = 72
MENU_FONT_SIZE = 48
CREDIT_FONT_SIZE = 24


def load_fonts():
    """Load fonts from assets folder."""
    try:
        title_font = pygame.font.Font("assets/font/Kenney Pixel.ttf", TITLE_FONT_SIZE)
        menu_font = pygame.font.Font("assets/font/Kenney Pixel.ttf", MENU_FONT_SIZE)
        credit_font = pygame.font.Font("assets/font/Kenney Pixel.ttf", CREDIT_FONT_SIZE)
    except (FileNotFoundError, pygame.error):
        title_font = pygame.font.SysFont("monospace", TITLE_FONT_SIZE, bold=False)
        menu_font = pygame.font.SysFont("monospace", MENU_FONT_SIZE, bold=False)
        credit_font = pygame.font.SysFont("monospace", CREDIT_FONT_SIZE, bold=False)
    
    return title_font, menu_font, credit_font
