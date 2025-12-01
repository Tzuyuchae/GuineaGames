import pygame
import os
from minigame.settings import TILE_SIZE, BLACK

class Maze:
    def __init__(self, layout):
        self.layout = layout
        self.rows = len(layout)
        self.cols = len(layout[0])
        self.width = self.cols * TILE_SIZE
        self.height = self.rows * TILE_SIZE

        # --- PATH FINDING LOGIC ---
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try to locate the Tileset folder automatically
        path_a = os.path.join(current_dir, "../Global Assets/Sprites/Maze/Tileset/")
        path_b = os.path.join(current_dir, "../../Global Assets/Sprites/Maze/Tileset/")
        
        if os.path.exists(path_a):
            self.image_path = path_a
        elif os.path.exists(path_b):
            self.image_path = path_b
        else:
            # Fallback
            self.image_path = path_a
            print(f"Maze Warning: Tile directory not found at {path_a}")

        # 1. Load the wall tiles dictionary
        self.wall_tiles = self.load_wall_tiles()
        
        # 2. Load floor (User specified 000 is floor)
        self.floor_img = self._load_single_image("maze_tileset_000.png")
        
        # 3. Pre-calculate masks
        self.wall_masks = self._calculate_all_masks()

    def _load_single_image(self, filename):
        """Helper to load and scale a single image."""
        full_path = os.path.join(self.image_path, filename)
        try:
            img = pygame.image.load(full_path).convert_alpha()
            return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        except (FileNotFoundError, pygame.error):
            # Fallback: Magenta square for debugging missing files
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            surf.fill((255, 0, 255)) 
            return surf

    def load_wall_tiles(self):
        """
        Loads the correct images based on your provided mapping.
        Missing T-Junctions/Crosses are mapped to the 'Isolated' tile (001)
        to prevent holes in the maze.
        """
        tiles = {}
        
        # The 'Solid' fallback tile for missing intersections
        # Using "001" (Isolated Pillar) as it's a safe solid block
        FALLBACK_TILE = "maze_tileset_001.png"

        mapping = {
            # --- ISOLATED ---
            0:  "maze_tileset_001.png", 

            # --- END PIECES (Dead Ends) ---
            1:  "maze_tileset_016.png", # North
            2:  "maze_tileset_017.png", # South
            4:  "maze_tileset_014.png", # East
            8:  "maze_tileset_015.png", # West

            # --- STRAIGHT LINES ---
            3:  "maze_tileset_008.png", # Vertical
            12: "maze_tileset_009.png", # Horizontal

            # --- CORNERS ---
            5:  "maze_tileset_012.png", # Top-Right
            9:  "maze_tileset_013.png", # Top-Left
            6:  "maze_tileset_010.png", # Bottom-Right
            10: "maze_tileset_011.png", # Bottom-Left

            # --- MISSING INTERSECTIONS (Mapped to Fallback) ---
            7:  FALLBACK_TILE, # T-Right
            11: FALLBACK_TILE, # T-Left
            13: FALLBACK_TILE, # T-Up
            14: FALLBACK_TILE, # T-Down
            15: FALLBACK_TILE  # Cross
        }

        for mask_id, filename in mapping.items():
            tiles[mask_id] = self._load_single_image(filename)
                
        return tiles

    def _calculate_all_masks(self):
        masks = {}
        for y, row in enumerate(self.layout):
            for x, tile in enumerate(row):
                if tile == '1':
                    masks[(x, y)] = self.calculate_mask(x, y)
        return masks

    def calculate_mask(self, x, y):
        """Calculates the 4-bit number based on neighbors."""
        mask = 0
        # Check North
        if y > 0 and self.layout[y-1][x] == '1':
            mask += 1
        # Check South
        if y < self.rows - 1 and self.layout[y+1][x] == '1':
            mask += 2
        # Check East
        if x < self.cols - 1 and self.layout[y][x+1] == '1':
            mask += 4
        # Check West
        if x > 0 and self.layout[y][x-1] == '1':
            mask += 8
        return mask

    def draw(self, screen):
        for y, row in enumerate(self.layout):
            for x, tile in enumerate(row):
                dest = (x * TILE_SIZE, y * TILE_SIZE)
                
                # 1. Draw Floor (except void)
                if tile != '3' and tile != 'X' and tile != 'S': 
                    if self.floor_img:
                        screen.blit(self.floor_img, dest)
                    else:
                        pygame.draw.rect(screen, (20, 20, 30), (*dest, TILE_SIZE, TILE_SIZE))

                # 2. Draw Walls
                if tile == '1':
                    mask = self.wall_masks.get((x, y), 0)
                    image = self.wall_tiles.get(mask)
                    if image:
                        screen.blit(image, dest)
                    else:
                        # Absolute fallback if even the mapping fails
                        pygame.draw.rect(screen, (100, 100, 255), (*dest, TILE_SIZE, TILE_SIZE))
                
                # 3. Draw Void/Spawns
                elif tile == '3' or tile == 'X' or tile == 'S':
                    pygame.draw.rect(screen, BLACK, (*dest, TILE_SIZE, TILE_SIZE))

    def is_wall(self, x, y):
        if x < 0 or x >= self.cols or y < 0 or y >= self.rows:
            return True
        return self.layout[y][x] in ['1', '3', 'X']

    def is_loop(self, max_x, max_y, grid):
        for y in range(self.rows):
            for x in range(self.cols):
                if x == max_x and y == max_y:
                    if grid[y][x] == '0':
                        return True
        return False