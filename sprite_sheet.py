"""
Slice rectangular frames from a sprite sheet image.
"""
from pathlib import Path

import pygame


class SpriteSheet:
    """Fixed-size grid frames (e.g. Brackeys RPG knight sheet)."""

    def __init__(self, path, frame_width: int, frame_height: int):
        self.sheet = pygame.image.load(str(Path(path))).convert_alpha()
        self.fw = frame_width
        self.fh = frame_height
        sw, sh = self.sheet.get_size()
        self.cols = sw // frame_width
        self.rows = sh // frame_height

    def frame(self, col: int, row: int):
        """Return one frame as a standalone surface."""
        col = max(0, min(col, self.cols - 1))
        row = max(0, min(row, self.rows - 1))
        rect = pygame.Rect(col * self.fw, row * self.fh, self.fw, self.fh)
        surf = pygame.Surface((self.fw, self.fh), pygame.SRCALPHA)
        surf.blit(self.sheet, (0, 0), rect)
        return surf
