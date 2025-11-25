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
        
        # Load Image
        base_path = os.path.dirname(os.path.abspath(__file__))
        # FIX: Pointing to "frontend/game sprites/mini-game"
        image_path = os.path.join(base_path, "../../frontend/Global Assets/Sprites/Mini-game/MG_Dragon.png")

        
        try:
            raw_image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(raw_image, (TILE_SIZE, TILE_SIZE))
        except (FileNotFoundError, pygame.error):
            # Fallback if image not found
            print(f"Warning: Enemy image not found at {image_path}")
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(self.color)
            
        self.rect = self.image.get_rect()
        
        # Movement timer (enemies move slower than game FPS)
        self.move_timer = 0
        self.move_delay = 20  # Move every 20 frames

    def add_enemies(self, grid):
        """
        Randomly places the enemy on an empty spot ('0').
        CRITICAL: Must return the modified grid!
        """
        if self.seed is not None:
            random.seed(self.seed + 1) # Use different seed offset than player
            
        spawn_points = []
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                if tile == '0':
                    spawn_points.append((x, y))
        
        # Create a copy to modify
        new_grid = [list(row) for row in grid]
        
        if spawn_points:
            ex, ey = random.choice(spawn_points)
            new_grid[ey][ex] = 'E'
            self.pos_x = ex
            self.pos_y = ey
            
        return [''.join(row) for row in new_grid]

    def move_towards_player(self, player_pos, maze):
        """Simple AI to move towards the player."""
        self.move_timer += 1
        if self.move_timer < self.move_delay:
            return

        self.move_timer = 0
        px, py = player_pos
        ex, ey = self.pos_x, self.pos_y
        
        # Simple logic: try to close the gap on X, then Y
        potential_moves = []
        
        if ex < px: potential_moves.append((1, 0))  # Right
        if ex > px: potential_moves.append((-1, 0)) # Left
        if ey < py: potential_moves.append((0, 1))  # Down
        if ey > py: potential_moves.append((0, -1)) # Up
        
        # Shuffle to make it less predictable if stuck
        random.shuffle(potential_moves)
        
        for dx, dy in potential_moves:
            if not maze.is_wall(ex + dx, ey + dy):
                self.pos_x += dx
                self.pos_y += dy
                return # Moved successfully

    def enemy_pos(self):
        return (self.pos_x, self.pos_y)

    def draw(self, screen):
        pixel_x = self.pos_x * TILE_SIZE
        pixel_y = self.pos_y * TILE_SIZE
        self.rect.topleft = (pixel_x, pixel_y)
        screen.blit(self.image, self.rect)