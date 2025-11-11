import pygame 
import random
from settings import TILE_SIZE, RED

class Player:
    def __init__(self, x=0, y=0, color=RED, seed=None):
        self.pos_x = x
        self.pos_y = y
        self.color = color
        self.seed = seed

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
        """Draw the player on the given screen."""
        rect = pygame.Rect(self.pos_x * TILE_SIZE, self.pos_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, self.color, rect)