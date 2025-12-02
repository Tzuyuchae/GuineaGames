import pygame
from pixelButton import PixelButton

# --- UPDATED BUTTON PATHS ---
# We added 'frontend/' to the start of every image path here
button_start = PixelButton(336, 430, 'Play', 'frontend/images/titleButton.png', 'frontend/images/titleButtonHover.png', 'frontend/images/titleButtonPressed.png', (0,0,0))
button_settings = PixelButton(336, 520, 'Settings', 'frontend/images/titleButton.png', 'frontend/images/titleButtonHover.png', 'frontend/images/titleButtonPressed.png', (0,0,0))
button_quit = PixelButton(336, 610, 'Quit', 'frontend/images/titleButton.png', 'frontend/images/titleButtonHover.png', 'frontend/images/titleButtonPressed.png', (0,0,0))

def title_update(events):
    """Handles events for the title page."""
    mouse_pos = pygame.mouse.get_pos()

    for event in events:
        if button_start.check_mouseDown(event, mouse_pos):
            print("Start button clicked! Setting mousedown image.")

        if button_settings.check_mouseDown(event, mouse_pos):
            print("Settings button clicked! Setting mousedown image.")

        if button_quit.check_mouseDown(event, mouse_pos):
            print("Quit button clicked! Setting mousedown image.")

        if button_start.check_mouseUp(event):
            print("Start button clicked! Returning to homescreen.")
            return 'homescreen' 

        if button_settings.check_mouseUp(event):
            print("Settings button clicked")
            return 'settings' 

        if button_quit.check_mouseUp(event):
            print("Quit button clicked")
            return 'quit' 

    button_start.check_hover(mouse_pos)
    button_settings.check_hover(mouse_pos)
    button_quit.check_hover(mouse_pos)
    return None

def title_draw(screen):
    """Draws the title page."""
    
    # --- UPDATED BACKGROUND PATH ---
    background_img = pygame.image.load("frontend/images/BG_Title.png").convert()

    # Draw background image
    screen.blit(background_img, (0, 0))

    # --- UPDATED LOGO PATH ---
    logo_img = pygame.image.load("frontend/images/guineaGoneWildLogo.png").convert_alpha()
    
    logo_img = pygame.transform.scale(logo_img, (300, 300))
    logo_rect = logo_img.get_rect(center=(336, 200))   # X, Y position
    screen.blit(logo_img, logo_rect)

    # Draw the buttons
    button_start.draw(screen)
    button_settings.draw(screen)
    button_quit.draw(screen)