import pygame
import sys
import os

# --- Fix for Imports ---
# Add the parent directory (which is 'frontend/') to the Python path


# --- Imports (FIXED) ---
# Now that 'frontend' is on the path, we can import these directly.
from .button import Button
from .maze import Maze
from .player import Player
from .fruits import Fruit

# --- MINIGAME Imports (FIXED) ---
# Since 'frontend' is on the path, we import these from 'minigame'
# DO NOT use relative dots ('.') here.
from minigame.settings import *
from minigame.maze_generator import MazeGenerator
from minigame.enemy import Enemy


# Path to assets (this path is correct)
base_path = os.path.dirname(__file__)
assets_path = os.path.join(base_path, "../assets/audio/")

class Game:
    def __init__(self):
        pygame.mixer.init()

class Game:
    # --- All indentation has been fixed ---
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

        # Only update game logic if running
        if self.running:
            self.handle_player_input()
            self.check_lose()
            self.check_win()
            self.handle_loops()

            self.PACMAN_MAZE = self.fruit.if_collected(
                (self.player.pos_x, self.player.pos_y), self.PACMAN_MAZE
            )

        # If running is set to False (by button or game end), stop music and return
        if not self.running:
            pygame.mixer.music.stop()
            return 'homescreen'

        return None  # Stay on this screen

    def draw(self, screen):
        """Draws the game state onto the provided screen."""
        screen.fill(BLACK)

        self.maze.draw(screen)
        self.player.draw(screen)
        self.enemy.draw(screen)
        self.fruit.draw(screen, self.PACMAN_MAZE)
        self.button_back.draw(screen)
        
        # Draw guinea pig name HUD if available
        if self.selected_guinea_pig:
            self._draw_guinea_pig_hud(screen)

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
            print(f"Music Error: {e}")

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
