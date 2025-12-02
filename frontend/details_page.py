import pygame
from minigame.button import Button

# A 'Back' button
button_back = Button(400, 500, 200, 70, 'BACK', (150, 150, 0), (200, 200, 0))

def details_update(events):
    """Handles events for the details page."""
    mouse_pos = pygame.mouse.get_pos()
    
    for event in events:
        if button_back.check_click(event):
            print("Back button clicked! Returning to homescreen.")
            return 'homescreen' # Return to the menu
            
    button_back.check_hover(mouse_pos)
    return None

def details_draw(screen):
    """Draws the details page."""
    # You can draw other details here first
    
    # Draw the back button
    button_back.draw(screen)
