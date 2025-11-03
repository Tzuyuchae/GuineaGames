import pygame
from button import Button # <-- Import the new Button class

# Create the buttons
# (x, y, width, height, text)
button_play = Button(400, 180, 250, 70, 'PLAY', (0, 150, 0), (0, 200, 0))
button_details = Button(400, 280, 250, 70, 'DETAILS', (0, 0, 150), (0, 0, 200))
button_breeding = Button(400, 380, 250, 70, 'BREEDING', (150, 0, 0), (200, 0, 0))
button_minigame = Button(400, 480, 250, 70, 'MINIGAME', (150, 150, 0), (200, 200, 0))

# Put all buttons in a list to make them easy to manage
buttons = [button_details, button_breeding, button_minigame]

def menu_update(events):
    """Handles events for the main menu."""
    mouse_pos = pygame.mouse.get_pos()
    
    for event in events:
        # Check all buttons for clicks
        if button_details.check_click(event):
            return 'details'
        if button_breeding.check_click(event):
            return 'breeding'
        if button_minigame.check_click(event):
            return 'minigame'

    # Update all buttons to check for hover
    for button in buttons:
        button.check_hover(mouse_pos)
            
    return None  # No state change

def menu_draw(screen):
    """Draws the main menu."""
    # Draw all the buttons
    for button in buttons:
        button.draw(screen)
