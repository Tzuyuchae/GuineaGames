import pygame
import os
from frontend_button import Button

# Setup paths
base_path = os.path.dirname(os.path.abspath(__file__))
bg_path = os.path.join(base_path, "Global Assets", "Sprites", "More Sprites", "BG Art", "Title", "BG_Title.png")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)

# Button
button_start = Button(pygame.Rect(236, 400, 200, 60), 'START') # Centered roughly for 672w

def title_update(events):
    """Handles events for the title page."""
    for event in events:
         if button_start.is_clicked(event):
            print("Start button clicked! Going to homescreen.")
            return 'homescreen'
    return None

def title_draw(screen):
    """Draws the title page with background."""
    screen_w, screen_h = screen.get_size()
    
    # 1. Draw Background
    try:
        bg_img = pygame.image.load(bg_path).convert()
        bg_img = pygame.transform.scale(bg_img, (screen_w, screen_h))
        screen.blit(bg_img, (0, 0))
    except (FileNotFoundError, pygame.error):
        screen.fill((135, 206, 235)) # Sky blue fallback

    # 2. Draw Title Text
    # Using default font for now, but scaling it up
    try:
        title_font = pygame.font.Font(None, 80)
        shadow_font = pygame.font.Font(None, 80)
    except:
        title_font = pygame.font.SysFont("Arial", 60, bold=True)
        shadow_font = pygame.font.SysFont("Arial", 60, bold=True)

    text = "GUINEA GAMES"
    
    # Draw Shadow
    text_shadow = shadow_font.render(text, True, BLACK)
    shadow_rect = text_shadow.get_rect(center=(screen_w // 2 + 3, 153))
    screen.blit(text_shadow, shadow_rect)

    # Draw Main Text
    text_surf = title_font.render(text, True, GOLD)
    text_rect = text_surf.get_rect(center=(screen_w // 2, 150))
    screen.blit(text_surf, text_rect)

    # 3. Draw Button
    button_start.draw(screen)