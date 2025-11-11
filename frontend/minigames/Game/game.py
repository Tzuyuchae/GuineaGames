import pygame
import sys
import os
from maze import Maze
from player import Player
from settings import *
from maze_generator import MazeGenerator
from enemy import Enemy
from fruits import Fruit

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
        self.player = Player(seed=42)
        self.PACMAN_MAZE = self.player.add_player(self.PACMAN_MAZE)

        # Initialize Enemy
        self.enemy = Enemy(seed=42)
        self.PACMAN_MAZE = self.enemy.add_enemies(self.PACMAN_MAZE)
        
        # Initialize Fruit 
        self.fruit = Fruit(fruit_chance=0.1, seed=42)
        self.PACMAN_MAZE = self.fruit.add_fruits(self.PACMAN_MAZE)

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

    def handle_loops(self):
        """Handle loop points in the maze."""
        max_x = self.maze.cols - 1
        max_y = self.maze.rows - 1

        # Check horizontal loops
        if self.maze.is_loop(max_x, self.player.pos_y, self.PACMAN_MAZE) and self.player.pos_x == max_x:
            self.player.pos_x = 0
        elif self.maze.is_loop(0, self.player.pos_y, self.PACMAN_MAZE) and self.player.pos_x == 0:
            self.player.pos_x = max_x

        # Check vertical loops
        if self.maze.is_loop(self.player.pos_x, max_y, self.PACMAN_MAZE) and self.player.pos_y == max_y:
            self.player.pos_y = 0
        elif self.maze.is_loop(self.player.pos_x, 0, self.PACMAN_MAZE) and self.player.pos_y == 0:
            self.player.pos_y = max_y
            
    def check_lose(self):
        """Check if the player has collided with enemy."""
        # Ensure we don't index out of bounds; the maze layout should be consistent.
        if self.player.player_pos() == self.enemy.enemy_pos():
            print("You Lose!")
            self.running = False

    def check_win(self):
        """Check if the player has collected all fruits."""
        if self.fruit.all_fruits_collected(self.PACMAN_MAZE):
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

            self.handle_player_input()
            self.check_lose()
            self.check_win()
            self.handle_loops()

            # Draw maze, player, enemy, and fruits
            self.screen.fill(BLACK)
            self.maze.draw(self.screen)
            self.player.draw(self.screen)
            #self.enemy.move_towards_player((self.player.pos_x, self.player.pos_y), self.maze)
            self.enemy.draw(self.screen)
            self.PACMAN_MAZE = self.fruit.if_collected((self.player.pos_x, self.player.pos_y), self.PACMAN_MAZE)
            self.fruit.draw(self.screen, self.PACMAN_MAZE)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()