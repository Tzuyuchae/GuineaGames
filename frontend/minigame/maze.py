import pygame
import os
from .settings import TILE_SIZE, BLACK

class Maze:
    def __init__(self, layout):
        self.layout = layout
        self.rows = len(layout)
        self.cols = len(layout[0])
        self.width = self.cols * TILE_SIZE
        self.height = self.rows * TILE_SIZE

        # --- PATH FINDING LOGIC ---
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.image_path = os.path.join(base, "Global Assets/Sprites/Maze/Tileset/")
        
        self.wall_tiles = self.load_wall_tiles()
        self.floor_img = self._load_single_image("maze_tileset_000.png")
        self.wall_masks = self._calculate_all_masks()

    def _load_single_image(self, filename):
        full_path = os.path.join(self.image_path, filename)
        try:
            img = pygame.image.load(full_path).convert_alpha()
            return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        except:
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            s.fill((100, 100, 255)) 
            return s

    def load_wall_tiles(self):
        tiles = {}
        # Simple Mapping based on your files
        mapping = {
            0:  "maze_tileset_001.png", 
            1:  "maze_tileset_016.png", 2:  "maze_tileset_017.png",
            4:  "maze_tileset_014.png", 8:  "maze_tileset_015.png",
            3:  "maze_tileset_008.png", 12: "maze_tileset_009.png",
            5:  "maze_tileset_012.png", 9:  "maze_tileset_013.png",
            6:  "maze_tileset_010.png", 10: "maze_tileset_011.png",
            7:  "maze_tileset_001.png", 11: "maze_tileset_001.png",
            13: "maze_tileset_001.png", 14: "maze_tileset_001.png",
            15: "maze_tileset_001.png"
        }
        for k, v in mapping.items():
            tiles[k] = self._load_single_image(v)
        return tiles

    def _calculate_all_masks(self):
        masks = {}
        for y, row in enumerate(self.layout):
            for x, tile in enumerate(row):
                if tile == '1':
                    masks[(x, y)] = self.calculate_mask(x, y)
        return masks

    def calculate_mask(self, x, y):
        mask = 0
        if y > 0 and self.layout[y-1][x] == '1': mask += 1
        if y < self.rows - 1 and self.layout[y+1][x] == '1': mask += 2
        if x < self.cols - 1 and self.layout[y][x+1] == '1': mask += 4
        if x > 0 and self.layout[y][x-1] == '1': mask += 8
        return mask

    def draw(self, screen, offset_x=0, offset_y=0):
        for y, row in enumerate(self.layout):
            for x, tile in enumerate(row):
                dest = (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y)
                
                # Draw Floor everywhere (except void)
                if tile not in ['3', 'X', 'S']:
                    if self.floor_img: screen.blit(self.floor_img, dest)
                
                # Draw Walls
                if tile == '1':
                    mask = self.wall_masks.get((x, y), 0)
                    img = self.wall_tiles.get(mask, self.wall_tiles.get(0))
                    if img: screen.blit(img, dest)
                
                elif tile in ['3', 'X', 'S']:
                    pygame.draw.rect(screen, BLACK, (*dest, TILE_SIZE, TILE_SIZE))

    def is_wall(self, x, y, is_enemy=False):
        if x < 0 or x >= self.cols or y < 0 or y >= self.rows: 
            return True
        
        tile = self.layout[y][x]

        # '1' is Wall, '3' is Void. These are always blocked.
        if tile in ['1', '3']:
            return True
        
        # 'X' is the Gate. 
        # If it is an enemy, they can pass. If it's the player, they are blocked.
        if tile == 'X':
            return not is_enemy

        return False
    
    def is_loop(self, max_x, max_y, grid):
        return False