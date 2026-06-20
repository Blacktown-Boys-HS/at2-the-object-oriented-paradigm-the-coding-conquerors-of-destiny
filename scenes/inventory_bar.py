"""
Bottom inventory hotbar for the RPG game.
"""
import pygame

from globals import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_ANTIALIAS, WHITE, GRAY


class InventoryBar:
    """Minecraft-style bottom hotbar with animated selected slot."""

    SLOT_COUNT = 9

    def __init__(self, font):
        self.font = font
        self.slot_size = 52
        self.gap = 6
        self.margin_bottom = 22
        self.selected = 0
        self.items = [None for _ in range(self.SLOT_COUNT)]
        self.slot_scale = [1.0 for _ in range(self.SLOT_COUNT)]

    def handle_event(self, event):
        """Handle number keys and mouse wheel slot selection."""
        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_9:
                self.selected = event.key - pygame.K_1

        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self.selected = (self.selected - 1) % self.SLOT_COUNT
            elif event.y < 0:
                self.selected = (self.selected + 1) % self.SLOT_COUNT

    def update(self, dt):
        """Animate selected slot size."""
        for i in range(self.SLOT_COUNT):
            target = 1.10 if i == self.selected else 1.0
            self.slot_scale[i] += (target - self.slot_scale[i]) * min(1, dt * 12)

    def set_slot(self, index, item_name):
        """Put an item name in a slot."""
        if 0 <= index < self.SLOT_COUNT:
            self.items[index] = item_name

    def clear_slot(self, index):
        """Clear an inventory slot."""
        if 0 <= index < self.SLOT_COUNT:
            self.items[index] = None

    def render(self, screen):
        """Draw the hotbar."""
        total_width = self.SLOT_COUNT * self.slot_size + (self.SLOT_COUNT - 1) * self.gap
        start_x = (SCREEN_WIDTH - total_width) // 2
        y = SCREEN_HEIGHT - self.slot_size - self.margin_bottom

        bg_rect = pygame.Rect(start_x - 10, y - 10, total_width + 20, self.slot_size + 20)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            bg_surface,
            (12, 12, 18, 170),
            bg_surface.get_rect(),
            border_radius=8
        )
        screen.blit(bg_surface, bg_rect.topleft)

        gold = (225, 185, 80)
        slot_border = (110, 110, 120)
        slot_fill = (24, 24, 32, 220)

        for i in range(self.SLOT_COUNT):
            base_x = start_x + i * (self.slot_size + self.gap)
            scale = self.slot_scale[i]
            size = int(self.slot_size * scale)
            offset = (size - self.slot_size) // 2
            rect = pygame.Rect(base_x - offset, y - offset, size, size)

            slot_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.rect(
                slot_surface,
                slot_fill,
                slot_surface.get_rect(),
                border_radius=6
            )
            screen.blit(slot_surface, rect.topleft)

            border_color = gold if i == self.selected else slot_border
            border_width = 3 if i == self.selected else 2
            pygame.draw.rect(screen, border_color, rect, width=border_width, border_radius=6)

            number = self.font.render(str(i + 1), FONT_ANTIALIAS, GRAY)
            screen.blit(number, (rect.left + 5, rect.top + 3))

            item_name = self.items[i]
            if item_name:
                if str(item_name).lower() == "key":
                    self._draw_key_icon(screen, rect)
                else:
                    icon_text = self.font.render(str(item_name)[:1].upper(), FONT_ANTIALIAS, WHITE)
                    icon_rect = icon_text.get_rect(center=(rect.centerx, rect.centery + 4))
                    screen.blit(icon_text, icon_rect)

    def _draw_key_icon(self, screen, rect):
        """Draw a small gold key icon inside a hotbar slot."""
        gold = (225, 185, 80)
        highlight = (255, 230, 135)
        shadow = (80, 55, 28)

        cx = rect.centerx - 6
        cy = rect.centery + 3
        pygame.draw.circle(screen, shadow, (cx + 1, cy + 1), 8, width=3)
        pygame.draw.circle(screen, gold, (cx, cy), 8, width=3)
        pygame.draw.line(screen, shadow, (cx + 8, cy + 1), (cx + 25, cy + 1), 5)
        pygame.draw.line(screen, gold, (cx + 8, cy), (cx + 25, cy), 5)
        pygame.draw.line(screen, gold, (cx + 20, cy), (cx + 20, cy + 8), 4)
        pygame.draw.line(screen, gold, (cx + 25, cy), (cx + 25, cy + 6), 4)
        pygame.draw.circle(screen, highlight, (cx - 3, cy - 3), 2)
