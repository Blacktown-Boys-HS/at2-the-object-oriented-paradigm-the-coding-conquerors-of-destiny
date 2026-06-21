"""
HUD for the RPG game.

This module handles all UI rendering for the game

All rendering functions take a screen object and camera position to properly display
elements in world space on the player's viewport.
"""

import math

import pygame

from globals import FONT_ANTIALIAS, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE
from scenes.aesthetic import GOTHIC_GOLD, GOTHIC_GOLD_DIM, GOTHIC_PANEL_INNER

# PLAYER HUD ELEMENTS

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


def draw_attack_cooldown(screen, player, font, time_seconds=0.0):
    """Gothic ability cooldown panel fixed under the health panel."""
    margin = 18
    panel_x = margin
    panel_y = 120
    panel_w = 245
    panel_h = 104
    pad = 12
    bar_w = panel_w - pad * 2
    bar_h = 8

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(panel, GOTHIC_GOLD, panel.get_rect(), border_radius=10)
    inner = panel.get_rect().inflate(-5, -5)
    pygame.draw.rect(panel, (*GOTHIC_PANEL_INNER, 245), inner, border_radius=8)
    screen.blit(panel, (panel_x, panel_y))

    def draw_ability_row(label, cooldown, duration, row_y, ready_color, fill_color, fill_hi):
        duration = max(0.01, duration)
        cooldown = max(0.0, cooldown)
        ready = cooldown <= 0
        fill_pct = 1.0 if ready else 1.0 - min(1.0, cooldown / duration)

        pulse = 0.5 + 0.5 * math.sin(time_seconds * 5.0)
        title_color = GOTHIC_GOLD if ready else (165, 150, 120)
        if ready:
            title_color = (
                min(255, int(ready_color[0] + 20 * pulse)),
                min(255, int(ready_color[1] + 20 * pulse)),
                min(255, int(ready_color[2] + 10 * pulse)),
            )

        title = font.render(label, FONT_ANTIALIAS, title_color)
        status_text = "Ready" if ready else f"{cooldown:.1f}s"
        status_color = (120, 220, 160) if ready else (185, 175, 150)
        status = font.render(status_text, FONT_ANTIALIAS, status_color)

        screen.blit(title, (panel_x + pad, row_y))
        status_rect = status.get_rect(topright=(panel_x + panel_w - pad, row_y))
        screen.blit(status, status_rect)

        bar_x = panel_x + pad
        bar_y = row_y + 28
        track = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
        pygame.draw.rect(screen, (22, 18, 24), track, border_radius=5)
        pygame.draw.rect(screen, (55, 45, 42), track, width=1, border_radius=5)

        fill_w = max(0, int(bar_w * fill_pct))
        if fill_w > 0:
            fill = pygame.Rect(bar_x, bar_y, fill_w, bar_h)
            current_fill = ready_color if ready else fill_color
            pygame.draw.rect(screen, current_fill, fill, border_radius=5)
            shine = pygame.Rect(bar_x, bar_y, fill_w, max(2, bar_h // 3))
            pygame.draw.rect(screen, fill_hi, shine, border_radius=5)

    draw_ability_row(
        "[F] Slash",
        player.attack_cooldown,
        player.attack_cooldown_duration,
        panel_y + 9,
        (225, 185, 80),
        (90, 150, 220),
        (130, 195, 245),
    )
    draw_ability_row(
        "[RMB/R] Fireball",
        player.fireball_cooldown,
        player.fireball_cooldown_duration,
        panel_y + 53,
        (245, 145, 65),
        (210, 80, 45),
        (255, 180, 90),
    )


def draw_boss_health_bar(screen, boss, font, time_seconds=0.0):
    """Render the boss name and health bar at the top of the screen."""
    if boss is None or boss.is_dead:
        return

    panel_w = 620
    panel_h = 74
    panel_x = (SCREEN_WIDTH - panel_w) // 2
    panel_y = 18
    pad = 14
    bar_h = 16

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(panel, GOTHIC_GOLD, panel.get_rect(), border_radius=10)
    inner = panel.get_rect().inflate(-5, -5)
    pygame.draw.rect(panel, (*GOTHIC_PANEL_INNER, 245), inner, border_radius=8)
    screen.blit(panel, (panel_x, panel_y))

    pulse = 0.5 + 0.5 * math.sin(time_seconds * 3.5)
    name_color = (
        min(255, int(185 + 35 * pulse)),
        min(255, int(95 + 25 * pulse)),
        min(255, int(230 + 20 * pulse)),
    )
    name = getattr(boss, "NAME", "Boss")
    title = font.render(name, FONT_ANTIALIAS, name_color)
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 22))
    screen.blit(title, title_rect)

    bar_x = panel_x + pad
    bar_y = panel_y + 44
    bar_w = panel_w - pad * 2
    track_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)

    pygame.draw.rect(screen, (42, 8, 45), track_rect, border_radius=8)
    pygame.draw.rect(screen, (14, 10, 18), track_rect, width=1, border_radius=8)

    health_pct = max(0, boss.health / boss.MAX_HEALTH)
    fill_w = int(bar_w * health_pct)
    if fill_w > 0:
        fill_rect = pygame.Rect(bar_x, bar_y, fill_w, bar_h)
        pygame.draw.rect(screen, (135, 54, 196), fill_rect, border_radius=8)
        shine_rect = pygame.Rect(bar_x, bar_y, fill_w, max(3, bar_h // 3))
        pygame.draw.rect(screen, (205, 130, 255), shine_rect, border_radius=8)

    hp_text = font.render(
        f"{int(boss.health)} / {int(boss.MAX_HEALTH)}",
        FONT_ANTIALIAS,
        WHITE,
    )
    hp_rect = hp_text.get_rect(center=track_rect.center)
    screen.blit(hp_text, hp_rect)


def draw_debug_coords(screen, player, font):
    """Draw player coordinates for debugging."""
    coord_text = font.render(
        f"x:{player.position.x:.1f}  y:{player.position.y:.1f}",
        FONT_ANTIALIAS,
        (255, 255, 0),
    )
    screen.blit(coord_text, (10, 90))

# INTERACTION PROMPTS

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


def draw_exit_prompt(screen, player, camera, zoom, font):
    """Draw an exit interaction prompt above the player."""
    sx, sy = _player_screen_pos(player, camera, zoom)
    _draw_simple_prompt(screen, sx, sy, font, "Escape", GOTHIC_GOLD_DIM)


def draw_go_back_prompt(screen, player, camera, zoom, font):
    """Draw a return interaction prompt above the player."""
    sx, sy = _player_screen_pos(player, camera, zoom)
    _draw_simple_prompt(screen, sx, sy, font, "Go Back", GOTHIC_GOLD_DIM)


def draw_objective_arrow(
    screen,
    player,
    target_rect,
    camera,
    zoom,
    font,
    time_seconds=0.0,
    label_text="Boss door",
):
    """Draw a pulsing arrow that points from the player toward a world target."""
    if target_rect is None:
        return

    player_x, player_y = _player_screen_pos(player, camera, zoom)
    target_x = (target_rect.centerx - camera.x) * zoom + SCREEN_WIDTH / 2
    target_y = (target_rect.centery - camera.y) * zoom + SCREEN_HEIGHT / 2

    dx = target_x - player_x
    dy = target_y - player_y
    distance = math.hypot(dx, dy)
    if distance < 1:
        return

    dx /= distance
    dy /= distance

    pulse = 0.5 + 0.5 * math.sin(time_seconds * 5.0)
    arrow_distance = 54 + int(6 * pulse)
    center = (
        int(player_x + dx * arrow_distance),
        int(player_y + dy * arrow_distance - 28),
    )

    angle = math.atan2(dy, dx)
    tip = (
        int(center[0] + math.cos(angle) * 18),
        int(center[1] + math.sin(angle) * 18),
    )
    left = (
        int(center[0] + math.cos(angle + 2.45) * 14),
        int(center[1] + math.sin(angle + 2.45) * 14),
    )
    right = (
        int(center[0] + math.cos(angle - 2.45) * 14),
        int(center[1] + math.sin(angle - 2.45) * 14),
    )

    shadow_tip = (tip[0] + 2, tip[1] + 2)
    shadow_left = (left[0] + 2, left[1] + 2)
    shadow_right = (right[0] + 2, right[1] + 2)
    pygame.draw.polygon(screen, (25, 18, 12), [shadow_tip, shadow_left, shadow_right])
    pygame.draw.polygon(screen, GOTHIC_GOLD, [tip, left, right])
    pygame.draw.polygon(screen, (255, 230, 140), [tip, left, right], width=2)

    label = font.render(label_text, FONT_ANTIALIAS, GOTHIC_GOLD)
    label_rect = label.get_rect(center=(center[0], center[1] + 28))
    screen.blit(label, label_rect)

# DEBUG VISUALIZATION

def draw_debug_collision(screen, collision_rects, camera, zoom):
    """Draw collision rects for debugging."""
    for rect in collision_rects:
        screen_x = (rect.x - camera.x) * zoom + SCREEN_WIDTH / 2
        screen_y = (rect.y - camera.y) * zoom + SCREEN_HEIGHT / 2
        debug_rect = pygame.Rect(
            screen_x, screen_y, rect.width * zoom, rect.height * zoom
        )
        #pygame.draw.rect(screen, (255, 0, 0), debug_rect, 1)
