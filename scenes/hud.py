"""
HUD (Heads Up Display) for the RPG game.

This module handles all UI rendering for the game, organized into three categories:

1. PLAYER HUD ELEMENTS: Health bar and coordinate display above the player.
2. INTERACTION PROMPTS: Visual feedback for player interactions (doors, keys, locked doors).
3. DEBUG VISUALIZATION: Collision rects and other debug information.

All rendering functions take a screen object and camera position to properly display
elements in world space on the player's viewport.
"""

import math

import pygame

from globals import FONT_ANTIALIAS, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE
from scenes.aesthetic import GOTHIC_GOLD, GOTHIC_GOLD_DIM, GOTHIC_PANEL_INNER

# ============================================================================
# PLAYER HUD ELEMENTS
# ============================================================================


def draw_player_health_bar(screen, player, font, time_seconds=0.0):
    """Gothic health panel fixed to the top-left of the screen."""
    margin = 18
    bar_width = 190
    bar_height = 12
    pad_x, pad_y = 14, 10
    label_h = font.get_height()

    hp_text = font.render(
        f"{int(player.health)} / {int(player.max_health)}",
        FONT_ANTIALIAS,
        WHITE,
    )
    title = font.render("Health", FONT_ANTIALIAS, GOTHIC_GOLD)

    panel_w = max(bar_width, title.get_width(), hp_text.get_width()) + pad_x * 2
    panel_h = label_h + 8 + bar_height + 6 + label_h + pad_y * 2
    panel_x = margin
    panel_y = margin

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(panel, GOTHIC_GOLD, panel.get_rect(), border_radius=10)
    inner = panel.get_rect().inflate(-5, -5)
    pygame.draw.rect(panel, (*GOTHIC_PANEL_INNER, 245), inner, border_radius=8)
    screen.blit(panel, (panel_x, panel_y))

    title_rect = title.get_rect(topleft=(panel_x + pad_x, panel_y + pad_y))
    screen.blit(title, title_rect)

    bar_x = panel_x + pad_x
    bar_y = title_rect.bottom + 8
    track_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)

    pygame.draw.rect(screen, (40, 12, 14), track_rect, border_radius=6)
    pygame.draw.rect(screen, (20, 16, 22), track_rect, width=1, border_radius=6)

    health_pct = player.health / player.max_health
    fill_width = max(0, int(bar_width * health_pct))
    if health_pct > 0.6:
        fill_color = (72, 168, 88)
        fill_hi = (110, 210, 125)
    elif health_pct > 0.3:
        fill_color = (200, 150, 45)
        fill_hi = (235, 190, 80)
    else:
        fill_color = (190, 55, 55)
        fill_hi = (230, 90, 90)

    if player.is_regenerating:
        pulse = 0.5 + 0.5 * math.sin(time_seconds * 5.0)
        boost = int(40 * pulse)
        fill_color = tuple(
            min(255, int(c * (0.85 + 0.15 * pulse) + (boost if i == 1 else 0)))
            for i, c in enumerate(fill_color)
        )
        fill_hi = (120, 220, 140)

    if fill_width > 0:
        fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
        pygame.draw.rect(screen, fill_color, fill_rect, border_radius=6)
        shine_h = max(2, bar_height // 3)
        shine = pygame.Rect(bar_x, bar_y, fill_width, shine_h)
        pygame.draw.rect(screen, fill_hi, shine, border_radius=6)

    hp_rect = hp_text.get_rect(topleft=(bar_x, bar_y + bar_height + 6))
    screen.blit(hp_text, hp_rect)

    if player.is_regenerating:
        regen = font.render("Regenerating", FONT_ANTIALIAS, (130, 210, 140))
        regen_rect = regen.get_rect(topright=(panel_x + panel_w - pad_x, panel_y + pad_y))
        screen.blit(regen, regen_rect)
    elif (
        player.health < player.max_health
        and player.time_since_last_damage < player.REGEN_DELAY
    ):
        wait = player.REGEN_DELAY - player.time_since_last_damage
        regen_soon = font.render(f"Regen in {wait:.0f}s", FONT_ANTIALIAS, (150, 145, 155))
        regen_rect = regen_soon.get_rect(
            topright=(panel_x + panel_w - pad_x, panel_y + pad_y)
        )
        screen.blit(regen_soon, regen_rect)


def draw_debug_coords(screen, player, font):
    """Draw player coordinates for debugging."""
    coord_text = font.render(
        f"x:{player.position.x:.1f}  y:{player.position.y:.1f}",
        FONT_ANTIALIAS,
        (255, 255, 0),
    )
    screen.blit(coord_text, (10, 90))


# ============================================================================
# INTERACTION PROMPTS
# ============================================================================


def _player_screen_pos(player, camera, zoom):
    screen_x = (player.position.x - camera.x) * zoom + SCREEN_WIDTH / 2
    screen_y = (player.position.y - camera.y) * zoom + SCREEN_HEIGHT / 2
    return screen_x, screen_y


def _draw_simple_prompt(screen, center_x, center_y, font, text, border_color):
    """Minimal prompt above the player: dark box, thin border, [E] label."""
    key = font.render("[E]", FONT_ANTIALIAS, GOTHIC_GOLD)
    label = font.render(text, FONT_ANTIALIAS, WHITE)
    pad_x, pad_y = 10, 7
    gap = 6
    box_w = key.get_width() + gap + label.get_width() + pad_x * 2
    box_h = max(key.get_height(), label.get_height()) + pad_y * 2
    box_x = int(center_x - box_w / 2)
    box_y = int(center_y - 72)

    box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    box_surf.fill((*GOTHIC_PANEL_INNER, 215))
    screen.blit(box_surf, (box_x, box_y))
    pygame.draw.rect(
        screen, border_color, (box_x, box_y, box_w, box_h), 1, border_radius=6
    )

    row_y = box_y + (box_h - label.get_height()) // 2
    screen.blit(key, (box_x + pad_x, row_y))
    screen.blit(label, (box_x + pad_x + key.get_width() + gap, row_y))


def draw_door_prompt(screen, player, camera, zoom, font):
    """Draw a door interaction prompt above the player."""
    sx, sy = _player_screen_pos(player, camera, zoom)
    _draw_simple_prompt(screen, sx, sy, font, "Open Door", (100, 150, 110))


def draw_key_prompt(screen, player, camera, zoom, font):
    """Draw a key pickup prompt above the player."""
    sx, sy = _player_screen_pos(player, camera, zoom)
    _draw_simple_prompt(screen, sx, sy, font, "Pick Up Key", GOTHIC_GOLD_DIM)


def draw_locked_door_prompt(screen, player, camera, zoom, font):
    """Draw a locked door message above the player."""
    sx, sy = _player_screen_pos(player, camera, zoom)
    _draw_simple_prompt(screen, sx, sy, font, "Locked — need key", (180, 80, 80))


# ============================================================================
# DEBUG VISUALIZATION
# ============================================================================


def draw_debug_collision(screen, collision_rects, camera, zoom):
    """Draw collision rects for debugging."""
    for rect in collision_rects:
        screen_x = (rect.x - camera.x) * zoom + SCREEN_WIDTH / 2
        screen_y = (rect.y - camera.y) * zoom + SCREEN_HEIGHT / 2
        debug_rect = pygame.Rect(
            screen_x, screen_y, rect.width * zoom, rect.height * zoom
        )
        pygame.draw.rect(screen, (255, 0, 0), debug_rect, 1)
