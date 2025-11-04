import pygame
import sys
from maze import Maze
from player import Player
from settings import *

class Game: 
    def __init__(self): 
        pygame.init()

        # Maze layout: 0 = path, 1 = wall, P = player, E = exit
        self.maze_layout = [
            "11111111111", 
            "1P0000000E1",
            "10111111101",
            "10000000001",
            "11111111111",
        ]

        # Find player start position
        for y, row in enumerate(self.maze_layout):
            for x, tile in enumerate(row):
                if tile == 'P':
                    self.player_start = Player(x, y)

        # Create maze
        self.maze = Maze(self.maze_layout)
        self.screen = pygame.display.set_mode((self.maze.width, self.maze.height))
        pygame.display.set_caption("Maze Game")

        self.clock = pygame.time.Clock()
        self.running = True
    def handle_input(self):
        """Handle user input for player movement."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player_start.move(0, -1, self.maze)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player_start.move(0, 1, self.maze)
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_start.move(-1, 0, self.maze)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_start.move(1, 0, self.maze)

    def check_win(self):
        """Check if the player has reached the exit."""
        # Ensure we don't index out of bounds; the maze layout should be consistent.
        if self.maze_layout[self.player_start.pos_y][self.player_start.pos_x] == 'E':
            print("You Win!")
            self.running = False

    def run(self):
        """Main game loop."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.handle_input()
            self.check_win()

            self.screen.fill(BLACK)
            self.maze.draw(self.screen)
            self.player_start.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()