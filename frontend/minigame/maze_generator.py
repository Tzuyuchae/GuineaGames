import random
import os

# Define file path for maps relative to this script
base_path = os.path.dirname(os.path.abspath(__file__))
# You can change "maze_layouts" to "../assets/layouts/" if you move the folder later
assets_path = os.path.join(base_path, "maze_layouts")

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
        
        # Mappings from ASCII characters to Game Grid numbers/codes
        self.mapping = {
            '|': '1',  # Wall
            '.': '0',  # Walkable path
            '_': '3',  # Out of bounds/Gate
            '-': 'X',  # Enemy spawn exit
            ' ': '0',  # Empty space (treated as path)
            '*': 'S',  # Enemy spawns
            '\n': '\n' # Preserve newlines for splitting later
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
        """
        Lists all files in the assets/layouts directory, 
        randomly selects one, and reads its contents.
        """
        try:
            # Check if directory exists first
            if not os.path.exists(assets_path):
                print(f"Warning: Directory not found at '{assets_path}'. Using default maze.")
                return self.default_layout

            # Get all files in the layouts directory (ignoring hidden files)
            map_files = [
                f for f in os.listdir(assets_path) 
                if os.path.isfile(os.path.join(assets_path, f)) and not f.startswith('.')
            ]
            
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

        except Exception as e:
            print(f"Error loading map: {e}. Using default maze.")
            return self.default_layout

    def convert_ascii(self):
        """Converts ASCII maze symbols into numerical grid representation."""
        # Convert chars based on mapping, default to original char if not found
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
            new_row_chars = []
            for tile in row:
                # If tile is a path ('0') check chance to become fruit ('2')
                if tile == '0' and random.random() < self.fruit_chance:
                    new_row_chars.append('2')  # fruit
                else:
                    new_row_chars.append(tile)
            new_grid.append("".join(new_row_chars))
        return new_grid

    def generate(self, use_random_map=False):
        """
        Full generation process:
        1. Get ASCII layout (default or random)
        2. Convert ASCII -> numeric grid
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
    
    # Print first 5 rows just to check
    for row in maze[:5]:
        print(f'"{row}",')
    print("... (truncated) ...")

    # Test 2: Generate a random maze
    print("\n--- GENERATING RANDOM MAZE ---")
    
    # Create a dummy directory and file just so the test works immediately
    if not os.path.exists(assets_path):
        try:
            os.makedirs(assets_path)
            dummy_map_path = os.path.join(assets_path, "test_map.txt")
            with open(dummy_map_path, "w") as f:
                f.write("|||||\n|...|\n|||||")
            print(f"(Created temporary test map at {dummy_map_path})")
        except OSError:
            pass

    random_generator = MazeGenerator(fruit_chance=0.5) # Higher chance to see fruits
    random_maze = random_generator.generate(use_random_map=True) 
    for row in random_maze:
        print(f'"{row}",')