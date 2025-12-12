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
        if guinea_pig_data and isinstance(guinea_pig_data, dict) and 'sprite' in guinea_pig_data:
            self.image = guinea_pig_data['sprite']
        else:
            self.image = self._load_sprite(guinea_pig_data)

        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)

        # --- STATS ---
        raw_speed = 50
        raw_endurance = 50
        
        if guinea_pig_data:
            if isinstance(guinea_pig_data, dict):
                raw_speed = guinea_pig_data.get('speed', 50)
                raw_endurance = guinea_pig_data.get('endurance', 50)
            else:
                raw_speed = getattr(guinea_pig_data, 'speed', 50)
                raw_endurance = getattr(guinea_pig_data, 'endurance', 50)

        # Movement Speed (Lower delay = Faster)
        self.BASE_DELAY = 150 - (raw_speed * 0.5)  # Start speed
        self.MIN_DELAY = 60 - (raw_speed * 0.3)    # Top speed
        self.FATIGUE_DELAY = 220                   # Punishment speed (Very Slow)

        # --- STAMINA SYSTEM (New) ---
        # Base stamina is 100. High endurance adds up to +200 bonus.
        self.max_stamina = 100 + (raw_endurance * 2) 
        self.current_stamina = self.max_stamina
        
        # Drain Rate: How fast you get tired
        self.drain_rate = 2.5 
        
        # Recovery Rate: How fast you recover when stopped
        # Higher endurance = slightly faster recovery
        self.recovery_rate = 1.5 + (raw_endurance * 0.02)

        # State Variables
        self.current_delay = self.BASE_DELAY
        self.last_move_time = 0
        self.momentum_start_time = 0
        self.is_moving = False
        self.is_fatigued = False

    def _determine_hair_type(self, pet_data):
        """Helper to determine Short (SH) or Long (LH) hair."""
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

        long_hair_breeds = ["Abyssinian", "Peruvian", "Silkie", "Sheba", "Coronet", "Alpaca", "Lunkarya", "Texel"]
        if species in long_hair_breeds: return 'Long'
        return 'Short'

    def _load_sprite(self, pet_data):
        """Loads specific sprite using robust path finding logic."""
        color = "white"
        pig_id = 0
        if pet_data:
            if isinstance(pet_data, dict):
                color = pet_data.get('color_phenotype', pet_data.get('color', 'White'))
                pig_id = pet_data.get('id', 0)
            else:
                pig_id = getattr(pet_data, 'id', 0)
                if hasattr(pet_data, 'color'): color = str(pet_data.color)

        color = str(color).lower()
        hair_type = self._determine_hair_type(pet_data)
        prefix = "LH" if hair_type == 'Long' else "SH"

        sprite_color = "White"
        if "brown" in color: sprite_color = "Brown"
        elif "orange" in color: sprite_color = "Orange"
        elif "black" in color: sprite_color = "Brown"
        elif "mixed" in color: sprite_color = "Orange"

        try:
            numeric_id = pig_id if isinstance(pig_id, int) else sum(ord(c) for c in str(pig_id))
            variant_num = (numeric_id % 9) + 1
        except: variant_num = 1
            
        filename = f"{prefix}_GP_{sprite_color}_{variant_num:02d}.png"
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        folder_name = f"{prefix}_GP_Sprites"
        
        possible_paths = [
            os.path.join(base_dir, "Global Assets", "Sprites", "Guinea Pigs", folder_name, folder_name, filename),
            os.path.join(base_dir, "Global Assets", "Sprites", "Guinea Pigs", folder_name, filename)
        ]

        for full_path in possible_paths:
            if os.path.exists(full_path):
                try: return pygame.image.load(full_path).convert_alpha()
                except: pass

        return pygame.Surface((TILE_SIZE, TILE_SIZE))

    def handle_input(self, maze):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
        
        dx, dy = 0, 0
        wants_to_move = False

        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -1; wants_to_move = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = 1; wants_to_move = True
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -1; wants_to_move = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1; wants_to_move = True
        
        if wants_to_move:
            # Start momentum
            if not self.is_moving:
                self.is_moving = True
                self.momentum_start_time = now

            # --- STAMINA LOGIC ---
            # Drain stamina
            self.current_stamina -= self.drain_rate
            if self.current_stamina <= 0:
                self.current_stamina = 0
                self.is_fatigued = True
            
            # --- SPEED LOGIC ---
            if not self.is_fatigued:
                # Accelerate
                time_moving = now - self.momentum_start_time
                acceleration_bonus = int(time_moving / 200) * 10
                self.current_delay = max(self.MIN_DELAY, self.BASE_DELAY - acceleration_bonus)
            else:
                # Punishment speed
                self.current_delay = self.FATIGUE_DELAY

            # Move based on delay
            if now - self.last_move_time >= self.current_delay:
                move_success = self.move(dx, dy, maze)
                self.last_move_time = now
                if not move_success:
                    self.reset_momentum()
        else:
            # Stopped
            if self.is_moving:
                self.reset_momentum()
            
            # Recover Stamina
            if self.current_stamina < self.max_stamina:
                self.current_stamina += self.recovery_rate
                if self.current_stamina > self.max_stamina:
                    self.current_stamina = self.max_stamina
            
            # Recover from Fatigue
            # You must recover 30% of your bar before you stop being tired
            if self.is_fatigued and self.current_stamina > (self.max_stamina * 0.3):
                self.is_fatigued = False

    def reset_momentum(self):
        self.is_moving = False
        self.current_delay = self.BASE_DELAY
        # Note: We do NOT reset stamina here anymore!

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
        pixel_x = self.pos_x * TILE_SIZE + off_x
        pixel_y = self.pos_y * TILE_SIZE + off_y
        
        self.rect.topleft = (pixel_x, pixel_y)
        
        # Draw Pig
        screen.blit(self.image, self.rect)

        # --- DRAW STAMINA BAR ---
        bar_width = TILE_SIZE
        bar_height = 4
        
        # Calculate percentage
        pct = self.current_stamina / self.max_stamina
        
        # Background (Black)
        bg_rect = pygame.Rect(pixel_x, pixel_y - 8, bar_width, bar_height)
        pygame.draw.rect(screen, (0,0,0), bg_rect)
        
        # Foreground
        # Green if good, Red if fatigued, Yellow if low
        if self.is_fatigued: color = (255, 0, 0)
        elif pct < 0.3: color = (255, 165, 0)
        else: color = (0, 255, 0)
        
        fg_rect = pygame.Rect(pixel_x, pixel_y - 8, int(bar_width * pct), bar_height)
        pygame.draw.rect(screen, color, fg_rect)