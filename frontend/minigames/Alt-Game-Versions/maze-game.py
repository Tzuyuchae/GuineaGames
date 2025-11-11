import pygame, sys

"""
1 = wall
0 = path
P = player start
E = exit
"""

# Initialize pygame
pygame.init()

# Colors
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Maze layout 
maze = [ 
    "11111111111", 
    "1P0000000E1",
    "10111111101",
    "10000000001",
    "11111111111",
]

# Constants
TILE_SIZE = 50
ROWS = len(maze)
COLS = len(maze[0])
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game")

# Player position
for row_idx, row in enumerate(maze):
    for col_idx, tile in enumerate(row):
        if tile == 'P':
            player_pos = [col_idx, row_idx]


# Game loop
clock = pygame.time.Clock()
running = True 

while running:
    screen.fill(BLACK)

    # Draw maze 
    for row_idx, row in enumerate(maze):
        for col_idx, tile in enumerate(row):
            x = col_idx * TILE_SIZE
            y = row_idx * TILE_SIZE
            if tile == '1':
                pygame.draw.rect(screen, BLUE, (x, y, TILE_SIZE, TILE_SIZE))
            elif tile == 'E':
                pygame.draw.rect(screen, GREEN, (x, y, TILE_SIZE, TILE_SIZE))

    # Draw player
    pygame.draw.rect(screen, RED, (player_pos[0] * TILE_SIZE, player_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            new_pos = player_pos.copy()
            if event.key == pygame.K_UP:
                new_pos[1] -= 1
            elif event.key == pygame.K_DOWN:
                new_pos[1] += 1
            elif event.key == pygame.K_LEFT:
                new_pos[0] -= 1
            elif event.key == pygame.K_RIGHT:
                new_pos[0] += 1

            # Check for valid move
            if maze[new_pos[1]][new_pos[0]] != '1':
                player_pos = new_pos

            # Check for win condition
            if maze[player_pos[1]][player_pos[0]] == 'E':
                print("You Win!")
                running = False

    pygame.display.flip()
    clock.tick(10)

pygame.quit()
sys.exit()