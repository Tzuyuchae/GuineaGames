import pygame
from frontend.minigame.button import Button

# A 'Back' button
button_back = Button(400, 500, 200, 70, 'BACK', (150, 0, 0), (200, 0, 0))

def breeding_update(events):
    """Handles events for the breeding page."""
    mouse_pos = pygame.mouse.get_pos()
    
    for event in events:
        if button_back.check_click(event):
            print("Back button clicked! Returning to homescreen.")
            return 'homescreen' # Return to the menu
            
    button_back.check_hover(mouse_pos)
    return None

def breeding_draw(screen):
    """Draws the breeding page."""
    # Draw the back button
    button_back.draw(screen)
