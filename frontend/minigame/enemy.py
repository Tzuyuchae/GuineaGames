import pygame
import random
import os
from minigame.settings import TILE_SIZE, BLUE

class Enemy:
    def __init__(self, seed=None):
        """Initialize the enemy."""
        self.pos_x = 0
        self.pos_y = 0
        self.seed = seed
        self.color = BLUE
        
        # --- ROBUST IMAGE LOADING ---
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Check paths for Dragon or fallback Enemy
        paths_to_check = [
            os.path.join(base_path, "../Global Assets/Sprites/Mini-game/MG_Dragon.png"),
            os.path.join(base_path, "../../Global Assets/Sprites/Mini-game/MG_Dragon.png"),
            os.path.join(base_path, "../images/enemy.png"),
            os.path.join(base_path, "../../images/enemy.png")
        ]
        
        self.image = None
        for p in paths_to_check:
            if os.path.exists(p):
                try:
                    raw_image = pygame.image.load(p).convert_alpha()
                    self.image = pygame.transform.scale(raw_image, (TILE_SIZE, TILE_SIZE))
                    print(f"Enemy: Loaded sprite from {p}")
                    break
                except:
                    pass
                    
        if self.image is None:
            print("Enemy: Could not find sprite. Using Fallback.")
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((255, 0, 0)) # Red Square Fallback
            # Draw 'E' or eyes for visibility
            pygame.draw.rect(self.image, (0,0,0), (5, 5, 5, 5))
            pygame.draw.rect(self.image, (0,0,0), (15, 5, 5, 5))
            
        self.rect = self.image.get_rect()
        
        # Movement
        self.move_timer = 0
        self.move_delay = 20  

    def add_enemies(self, grid):
        if self.seed is not None:
            random.seed(self.seed + 1) 
            
        spawn_points = []
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                if tile == '0':
                    spawn_points.append((x, y))
        
        new_grid = [list(row) for row in grid]
        
        if spawn_points:
            ex, ey = random.choice(spawn_points)
            new_grid[ey][ex] = 'E'
            self.pos_x = ex
            self.pos_y = ey
            
        return [''.join(row) for row in new_grid]

    def move_towards_player(self, player_pos, maze):
        self.move_timer += 1
        if self.move_timer < self.move_delay:
            return

        self.move_timer = 0
        px, py = player_pos
        ex, ey = self.pos_x, self.pos_y
        
        potential_moves = []
        if ex < px: potential_moves.append((1, 0)) 
        if ex > px: potential_moves.append((-1, 0)) 
        if ey < py: potential_moves.append((0, 1)) 
        if ey > py: potential_moves.append((0, -1)) 
        
        random.shuffle(potential_moves)
        
        for dx, dy in potential_moves:
            if not maze.is_wall(ex + dx, ey + dy):
                self.pos_x += dx
                self.pos_y += dy
                return

    def enemy_pos(self):
        return (self.pos_x, self.pos_y)

    def draw(self, screen, offset_x=0, offset_y=0):
        """Draw the enemy with centering offset."""
        pixel_x = self.pos_x * TILE_SIZE + offset_x
        pixel_y = self.pos_y * TILE_SIZE + offset_y
        self.rect.topleft = (pixel_x, pixel_y)
        screen.blit(self.image, self.rect)