    ### FIX ME ###
    # We need to creates some kind of method to randomly generate mazes
    # or at least load different maze layouts from files.

import random

class MazeGenerator:
    def __init__(self, width, height):
        self.width = width if width % 2 == 1 else width + 1   # must be odd
        self.height = height if height % 2 == 1 else height + 1
        self.maze = [["1" for _ in range(self.width)] for _ in range(self.height)]

    def generate(self):
        """Generates a maze using recursive backtracking"""
        start_x, start_y = 1, 1
        self.maze[start_y][start_x] = "0"
        stack = [(start_x, start_y)]

        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]

        while stack:
            x, y = stack[-1]
            neighbors = []

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 1 <= nx < self.width - 1 and 1 <= ny < self.height - 1:
                    if self.maze[ny][nx] == "1":
                        neighbors.append((nx, ny, dx, dy))

            if neighbors:
                nx, ny, dx, dy = random.choice(neighbors)
                self.maze[y + dy // 2][x + dx // 2] = "0"  # remove wall
                self.maze[ny][nx] = "0"                    # mark new cell
                stack.append((nx, ny))
            else:
                stack.pop()

        # Optionally add loops (extra openings)
        self._add_loops(loops=10)
        self._add_exit()
        return self.maze

    def _add_loops(self, loops=10):
        """Randomly remove some walls to make loops (like Pac-Man)"""
        for _ in range(loops):
            x = random.randrange(1, self.width - 1)
            y = random.randrange(1, self.height - 1)
            if self.maze[y][x] == "1":
                self.maze[y][x] = "0"

    def _add_exit(self):
        """Add an exit (E) to one random border cell"""
        edges = []
        for x in range(self.width):
            edges.append((x, 0))
            edges.append((x, self.height - 1))
        for y in range(self.height):
            edges.append((0, y))
            edges.append((self.width - 1, y))

        ex, ey = random.choice(edges)
        self.maze[ey][ex] = "E"
