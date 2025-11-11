import pygame 
from settings import TILE_SIZE,BLUE, GREEN, GOLD, BLACK, RED

class Maze: 
    def __init__(self, layout):
        self.layout = layout
        self.rows = len(layout)
        self.cols = len(layout[0])
        self.width = self.cols * TILE_SIZE
        self.height = self.rows * TILE_SIZE

    def draw(self, screen):
        """Draw the maze on the given screen."""
        for y,row in enumerate(self.layout):
            for x, tile in enumerate(row):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if tile == "1":
                    pygame.draw.rect(screen, BLUE, rect) # Blue for walls
                elif tile == "3" or tile == "X" or tile == "S":
                    pygame.draw.rect(screen, BLACK, rect)  # Black for out of bounds, enemy spawn exit, and enemy spawn points

    def is_wall(self, x, y, tile="1"):
        """Return True when the tile at (x,y) is a wall (or out of bounds).

        A wall is represented by the character in `tile` (default '1').
        Out-of-bounds coordinates are treated as walls to prevent movement off the map.
        """
        if 0 <= y < self.rows and 0 <= x < self.cols:
            return self.layout[y][x] == tile
        # Treat coordinates outside the maze as walls
        return True
    
    def is_loop(self, max_x, max_y, grid):
        """Return True when the tile at (x,y) is a loop point.

        Out-of-bounds coordinates are treated as non-loop points.
        """
        for y in range(self.rows):
            for x in range(self.cols):
                if x == max_x and y == max_y:
                    if grid[y][x] == '0':
                        return True