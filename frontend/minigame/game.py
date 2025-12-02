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

base_path = os.path.dirname(__file__)
assets_path = os.path.join(base_path, "../../assets/audio/")

class Game: 
    def __init__(self, selected_guinea_pig=None, player_inventory=None): 
        pygame.mixer.init() 
        self.running = True
        self.selected_guinea_pig = selected_guinea_pig
        self.player_inventory = player_inventory
        self.collected_amount = 0

        # Screen Dimensions (Should match main.py)
        self.SCREEN_WIDTH = 672
        self.SCREEN_HEIGHT = 864

        # 1. Load Styling Assets (Background)
        self.background_img = self._load_background()
        
        # 2. Generate Maze
        generator = MazeGenerator(fruit_chance=0.1, seed=42)
        self.PACMAN_MAZE = generator.generate()

        # 3. Create Components
        self.player = Player(seed=42, guinea_pig_data=selected_guinea_pig)
        self.PACMAN_MAZE = self.player.add_player(self.PACMAN_MAZE)
        
        self.enemy = Enemy(seed=42)
        self.PACMAN_MAZE = self.enemy.add_enemies(self.PACMAN_MAZE)
        
        self.fruit = Fruit(fruit_chance=0.1, seed=42)
        self.PACMAN_MAZE = self.fruit.add_fruits(self.PACMAN_MAZE)

        self.maze = Maze(self.PACMAN_MAZE)
        
        # 4. Calculate Centering Offsets
        self.offset_x = (self.SCREEN_WIDTH - self.maze.width) // 2
        self.offset_y = (self.SCREEN_HEIGHT - self.maze.height) // 2
        
        # 5. Setup 'Back' Button (Styled Gold/Red)
        button_w = 200
        button_h = 60
        button_x = (self.SCREEN_WIDTH - button_w) // 2
        button_y = self.SCREEN_HEIGHT - button_h - 30
        
        # Colors: (Normal, Hover, Text) -> Using Red theme for Back button
        self.button_back = Button(button_x, button_y, button_w, button_h,
                                  'BACK', (178, 34, 34), (200, 50, 50))

        self.play_music("music.wav")

    def _load_background(self):
        """Loads and scales the title background."""
        paths_to_check = [
            os.path.join(base_path, "../../images/BG_Title.png"),
            os.path.join(base_path, "../../Global Assets/Sprites/More Sprites/BG Art/Title/BG_Title.png")
        ]
        
        for p in paths_to_check:
            if os.path.exists(p):
                try:
                    img = pygame.image.load(p).convert()
                    return pygame.transform.scale(img, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
                except:
                    pass
        return None

    def play_music(self, filename):
        try:
            pygame.mixer.music.load(os.path.join(assets_path, filename))
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass

    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if self.button_back.check_click(event):
                self.running = False

        self.button_back.check_hover(mouse_pos)

        if self.running:
            self.player.handle_input(self.maze)
            self.enemy.move_towards_player(self.player.player_pos(), self.maze)
            
            self.check_lose()
            self.check_win()
            self.check_exit()

            self.PACMAN_MAZE, self.collected_amount = self.fruit.if_collected(
                (self.player.pos_x, self.player.pos_y), self.PACMAN_MAZE
            )
            
            if self.collected_amount > 0 and self.player_inventory:
                self.player_inventory.add_food('Banana', self.collected_amount)
                print(f"Collected fruit! Total Food: {self.player_inventory.food}")

    def check_exit(self):
        if (self.player.pos_x == 0 or self.player.pos_x == self.maze.cols - 1 or
            self.player.pos_y == 0 or self.player.pos_y == self.maze.rows - 1):
            print("Exited the maze!")
            self.running = False

    def draw(self, screen):
        # 1. Draw Background
        if self.background_img:
            screen.blit(self.background_img, (0, 0))
        else:
            screen.fill((40, 40, 60)) # Fallback color

        # 2. Draw Translucent Backdrop for Maze (Makes it pop)
        backdrop_rect = pygame.Rect(
            self.offset_x - 10, 
            self.offset_y - 10, 
            self.maze.width + 20, 
            self.maze.height + 20
        )
        # Create a surface for transparency
        s = pygame.Surface((backdrop_rect.width, backdrop_rect.height))
        s.set_alpha(180) # Semi-transparent black
        s.fill((0, 0, 0))
        screen.blit(s, (backdrop_rect.x, backdrop_rect.y))
        
        # Draw Border around maze
        pygame.draw.rect(screen, GOLD, backdrop_rect, 3, border_radius=5)

        # 3. Draw Game Elements
        self.maze.draw(screen, self.offset_x, self.offset_y)
        self.fruit.draw(screen, self.PACMAN_MAZE, self.offset_x, self.offset_y)
        self.player.draw(screen, self.offset_x, self.offset_y)
        self.enemy.draw(screen, self.offset_x, self.offset_y)
        
        # 4. Draw UI Elements
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
        text_rect.centerx = self.SCREEN_WIDTH // 2
        text_rect.top = self.offset_y - 40 # Float above maze

        # Draw styled box behind text
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0), bg_rect, border_radius=5)
        pygame.draw.rect(screen, GOLD, bg_rect, 2, border_radius=5)
        screen.blit(text, text_rect)