import pygame
import os
import sys

# --- Imports ---
from minigame.button import Button
from minigame.maze import Maze
from minigame.player import Player
from minigame.settings import *
from minigame.maze_generator import MazeGenerator
from minigame.enemy import Enemy
from minigame.fruits import Fruit

# Path to assets 
base_path = os.path.dirname(__file__)
assets_path = os.path.join(base_path, "../../assets/audio/")

class Game: 
    def __init__(self, selected_guinea_pig=None): 
        """
        Initialize the game.
        """
        pygame.mixer.init() 

        self.running = True
        self.selected_guinea_pig = selected_guinea_pig

        # 1. Generate Maze
        generator = MazeGenerator(fruit_chance=0.1, seed=42)
        self.PACMAN_MAZE = generator.generate()

        # 2. Create player with guinea pig data
        self.player = Player(seed=42, guinea_pig_data=selected_guinea_pig)
        self.PACMAN_MAZE = self.player.add_player(self.PACMAN_MAZE)

        # 3. Create Enemies
        self.enemy = Enemy(seed=42)
        self.PACMAN_MAZE = self.enemy.add_enemies(self.PACMAN_MAZE)

        # 4. Create Fruits
        self.fruit = Fruit(fruit_chance=0.1, seed=42)
        self.PACMAN_MAZE = self.fruit.add_fruits(self.PACMAN_MAZE)

        # 5. Initialize Maze Render Object
        self.maze = Maze(self.PACMAN_MAZE)

        # 6. Setup 'Back' Button
        button_w = 200
        button_h = 70
        button_x = (self.maze.width - button_w) // 2
        button_y = self.maze.height - button_h - 10
        self.button_back = Button(button_x, button_y, button_w, button_h,
                                  'BACK', (150, 150, 0), (200, 200, 0))

        # 7. Start Music
        self.play_music("music.wav")

    def play_music(self, filename):
        """Safely loads and plays music."""
        try:
            pygame.mixer.music.load(os.path.join(assets_path, filename))
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            print(f"Music Error (check assets path): {e}")

    def update(self, events):
        """Handles all game logic for one frame."""
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            # 1. Handle Button Click
            if self.button_back.check_click(event):
                print("Back button clicked! Returning to homescreen.")
                self.running = False

            # 2. Handle Player Movement (Discrete Steps)
            if self.running and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.player.move(0, -1, self.maze)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.player.move(0, 1, self.maze)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.player.move(-1, 0, self.maze)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player.move(1, 0, self.maze)

        self.button_back.check_hover(mouse_pos)

        if self.running:
            # --- FIX: Update Enemy Movement ---
            # This line was missing!
            self.enemy.move_towards_player(self.player.player_pos(), self.maze)
            
            # Check game states
            self.check_lose()
            self.check_win()

            # Check fruit collision
            self.PACMAN_MAZE = self.fruit.if_collected(
                (self.player.pos_x, self.player.pos_y), self.PACMAN_MAZE
            )

        # If game is over or user clicked back
        if not self.running:
            pygame.mixer.music.stop()
            return 'homescreen'

        return None

    def draw(self, screen):
        """Draws the game state onto the screen."""
        screen.fill(BLACK)

        self.maze.draw(screen)
        self.player.draw(screen)
        self.enemy.draw(screen)
        self.fruit.draw(screen, self.PACMAN_MAZE)
        self.button_back.draw(screen)

        # Draw guinea pig name HUD if available
        if self.selected_guinea_pig:
            self._draw_guinea_pig_hud(screen)

    def check_lose(self):
        """Check if player touched an enemy."""
        if self.player.player_pos() == self.enemy.enemy_pos():
            print("You Lose!")
            self.running = False

    def check_win(self):
        """Check if all fruits are collected."""
        if self.fruit.all_fruits_collected(self.PACMAN_MAZE):
            print("You Win!")
            self.running = False

    def _draw_guinea_pig_hud(self, screen):
        """Draw HUD showing which guinea pig is playing."""
        try:
            hud_font = pygame.font.SysFont('Arial', 20, bold=True)
        except:
            hud_font = pygame.font.Font(None, 24)

        # Create text
        name = self.selected_guinea_pig.get('name', 'Unknown')
        text = hud_font.render(f"Playing as: {name}", True, GOLD)

        # Position at top center
        text_rect = text.get_rect()
        text_rect.centerx = self.maze.width // 2
        text_rect.top = 10

        # Draw background
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(screen, BLACK, bg_rect, border_radius=5)
        pygame.draw.rect(screen, GOLD, bg_rect, 2, border_radius=5)

        # Draw text
        screen.blit(text, text_rect)