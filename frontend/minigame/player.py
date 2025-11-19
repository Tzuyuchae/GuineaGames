### File: minigame/player.py ###

import pygame 
import random
import os  # <-- 1. Import os for file paths
from minigame.settings import TILE_SIZE, RED

# --- 2. ADD THIS PATH ---
# Define the path to your 'frontend/images/' folder
base_path = os.path.dirname(__file__)
image_path = os.path.join(base_path, "../images/") 

class Player:
    def __init__(self, x=0, y=0, color=RED, seed=None):
        self.pos_x = x
        self.pos_y = y
        self.color = color
        self.seed = seed
    def __init__(self, x=0, y=0, color=RED, seed=None, guinea_pig_data=None):
        """
        Initialize the player.
        
        Args:
            x: Starting x position
            y: Starting y position
            color: Player color (will be overridden if guinea_pig_data provided)
            seed: Random seed for spawn position
            guinea_pig_data: Dictionary containing guinea pig info (name, color, speed, etc.)
        """
        self.pos_x = x
        self.pos_y = y
        self.seed = seed
        self.guinea_pig_data = guinea_pig_data
        
        # Set color based on guinea pig data if provided
        if guinea_pig_data and 'color' in guinea_pig_data:
            self.color = self._get_color_from_name(guinea_pig_data['color'])
        else:
            self.color = color
        
        # Store guinea pig stats
        self.name = guinea_pig_data.get('name', 'Player') if guinea_pig_data else 'Player'
        self.speed_stat = guinea_pig_data.get('speed', 50) if guinea_pig_data else 50
    
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

        # --- 3. ADD THIS BLOCK to load the image ---
        try:
            # Load your player image from 'frontend/images/player.png'
            self.image = pygame.image.load(os.path.join(image_path, "player.png")).convert_alpha()
            # Scale it to fit the tile
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        except FileNotFoundError:
            # Fallback if image is missing
            print("Warning: 'player.png' not found. Using fallback color.")
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(self.color)
        # --- END OF ADDED BLOCK ---

    def move(self, dx, dy, maze):
        """Move the player by (dx, dy) if the target position is not a wall."""
        new_x = self.pos_x + dx
        new_y = self.pos_y + dy
        # Only move when the destination is not a wall
        if not maze.is_wall(new_x, new_y):
            self.pos_x = new_x
            self.pos_y = new_y

    def add_player(self, grid):
        """Randomly add player ('P') to the maze."""
        if self.seed is not None:
            random.seed(self.seed)
        
        # Find all spawn points
        spawn_points = []
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                if tile == '0':
                    spawn_points.append((x, y))
        
        # If there are spawn points, randomly select one for the player
        new_grid = [list(row) for row in grid]  # Convert strings to lists for easier modification
        if spawn_points:
            player_x, player_y = random.choice(spawn_points)
            new_grid[player_y][player_x] = 'P'
            # Update this Player instance so its coordinates match the placed 'P'
            self.pos_x = player_x
            self.pos_y = player_y
        
        # Convert back to strings
        return [''.join(row) for row in new_grid]

    def player_pos(self):
        return (self.pos_x, self.pos_y)

    def draw(self, screen):
        """Draw the player's image on the given screen."""
        
        # --- 4. REPLACE THE OLD DRAW CODE WITH THIS ---
        
        # Calculate the screen position
        rect = pygame.Rect(self.pos_x * TILE_SIZE, self.pos_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        
        # Draw the loaded image onto the screen
        screen.blit(self.image, rect)