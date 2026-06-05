"""
Shared visual style: gothic menu theme, backgrounds, typography helpers.
"""
import random
import pygame

from globals import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    WHITE,
    GRAY,
    FONT_ANTIALIAS,
)

FOOTER_HINT_COLOR = (150, 145, 155)
SUBTITLE_COLOR = (185, 180, 190)
BODY_MUTED = (160, 155, 165)

GOTHIC_GOLD = (196, 158, 78)
GOTHIC_GOLD_DIM = (118, 92, 48)
GOTHIC_STONE = (10, 8, 14)
GOTHIC_PANEL_INNER = (18, 14, 24)
GOTHIC_TEXT_MUTED = (145, 140, 150)
GOTHIC_SHADOW = (28, 22, 36)


def safe_scale_surface(surface, scale_factor):
    """Scale surfaces with nearest neighbor so text stays crisp (no smooth blur)."""
    target_width = max(1, int(surface.get_width() * scale_factor))
    target_height = max(1, int(surface.get_height() * scale_factor))
    converted = surface.convert_alpha()
    return pygame.transform.scale(converted, (target_width, target_height))


class SharedBackground:
    """Dark stone gradient with drifting embers."""

    def __init__(self, width=None, height=None, dot_count=50):
        self.width = width or SCREEN_WIDTH
        self.height = height or SCREEN_HEIGHT
        self.dots = []
        for _ in range(dot_count):
            self.dots.append(
                {
                    "x": random.randint(0, self.width),
                    "y": random.randint(0, self.height),
                    "radius": random.randint(1, 2),
                    "speed": random.uniform(0.2, 0.9),
                    "alpha": random.randint(30, 90),
                }
            )

    def update(self, dt):
        for dot in self.dots:
            dot["y"] += dot["speed"]
            if dot["y"] > self.height + dot["radius"]:
                dot["y"] = -dot["radius"]
                dot["x"] = random.randint(0, self.width)

    def draw(self, screen):
        screen.fill(GOTHIC_STONE)
        for y in range(0, self.height, 4):
            shade = 8 + int((y / self.height) * 18)
            pygame.draw.rect(
                screen,
                (shade, shade - 1, shade + 6),
                (0, y, self.width, 4),
            )

        dot_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for dot in self.dots:
            color = (GOTHIC_GOLD[0], GOTHIC_GOLD[1], GOTHIC_GOLD[2], dot["alpha"])
            pygame.draw.circle(
                dot_surface,
                color,
                (int(dot["x"]), int(dot["y"])),
                dot["radius"],
            )
        screen.blit(dot_surface, (0, 0))


def draw_gothic_title(screen, font, text, center_x, center_y, color=WHITE):
    """Static white title with a soft shadow — no pulse or shimmer."""
    shadow = font.render(text, FONT_ANTIALIAS, GOTHIC_SHADOW)
    main = font.render(text, FONT_ANTIALIAS, color)
    rect = main.get_rect(center=(center_x, center_y))
    screen.blit(shadow, (rect.x + 2, rect.y + 2))
    screen.blit(main, rect)

    title_w = main.get_width()
    bar_y = rect.bottom + 10
    bar_x0 = center_x - int(title_w * 0.34)
    bar_x1 = center_x + int(title_w * 0.34)
    pygame.draw.line(screen, GOTHIC_GOLD_DIM, (bar_x0, bar_y + 1), (bar_x1, bar_y + 1), 3)
    pygame.draw.line(screen, GOTHIC_GOLD, (bar_x0, bar_y), (bar_x1, bar_y), 2)


def draw_pulsing_title(screen, font, text, center_x, center_y, time_seconds):
    """Alias for gothic static title (kept for scene compatibility)."""
    del time_seconds
    draw_gothic_title(screen, font, text, center_x, center_y)


def draw_subtitle_centered(screen, font, text, center_x, center_y, color=SUBTITLE_COLOR):
    surf = font.render(text, FONT_ANTIALIAS, color)
    rect = surf.get_rect(center=(center_x, center_y))
    screen.blit(surf, rect)


def draw_footer_hint(screen, font, text, margin_bottom=45, color=FOOTER_HINT_COLOR):
    surf = font.render(text, FONT_ANTIALIAS, color)
    rect = surf.get_rect(
        center=(screen.get_width() // 2, screen.get_height() - margin_bottom)
    )
    screen.blit(surf, rect)


def draw_gothic_panel(screen, rect, border_radius=10):
    """Gold-trimmed dark panel."""
    outer = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(outer, GOTHIC_GOLD, outer.get_rect(), border_radius=border_radius)
    inner = outer.get_rect().inflate(-6, -6)
    pygame.draw.rect(outer, (*GOTHIC_PANEL_INNER, 245), inner, border_radius=border_radius - 2)
    screen.blit(outer, rect.topleft)


def draw_gothic_selection_box(
    screen,
    rect,
    activating=False,
    activation_progress=0.0,
):
    """Menu selection highlight — dark fill, gold border."""
    box_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    box_alpha = 28
    if activating:
        box_alpha = 28 + int(55 * (1.0 - activation_progress))
    box_surface.fill((GOTHIC_GOLD[0], GOTHIC_GOLD[1], GOTHIC_GOLD[2], box_alpha))
    screen.blit(box_surface, rect.topleft)
    border = GOTHIC_GOLD_DIM
    if activating:
        border = GOTHIC_GOLD
    pygame.draw.rect(screen, border, rect, width=2, border_radius=8)


def draw_gothic_menu_item(
    screen,
    font,
    text,
    topleft,
    selected,
    hover_scale=1.0,
    scale_fn=safe_scale_surface,
):
    """Draw one menu row; returns hit rect."""
    x, y = topleft
    if selected:
        arrow = font.render("> ", FONT_ANTIALIAS, GOTHIC_GOLD)
        label = font.render(text, FONT_ANTIALIAS, WHITE)
        if hover_scale != 1.0:
            arrow = scale_fn(arrow, hover_scale)
            label = scale_fn(label, hover_scale)
        arrow_rect = arrow.get_rect(topleft=(x, y))
        label_rect = label.get_rect(topleft=(arrow_rect.right, y))
        screen.blit(arrow, arrow_rect)
        screen.blit(label, label_rect)
        return arrow_rect.union(label_rect)

    label = font.render(text, FONT_ANTIALIAS, GRAY)
    if hover_scale != 1.0:
        label = scale_fn(label, hover_scale)
    label_rect = label.get_rect(topleft=(x, y))
    screen.blit(label, label_rect)
    return label_rect
