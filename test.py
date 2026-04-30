import pygame
import sys

pygame.init()

# Screen setup
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RPG Game")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
LIGHT_GRAY = (180, 180, 180)
HOVER_COLOR = (200, 200, 200)

# Clock for FPS
clock = pygame.time.Clock()
FPS = 60

# Try to use the Pixelify font, fallback to system monospace font
try:
    title_font = pygame.font.Font("assets/font/PixelifySans-Regular.ttf", 72)
    menu_font = pygame.font.Font("assets/font/PixelifySans-Regular.ttf", 48)
    credit_font = pygame.font.Font("assets/font/PixelifySans-Regular.ttf", 24)
except (FileNotFoundError, pygame.error):
    title_font = pygame.font.SysFont("monospace", 72, bold=False)
    menu_font = pygame.font.SysFont("monospace", 48, bold=False)
    credit_font = pygame.font.SysFont("monospace", 24, bold=False)

# Menu items
menu_items = ["Play Game", "Settings", "Credits"]
selected_item = 0
menu_item_rects = []
hover_scale = [1.0, 1.0, 1.0]  # For smooth hover animations
current_scene = "menu"  # Track which scene we're in

# Game loop
running = True

while running:
    clock.tick(FPS)
    
    # Get mouse position
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                current_scene = "menu"
            elif current_scene == "menu":
                if event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    if menu_items[selected_item] == "Play Game":
                        print("Starting game...")
                    elif menu_items[selected_item] == "Settings":
                        print("Opening settings...")
                    elif menu_items[selected_item] == "Credits":
                        current_scene = "credits"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if current_scene == "menu":
                # Check if clicked on any menu item
                for i, rect in enumerate(menu_item_rects):
                    if rect.collidepoint(mouse_pos):
                        if menu_items[i] == "Play Game":
                            print("Starting game...")
                        elif menu_items[i] == "Settings":
                            print("Opening settings...")
                        elif menu_items[i] == "Credits":
                            current_scene = "credits"
    
    screen.fill(BLACK)

    if current_scene == "menu":
        # Draw main menu
        title_text = title_font.render("RPG Placeholder Title", False, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        screen.blit(title_text, title_rect)

        for i in range(len(menu_items)):
            if i == selected_item:
                hover_scale[i] = min(hover_scale[i] + 0.05, 1.15)
            else:
                hover_scale[i] = max(hover_scale[i] - 0.05, 1.0)

        menu_start_y = 300
        menu_item_rects = []
        for i, item in enumerate(menu_items):
            if i == selected_item:
                color = WHITE
                text = menu_font.render(f"> {item} <", False, color)
            else:
                color = GRAY
                text = menu_font.render(item, False, color)
            
            if hover_scale[i] != 1.0:
                scaled_width = int(text.get_width() * hover_scale[i])
                scaled_height = int(text.get_height() * hover_scale[i])
                text = pygame.transform.scale(text, (scaled_width, scaled_height))
            
            text_rect = text.get_rect(topleft=(150, menu_start_y + i * 100))
            menu_item_rects.append(text_rect)
            screen.blit(text, text_rect)
        
        for i, rect in enumerate(menu_item_rects):
            if rect.collidepoint(mouse_pos):
                selected_item = i
                break
    
    elif current_scene == "credits":
        # Draw credits scene
        credits_title = title_font.render("CREDITS", False, WHITE)
        credits_title_rect = credits_title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(credits_title, credits_title_rect)
        
        credits_items = [
            "Software Assessment",
            "",
            "Made by The Coding Conquerors of Destiny™",
            "",
            "Blacktown Boys High School"
        ]
        
        credits_start_y = 200
        for i, item in enumerate(credits_items):
            if item:  # Only render non-empty lines
                credits_text = credit_font.render(item, False, WHITE)
                credits_rect = credits_text.get_rect(center=(SCREEN_WIDTH // 2, credits_start_y + i * 60))
                screen.blit(credits_text, credits_rect)
        
        # Draw "Press ESC to return" hint
        esc_text = credit_font.render("Press ESC to return to menu", False, GRAY)
        esc_rect = esc_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(esc_text, esc_rect)
    
    pygame.display.update()

pygame.quit()
sys.exit()