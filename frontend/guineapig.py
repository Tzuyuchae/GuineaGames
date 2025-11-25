# This is the content of guineapig.py
import pygame
import os # <-- 1. Import the 'os' module

# 2. Get the full path to the directory this file (guineapig.py) is in
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 3. Join that directory path with the relative image path
IMAGE_PATH = os.path.join(SCRIPT_DIR, 'images', 'guineapig.png')

class Guineapig:
    def __init__(self, x, y):
        """This runs when you create a new Guineapig()"""
        try:
            # 4. Load the image using the new, full path
            self.image = pygame.image.load(IMAGE_PATH) 
        except pygame.error as message:
            # 5. (Optional) Make the error message more helpful
            print(f"Cannot load image at: {IMAGE_PATH}") 
            print(f"Pygame error: {message}")
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