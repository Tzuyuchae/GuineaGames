import pygame
import sys
import os
from maze import Maze
from player import Player
from settings import *
from maze_generator import MazeGenerator

# Path to assets 
base_path = os.path.dirname(__file__)
assets_path = os.path.join(base_path, "../assets/audio/")

class Game: 
    def __init__(self): 
        pygame.init()
        pygame.mixer.init()

        # Maze layout: 0 = path, 1 = wall, P = player, E = exit
        generator = MazeGenerator(21, 15)  # odd numbers work best
        self.maze_layout = generator.generate()

        # Find a place for the player
        for y, row in enumerate(self.maze_layout):
            for x, tile in enumerate(row):
                if tile == "0":
                    self.player = Player(x, y)
                    break
            else:
                continue
            break

        self.maze = Maze(self.maze_layout)
        self.screen = pygame.display.set_mode((self.maze.width, self.maze.height))
        pygame.display.set_caption("Procedural Maze")

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

    def play_music(self, filename):
        """Play background music."""
        pygame.mixer.music.load(os.path.join(assets_path, filename))
        pygame.mixer.music.play(-1)  # Loop indefinitely
    
    def run(self):
        """Main game loop."""
        self.play_music("music.wav")
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