import pygame 
from minigame.settings import TILE_SIZE, BLUE, BLACK, GREEN, GOLD, RED
import os 

# --- PATH CONFIGURATION ---
base_path = os.path.dirname(__file__) 
# FIX: Point to "frontend/game sprites/mini-game"
image_path = os.path.join(base_path, "../../frontend/Global Assets/Sprites/Mini-game/")


class Maze: 
    def __init__(self, layout):
        self.layout = layout
        self.rows = len(layout)
        self.cols = len(layout[0])
        self.width = self.cols * TILE_SIZE
        self.height = self.rows * TILE_SIZE
        
        # Load all tile images into a dictionary
        self.tile_images = self.load_images()

    def load_images(self):
        """
        Loads all images for the maze tiles and scales them.
        Returns a dictionary mapping tile characters to pygame.Surface objects.
        """
        images = {}
        # Map tile characters to their image filenames
        image_map = {
            '1': 'wall.png',
            '0': 'floor.png',          # Walkable floor
            '2': 'fruit.png',          # Fruit/Coin
            '3': 'out_of_bounds.png',  # The void/black area
            'X': 'enemy_exit.png',     # Gate for enemies
            'S': 'enemy_spawn.png'     # Spawn point
        }
        
        # Fallback colors if images are missing
        fallback_colors = {
            '1': BLUE,
            '0': BLACK,
            '2': GOLD, 
            '3': (20, 20, 20), # Dark Gray for out of bounds
            'X': (100, 100, 100), # Gray for exit
            'S': (50, 0, 0) # Dark Red for spawn
        }

        for tile_char, filename in image_map.items():
            full_path = os.path.join(image_path, filename) 
            try:
                # Load the image
                image = pygame.image.load(full_path).convert_alpha()
                # Scale it to TILE_SIZE
                image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
                images[tile_char] = image
            except (FileNotFoundError, pygame.error):
                # If image is missing, create a colored square as a fallback
                # We silence the print warning to keep console clean
                images[tile_char] = pygame.Surface((TILE_SIZE, TILE_SIZE))
                images[tile_char].fill(fallback_colors.get(tile_char, BLACK))
                
        return images

    def draw(self, screen):
        """Draw the maze on the given screen using images."""
        for y, row in enumerate(self.layout):
            for x, tile in enumerate(row):
                # Calculate the position 
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                
                # 1. Draw Default Background (Black)
                pygame.draw.rect(screen, BLACK, rect)

                # 2. Get the correct image for this tile type
                image_to_draw = self.tile_images.get(tile)
                
                if image_to_draw:
                    screen.blit(image_to_draw, rect)

    def is_wall(self, x, y):
        """
        Return True if the tile at (x,y) is a wall, out of bounds, or an enemy gate.
        This prevents the player from walking into void or walls.
        """
        # Check boundaries first
        if x < 0 or x >= self.cols or y < 0 or y >= self.rows:
            return True

        tile = self.layout[y][x]
        
        # '1' = Wall
        # '3' = Out of Bounds (The void)
        # 'X' = Enemy Gate (Player shouldn't enter)
        return tile in ['1', '3', 'X']

    def is_loop(self, max_x, max_y, grid):
        """Return True when the tile at (x,y) is a loop point."""
        for y in range(self.rows):
            for x in range(self.cols):
                if x == max_x and y == max_y:
                    if grid[y][x] == '0':
                        return True
        return False