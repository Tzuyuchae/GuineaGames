import pygame
import sys
import os

# --- Imports for the GAME class ---
from button import Button
from maze import Maze
from player import Player
from minigame.settings import *
from minigame.maze_generator import MazeGenerator
from minigame.enemy import Enemy
from fruits import Fruit

# Path to assets 
base_path = os.path.dirname(__file__)
assets_path = os.path.join(base_path, "../assets/audio/")


class Game: 
    def __init__(self): 
        pygame.mixer.init() 

        generator = MazeGenerator(fruit_chance=0.1, seed=42)
        self.PACMAN_MAZE = generator.generate()
        
        self.player = Player(seed=42)
        self.PACMAN_MAZE = self.player.add_player(self.PACMAN_MAZE)

        self.enemy = Enemy(seed=42)
        self.PACMAN_MAZE = self.enemy.add_enemies(self.PACMAN_MAZE)
        
        self.fruit = Fruit(fruit_chance=0.1, seed=42)
        self.PACMAN_MAZE = self.fruit.add_fruits(self.PACMAN_MAZE)

        self.maze = Maze(self.PACMAN_MAZE)
        
        self.running = True 
        
        # --- 'Back' button for the GAME ---
        button_w = 200
        button_h = 70
        button_x = (self.maze.width - button_w) // 2
        button_y = self.maze.height - button_h - 10 
        self.button_back = Button(button_x, button_y, button_w, button_h, 
                                  'BACK', (150, 150, 0), (200, 200, 0))
        
        self.play_music("music.wav")

    def update(self, events):
        """Handles all game logic for one frame."""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if self.button_back.check_click(event):
                print("Back button clicked! Returning to homescreen.")
                self.running = False 
        
        self.button_back.check_hover(mouse_pos)

        self.handle_player_input()
        self.check_lose()
        self.check_win()
        self.handle_loops()
        
        self.PACMAN_MAZE = self.fruit.if_collected(
            (self.player.pos_x, self.player.pos_y), self.PACMAN_MAZE
        )

        if not self.running:
            pygame.mixer.music.stop() 
            return 'homescreen' 
        
        return None

    def draw(self, screen):
        """Draws the game state onto the provided screen."""
        screen.fill(BLACK) 
        
        self.maze.draw(screen)
        self.player.draw(screen)
        self.enemy.draw(screen)
        self.fruit.draw(screen, self.PACMAN_MAZE)
        self.button_back.draw(screen)

    # --- (All other helper methods are unchanged) ---

    def handle_player_input(self):
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
        max_x = self.maze.cols - 1
        max_y = self.maze.rows - 1
        if self.maze.is_loop(max_x, self.player.pos_y, self.PACMAN_MAZE) and self.player.pos_x == max_x:
            self.player.pos_x = 0
        elif self.maze.is_loop(0, self.player.pos_y, self.PACMAN_MAZE) and self.player.pos_x == 0:
            self.player.pos_x = max_x
        if self.maze.is_loop(self.player.pos_x, max_y, self.PACMAN_MAZE) and self.player.pos_y == max_y:
            self.player.pos_y = 0
        elif self.maze.is_loop(self.player.pos_x, 0, self.PACMAN_MAZE) and self.player.pos_y == 0:
            self.player.pos_y = max_y
            
    def check_lose(self):
        if self.player.player_pos() == self.enemy.enemy_pos():
            print("You Lose!")
            self.running = False

    def check_win(self):
        if self.fruit.all_fruits_collected(self.PACMAN_MAZE):
            print("You Win!")
            self.running = False

    def play_music(self, filename):
        try:
            pygame.mixer.music.load(os.path.join(assets_path, filename))
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            print(f"Cannot load music: {filename} - {e}")