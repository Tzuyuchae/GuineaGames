import pygame 
import random
import os
from minigame.settings import TILE_SIZE, RED

class Player:
    def __init__(self, x=0, y=0, color=RED, seed=None, guinea_pig_data=None):
        """
        Initialize the player with stats, color, and image.
        """
        self.pos_x = x
        self.pos_y = y
        self.seed = seed
        self.guinea_pig_data = guinea_pig_data
        
        # --- 1. Handle Stats & Color ---
        self.name = guinea_pig_data.get('name', 'Player') if guinea_pig_data else 'Player'
        self.speed_stat = guinea_pig_data.get('speed', 50) if guinea_pig_data else 50

        if guinea_pig_data and 'color' in guinea_pig_data:
            self.color = self._get_color_from_name(guinea_pig_data['color'])
        else:
            self.color = color

        # --- 2. Load Image ---
        base_path = os.path.dirname(os.path.abspath(__file__))
        # Look for image in frontend/images/ relative to this file
        image_path = os.path.join(base_path, "../../frontend/images/player.png")
        
        # If your images are actually in 'assets/images', use this line instead:
        # image_path = os.path.join(base_path, "../../assets/images/player.png")

        try:
            raw_image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(raw_image, (TILE_SIZE, TILE_SIZE))
        except (FileNotFoundError, pygame.error):
            print(f"Warning: Could not load player image at {image_path}. Using color block.")
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(self.color)

        self.rect = self.image.get_rect()

    def _get_color_from_name(self, color_name):
        """Convert color name to RGB tuple."""
        color_map = {
            'brown': (139, 69, 19),
            'white': (255, 255, 255),
            'orange': (255, 165, 0),
            'black': (50, 50, 50),
            'gray': (128, 128, 128),
            'gold': (255, 215, 0),
            'red': RED
        }
        return color_map.get(color_name.lower(), RED)

    def move(self, dx, dy, maze):
        """Move the player by (dx, dy) if the target position is not a wall."""
        new_x = self.pos_x + dx
        new_y = self.pos_y + dy
        
        if not maze.is_wall(new_x, new_y):
            self.pos_x = new_x
            self.pos_y = new_y

    # --- THIS WAS MISSING ---
    def add_player(self, grid):
        """Randomly add player ('P') to the maze and update coordinates."""
        if self.seed is not None:
            random.seed(self.seed)
        
        # Find all valid spawn points (empty '0' tiles)
        spawn_points = []
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                if tile == '0':
                    spawn_points.append((x, y))
        
        # Create a copy of the grid to modify
        new_grid = [list(row) for row in grid]
        
        if spawn_points:
            # Pick a random spot
            player_x, player_y = random.choice(spawn_points)
            
            # Mark it on the grid map
            new_grid[player_y][player_x] = 'P'
            
            # Update the player object's internal coordinates
            self.pos_x = player_x
            self.pos_y = player_y
        
        # Return the grid back as a list of strings
        return [''.join(row) for row in new_grid]

    def player_pos(self):
        return (self.pos_x, self.pos_y)

    def draw(self, screen):
        """Draw the player's image on the given screen."""
        pixel_x = self.pos_x * TILE_SIZE
        pixel_y = self.pos_y * TILE_SIZE
        
        self.rect.topleft = (pixel_x, pixel_y)
        screen.blit(self.image, self.rect)