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

# --- Path to assets ---
base_path = os.path.dirname(__file__)
assets_path = os.path.join(base_path, "../../assets/audio/")

class Game: 
    def __init__(self, selected_guinea_pig=None, player_inventory=None): 
        """
        Initialize the game.
        Args:
            player_inventory: The main PlayerInventory object to update
        """
        pygame.mixer.init() 

        self.running = True
        self.selected_guinea_pig = selected_guinea_pig
        self.player_inventory = player_inventory

        # 1. Generate Maze
        generator = MazeGenerator(fruit_chance=0.1, seed=42)
        self.PACMAN_MAZE = generator.generate()

        # 2. Create player
        self.player = Player(seed=42, guinea_pig_data=selected_guinea_pig)
        self.PACMAN_MAZE = self.player.add_player(self.PACMAN_MAZE)

        # 3. Create Enemies
        self.enemy = Enemy(seed=42)
        try:
            self.PACMAN_MAZE = self.enemy.add_enemies(self.PACMAN_MAZE)
        except Exception as e:
            print(f"Warning: Enemy generation failed: {e}")

        # 4. Create Fruits
        self.fruit = Fruit(fruit_chance=0.1, seed=42)
        try:
            self.PACMAN_MAZE = self.fruit.add_fruits(self.PACMAN_MAZE)
        except Exception as e:
            print(f"Warning: Fruit generation failed: {e}")

        # 5. Initialize Maze Render Object
        self.maze = Maze(self.PACMAN_MAZE)
        
        # 6. Setup 'Back' Button
        if hasattr(self.maze, 'width') and hasattr(self.maze, 'height'):
            button_w = 200
            button_h = 70
            button_x = (self.maze.width - button_w) // 2
            button_y = self.maze.height - button_h - 10
        else:
            button_x, button_y, button_w, button_h = 100, 500, 200, 70
            
        self.button_back = Button(button_x, button_y, button_w, button_h,
                                  'BACK', (150, 150, 0), (200, 200, 0))

        # 7. Start Music
        self.play_music("music.wav")

    def play_music(self, filename):
        try:
            pygame.mixer.music.load(os.path.join(assets_path, filename))
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            # print(f"Music Error: {e}")
            pass

    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if hasattr(self, 'button_back') and self.button_back.check_click(event):
                print("Back button clicked! Returning to homescreen.")
                self.running = False

        if hasattr(self, 'button_back'):
            self.button_back.check_hover(mouse_pos)

        if self.running:
            self.player.handle_input(self.maze)
            self.enemy.move_towards_player(self.player.player_pos(), self.maze)
            
            self.check_lose()
            self.check_win()
            self.check_exit()

            # --- CHECK FRUIT COLLISION & UPDATE INVENTORY ---
            # Get both the new grid AND the number of collected items
            self.PACMAN_MAZE, collected_amount = self.fruit.if_collected(
                (self.player.pos_x, self.player.pos_y), self.PACMAN_MAZE
            )
            
            if collected_amount > 0 and self.player_inventory:
                # Assuming 'Banana' is the default fruit found in maze
                # You can change this to random fruits if desired
                self.player_inventory.add_food('Banana', collected_amount)
                print(f"Collected fruit! Total Food: {self.player_inventory.food}")

    def check_exit(self):
        if (self.player.pos_x == 0 or self.player.pos_x == self.maze.cols - 1 or
            self.player.pos_y == 0 or self.player.pos_y == self.maze.rows - 1):
            print("Exited the maze!")
            self.running = False

    def draw(self, screen):
        screen.fill(BLACK)
        self.maze.draw(screen)
        self.player.draw(screen)
        self.enemy.draw(screen)
        self.fruit.draw(screen, self.PACMAN_MAZE)
        
        if hasattr(self, 'button_back'):
            self.button_back.draw(screen)

        if self.selected_guinea_pig:
            self._draw_guinea_pig_hud(screen)

    def check_lose(self):
        if self.player.player_pos() == self.enemy.enemy_pos():
            print("You Lose!")
            self.running = False

    def check_win(self):
        if self.fruit.all_fruits_collected(self.PACMAN_MAZE):
            print("You Win!")
            self.running = False

    def _draw_guinea_pig_hud(self, screen):
        try:
            hud_font = pygame.font.SysFont('Arial', 20, bold=True)
        except:
            hud_font = pygame.font.Font(None, 24)

        name = self.selected_guinea_pig.get('name', 'Unknown')
        text = hud_font.render(f"Playing as: {name}", True, GOLD) 
        text_rect = text.get_rect()
        text_rect.centerx = self.maze.width // 2
        text_rect.top = 10

        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(screen, BLACK, bg_rect, border_radius=5)
        pygame.draw.rect(screen, GOLD, bg_rect, 2, border_radius=5)
        screen.blit(text, text_rect)