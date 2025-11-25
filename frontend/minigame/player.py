import pygame 
import random
import os
from minigame.settings import TILE_SIZE, RED

class Player:
    def __init__(self, x=0, y=0, color=RED, seed=None, guinea_pig_data=None):
        """
        Initialize the player with stats, color, image, and momentum physics.
        Args:
            guinea_pig_data: Dict containing 'name', 'color', 'speed', etc.
        """
        self.pos_x = x
        self.pos_y = y
        self.seed = seed
        self.guinea_pig_data = guinea_pig_data
        
        # --- 1. Handle Stats & Color ---
        self.name = guinea_pig_data.get('name', 'Player') if guinea_pig_data else 'Player'
        
        # Extract Stats (0-100 scale assumed)
        raw_speed = guinea_pig_data.get('speed', 50) if guinea_pig_data else 50
        raw_endurance = guinea_pig_data.get('endurance', 50) if guinea_pig_data else 50

        # --- MOMENTUM PHYSICS SETTINGS ---
        # Base delay calculation: Higher speed stat = Lower delay (faster movement)
        self.BASE_DELAY = 300 - (raw_speed * 1)     # Starting speed
        self.MIN_DELAY = 120 - (raw_speed * 0.5)    # Max speed cap
        self.FATIGUE_DELAY = 450                    # Speed when tired
        
        # Endurance: How long (ms) you can run at top speed
        self.ENDURANCE_LIMIT = 1000 + (raw_endurance * 40) 

        # Physics State Variables
        self.current_delay = self.BASE_DELAY
        self.last_move_time = 0
        self.momentum_start_time = 0
        self.at_top_speed_since = 0
        self.is_moving = False
        self.is_fatigued = False

        # Set Color from Data
        if guinea_pig_data and 'color' in guinea_pig_data:
            self.color = self._get_color_from_name(guinea_pig_data['color'])
        else:
            self.color = color

        # --- 2. Load Image ---
        base_path = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_path, "../../frontend/images/player.png")

        try:
            raw_image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(raw_image, (TILE_SIZE, TILE_SIZE))
            # Note: If you want to tint the actual image based on color, do it here
        except (FileNotFoundError, pygame.error):
            # Fallback: Create a colored square if image fails
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(self.color)

        self.rect = self.image.get_rect()

    def _get_color_from_name(self, color_name):
        """Convert string color names to RGB tuples."""
        color_map = {
            'brown': (139, 69, 19), 'white': (255, 255, 255),
            'orange': (255, 165, 0), 'black': (50, 50, 50),
            'gray': (128, 128, 128), 'gold': (255, 215, 0), 'red': RED
        }
        return color_map.get(color_name.lower(), RED)

    def handle_input(self, maze):
        """
        Checks keyboard state and handles momentum-based movement.
        Call this every frame in game.update().
        """
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
        
        dx, dy = 0, 0
        wants_to_move = False

        # Check input (only allows 4-directional movement)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
            wants_to_move = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
            wants_to_move = True
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
            wants_to_move = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
            wants_to_move = True

        # --- MOMENTUM LOGIC ---
        if wants_to_move:
            if not self.is_moving:
                # Just started moving
                self.is_moving = True
                self.momentum_start_time = now
                self.current_delay = self.BASE_DELAY
                self.is_fatigued = False
                self.at_top_speed_since = 0

            # Calculate Acceleration
            time_moving = now - self.momentum_start_time
            
            if not self.is_fatigued:
                # Accelerate over time
                acceleration_bonus = int(time_moving / 200) * 15 
                target_delay = max(self.MIN_DELAY, self.BASE_DELAY - acceleration_bonus)
                self.current_delay = target_delay

                # Check Endurance Cap
                if self.current_delay <= self.MIN_DELAY:
                    if self.at_top_speed_since == 0:
                        self.at_top_speed_since = now
                    
                    # If we've been at top speed longer than endurance allows...
                    if (now - self.at_top_speed_since) > self.ENDURANCE_LIMIT:
                        self.is_fatigued = True
            else:
                # Fatigued State
                self.current_delay = self.FATIGUE_DELAY

            # Check if it's time to take a step
            if now - self.last_move_time >= self.current_delay:
                move_success = self.move(dx, dy, maze)
                self.last_move_time = now
                
                # If we hit a wall, kill momentum
                if not move_success:
                    self.reset_momentum()

        else:
            # Player let go of keys
            if self.is_moving:
                self.reset_momentum()

    def reset_momentum(self):
        """Resets speed to base values."""
        self.is_moving = False
        self.current_delay = self.BASE_DELAY
        self.at_top_speed_since = 0
        self.is_fatigued = False

    def move(self, dx, dy, maze):
        """Attempts to move. Returns True if moved, False if hit wall."""
        new_x = self.pos_x + dx
        new_y = self.pos_y + dy
        
        if not maze.is_wall(new_x, new_y):
            self.pos_x = new_x
            self.pos_y = new_y
            return True
        return False

    def add_player(self, grid):
        """Randomly add player ('P') to the maze and update coordinates."""
        if self.seed is not None:
            random.seed(self.seed)
        
        spawn_points = []
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                if tile == '0':
                    spawn_points.append((x, y))
        
        new_grid = [list(row) for row in grid]
        
        if spawn_points:
            player_x, player_y = random.choice(spawn_points)
            new_grid[player_y][player_x] = 'P'
            self.pos_x = player_x
            self.pos_y = player_y
        
        return [''.join(row) for row in new_grid]

    def player_pos(self):
        return (self.pos_x, self.pos_y)

    def draw(self, screen):
        pixel_x = self.pos_x * TILE_SIZE
        pixel_y = self.pos_y * TILE_SIZE
        self.rect.topleft = (pixel_x, pixel_y)
        
        # Visual indicator for Fatigue (Tint red)
        if self.is_fatigued:
            tinted_img = self.image.copy()
            tinted_img.fill((100, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(tinted_img, self.rect)
        else:
            screen.blit(self.image, self.rect)