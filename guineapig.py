# This is the content of guineapig.py
import pygame
import os 

# Gets the directory where this file (guineapig.py) is located
# e.g., C:\Users\ashty\GuineaGames\frontend
base_path = os.path.dirname(__file__) 

# Joins that path with the 'images' folder and the 'guineapig.png' file
# e.g., C:\Users\ashty\GuineaGames\frontend\images\guineapig.png
image_path = os.path.join(base_path,'frontend', 'images', 'guineapig.png')


class Guineapig:

    food_level = 3
    def __init__(self, x, y):
        """This runs when you create a new Guineapig()"""
        try:
            # Load the image using the new, correct path
            self.image = pygame.image.load(image_path) 
            
        except pygame.error as message:
            print(f"Cannot load image at path: {image_path}") # Print the path we tried
            raise SystemExit(message) # Exit if the image can't be found
        
        # Get the rectangle and set its starting position
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self, surface):
        """A custom method to draw the object on the screen"""
        surface.blit(self.image, self.rect)