# This is the content of guineapig.py
import pygame

class Guineapig:
    def __init__(self, x, y):
        """This runs when you create a new Guineapig()"""
        try:
            # The class loads its own image
            self.image = pygame.image.load('images/guineapig.png')
        except pygame.error as message:
            print(f"Cannot load image: {message}")
            raise SystemExit(message) # Exit if the image can't be found
        
        # Get the rectangle and set its starting position
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self, surface):
        """A custom method to draw the object on the screen"""
        surface.blit(self.image, self.rect)
        
    # You could add an update() method here later for movement
    # def update(self):
    #     self.rect.x += 1