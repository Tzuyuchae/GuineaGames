import pygame
import os

class GuineaPigSprite:
    """
    Visual wrapper for API pet data.
    Displays pigs walking on the homescreen with correct color sprites.
    """
    def __init__(self, x, y, data_dict):
        # Ensure we store the data dictionary
        self.data = data_dict
        
        self.rect = pygame.Rect(x, y - 60, 60, 60) # Default size
        
        # Load the correct image based on color
        self.image = self._load_smart_sprite()
        
        # Update rect to match image size
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

    def _load_smart_sprite(self):
        """Loads correct sprite file based on pet color"""
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Path to your sprite folder
        sprite_folder = os.path.join(base_path, "Global Assets", "Sprites", "Guinea Pigs", "SH_GP_Sprites", "SH_GP_Sprites")
        
        # Determine filename based on phenotype/color
        color = self.data.get('color_phenotype', self.data.get('color', 'White')).lower()
        filename = "SH_GP_White_01.png" # Default
        
        if "brown" in color:
            filename = "SH_GP_Brown_01.png"
        elif "orange" in color:
            filename = "SH_GP_Orange_01.png"
            
        full_path = os.path.join(sprite_folder, filename)
        
        try:
            if os.path.exists(full_path):
                img = pygame.image.load(full_path).convert_alpha()
                return pygame.transform.scale(img, (80, 80))
        except Exception as e:
            print(f"Sprite Load Error: {e}")
            
        # Fallback 1: Generic image
        try:
            generic_path = os.path.join(base_path, "images", "guineapig.png")
            if os.path.exists(generic_path):
                return pygame.transform.scale(pygame.image.load(generic_path).convert_alpha(), (80, 80))
        except:
            pass

        # Fallback 2: Brown Square
        s = pygame.Surface((80, 80))
        s.fill((150, 75, 0))
        return s

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def get_stats(self):
        """
        Extracts stats for the popup window.
        NOW SUPPORTS DICTIONARIES CORRECTLY.
        """
        # --- FIX: Use .get() for dictionary access instead of getattr() ---
        return {
            "Name": self.data.get('name', 'Unknown'),
            "Speed": self.data.get('speed', 0),
            "Endurance": self.data.get('endurance', 0),
            "Hunger": f"{self.data.get('hunger', 0)}/3",
            "Age": "Adult" if self.data.get('age_days', 0) > 0 else "Baby",
            "image_surface": self.image,
            "pet_id": self.data.get('id'),
            "raw_data": self.data  # Critical for renaming to work!
        }