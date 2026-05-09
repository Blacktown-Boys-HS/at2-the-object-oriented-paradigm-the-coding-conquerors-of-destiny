"""
Global variables and constants for the RPG game.
"""
from pathlib import Path
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
BACKGROUND = (30, 30, 30)  
BLUE = (126, 193, 245)

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
DEBUG_FONT_SIZE = 32

# pygame.font.Font.render(…, antialias, …) — False keeps pixel fonts crisp
FONT_ANTIALIAS = False


def load_fonts():
    """Load fonts from assets folder."""
    base_dir = Path(__file__).resolve().parent
    font_candidates = [
        base_dir / "assets" / "fonts" / "Kenney Pixel.ttf",
        base_dir / "assets" / "font" / "Kenney Pixel.ttf",
    ]
    try:
        font_path = next(path for path in font_candidates if path.exists())
        title_font = pygame.font.Font(str(font_path), TITLE_FONT_SIZE)
        menu_font = pygame.font.Font(str(font_path), MENU_FONT_SIZE)
        credit_font = pygame.font.Font(str(font_path), CREDIT_FONT_SIZE)
        debug_font = pygame.font.Font(str(font_path), DEBUG_FONT_SIZE)
    except (StopIteration, FileNotFoundError, pygame.error):
        title_font = pygame.font.SysFont("monospace", TITLE_FONT_SIZE, bold=False)
        menu_font = pygame.font.SysFont("monospace", MENU_FONT_SIZE, bold=False)
        credit_font = pygame.font.SysFont("monospace", CREDIT_FONT_SIZE, bold=False)
        debug_font = pygame.font.SysFont("monospace", DEBUG_FONT_SIZE, bold=False)
    
    return title_font, menu_font, credit_font, debug_font
