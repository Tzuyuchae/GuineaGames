import pygame
from frontend_button import Button

# Optional: Import API client for database connectivity
try:
    from api_client import api
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    print("API client not available. Run in standalone mode.")

# A 'Back' button
button_start = Button(pygame.Rect(400, 500, 200, 70), 'Start')

def title_update(events):
    """Handles events for the breeding page."""
    mouse_pos = pygame.mouse.get_pos()
    
    for event in events:
         if button_start.is_clicked(event):
            print("Start button clicked! Returning to homescreen.")
            return 'homescreen'  # Return to the menu

   # button_start.check_hover(mouse_pos)
    return None

def title_draw(screen):
    """Draws the breeding page."""
    # Draw the back button
    button_start.draw(screen)

    # Optional: Display API connection status (commented out by default)
    # if API_AVAILABLE:
    #     font = pygame.font.Font(None, 24)
    #     if api.check_connection():
    #         status_text = font.render("API: Connected", True, (0, 128, 0))
    #     else:
    #         status_text = font.render("API: Offline", True, (255, 0, 0))
    #     screen.blit(status_text, (10, 10))
