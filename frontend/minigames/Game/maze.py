import pygame 
from settings import TILE_SIZE,BLUE, GREEN

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
                elif tile == "E":
                    pygame.draw.rect(screen, GREEN, rect)

    def is_wall(self, x, y): 
        """Checks if the tile is walkable or not (not a wall)"""
        if 0 <= y < self.rows and 0 <= x < self.cols:
            return self.layout[y][x] != "1"
        return False