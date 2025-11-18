import random
import os

# Define file path for maps for future use
base_path = os.path.dirname(__file__)
assets_path = os.path.join(base_path, "../assets/layouts/")

class MazeGenerator:
    """
    Generates a maze layout either from a hardcoded ASCII design
    or from a randomly selected file.
    """

    def __init__(self, ascii_maze=None, fruit_chance=0.1, seed=None):
        self.default_layout = ascii_maze or self.default_maze()
        self.ascii_maze = self.default_layout
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
        # ... (your default maze string is fine) ...
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
        """
        Lists all files in the assets/layouts directory, 
        randomly selects one, and reads its contents.
        """
        try:
            # Get all files in the layouts directory
            map_files = [f for f in os.listdir(assets_path) if os.path.isfile(os.path.join(assets_path, f))]
            
            if not map_files:
                print(f"Warning: No map files found in '{assets_path}'. Using default maze.")
                return self.default_layout

            # Randomly select one
            chosen_map_file = random.choice(map_files)
            map_path = os.path.join(assets_path, chosen_map_file)
            print(f"Loading random map: {chosen_map_file}")

            # Read and return the content
            with open(map_path, 'r') as f:
                return f.read()

        except FileNotFoundError:
            print(f"Error: 'assets/layouts/' directory not found at '{assets_path}'. Using default maze.")
            return self.default_layout
        except Exception as e:
            print(f"Error loading map: {e}. Using default maze.")
            return self.default_layout


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

    def generate(self, use_random_map=False):
        """
        Full generation process:
        1. Get ASCII layout (default or random)
        2. Convert ASCII → numeric grid
        3. Add random fruits
        4. Return final grid
        """
        # Step 1: Get ASCII layout
        if use_random_map:
            self.ascii_maze = self.random_map_choice()
        else:
            self.ascii_maze = self.default_layout
            
        # Step 2: Convert
        base_grid = self.convert_ascii()
        
        # Step 3: Add fruits
        fruit_grid = self.add_fruits(base_grid)
        
        # Step 4: Return
        return fruit_grid


# Debug/Test Run
if __name__ == "__main__":
    # Test 1: Generate the default maze
    print("--- GENERATING DEFAULT MAZE ---")
    generator = MazeGenerator(fruit_chance=0.1, seed=42)
    maze = generator.generate(use_random_map=False)
    for row in maze:
        print(f'"{row}",')

    # Test 2: Generate a random maze (assuming you have files in 'assets/layouts/')
    print("\n--- GENERATING RANDOM MAZE ---")
    random_generator = MazeGenerator(fruit_chance=0.1)
    # This will now call your random_map_choice function
    random_maze = random_generator.generate(use_random_map=True) 
    for row in random_maze:
        print(f'"{row}",')