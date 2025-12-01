import pygame
import random 
import os
from minigame.settings import TILE_SIZE

class Fruit:
    def __init__(self, fruit_chance=0.1, seed=None):
        self.fruit_chance = fruit_chance
        self.seed = seed
        self.spawned_fruits = {} # Maps coordinate (x,y) -> image
        self.fruit_images = []
        
        # Load Images
        self._load_images()

    def _load_images(self):
        """Robustly finds and loads the 6 fruit assets."""
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Attempt to find the folder with the 6 fruits
        # Path A: Standard structure
        path_a = os.path.join(base_path, "../minigames/Game/assets/images/fruit/")
        # Path B: Global Assets fallback
        path_b = os.path.join(base_path, "../../Global Assets/Sprites/Mini-game/")
        
        image_path = path_a
        if not os.path.exists(path_a):
            if os.path.exists(path_b):
                image_path = path_b
            else:
                print(f"Fruit Warning: Could not find fruit images at {path_a} or {path_b}")
        
        # Specific filenames for the 6 assets
        filenames = [
            "MG_Banana.png", 
            "MG_BellPepper.png", 
            "MG_Blueberry.png",
            "MG_Cabbage.png", 
            "MG_Carrot.png", 
            "MG_Strawberry.png"
        ]
        
        for fname in filenames:
            full_path = os.path.join(image_path, fname)
            try:
                img = pygame.image.load(full_path).convert_alpha()
                img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                self.fruit_images.append(img)
            except (FileNotFoundError, pygame.error):
                continue
        
        # Fallback if images missing
        if not self.fruit_images:
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            s.fill((0, 255, 0)) # Green square
            self.fruit_images.append(s)

    def add_fruits(self, grid):
        """
        Randomly places fruits ('2') on the grid.
        Assigns a specific random image to each location.
        """
        if self.seed is not None:
            random.seed(self.seed)

        self.spawned_fruits = {} # Reset dictionary
        new_grid = []
        
        for y, row in enumerate(grid):
            new_row = ""
            for x, tile in enumerate(row):
                # Place fruit on empty tiles ('0') based on chance
                if tile == '0' and random.random() < self.fruit_chance:
                    new_row += '2'  # Mark as fruit in grid
                    
                    # Assign a random image to this specific coordinate
                    random_img = random.choice(self.fruit_images)
                    self.spawned_fruits[(x, y)] = random_img
                else:
                    new_row += tile
            new_grid.append(new_row)
            
        return new_grid
    
    def if_collected(self, player_pos, grid):
        """
        Checks collision. Removes fruit from grid AND from the image dictionary.
        Returns: (updated_grid, collected_amount)
        """
        x, y = player_pos
        collected = 0
        
        if grid[y][x] == '2':
            # 1. Remove from visual dictionary
            if (x, y) in self.spawned_fruits:
                del self.spawned_fruits[(x, y)]
            
            # 2. Remove from logical grid
            new_row = list(grid[y])
            new_row[x] = '0'  # Replace fruit with floor
            grid[y] = ''.join(new_row)
            
            collected = 1
            
        return grid, collected

    def all_fruits_collected(self, grid):
        """Returns True if no fruits left."""
        return len(self.spawned_fruits) == 0

    def draw(self, screen, grid):
        """Draws the assigned fruit image at every recorded location."""
        for (x, y), img in self.spawned_fruits.items():
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            screen.blit(img, rect)