import pygame

# Initialize font module.
pygame.font.init() 
# You can also use pygame.font.SysFont() if you
# don't want to call init(), but this is safer.
try:
    # Try to load a nicer, common font
    BUTTON_FONT = pygame.font.SysFont('Arial', 30, bold=True)
except:
    # Fallback to the default pygame font
    BUTTON_FONT = pygame.font.Font(None, 40)


class Button:
    """A clickable button class."""
    
    def __init__(self, x, y, width, height, text, 
                 color=(0, 150, 0), 
                 hover_color=(0, 200, 0), 
                 text_color=(255, 255, 255)):
        
        # This creates the rect at the (x, y) top-left coordinate
        self.rect = pygame.Rect(x, y, width, height)
        
        # I removed the line 'self.rect.center = (x, y)'
        # as that was likely a bug moving your button unexpectedly.
        
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        
        # Create the text surface
        self.text_surf = BUTTON_FONT.render(text, True, self.text_color)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        
        self.is_hovered = False

    def draw(self, screen):
        """Draws the button on the screen."""
        current_color = self.hover_color if self.is_hovered else self.color
        
        # Draw the button rectangle
        pygame.draw.rect(screen, current_color, self.rect, border_radius=12)
        
        # Draw the text
        screen.blit(self.text_surf, self.text_rect)

    def check_hover(self, mouse_pos):
        """Checks if the mouse is hovering over the button."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self, event):
        """
        Checks if the button was clicked.
        Returns True if clicked, False otherwise.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False