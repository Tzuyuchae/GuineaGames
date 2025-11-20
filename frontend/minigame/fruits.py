### File: minigame/fruits.py ###

import pygame
import random 
import os
from minigame.settings import GREEN, TILE_SIZE

# Defining path to fruit assets (if needed in future)
base_path = os.path.dirname(__file__)
image_path = os.path.join(base_path, "../images/")

class Fruit:
    def __init__(self, fruit_chance=0.1, color=GREEN, seed=None):
        self.fruit_chance = fruit_chance
        self.color = color
        self.seed = seed
        
        # --- NO IMAGE LOADING NEEDED HERE ---
        # (See the note below)
    
    def add_fruits(self, grid):
        """Randomly add fruits ('2') to the maze."""
        if self.seed is not None:
            random.seed(self.seed)

        new_grid = []
        for row in grid:
            new_row = ''
            for tile in row:
                # Check if tile is path '0' and not player 'P'
                if tile == '0' and random.random() < self.fruit_chance and tile != 'P':
                    new_row += '2'  # fruit
                else:
                    new_row += tile
            new_grid.append(new_row)
        return new_grid
    
    def if_collected(self, player_pos, grid):
        """Check if the player has collected a fruit."""
        x, y = player_pos
        if grid[y][x] == '2':
            # Remove the fruit from the grid
            new_row = list(grid[y])
            new_row[x] = '0'  # Replace fruit with path
            grid[y] = ''.join(new_row)
        return grid

    def all_fruits_collected(self, grid):
        """Check if all fruits have been collected."""
        for row in grid:
            if '2' in row:
                return False
        return True

    def draw(self, screen, grid):
        """
        This method is no longer needed.
        The Maze.draw() method now handles drawing the fruit images.
        """
        # --- 1. REMOVE THE OLD DRAW CODE ---
        # By doing nothing, we stop this class from
        # drawing colored squares on top of your fruit art.
        pass