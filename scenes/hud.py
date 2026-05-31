"""
HUD (Heads Up Display) for the RPG game.
Handles health bar above player and debug overlays.
"""

import pygame
from globals import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_ANTIALIAS

def draw_player_health_bar(screen, player, camera, zoom):
    """Draw a health bar above the player sprite."""
    screen_x = (player.position.x - camera.x) * zoom + SCREEN_WIDTH / 2
    screen_y = (player.position.y - camera.y) * zoom + SCREEN_HEIGHT / 2

    bar_width = 40
    bar_height = 6
    bar_x = int(screen_x - bar_width / 2)
    bar_y = int(screen_y - 44)

    # Shadow
    pygame.draw.rect(screen, (0, 0, 0), (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2), border_radius=3)

    # Background
    pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y, bar_width, bar_height), border_radius=3)

    # Health fill
    health_pct = player.health / player.max_health
    fill_width = max(0, int(bar_width * health_pct))
    if health_pct > 0.6:
        fill_color = (0, 200, 0)
    elif health_pct > 0.3:
        fill_color = (220, 180 ,0)
    else:
        fill_color = (220, 40, 40)
    if fill_width > 0:
        pygame.draw.rect(screen, fill_color, (bar_x, bar_y, fill_width, bar_height), border_radius=3) 

    # Border
    pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 1, border_radius=3)

def draw_debug_collision(screen, collision_rects, camera, zoom):
    """"Draw collision rects for debugging"""
    for rect in collision_rects:
        screen_x = (rect.x - camera.x) * zoom + SCREEN_WIDTH / 2
        screen_y = (rect.y - camera.y) * zoom + SCREEN_HEIGHT / 2
        debug_rect = pygame.Rect(screen_x, screen_y, rect.width * zoom, rect.height * zoom)

        pygame.draw.rect(screen, (255, 0, 0), debug_rect, 1)

def draw_debug_coords(screen, player, font):
    """Draw player coordinates for debugging."""
    coord_text = font.render(
        f"x:{player.position.x:.1f}  y:{player.position.y:.1f}",
        FONT_ANTIALIAS,
        (255, 255, 0),
    )
    screen.blit(coord_text, (10, 90))

def draw_door_prompt(screen, player, camera, zoom, font):
    """Draw a styled door interaction prompt above the player."""
    screen_x = (player.position.x - camera.x) * zoom + SCREEN_WIDTH / 2
    screen_y = (player.position.y - camera.y) * zoom + SCREEN_HEIGHT / 2

    # Render text
    arrow = font.render("> E ", FONT_ANTIALIAS, (100, 160, 120))
    label = font.render("Open Door", FONT_ANTIALIAS, (255, 255, 255))

    total_w = arrow.get_width() + label.get_width()
    pad_x, pad_y = 20, 12
    box_w = total_w + pad_x * 2
    box_h = label.get_height() + pad_y * 2

    box_x = int(screen_x - box_w / 2)
    box_y = int(screen_y - 80)

    # Box background
    box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    box_surf.fill((30, 30, 30, 200))
    screen.blit(box_surf, (box_x, box_y))

    # Border
    pygame.draw.rect(screen, (130, 130, 130), (box_x, box_y, box_w, box_h), 2, border_radius=8)

    # Text
    screen.blit(arrow, (box_x + pad_x, box_y + pad_y))
    screen.blit(label, (box_x + pad_x + arrow.get_width(), box_y + pad_y))
