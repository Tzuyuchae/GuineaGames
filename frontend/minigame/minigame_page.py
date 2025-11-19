import pygame
from frontend.minigame.button import Button

# A 'Back' button, positioned for the 672x864 screen
button_back = Button(236, 500, 200, 70, 'BACK', (150, 150, 0), (200, 200, 0))

def minigame_update(events):
    """Handles events for the minigame page."""
    mouse_pos = pygame.mouse.get_pos()
    
    for event in events:
        if button_back.check_click(event):
            print("Back button clicked! Returning to homescreen.")
            return 'homescreen' # Return to the menu
            
    button_back.check_hover(mouse_pos)
    return None # Stay on this screen

def minigame_draw(screen):
    """Draws the minigame page."""
    # Draw the back button
    button_back.draw(screen)