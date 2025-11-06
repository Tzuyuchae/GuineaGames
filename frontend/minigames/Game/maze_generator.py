# maze_generation.py
import random
import os

# Define file path for maps for future use
base_path = os.path.dirname(__file__)
assets_path = os.path.join(base_path, "../assets/layouts/")

class MazeGenerator:
    """
    Generates a maze layout either from a hardcoded ASCII design
    or (in future versions) from procedural generation.
    """

    def __init__(self, ascii_maze=None, fruit_chance=0.1, seed=None):
        self.ascii_maze = ascii_maze or self.default_maze()
        self.fruit_chance = fruit_chance
        self.seed = seed
        self.mapping = {
            '|': '1',  # Wall
            '.': '0',  # Walkable path
            '_': '3',  # Out of bounds
            '-': 'X',  # Enemy spawn exit
            ' ': '0',  # Empty space
            '*': 'S',  # Enemy spawns
            '\n': '\n' # Newline
        }

    def default_maze(self):
        """Returns a default Pac-Man-style ASCII maze."""
        return """
||||||||||||||||||||||||||||
|............||............|
|.||||.|||||.||.|||||.||||.|
|.|__|.|___|.||.|___|.|__|.|
|.||||.|||||.||.|||||.||||.|
|..........................|
|.||||.||.||||||||.||.||||.|
|.||||.||.||||||||.||.||||.|
|......||....||....||......|
||||||.|||||.||.|||||.||||||
_____|.|||||.||.|||||.|_____
_____|.||..........||.|_____
_____|.||.|||--|||.||.|_____
||||||.||.|******|.||.||||||
..........|******|..........
||||||.||.|******|.||.||||||
_____|.||.||||||||.||.|_____
_____|.||..........||.|_____
_____|.||.||||||||.||.|_____
||||||.||.||||||||.||.||||||
|............||............|
|.||||.|||||.||.|||||.||||.|
|.||||.|||||.||.|||||.||||.|
|...||................||...|
|||.||.||.||||||||.||.||.|||
|||.||.||.||||||||.||.||.|||
|......||....||....||......|
|.||||||||||.||.||||||||||.|
|.||||||||||.||.||||||||||.|
|..........................|
||||||||||||||||||||||||||||
"""

    def random_map_choice(self):
        pass

    def convert_ascii(self):
        """Converts ASCII maze symbols into numerical grid representation."""
        converted = ''.join(self.mapping.get(ch, ch) for ch in self.ascii_maze)
        # Split into lines and remove any empty ones
        grid = [row for row in converted.strip().splitlines() if row]
        return grid

    def add_fruits(self, grid):
        """Randomly add fruits ('2') to the maze."""
        if self.seed is not None:
            random.seed(self.seed)

        new_grid = []
        for row in grid:
            new_row = ''
            for tile in row:
                if tile == '0' and random.random() < self.fruit_chance:
                    new_row += '2'  # fruit
                else:
                    new_row += tile
            new_grid.append(new_row)
        return new_grid

    def add_enemies(self, grid):
        """Randomly add enemies ('E') to the maze."""
        if self.seed is not None:
            random.seed(self.seed)
        
        # Find all spawn points
        spawn_points = []
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                if tile == 'S':
                    spawn_points.append((x, y))
        
        # If there are spawn points, randomly select one for the enemy
        new_grid = [list(row) for row in grid]  # Convert strings to lists for easier modification
        if spawn_points:
            enemy_x, enemy_y = random.choice(spawn_points)
            new_grid[enemy_y][enemy_x] = 'E'
        
        # Convert back to strings
        return [''.join(row) for row in new_grid]

    def generate(self):
        """
        Full generation process:
        1. Convert ASCII → numeric grid
        2. Add random fruits
        3. Return final grid
        """
        base_grid = self.convert_ascii()
        fruit_grid = self.add_fruits(base_grid)
        final_grid = self.add_enemies(fruit_grid)
        return final_grid


# Debug/Test Run
if __name__ == "__main__":
    generator = MazeGenerator(fruit_chance=0.1, seed=42)
    maze = generator.generate()

    for row in maze:
        print(f'"{row}",')
