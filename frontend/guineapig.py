import pygame
import os

# Safe path handling
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Default image path
IMAGE_PATH = os.path.join(SCRIPT_DIR, 'images', 'guineapig.png')

class GuineaPigSprite:
    """
    Visual wrapper for the logical GuineaPig data.
    Used to display pigs walking around on the homescreen.
    """
    def __init__(self, x, y, data_object):
        """
        x, y: Position on screen
        data_object: The logical GuineaPig instance from breeding.py/store_module.py
        """
        self.data = data_object
        
        # Try to load image
        try:
            self.image = pygame.image.load(IMAGE_PATH).convert_alpha()
            # Scale it down slightly for the yard
            self.image = pygame.transform.scale(self.image, (64, 64))
        except Exception as e:
            print(f"Error loading sprite: {e}")
            self.image = pygame.Surface((64, 64))
            self.image.fill((150, 75, 0)) # Brown square fallback

        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y) # Position feet on the ground

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def get_stats(self):
        """Extracts stats from the logical data object for the popup."""
        # Check if it's a breeding.py object or simple dict
        name = getattr(self.data, 'name', 'Unknown')
        speed = getattr(self.data, 'speed', 0)
        endurance = getattr(self.data, 'endurance', 0)
        
        # Handle hunger (logic might be in backend, usually 0-3)
        # Defaulting to 3 (Full) if not found
        hunger = getattr(self.data, 'hunger', 3) 
        
        # Calculate Age
        age_val = "Baby"
        if hasattr(self.data, 'get_age_stage'):
            age_val = self.data.get_age_stage()

        return {
            "Name": name,
            "Speed": speed,
            "Endurance": endurance,
            "Hunger": f"{hunger}/3",
            "Age": age_val,
            "image_surface": self.image # Pass image to popup
        }