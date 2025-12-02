import pygame
from frontend.minigame.button import Button

# Initialize font module
pygame.font.init()

# Define title font
try:
    TITLE_FONT = pygame.font.SysFont('Arial', 48, bold=True)
except pygame.error:
    TITLE_FONT = pygame.font.Font(None, 60)

# Colors
TITLE_COLOR = (255, 215, 0)  # Gold
BACKGROUND_COLOR = (20, 20, 20)

# Create buttons
button_play = Button(336, 300, 250, 70, 'PLAY', (0, 150, 0), (0, 200, 0))
button_settings = Button(336, 400, 250, 70, 'SETTINGS', (0, 0, 150), (0, 0, 200))
button_quit = Button(336, 500, 250, 70, 'QUIT', (150, 0, 0), (200, 0, 0))

buttons = [button_play, button_settings, button_quit]

def title_update(events):
    """Handles events for the title page."""
    mouse_pos = pygame.mouse.get_pos()
    
    for event in events:
        if button_play.check_click(event):
            print("Play button clicked! Starting game.")
            return 'homescreen'
        
        if button_settings.check_click(event):
            print("Settings button clicked! Opening settings.")
            return 'settings'
        
        if button_quit.check_click(event):
            print("Quit button clicked! Exiting game.")
            pygame.quit()
            exit()
    
    # Update all buttons to check for hover
    for button in buttons:
        button.check_hover(mouse_pos)
    
    return None

def title_draw(screen):
    """Draws the title page."""
    # Draw background
    screen.fill(BACKGROUND_COLOR)
    
    # Draw game title
    title_surface = TITLE_FONT.render("Guinea Gone Wild", True, TITLE_COLOR)
    title_rect = title_surface.get_rect(centerx=336, y=120)
    screen.blit(title_surface, title_rect)
    
    # Draw all buttons
    for button in buttons:
        button.draw(screen)
