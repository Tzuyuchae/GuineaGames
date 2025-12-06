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
        self.data = data_dict
        
        # --- DETERMINE COAT LENGTH ---
        # 1. Try to get explicit length from data
        c_len = self.data.get('coat_length', None)
        h_type = self.data.get('hair_type', None)
        
        final_len = "Short" # Default
        
        # Check explicit flags
        if c_len and str(c_len).lower() in ['long', 'fluffy', 'lh']: final_len = "Long"
        if h_type and str(h_type).lower() in ['long', 'fluffy', 'lh']: final_len = "Long"

        # 2. If still Short, check Breed/Species list
        if final_len == "Short":
            species = self.data.get('species', 'Guinea Pig')
            # List of breeds that are known to be Long Haired
            long_hair_breeds = [
                "Abyssinian", "Peruvian", "Silkie", "Sheba", 
                "Coronet", "Alpaca", "Lunkarya", "Texel"
            ]
            if species in long_hair_breeds:
                final_len = "Long"

        # Determine Phenotype for sprite loading
        self.phenotype = {
            'coat_color': self.data.get('color_phenotype', self.data.get('color', 'White')),
            'coat_length': final_len
        }

        # Load the correct sprite
        self.image = self._load_sprite_by_phenotype()

        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

    def _load_sprite_by_phenotype(self):
        """Load sprite based on guinea pig's phenotype string from API"""
        try:
            coat_length = self.phenotype.get('coat_length', 'Short')
            raw_color = self.phenotype.get('coat_color', 'White')
            
            # Simple mapping to handle complex API strings
            coat_color = 'White'
            if 'Brown' in raw_color: coat_color = 'Brown'
            elif 'Orange' in raw_color: coat_color = 'Orange'
            elif 'Black' in raw_color: coat_color = 'Brown' # Fallback
            elif 'Mixed' in raw_color: coat_color = 'Orange' # Fallback
            
            # Determine sprite prefix (SH = Short Hair, LH = Long Hair)
            prefix = 'SH' if 'Short' in coat_length else 'LH'

            # --- FIX: STABLE VARIANT SELECTION ---
            # Don't use hash(), it changes every restart. Use int(id).
            if 'id' in self.data:
                try:
                    # Convert ID to int (sum of chars if it's a string, or just int)
                    pid = self.data['id']
                    if isinstance(pid, int):
                        numeric_id = pid
                    else:
                        numeric_id = sum(ord(c) for c in str(pid))
                    
                    variant = (numeric_id % 9) + 1
                except:
                    variant = 1
            else:
                variant = random.randint(1, 9)
            
            variant_str = f"{variant:02d}"

            # Build path to sprite
            folder_name = f"{prefix}_GP_Sprites"
            filename = f"{prefix}_GP_{coat_color}_{variant_str}.png"
            
            # Construct possible paths
            # Note: SCRIPT_DIR is inside 'frontend', assets are usually in 'frontend/Global Assets'
            paths_to_check = [
                os.path.join(SCRIPT_DIR, "Global Assets", "Sprites", "Guinea Pigs", folder_name, folder_name, filename),
                os.path.join(SCRIPT_DIR, "Global Assets", "Sprites", "Guinea Pigs", folder_name, filename),
                os.path.join(SCRIPT_DIR, "../Global Assets/Sprites/Guinea Pigs", folder_name, folder_name, filename)
            ]

            for p in paths_to_check:
                if os.path.exists(p):
                    img = pygame.image.load(p).convert_alpha()
                    return pygame.transform.scale(img, (80, 80)) 
            
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
        health = self.data.get('health', 100)
        age_val = "Adult" if self.data.get('age_days', 0) >= 1 else "Baby"
        breed_val = self.data.get('species', 'Guinea Pig')

        # Check death status
        is_dead = False
        if health <= 0 or self.data.get('is_dead', False):
            is_dead = True

        return {
            "Name": name,
            "Breed": breed_val,
            "Speed": speed,
            "Endurance": endurance,
            "Hunger": f"{hunger}/3",
            "Health": f"{health}/100",
            "Age": age_val,
            "image_surface": self.image,
            "pet_id": self.data.get('id'),
            "raw_data": self.data,
            "is_dead": is_dead
        }
    
    def update(self):
        # Placeholder for simple animations (hopping)
        pass