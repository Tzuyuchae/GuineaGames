import pygame 
from settings import TILE_SIZE, RED

class Player:
    def __init__(self, x, y, color=RED):
        self.pos_x = x
        self.pos_y = y
        self.color = color

    def move(self, dx, dy, maze):
        """Move the player by (dx, dy) if the target position is not a wall."""
        new_x = self.pos_x + dx
        new_y = self.pos_y + dy
        if maze.is_wall(new_x, new_y):
            self.pos_x = new_x
            self.pos_y = new_y

    def draw(self, screen):
        """Draw the player on the given screen."""
        rect = pygame.Rect(self.pos_x * TILE_SIZE, self.pos_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, self.color, rect)