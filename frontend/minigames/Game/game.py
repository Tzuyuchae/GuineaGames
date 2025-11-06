import pygame
import sys
import os
from maze import Maze
from player import Player
from settings import *

# Path to assets 
base_path = os.path.dirname(__file__)
assets_path = os.path.join(base_path, "../assets/audio/")

class Game: 
    def __init__(self): 
        pygame.init()
        pygame.mixer.init()

        # Maze layout: 0 = path, 1 = wall, P = player, E = exit
        # in maze.py or imported into Game
        self.PACMAN_MAZE = [
            "1111111111111111111111111111",
            "10200000202001120000002000E1",
            "1011110111112112111110111101",
            "1010010100010110100210102101",
            "1011110111110110111110111101",
            "1000000000000000200000000001",
            "1011110110111111110110111101",
            "1011110110111111110112111121",
            "1000020110000112000110000001",
            "1111110111110110111110111111",
            "0000010111110110111110102020",
            "0002010112020000000110100000",
            "0000010110111--1110110102000",
            "1111110112100000010110111111",
            "0020000002100000010000000200",
            "1111110110100000210110111111",
            "0000010110111111110110100000",
            "2000010112000000000110100000",
            "0000010112111111110110102000",
            "1111110110111111110110111111",
            "1000002000000110000000000021",
            "1011110111112110111110111101",
            "1011110111110112111112111101",
            "1000110000000000000000110001",
            "1110110112111111110110110111",
            "1110110110111111110110110111",
            "1000000110020110000110000001",
            "1011111111110110111111111101",
            "1011111111110110111111111101",
            "1000000200000020000000000001",
            "1111111111111111111111111111",
        ]


        # Find a place for the player
        for y, row in enumerate(self.PACMAN_MAZE):
            for x, tile in enumerate(row):
                if tile == "0":
                    self.player_start = Player(x, y)
                    break
            else:
                continue
            break

        self.maze = Maze(self.PACMAN_MAZE)
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
        if self.PACMAN_MAZE[self.player_start.pos_y][self.player_start.pos_x] == 'E':
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