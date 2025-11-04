    ### FIX ME ###
    # We need to creates some kind of method to randomly generate mazes
    # or at least load different maze layouts from files.

import random
import pygame 

class MazeGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = self.generate_maze()

    def generate_maze(self):
        # Simple maze generation logic (placeholder)
        maze = [['1' for _ in range(self.width)] for _ in range(self.height)]
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                if random.choice([0, 1]) == 0:
                    maze[y][x] = '0'  # Path
        maze[1][1] = 'P'  # Player start
        maze[self.height-2][self.width-2] = 'E'  # Exit
        return maze

    def get_maze(self):
        return self.maze