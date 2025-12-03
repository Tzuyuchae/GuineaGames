import pygame
import random
import os
from .settings import TILE_SIZE

class Fruit:
    def __init__(self, fruit_chance=0.1, seed=None):
        self.fruit_chance = fruit_chance
        self.seed = seed
        self.spawned_fruits = {}
        self.images = self._load_images()

    def _load_images(self):
        imgs = []
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base, "Global Assets/Sprites/Mini-game/")
        
        files = ["MG_Banana.png", "MG_Strawberry.png", "MG_Carrot.png"]
        for f in files:
            try:
                i = pygame.image.load(os.path.join(path, f)).convert_alpha()
                imgs.append(pygame.transform.scale(i, (TILE_SIZE, TILE_SIZE)))
            except: pass
            
        if not imgs:
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            s.fill((0,255,0))
            imgs.append(s)
        return imgs

    def add_fruits(self, grid):
        if self.seed is not None: random.seed(self.seed)
        self.spawned_fruits = {}
        new_grid = []
        
        for y, row in enumerate(grid):
            new_row = ""
            for x, tile in enumerate(row):
                if tile == '0' and random.random() < self.fruit_chance:
                    new_row += '2'
                    self.spawned_fruits[(x,y)] = random.choice(self.images)
                else:
                    new_row += tile
            new_grid.append(new_row)
        return new_grid

    def if_collected(self, player_pos, grid):
        x, y = player_pos
        collected = 0
        if grid[y][x] == '2':
            if (x,y) in self.spawned_fruits:
                del self.spawned_fruits[(x,y)]
            new_row = list(grid[y])
            new_row[x] = '0'
            grid[y] = "".join(new_row)
            collected = 10
        return grid, collected

    def all_fruits_collected(self, grid):
        return len(self.spawned_fruits) == 0

    def draw(self, screen, grid, offset_x=0, offset_y=0):
        for (x,y), img in self.spawned_fruits.items():
            screen.blit(img, (x*TILE_SIZE+offset_x, y*TILE_SIZE+offset_y))