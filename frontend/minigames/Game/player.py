import pygame 
from settings import TILE_SIZE, RED

class Player:
    def __init__(self, x=0, y=0, color=RED):
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

    def player_spawn(self, maze):
        """Place the player at the starting position in the maze."""
        for y, row in enumerate(maze.layout):
            for x, tile in enumerate(row):
                if tile == '0':  # For now spawn player at first walkable tile (Eventually with change to being random)
                    self.pos_x = x
                    self.pos_y = y
                    return

    def draw(self, screen):
        """Draw the player on the given screen."""
        rect = pygame.Rect(self.pos_x * TILE_SIZE, self.pos_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, self.color, rect)