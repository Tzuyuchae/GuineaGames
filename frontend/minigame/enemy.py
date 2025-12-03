import pygame 
import random
import os
from .settings import TILE_SIZE, GOLD

class Enemy:
    def __init__(self, pos_x=0, pos_y=0, color=GOLD, seed=None):
        self.position = [pos_x, pos_y]
        self.color = color
        self.seed = seed
        self.move_timer = 0
        self.image = self._load_sprite()

    def _load_sprite(self):
        try:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(base, "Global Assets", "Sprites", "Mini-game", "MG_Dragon.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        except: pass
        
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        s.fill(self.color)
        return s
    
    def move_towards_player(self, player_pos, maze):
        # Slow down enemy (move every 20 frames)
        self.move_timer += 1
        if self.move_timer < 20: return
        self.move_timer = 0

        px, py = player_pos
        ex, ey = self.position
        
        # Simple AI: Try horizontal, then vertical
        if ex < px and not maze.is_wall(ex + 1, ey): self.position[0] += 1
        elif ex > px and not maze.is_wall(ex - 1, ey): self.position[0] -= 1
        elif ey < py and not maze.is_wall(ex, ey + 1): self.position[1] += 1
        elif ey > py and not maze.is_wall(ex, ey - 1): self.position[1] -= 1
    
    def add_enemies(self, grid):
        if self.seed is not None: random.seed(self.seed)
        spawn_points = [(x, y) for y, row in enumerate(grid) for x, tile in enumerate(row) if tile == 'S']
        new_grid = [list(row) for row in grid]
        if spawn_points:
            self.position = list(random.choice(spawn_points))
            new_grid[self.position[1]][self.position[0]] = 'E'
        return [''.join(row) for row in new_grid]
    
    def enemy_pos(self):
        return tuple(self.position)

    def draw(self, screen, off_x=0, off_y=0):
        rect = pygame.Rect(
            off_x + self.position[0] * TILE_SIZE, 
            off_y + self.position[1] * TILE_SIZE, 
            TILE_SIZE, TILE_SIZE
        )
        screen.blit(self.image, rect)