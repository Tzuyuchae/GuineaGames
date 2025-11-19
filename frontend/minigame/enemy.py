### File: minigame/enemy.py ###

import pygame 
import random
import os
from minigame.settings import TILE_SIZE, GOLD
from minigame.maze_generator import MazeGenerator # This import seems unused, but fine

# --- 1. UPDATE THIS PATH ---
# This path should point to 'frontend/images/'
base_path = os.path.dirname(__file__)
image_path = os.path.join(base_path, "../images/") # Corrected path

class Enemy:
    def __init__(self, pos_x=0, pos_y=0, color=GOLD, seed=None):
        self.position = [pos_x, pos_y]
        self.color = color 
        self.seed = seed
        
        # --- 2. ADD THIS BLOCK to load the image ---
        try:
            # Load your enemy image from 'frontend/images/enemy.png'
            self.image = pygame.image.load(os.path.join(image_path, "enemy.png")).convert_alpha()
            # Scale it to fit the tile
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        except FileNotFoundError:
            # Fallback if image is missing
            print("Warning: 'enemy.png' not found. Using fallback color.")
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(self.color)
        # --- END OF ADDED BLOCK ---
    
    def move_towards_player(self, player_pos, maze):
        """Move the enemy one step towards the player if possible."""
        # Simple logic to move towards the player
        if self.position[0] < player_pos[0] and maze.is_wall(self.position[0] + 1, self.position[1]) == False:
            self.position[0] += 1
        elif self.position[0] > player_pos[0] and maze.is_wall(self.position[0] - 1, self.position[1]) == False:
            self.position[0] -= 1
        elif self.position[1] < player_pos[1] and maze.is_wall(self.position[0], self.position[1] + 1) == False:
            self.position[1] += 1
        elif self.position[1] > player_pos[1] and maze.is_wall(self.position[0], self.position[1] - 1) == False:
            self.position[1] -= 1
    
    def add_enemies(self, grid):
        """Randomly add enemies ('E') to the maze."""
        if self.seed is not None:
            random.seed(self.seed)
        
        # Find all spawn points
        spawn_points = []
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                if tile == 'S':
                    spawn_points.append((x, y))
        
        # If there are spawn points, randomly select one for the enemy
        new_grid = [list(row) for row in grid]  # Convert strings to lists for easier modification
        if spawn_points:
            enemy_x, enemy_y = random.choice(spawn_points)
            new_grid[enemy_y][enemy_x] = 'E'
            self.position = [enemy_x, enemy_y]
        
        # Convert back to strings
        return [''.join(row) for row in new_grid]
    
    def enemy_pos(self):
        return (self.position[0], self.position[1])

    def draw(self, screen):
        """Draw the enemy's image on the given screen."""
        
        # --- 3. REPLACE THE OLD DRAW CODE WITH THIS ---
        
        # Calculate the screen position
        rect = pygame.Rect(self.position[0] * TILE_SIZE, self.position[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        
        # Draw the loaded image onto the screen
        screen.blit(self.image, rect)