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
        
        # Load Sprite
        self.image = self._load_sprite(guinea_pig_data)
        self.rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)

        # --- PHYSICS & MOMENTUM ---
        # Get stats from pet data
        raw_speed = 50
        raw_endurance = 50
        if guinea_pig_data:
            raw_speed = guinea_pig_data.get('speed', 50)
            raw_endurance = guinea_pig_data.get('endurance', 50)

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

    def _load_sprite(self, pet_data):
        # Try Loading specific pet color
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filename = "SH_GP_White_01.png"
        
        if pet_data:
            color = pet_data.get('color_phenotype', pet_data.get('color', 'White')).lower()
            if "brown" in color: filename = "SH_GP_Brown_01.png"
            elif "orange" in color: filename = "SH_GP_Orange_01.png"
            
        path = os.path.join(base, "Global Assets", "Sprites", "Guinea Pigs", "SH_GP_Sprites", "SH_GP_Sprites", filename)
        
        try:
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        except: pass

        # Fallback
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

            