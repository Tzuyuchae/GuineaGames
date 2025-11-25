import pygame
from button import Button

# Initialize font module
pygame.font.init()

# Define fonts
try:
    TITLE_FONT = pygame.font.SysFont('Arial', 32, bold=True)
    TEXT_FONT = pygame.font.SysFont('Arial', 20)
except pygame.error:
    TITLE_FONT = pygame.font.Font(None, 42)
    TEXT_FONT = pygame.font.Font(None, 26)

# Colors
TEXT_COLOR = (255, 255, 255)
HEADING_COLOR = (255, 215, 0)  # Gold
BACKGROUND_COLOR = (20, 20, 20)

# Create buttons
button_help = Button(336, 250, 250, 70, 'HELP', (0, 0, 150), (0, 0, 200))
button_volume = Button(336, 350, 250, 70, 'VOLUME', (0, 150, 0), (0, 200, 0))
button_restart = Button(336, 450, 250, 70, 'RESTART', (150, 0, 0), (200, 0, 0))
button_back = Button(336, 600, 250, 70, 'BACK', (150, 150, 0), (200, 200, 0))

buttons = [button_help, button_volume, button_restart, button_back]

def settings_update(events):
    """Handles events for the settings page."""
    mouse_pos = pygame.mouse.get_pos()
    
    for event in events:
        if button_help.check_click(event):
            print("Help button clicked! Opening help page.")
            return 'help'
        
        if button_volume.check_click(event):
            print("Volume button clicked! (Volume adjustment not implemented yet)")
            # TODO: Implement volume adjustment
            
        if button_restart.check_click(event):
            print("Restart button clicked! (Restart confirmation not implemented yet)")
            # TODO: Implement restart confirmation dialog
            
        if button_back.check_click(event):
            print("Back button clicked! Returning to title screen.")
            return 'title'
    
    # Update all buttons to check for hover
    for button in buttons:
        button.check_hover(mouse_pos)
    
    return None

def settings_draw(screen):
    """Draws the settings page."""
    # Draw background
    screen.fill(BACKGROUND_COLOR)
    
    # Draw title
    title_surface = TITLE_FONT.render("SETTINGS", True, HEADING_COLOR)
    title_rect = title_surface.get_rect(centerx=336, y=100)
    screen.blit(title_surface, title_rect)
    
    # Draw all buttons
    for button in buttons:
        button.draw(screen)
