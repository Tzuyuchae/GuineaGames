import pygame 
import os
import random
from .settings import TILE_SIZE, RED

class Player:
    def __init__(self, x=0, y=0, color=RED, seed=None, guinea_pig_data=None):
        self.pos_x = x
        self.pos_y = y
        self.color = color
        self.seed = seed
        
        # --- SPRITE LOADING ---
        # 1. Check if the data already contains the loaded Surface (from Selector)
        # This guarantees visual consistency with the menu.
        if guinea_pig_data and isinstance(guinea_pig_data, dict) and 'sprite' in guinea_pig_data:
            self.image = guinea_pig_data['sprite']
        else:
            # 2. Fallback: Load it ourselves if missing
            self.image = self._load_sprite(guinea_pig_data)

        # Scale to fit tile size perfectly
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)

        # --- PHYSICS & MOMENTUM ---
        # Get stats from pet data
        raw_speed = 50
        raw_endurance = 50
        
        if guinea_pig_data:
            if isinstance(guinea_pig_data, dict):
                raw_speed = guinea_pig_data.get('speed', 50)
                raw_endurance = guinea_pig_data.get('endurance', 50)
            else:
                # Legacy Object support
                raw_speed = getattr(guinea_pig_data, 'speed', 50)
                raw_endurance = getattr(guinea_pig_data, 'endurance', 50)

        # Movement Constants (Lower delay = Faster)
        self.BASE_DELAY = 150 - (raw_speed * 0.5)  # Start speed
        self.MIN_DELAY = 60 - (raw_speed * 0.3)    # Top speed
        self.FATIGUE_DELAY = 250                   # Slow speed when tired
        self.ENDURANCE_LIMIT = 2000 + (raw_endurance * 50) # How long (ms) before tired

        # State Variables
        self.current_delay = self.BASE_DELAY
        self.last_move_time = 0
        self.momentum_start_time = 0
        self.at_top_speed_since = 0
        self.is_moving = False
        self.is_fatigued = False

    def _determine_hair_type(self, pet_data):
        """Helper to determine Short (SH) or Long (LH) hair."""
        # 1. Check explicit fields
        if isinstance(pet_data, dict):
            raw = pet_data.get('hair_type', pet_data.get('coat_length', None))
            species = pet_data.get('species', '')
        else:
            raw = getattr(pet_data, 'hair_type', None)
            species = getattr(pet_data, 'species', '')

        if raw:
            rt = str(raw).lower()
            if rt in ['long', 'fluffy', 'lh']: return 'Long'
            if rt in ['short', 'smooth', 'sh']: return 'Short'

        # 2. Infer from Species
        long_hair_breeds = [
            "Abyssinian", "Peruvian", "Silkie", "Sheba", 
            "Coronet", "Alpaca", "Lunkarya", "Texel"
        ]
        if species in long_hair_breeds:
            return 'Long'
        
        return 'Short'

    def _load_sprite(self, pet_data):
        """Loads specific sprite using robust path finding logic."""
        
        # 1. Determine Color, ID, and Hair Type
        color = "white"
        pig_id = 0
        
        if pet_data:
            if isinstance(pet_data, dict):
                color = pet_data.get('color_phenotype', pet_data.get('color', 'White'))
                pig_id = pet_data.get('id', 0)
            else:
                # Legacy Object
                if hasattr(pet_data, 'phenotype') and isinstance(pet_data.phenotype, dict):
                    color = pet_data.phenotype.get('coat_color', 'white')
                elif hasattr(pet_data, 'color'):
                    color = str(pet_data.color)
                pig_id = getattr(pet_data, 'id', 0)

        color = str(color).lower()
        hair_type = self._determine_hair_type(pet_data)
        
        # Determine Prefix
        prefix = "LH" if hair_type == 'Long' else "SH"

        # 2. Map color to filename keywords
        sprite_color = "White" # Default
        if "brown" in color: sprite_color = "Brown"
        elif "orange" in color: sprite_color = "Orange"
        elif "black" in color: sprite_color = "Brown" # Fallback
        elif "mixed" in color: sprite_color = "Orange" # Fallback

        # 3. Pick a variant (01-09) consistently based on ID
        # Uses the exact same math as Selector/Homescreen
        try:
            if isinstance(pig_id, int):
                numeric_id = pig_id
            else:
                numeric_id = sum(ord(c) for c in str(pig_id))
            
            variant_num = (numeric_id % 9) + 1
        except:
            variant_num = 1
            
        variant_str = f"{variant_num:02d}"
        
        # 4. Build Filename
        filename = f"{prefix}_GP_{sprite_color}_{variant_str}.png"

        # 5. Build Path
        # Base = frontend/minigame -> go up to frontend -> Global Assets
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        folder_name = f"{prefix}_GP_Sprites"
        
        possible_paths = [
            os.path.join(base_dir, "Global Assets", "Sprites", "Guinea Pigs", folder_name, folder_name, filename),
            os.path.join(base_dir, "Global Assets", "Sprites", "Guinea Pigs", folder_name, filename)
        ]

        # 6. Load
        for full_path in possible_paths:
            if os.path.exists(full_path):
                try:
                    img = pygame.image.load(full_path).convert_alpha()
                    return img # Return original size, scaled in __init__
                except: pass

        # Fallback to variant 01
        fallback_name = f"{prefix}_GP_{sprite_color}_01.png"
        fallback_path = os.path.join(base_dir, "Global Assets", "Sprites", "Guinea Pigs", folder_name, folder_name, fallback_name)
        if os.path.exists(fallback_path):
            try:
                img = pygame.image.load(fallback_path).convert_alpha()
                return img
            except: pass

        # Final Fallback
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        s.fill(self.color)
        return s

    def handle_input(self, maze):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
        
        dx, dy = 0, 0
        wants_to_move = False

        if keys[pygame.K_UP] or keys[pygame.K_w]: 
            dy = -1; wants_to_move = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]: 
            dy = 1; wants_to_move = True
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]: 
            dx = -1; wants_to_move = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: 
            dx = 1; wants_to_move = True
        
        if wants_to_move:
            # Start momentum if just starting
            if not self.is_moving:
                self.is_moving = True
                self.momentum_start_time = now
                self.current_delay = self.BASE_DELAY
                self.is_fatigued = False
                self.at_top_speed_since = 0

            # Calculate Acceleration
            time_moving = now - self.momentum_start_time
            
            if not self.is_fatigued:
                # Speed up over time
                acceleration_bonus = int(time_moving / 200) * 10
                target_delay = max(self.MIN_DELAY, self.BASE_DELAY - acceleration_bonus)
                self.current_delay = target_delay

                # Check Endurance
                if self.current_delay <= self.MIN_DELAY:
                    if self.at_top_speed_since == 0:
                        self.at_top_speed_since = now
                    
                    # If running at top speed too long -> Fatigue
                    if (now - self.at_top_speed_since) > self.ENDURANCE_LIMIT:
                        self.is_fatigued = True
                        print("Guinea Pig is tired!")
            else:
                # Slow down if tired
                self.current_delay = self.FATIGUE_DELAY

            # Move logic based on timer
            if now - self.last_move_time >= self.current_delay:
                move_success = self.move(dx, dy, maze)
                self.last_move_time = now
                
                # If hit a wall, lose momentum
                if not move_success:
                    self.reset_momentum()
        else:
            # Stop keys released
            if self.is_moving:
                self.reset_momentum()

    def reset_momentum(self):
        self.is_moving = False
        self.current_delay = self.BASE_DELAY
        self.at_top_speed_since = 0
        self.is_fatigued = False

    def move(self, dx, dy, maze):
        new_x = self.pos_x + dx
        new_y = self.pos_y + dy
        if not maze.is_wall(new_x, new_y):
            self.pos_x = new_x
            self.pos_y = new_y
            return True
        return False

    def add_player(self, grid):
        if self.seed is not None: random.seed(self.seed)
        spawn_points = [(x, y) for y, row in enumerate(grid) for x, tile in enumerate(row) if tile == '0']
        new_grid = [list(row) for row in grid]
        if spawn_points:
            self.pos_x, self.pos_y = random.choice(spawn_points)
            new_grid[self.pos_y][self.pos_x] = 'P'
        return [''.join(row) for row in new_grid]

    def player_pos(self):
        return (self.pos_x, self.pos_y)

    def draw(self, screen, off_x=0, off_y=0):
        # Calculate pixel position with offset
        pixel_x = self.pos_x * TILE_SIZE + off_x
        pixel_y = self.pos_y * TILE_SIZE + off_y
        
        self.rect.topleft = (pixel_x, pixel_y)
        
        if self.is_fatigued:
            # Draw red tint if tired
            tint = self.image.copy()
            tint.fill((100, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(tint, self.rect)
        else:
            screen.blit(self.image, self.rect)