### FIX ME ###
    # We need to implement an enemy that chases the player around the maze
    # and causes the player to lose if they come into contact with it.
import pygame 
import random
import os
from settings import TILE_SIZE, GOLD
from maze_generator import MazeGenerator

# Define path to enemy assets (if needed in future)
base_path = os.path.dirname(__file__)
assets_path = os.path.join(base_path, "../assets/images/")

class Enemy:
    def __init__(self, pos_x=0, pos_y=0, color=GOLD, seed=None):
        self.position = [pos_x, pos_y]
        self.color = color
        self.seed = seed
    
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
        """Draw the enemy on the given screen."""
        rect = pygame.Rect(self.position[0] * TILE_SIZE, self.position[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, self.color, rect)
    