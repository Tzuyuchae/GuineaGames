import pygame
from .maze import Maze
from .player import Player
from .settings import *
from .maze_generator import MazeGenerator
from .enemy import Enemy
from .fruits import Fruit
from .button import Button

class Game: 
    def __init__(self, selected_guinea_pig=None, player_inventory=None): 
        self.running = True
        
        # This data holds the color/sprite info
        self.selected_guinea_pig = selected_guinea_pig 
        
        self.player_inventory = player_inventory
        self.collected_amount = 0 

        self.SCREEN_WIDTH = 672
        self.SCREEN_HEIGHT = 864

        # 1. Generate Maze
        generator = MazeGenerator(fruit_chance=0.1) 
        self.PACMAN_MAZE = generator.generate()

        # 2. Components
        # We pass the full pig data dict to Player
        self.player = Player(guinea_pig_data=self.selected_guinea_pig)
        self.PACMAN_MAZE = self.player.add_player(self.PACMAN_MAZE)
        
        self.enemy = Enemy()
        self.PACMAN_MAZE = self.enemy.add_enemies(self.PACMAN_MAZE)
        
        self.fruit = Fruit(fruit_chance=0.1)
        self.PACMAN_MAZE = self.fruit.add_fruits(self.PACMAN_MAZE)

        self.maze = Maze(self.PACMAN_MAZE)
        
        # 3. Center Calculation
        self.offset_x = (self.SCREEN_WIDTH - self.maze.width) // 2
        self.offset_y = (self.SCREEN_HEIGHT - self.maze.height) // 2
        
        # 4. Back Button
        self.button_back = Button(
            (self.SCREEN_WIDTH - 200) // 2, 
            self.SCREEN_HEIGHT - 80, 
            200, 60, 'BACK', (178, 34, 34), (200, 50, 50)
        )

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

            self.PACMAN_MAZE, count = self.fruit.if_collected(
                (self.player.pos_x, self.player.pos_y), self.PACMAN_MAZE
            )
            self.collected_amount += count 

    def check_exit(self):
        if (self.player.pos_x == 0 or self.player.pos_x == self.maze.cols - 1 or
            self.player.pos_y == 0 or self.player.pos_y == self.maze.rows - 1):
            print("Exited the maze!")
            self.running = False
            self.collected_amount += 2 

    def check_lose(self):
        if self.player.player_pos() == self.enemy.enemy_pos():
            print("You Lose!")
            self.running = False
            self.collected_amount = 0 

    def check_win(self):
        if self.fruit.all_fruits_collected(self.PACMAN_MAZE):
            print("You Win!")
            self.running = False
            self.collected_amount += 5 

    def draw(self, screen):
        screen.fill((40, 40, 60)) 

        # Draw Backdrop
        backdrop_rect = pygame.Rect(
            self.offset_x - 5, self.offset_y - 5, 
            self.maze.width + 10, self.maze.height + 10
        )
        pygame.draw.rect(screen, (0, 0, 0), backdrop_rect)
        pygame.draw.rect(screen, (255, 215, 0), backdrop_rect, 2)

        # Draw Elements
        self.maze.draw(screen, self.offset_x, self.offset_y)
        self.fruit.draw(screen, self.PACMAN_MAZE, self.offset_x, self.offset_y)
        self.player.draw(screen, self.offset_x, self.offset_y)
        self.enemy.draw(screen, self.offset_x, self.offset_y)
        
        self.button_back.draw(screen)