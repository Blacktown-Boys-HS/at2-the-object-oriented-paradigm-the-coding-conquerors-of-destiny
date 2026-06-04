import math
from posix import scandir
import pygame

from globals import SCREEN_WIDTH, FONT_ANTIALIAS, BLUE, WHITE, GRAY

class TaskPanel:
    """Animated task panel in the corner."""

    def __init__(self, font):
        self.font = font
        self.tasks = [
            {"text": "Find a key", "done": False}
        ]

        self.width = 310
        self.height = 120
        self.margin = 18
        self.tab_width = 34

        self.visible = True
        self.x = SCREEN_WIDTH - self.width - self.margin
        self.y = 18

        self.toggle_rect = pygame.Rect(0, 0, self.tab_width, 42)

    def toggle(self):
        """Makes the task panel visible or hidden."""
        self.visible = not self.visible

    def handle_event(self, event):
        """Handles events for the task panel."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.toggle_rect.collidepoint(event.pos):
                self.toggle()

    def update(self, dt):
        """Updates the task panel."""
        visible_x = SCREEN_WIDTH - self.width - self.margin
        hidden_x = SCREEN_WIDTH - self.tab_width - self.margin

        target_x = visible_x if self.visible else hidden_x
        self.x += (target_x - self.x) * min(1, dt * 10)

    def set_task_done(self, task_text):
        """Marks a task as done."""
        for task in self.tasks:
            if task["text"] == task_text:
                task["done"] = True

    def render(self, screen, time_seconds):
        """Renders the task panel on the screen."""
        panel_rect = pygame.Rect(int(self.x), self.y, self.width, self.height)

        # main panel
        panel_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        panel_surface.fill((16, 16, 24, 210))
        screen.blit(panel_surface, panel_rect.topleft)

        # Gold border
        gold = (225, 185, 80)
        pygame.draw.rect(screen, gold, panel_rect, width=2, border_radius=8)

        # Toggle tab
        tab_x = panel_rect.left - self.tab_width
        self.toggle_rect = pygame.Rect(tab_x, self.y + 16, self.width, 42)

        tab_surface = pygame.Surface((self.tab_width, 42), pygame.SRCALPHA)
        tab_surface.fill((20, 20, 28, 230))
        screen.blit(tab_surface, self.toggle_rect.topleft)
        pygame.draw.rect(screen, gold, self.toggle_rect, width=2, border_radius=8)

        arrow = ">" if self.visible else "<"
        arrow_surf = self.font.render(arrow, FONT_ANTIALIAS, gold)
        arrow_rect = arrow_surf.get_rect(center=self.toggle_rect.center)
        screen.blit(arrow_surf, arrow_rect)

        # Title shimmer
        shimmer = 0.5 + 0.5 * math.sin(time_seconds * 3)
        title_color = (
            int(126 + 30 * shimmer),
            int(193 + 20 * shimmer),
            int(245)
        )

        title = self.font.render("Tasks", FONT_ANTIALIAS, title_color)
        screen.blit(title, (panel_rect.left + 18, panel_rect.top + 14))

        # Task list
        y = panel_rect.top + 55
        for task in self.tasks:
            marker = "✓" if task["done"] else "•"
            color = GRAY if task["done"] else WHITE
            text = self.font.render(f"{marker} {task['text']}", FONT_ANTIALIAS, color)
            screen.blit(text, (panel_rect.left + 22, y))
            y += 28
