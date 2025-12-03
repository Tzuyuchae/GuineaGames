import os

# Screen settings
SCREEN_WIDTH = 672
SCREEN_HEIGHT = 864
FPS = 60

# Maze Settings
TILE_SIZE = 24  # 24px fits 672px perfectly (28 tiles wide)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GOLD = (255, 215, 0) 

# ASSET PATHS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "Global Assets", "Sprites")