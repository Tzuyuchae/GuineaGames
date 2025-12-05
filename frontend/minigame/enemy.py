import pygame 
import random
import os
from collections import deque
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
        # 1. Throttle speed (Move every 15 frames instead of 20 to make them slightly scarier)
        self.move_timer += 1
        if self.move_timer < 15: return
        self.move_timer = 0

        # 2. Find the smart path
        next_step = self.bfs_pathfind(tuple(self.position), player_pos, maze)

        # 3. Move
        if next_step:
            self.position = list(next_step)

    def bfs_pathfind(self, start, goal, maze):
        """
        Calculates the shortest path using Breadth-First Search.
        Returns the (x, y) of the immediate next step to take.
        """
        queue = deque([start])
        came_from = {start: None}
        
        found = False

        while queue:
            current = queue.popleft()
            if current == goal:
                found = True
                break

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                next_node = (current[0] + dx, current[1] + dy)
                
                # --- CHANGE IS HERE ---
                # We add 'is_enemy=True' so the ghost can walk through the 'X' gate
                if not maze.is_wall(next_node[0], next_node[1], is_enemy=True):
                    if next_node not in came_from:
                        queue.append(next_node)
                        came_from[next_node] = current
        
        if not found:
            return None # Player is unreachable

        # Backtrack from goal to start to find the FIRST step
        current = goal
        path = []
        while current != start:
            path.append(current)
            current = came_from[current]
        
        # The path is in reverse (Goal -> ... -> Next Step -> Start)
        # We want the last element (which is the Next Step)
        if path:
            return path[-1]
        return None
    
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