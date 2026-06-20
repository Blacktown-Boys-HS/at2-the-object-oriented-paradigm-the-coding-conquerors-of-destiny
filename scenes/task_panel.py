import pygame

from game_data import objective_task_list
from globals import SCREEN_WIDTH, FONT_ANTIALIAS, WHITE, GRAY
from scenes.aesthetic import GOTHIC_GOLD, GOTHIC_GOLD_DIM

class TaskPanel:
    """Animated task panel in the corner."""

    def __init__(self, font):
        self.font = font
        self.tasks = objective_task_list()

        self.width = 310
        self.height = 150
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

    def add_task(self, task_text):
        """Adds a new task if it is not already listed."""
        for task in self.tasks:
            if task["text"] == task_text:
                return
        self.tasks.append({"text": task_text, "done": False})

    def render(self, screen, time_seconds):
        """Renders the task panel on the screen."""
        panel_rect = pygame.Rect(int(self.x), self.y, self.width, self.height)

        # main panel
        gold = GOTHIC_GOLD
        panel_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        panel_outer_rect = panel_surface.get_rect()
        panel_inner_rect = panel_outer_rect.inflate(-4, -4)
        pygame.draw.rect(
            panel_surface,
            gold,
            panel_outer_rect,
            border_radius=8
        )
        pygame.draw.rect(
            panel_surface,
            (16, 16, 24, 235),
            panel_inner_rect,
            border_radius=6
        )
        screen.blit(panel_surface, panel_rect.topleft)

        # Toggle tab
        tab_x = panel_rect.left - self.tab_width
        self.toggle_rect = pygame.Rect(tab_x, self.y + 16, self.tab_width, 42)

        tab_surface = pygame.Surface((self.tab_width, 42), pygame.SRCALPHA)
        tab_outer_rect = tab_surface.get_rect()
        tab_inner_rect = tab_outer_rect.inflate(-4, -4)
        pygame.draw.rect(
            tab_surface,
            gold,
            tab_outer_rect,
            border_radius=8
        )
        pygame.draw.rect(
            tab_surface,
            (20, 20, 28, 245),
            tab_inner_rect,
            border_radius=6
        )
        screen.blit(tab_surface, self.toggle_rect.topleft)

        arrow = ">" if self.visible else "<"
        arrow_surf = self.font.render(arrow, FONT_ANTIALIAS, gold)
        arrow_rect = arrow_surf.get_rect(center=self.toggle_rect.center)
        screen.blit(arrow_surf, arrow_rect)

        del time_seconds
        title = self.font.render("Tasks", FONT_ANTIALIAS, GOTHIC_GOLD_DIM)
        screen.blit(title, (panel_rect.left + 18, panel_rect.top + 14))

        # Task list
        y = panel_rect.top + 55
        for task in self.tasks:
            marker = "✓" if task["done"] else "•"
            color = GRAY if task["done"] else WHITE
            text = self.font.render(f"{marker} {task['text']}", FONT_ANTIALIAS, color)
            screen.blit(text, (panel_rect.left + 22, y))
            y += 28
