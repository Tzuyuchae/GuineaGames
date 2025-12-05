import pygame
import os
import random

# Safe path handling
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class GuineaPigSprite:
    """
    Visual wrapper for API Pet Data.
    Combines the visual logic of the uploaded file with the data structure of the API.
    """
    def __init__(self, x, y, data_dict):
        """
        x, y: Position on screen
        data_dict: The dictionary returned from the API (e.g. {'name': 'Bob', 'color': 'Brown', ...})
        """
        self.data = data_dict
        
        # --- DETERMINE COAT LENGTH ---
        # 1. Try to get explicit length from data
        c_len = self.data.get('coat_length', None)
        
        # 2. If missing/null, infer from Species/Breed
        if not c_len or c_len == 'None':
            species = self.data.get('species', 'Guinea Pig')
            # List of breeds that are known to be Long Haired
            long_hair_breeds = ["Abyssinian", "Peruvian", "Silkie", "Sheba", "Coronet", "Alpaca", "Lunkarya"]
            
            if species in long_hair_breeds:
                c_len = "Long"
            else:
                c_len = "Short"

        # Determine Phenotype for sprite loading
        self.phenotype = {
            'coat_color': self.data.get('color_phenotype', self.data.get('color', 'White')),
            'coat_length': c_len
        }

        # Load the correct sprite
        self.image = self._load_sprite_by_phenotype()

        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

    def _load_sprite_by_phenotype(self):
        """Load sprite based on guinea pig's phenotype string from API"""
        try:
            coat_length = self.phenotype.get('coat_length', 'Short')
            # Clean up color string (e.g., "Brown" or "White")
            raw_color = self.phenotype.get('coat_color', 'White')
            
            # Simple mapping to handle complex API strings if necessary
            coat_color = 'White'
            if 'Brown' in raw_color: coat_color = 'Brown'
            elif 'Orange' in raw_color: coat_color = 'Orange'
            elif 'Black' in raw_color: coat_color = 'Brown' # Fallback for black if no specific sprite
            
            # Determine sprite prefix (SH = Short Hair, LH = Long Hair)
            prefix = 'SH' if 'Short' in coat_length else 'LH'

            # Pick a random variant (01-09) to make them look alive, 
            # or hash the ID so the same pig always has the same variant
            if 'id' in self.data:
                # distinct variant based on ID
                variant = (hash(str(self.data['id'])) % 9) + 1
            else:
                variant = random.randint(1, 9)
            
            variant_str = f"{variant:02d}"

            # Build path to sprite
            # Folder Structure: Global Assets/Sprites/Guinea Pigs/SH_GP_Sprites/SH_GP_Sprites/filename
            # We check a few variations to be safe against folder structure changes
            
            folder_name = f"{prefix}_GP_Sprites"
            filename = f"{prefix}_GP_{coat_color}_{variant_str}.png"
            
            # Construct possible paths
            paths_to_check = [
                os.path.join(SCRIPT_DIR, "Global Assets", "Sprites", "Guinea Pigs", folder_name, folder_name, filename),
                os.path.join(SCRIPT_DIR, "Global Assets", "Sprites", "Guinea Pigs", folder_name, filename),
                os.path.join(SCRIPT_DIR, "../Global Assets/Sprites/Guinea Pigs", folder_name, folder_name, filename)
            ]

            for p in paths_to_check:
                if os.path.exists(p):
                    img = pygame.image.load(p).convert_alpha()
                    return pygame.transform.scale(img, (80, 80)) # Scaled for UI
            
            # If specific variant missing, try 01
            fallback_name = f"{prefix}_GP_{coat_color}_01.png"
            fallback_path = os.path.join(SCRIPT_DIR, "Global Assets", "Sprites", "Guinea Pigs", folder_name, folder_name, fallback_name)
            
            if os.path.exists(fallback_path):
                img = pygame.image.load(fallback_path).convert_alpha()
                return pygame.transform.scale(img, (80, 80))

        except Exception as e:
            print(f"Error loading sprite: {e}")

        # Final fallback: colored square
        s = pygame.Surface((80, 80))
        # Default color brown-ish
        s.fill((150, 75, 0))
        return s

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def get_stats(self):
        """Extracts stats from the API Dict for the popup."""
        name = self.data.get('name', 'Unknown')
        speed = self.data.get('speed', 0)
        endurance = self.data.get('endurance', 0)
        hunger = self.data.get('hunger', 0)
        age_val = "Adult" if self.data.get('age_days', 0) >= 1 else "Baby"
        breed_val = self.data.get('species', 'Guinea Pig')

        return {
            "Name": name,
            "Breed": breed_val, # Add breed to stats
            "Speed": speed,
            "Endurance": endurance,
            "Hunger": f"{hunger}/3",
            "Age": age_val,
            "image_surface": self.image,
            "pet_id": self.data.get('id'), # Crucial for API calls
            "raw_data": self.data
        }