# For now we have the original pac-man maze hardcoded here.
# Below is a conversion script to help convert an ASCII maze into the format we need.

import random

maze_ascii = """
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
||||||.||.|______|.||.||||||
..........|______|..........
||||||.||.|______|.||.||||||
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

# Conversion dictionary
mapping = {
    '|': '1',
    '.': '0',
    '_': '0',   # tunnels or empty space treated as walkable
    ' ': '0',
    '\n': '\n'
}

# Convert maze
converted = ''.join(mapping.get(ch, ch) for ch in maze_ascii)

# Split into rows and remove empty lines
maze_grid = [row for row in converted.strip().splitlines() if row]

# Add random fruits everywhere there's a '0' with a small probability
random.seed(42)  # For reproducibility
for r in range(len(maze_grid)):
    new_row = ''
    for c in range(len(maze_grid[r])):
        if maze_grid[r][c] == '0' and random.random() < 0.1:  # 10% chance
            new_row += '2'  # '2' represents a fruit
        else:
            new_row += maze_grid[r][c]
    maze_grid[r] = new_row

# Print result
for row in maze_grid:
    print(f'"{row}",')
