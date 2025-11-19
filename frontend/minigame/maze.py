import pygame 
from minigame.settings import TILE_SIZE, BLUE, BLACK, GREEN, GOLD, RED
import os # Import os for path handling

# Define the path to your images
# This assumes 'maze.py' is in a 'minigame' folder, 
# which is inside the 'frontend' folder.
base_path = os.path.dirname(__file__) 

# Go UP one level from 'minigame' to 'frontend'
# Then join with 'images'
image_path = os.path.join(base_path, "../images/") 

# --- If the above path doesn't work, try this ---
# This assumes 'minigame' and 'images' are both inside 'frontend'
# image_path = os.path.join(os.path.dirname(base_path), "images")


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
            '0': 'path.png',
            '2': 'fruit.png',
            '3': 'out_of_bounds.png', # Or use 'path.png' if it's just black
            'X': 'enemy_exit.png',
            'S': 'enemy_spawn.png'
        }
        
        # Fallback colors from your original code
        fallback_colors = {
            '1': BLUE,
            '0': BLACK,
            '2': GOLD, 
            '3': BLACK,
            'X': BLACK,
            'S': BLACK
        }

        for tile_char, filename in image_map.items():
            # This path is now correct
            full_path = os.path.join(image_path, filename) 
            try:
                # Load the image
                image = pygame.image.load(full_path).convert_alpha()
                # Scale it to TILE_SIZE
                image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
                images[tile_char] = image
            except FileNotFoundError:
                # If image is missing, create a colored square as a fallback
                print(f"Warning: Image file not found '{full_path}'. Creating fallback color square.")
                images[tile_char] = pygame.Surface((TILE_SIZE, TILE_SIZE))
                images[tile_char].fill(fallback_colors.get(tile_char, BLACK))
                
        return images

    # ... (rest of your Maze class is the same) ...           
    def draw(self, screen):
        """Draw the maze on the given screen using images."""
        for y, row in enumerate(self.layout):
            for x, tile in enumerate(row):
                # Calculate the position 
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                
                # Get the correct image for this tile type
                image_to_draw = self.tile_images.get(tile)
                
                if image_to_draw:
                    # Blit (draw) the image onto the screen
                    screen.blit(image_to_draw, rect)

    def is_wall(self, x, y, tile="1"):
        """Return True when the tile at (x,y) is a wall (or out of bounds)."""
        if 0 <= y < self.rows and 0 <= x < self.cols:
            return self.layout[y][x] == tile
        return True
    
    def is_loop(self, max_x, max_y, grid):
        """Return True when the tile at (x,y) is a loop point."""
        for y in range(self.rows):
            for x in range(self.cols):
                if x == max_x and y == max_y:
                    if grid[y][x] == '0':
                        return True
        return False