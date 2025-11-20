import pygame 
import random
import os
from minigame.settings import TILE_SIZE, GOLD

class Enemy:
    def __init__(self, pos_x=0, pos_y=0, color=GOLD, seed=None):
        self.position = [pos_x, pos_y]
        self.color = color 
        self.seed = seed
        
        # --- MOVEMENT TIMER ---
        self.last_move_time = 0
        self.move_delay = 400  # Time in milliseconds (0.4 seconds) between moves

        # --- IMAGE LOADING ---
        base_path = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_path, "../../frontend/images/enemy.png")

        try:
            raw_img = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(raw_img, (TILE_SIZE, TILE_SIZE))
        except (FileNotFoundError, pygame.error):
            print(f"Warning: Enemy image not found at {image_path}. Using fallback.")
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(self.color)
    
    def move_towards_player(self, player_pos, maze):
        """
        Move the enemy one step towards the player.
        Includes a timer check to control speed.
        """
        # 1. Check Timer (Don't move too fast)
        now = pygame.time.get_ticks()
        if now - self.last_move_time < self.move_delay:
            return 
        
        self.last_move_time = now

        ex, ey = self.position
        px, py = player_pos
        
        # 2. Determine direction
        # We prefer to move along the axis with the biggest distance
        dx = px - ex
        dy = py - ey
        
        moved = False

        # Try moving horizontally first if distance X is bigger
        if abs(dx) >= abs(dy):
            if dx > 0 and not maze.is_wall(ex + 1, ey):
                self.position[0] += 1
                moved = True
            elif dx < 0 and not maze.is_wall(ex - 1, ey):
                self.position[0] -= 1
                moved = True
            # If horizontal failed (wall), try vertical
            if not moved:
                if dy > 0 and not maze.is_wall(ex, ey + 1):
                    self.position[1] += 1
                elif dy < 0 and not maze.is_wall(ex, ey - 1):
                    self.position[1] -= 1
        
        # Try moving vertically first
        else:
            if dy > 0 and not maze.is_wall(ex, ey + 1):
                self.position[1] += 1
                moved = True
            elif dy < 0 and not maze.is_wall(ex, ey - 1):
                self.position[1] -= 1
                moved = True
            # If vertical failed (wall), try horizontal
            if not moved:
                if dx > 0 and not maze.is_wall(ex + 1, ey):
                    self.position[0] += 1
                elif dx < 0 and not maze.is_wall(ex - 1, ey):
                    self.position[0] -= 1

    def add_enemies(self, grid):
        """Randomly add enemies ('E') to the maze."""
        if self.seed is not None:
            random.seed(self.seed)
        
        spawn_points = []
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                if tile == '0': # Changed from 'S' to '0' to ensure valid spawns
                    spawn_points.append((x, y))
        
        new_grid = [list(row) for row in grid]
        if spawn_points:
            # Pick a random spawn that isn't too close to 0,0 (Player start)
            valid_spawns = [p for p in spawn_points if p[0] > 5 and p[1] > 5]
            if not valid_spawns: valid_spawns = spawn_points

            enemy_x, enemy_y = random.choice(valid_spawns)
            new_grid[enemy_y][enemy_x] = 'E'
            self.position = [enemy_x, enemy_y]
        
        return [''.join(row) for row in new_grid]
    
    def enemy_pos(self):
        return (self.position[0], self.position[1])

    def draw(self, screen):
        rect = pygame.Rect(self.position[0] * TILE_SIZE, self.position[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        screen.blit(self.image, rect)