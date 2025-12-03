import pygame
import random 
import os
from minigame.settings import TILE_SIZE

class Fruit:
    def __init__(self, fruit_chance=0.1, seed=None):
        self.fruit_chance = fruit_chance
        self.seed = seed
        self.spawned_fruits = {} 
        self.fruit_images = []
        self._load_images()

    def _load_images(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Try finding the folder
        path_a = os.path.join(base_path, "../minigames/Game/assets/images/fruit/")
        path_b = os.path.join(base_path, "../../Global Assets/Sprites/Mini-game/")
        
        image_path = path_a
        if not os.path.exists(path_a):
            if os.path.exists(path_b):
                image_path = path_b
            else:
                print(f"Fruit Warning: Could not find fruit images.")
        
        filenames = [
            "MG_Banana.png", "MG_BellPepper.png", "MG_Blueberry.png",
            "MG_Cabbage.png", "MG_Carrot.png", "MG_Strawberry.png"
        ]
        
        for fname in filenames:
            full_path = os.path.join(image_path, fname)
            try:
                img = pygame.image.load(full_path).convert_alpha()
                img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                self.fruit_images.append(img)
            except:
                continue
        
        if not self.fruit_images:
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            s.fill((0, 255, 0))
            self.fruit_images.append(s)

    def add_fruits(self, grid):
        if self.seed is not None:
            random.seed(self.seed)

        self.spawned_fruits = {}
        new_grid = []
        
        for y, row in enumerate(grid):
            new_row = ""
            for x, tile in enumerate(row):
                if tile == '0' and random.random() < self.fruit_chance:
                    new_row += '2'
                    random_img = random.choice(self.fruit_images)
                    self.spawned_fruits[(x, y)] = random_img
                else:
                    new_row += tile
            new_grid.append(new_row)
            
        return new_grid
    
    def if_collected(self, player_pos, grid):
        x, y = player_pos
        collected = 0
        
        if grid[y][x] == '2':
            if (x, y) in self.spawned_fruits:
                del self.spawned_fruits[(x, y)]
            
            new_row = list(grid[y])
            new_row[x] = '0'
            grid[y] = ''.join(new_row)
            collected = 1
            
        return grid, collected

    def all_fruits_collected(self, grid):
        return len(self.spawned_fruits) == 0

    def draw(self, screen, grid, offset_x=0, offset_y=0):
        """Draw fruits with centering offset."""
        for (x, y), img in self.spawned_fruits.items():
            rect = pygame.Rect(x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y, TILE_SIZE, TILE_SIZE)
            screen.blit(img, rect)