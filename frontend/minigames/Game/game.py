import pygame
import sys
import os
from maze import Maze
from player import Player
from settings import *
from maze_generator import MazeGenerator
from enemy import Enemy

# Path to assets 
base_path = os.path.dirname(__file__)
assets_path = os.path.join(base_path, "../assets/audio/")

class Game: 
    def __init__(self): 
        pygame.init()
        pygame.mixer.init()

        # Maze layout: 0 = path, 1 = wall, P = player, E = exit
        # in maze.py or imported into Game
        # Generate maze using MazeGenerator
        generator = MazeGenerator(fruit_chance=0.1, seed=42)
        self.PACMAN_MAZE = generator.generate()
        
        # Initialize player
        self.player = Player()
        self.PACMAN_MAZE = self.player.add_player(self.PACMAN_MAZE)

        # Initialize Enemy
        self.enemy = Enemy()
        self.PACMAN_MAZE = self.enemy.add_enemies(self.PACMAN_MAZE)

        self.maze = Maze(self.PACMAN_MAZE)
        self.screen = pygame.display.set_mode((self.maze.width, self.maze.height))
        pygame.display.set_caption("Pac-Man Maze Game")

        self.clock = pygame.time.Clock()
        self.running = True

    def handle_player_input(self):
        """Handle user input for player movement."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player.move(0, -1, self.maze)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player.move(0, 1, self.maze)
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move(-1, 0, self.maze)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move(1, 0, self.maze)

    def check_lose(self):
        """Check if the player has collided with enemy."""
        # Ensure we don't index out of bounds; the maze layout should be consistent.
        if self.PACMAN_MAZE[self.player.pos_y][self.player.pos_x] == 'E':
            print("You Lose!")
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

            self.handle_player_input()
            self.check_lose()

            self.screen.fill(BLACK)
            self.maze.draw(self.screen)
            self.player.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()