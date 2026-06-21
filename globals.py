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
SCENE_TUTORIAL = "tutorial"
SCENE_QUIT = "quit"

# Game display name
GAME_TITLE = "Escape the Dungeon"

# Font sizes
TITLE_FONT_SIZE = 72
MENU_FONT_SIZE = 48
CREDIT_FONT_SIZE = 24
DEBUG_FONT_SIZE = 32

# False keeps pixel fonts crisp
FONT_ANTIALIAS = False


def _first_existing_path(candidates):
    return next(path for path in candidates if path.exists())


def _font_candidates(name):
    base_dir = Path(__file__).resolve().parent
    return [
        base_dir / "assets" / "fonts" / name,
        base_dir / "assets" / "font" / name,
    ]


def get_gothic_font_path():
    """Return path to GothicByte.ttf, or None if missing."""
    try:
        return _first_existing_path(_font_candidates("GothicByte.ttf"))
    except StopIteration:
        return None


def get_pixel_font_path():
    """Return path to Kenney Pixel.ttf, or None if missing."""
    try:
        return _first_existing_path(_font_candidates("Kenney Pixel.ttf"))
    except StopIteration:
        return None


def load_fonts():
    """GothicByte for titles; Kenney Pixel for menu, credits, and debug."""
    pixel_font_path = get_pixel_font_path()
    try:
        path = str(pixel_font_path)
        menu_font = pygame.font.Font(path, MENU_FONT_SIZE)
        credit_font = pygame.font.Font(path, CREDIT_FONT_SIZE)
        debug_font = pygame.font.Font(path, DEBUG_FONT_SIZE)
    except (TypeError, FileNotFoundError, pygame.error):
        menu_font = pygame.font.SysFont("monospace", MENU_FONT_SIZE, bold=False)
        credit_font = pygame.font.SysFont("monospace", CREDIT_FONT_SIZE, bold=False)
        debug_font = pygame.font.SysFont("monospace", DEBUG_FONT_SIZE, bold=False)

    gothic_font_path = get_gothic_font_path()
    try:
        title_font = pygame.font.Font(str(gothic_font_path), TITLE_FONT_SIZE)
    except (TypeError, FileNotFoundError, pygame.error):
        if pixel_font_path is not None:
            title_font = pygame.font.Font(str(pixel_font_path), TITLE_FONT_SIZE)
        else:
            title_font = pygame.font.SysFont("monospace", TITLE_FONT_SIZE, bold=False)

    return title_font, menu_font, credit_font, debug_font
