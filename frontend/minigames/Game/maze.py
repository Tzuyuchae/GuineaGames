import pygame 
from settings import TILE_SIZE,BLUE, GREEN, GOLD, BLACK

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
                    pygame.draw.rect(screen, BLUE, rect)
                elif tile == "2":
                    pygame.draw.rect(screen, GREEN, rect)
                elif tile == "E":
                    pygame.draw.rect(screen, GOLD, rect)  # Gold color for exit (Will represent enemy later)
                elif tile == "3" or tile == "X" or tile == "S":
                    pygame.draw.rect(screen, BLACK, rect)  # Black for out of bounds

    def is_wall(self, x, y, tile="1"): 
        """Checks if the tile is walkable or not (not a wall)"""
        if 0 <= y < self.rows and 0 <= x < self.cols:
            return self.layout[y][x] != tile
        return False