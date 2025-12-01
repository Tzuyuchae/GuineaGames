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
        """Extracts stats from the logical data object (object OR dict) for the popup."""
        # Support both backend dicts and local objects
        if isinstance(self.data, dict):
            name = self.data.get("name", "Unknown")
            # If you add genetics later, you can wire speed/endurance from there.
            speed = self.data.get("speed", 0)
            endurance = self.data.get("endurance", 0)
            hunger = self.data.get("hunger", 3)
            age_val = "Baby"
            # Example: if backend ever returns age_days, you can map to stages here
            if "age_days" in self.data:
                # simple placeholder mapping
                days = self.data["age_days"]
                if days > 60:
                    age_val = "Adult"
                elif days > 30:
                    age_val = "Teen"
        else:
            # Original object-style access
            name = getattr(self.data, 'name', 'Unknown')
            speed = getattr(self.data, 'speed', 0)
            endurance = getattr(self.data, 'endurance', 0)
            hunger = getattr(self.data, 'hunger', 3)

            age_val = "Baby"
            if hasattr(self.data, 'get_age_stage'):
                age_val = self.data.get_age_stage()

        return {
            "Name": name,
            "Speed": speed,
            "Endurance": endurance,
            "Hunger": f"{hunger}/3",
            "Age": age_val,
            "image_surface": self.image  # Pass image to popup
        }


        return {
            "Name": name,
            "Speed": speed,
            "Endurance": endurance,
            "Hunger": f"{hunger}/3",
            "Age": age_val,
            "image_surface": self.image # Pass image to popup
        }