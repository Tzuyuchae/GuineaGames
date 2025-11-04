import pygame
from button import Button

# A 'Back' button
button_start = Button(400, 500, 200, 70, 'Start', (150, 0, 0), (200, 0, 0))

def title_update(events):
    """Handles events for the breeding page."""
    mouse_pos = pygame.mouse.get_pos()
    
    for event in events:
        if button_start.check_click(event):
            print("Start button clicked! Returning to homescreen.")
            return 'homescreen' # Return to the menu
            
    button_start.check_hover(mouse_pos)
    return None

def title_draw(screen):
    """Draws the breeding page."""
    # Draw the back button
    button_start.draw(screen)
