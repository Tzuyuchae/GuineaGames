import pygame

# Initialize font module.
pygame.font.init()
# You can also use pygame.font.SysFont() if you
# don't want to call init(), but this is safer.
try:
    # Try to load a nicer, common font
    BUTTON_FONT = pygame.font.Font('../PixelatedEleganceRegular-ovyAA.ttf', 35)
except:
    # Fallback to the default pygame font
    BUTTON_FONT = pygame.font.Font(None, 40)


class PixelButton:
    """A clickable button class."""

    def __init__(self, x, y, text, img, img_hover, img_pressed,
                 text_color=(255, 255, 255)):

        self.x = x
        self.y = y

        self.text = text
        self.text_color = text_color

        self.rect = pygame.Rect(x, y, 240, 70)

        self.is_pressed = False
        self.is_hovered = False

    def load_img(self):
        start_img = pygame.image.load("images/titleButton.png").convert_alpha()
        start_img = pygame.transform.scale(start_img, (240, 70))  # optional resize

        start_img_hover = pygame.image.load("images/titleButtonHover.png").convert_alpha()
        start_img_hover = pygame.transform.scale(start_img_hover, (240, 70))  # optional resize

        start_img_pressed = pygame.image.load("images/titleButtonPressed.png").convert_alpha()
        start_img_pressed = pygame.transform.scale(start_img_pressed, (240, 70))  # optional resize##############

        self.img = start_img
        self.img_hover = start_img_hover
        self.img_pressed = start_img_pressed
        self.rect = self.img.get_rect(center=(self.x, self.y))

        # Create the text surface
        self.text_surf = BUTTON_FONT.render(self.text, True, self.text_color)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        self.text_rect.y -= 0 if self.is_pressed else 5

    def draw(self, screen):
        """Draws the button on the screen."""
        self.load_img()

        #current_color = self.hover_color if self.is_hovered else self.color
        current_img = self.img_hover if self.is_hovered else self.img
        current_img = self.img_pressed if self.is_pressed else current_img

        # Draw the button rectangle and text
        screen.blit(current_img, self.rect)
        screen.blit(self.text_surf, self.text_rect)

    def check_hover(self, mouse_pos):
        """Checks if the mouse is hovering over the button."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def check_mouseDown(self, event, mouse_pos):
        """Checks if the mouse is hovering over the button."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                self.is_pressed = True
                return True
        return False

    def check_mouseUp(self, event):
        """
        Checks if the button was clicked.
        Returns True if clicked, False otherwise.
        """
        if event.type == pygame.MOUSEBUTTONUP:
            self.is_pressed = False
            if self.is_hovered:
                return True
        return False
