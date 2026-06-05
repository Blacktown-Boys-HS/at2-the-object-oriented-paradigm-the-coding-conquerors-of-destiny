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

# Game display name
GAME_TITLE = "Escape the Dungeon"

# Font sizes
TITLE_FONT_SIZE = 72
MENU_FONT_SIZE = 48
CREDIT_FONT_SIZE = 24
DEBUG_FONT_SIZE = 32

# pygame.font.Font.render(…, antialias, …) — False keeps pixel fonts crisp
FONT_ANTIALIAS = False


def _first_existing_path(candidates):
    return next(path for path in candidates if path.exists())


def gothic_font_candidates():
    """Paths to GothicByte.ttf (preferred UI font)."""
    base_dir = Path(__file__).resolve().parent
    return [
        base_dir / "assets" / "fonts" / "GothicByte.ttf",
        base_dir / "assets" / "font" / "GothicByte.ttf",
    ]


def get_gothic_font_path():
    """Return path to GothicByte.ttf, or None if missing."""
    try:
        return _first_existing_path(gothic_font_candidates())
    except StopIteration:
        return None


def load_fonts():
    """Load GothicByte for all UI text sizes."""
    font_path = get_gothic_font_path()
    if font_path is not None:
        try:
            path = str(font_path)
            title_font = pygame.font.Font(path, TITLE_FONT_SIZE)
            menu_font = pygame.font.Font(path, MENU_FONT_SIZE)
            credit_font = pygame.font.Font(path, CREDIT_FONT_SIZE)
            debug_font = pygame.font.Font(path, DEBUG_FONT_SIZE)
            return title_font, menu_font, credit_font, debug_font
        except pygame.error:
            pass

    title_font = pygame.font.SysFont("monospace", TITLE_FONT_SIZE, bold=False)
    menu_font = pygame.font.SysFont("monospace", MENU_FONT_SIZE, bold=False)
    credit_font = pygame.font.SysFont("monospace", CREDIT_FONT_SIZE, bold=False)
    debug_font = pygame.font.SysFont("monospace", DEBUG_FONT_SIZE, bold=False)
    return title_font, menu_font, credit_font, debug_font
