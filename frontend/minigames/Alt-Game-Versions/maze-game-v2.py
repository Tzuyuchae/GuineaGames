import pygame
import sys

# --- Constants ---
TILE_SIZE = 50
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


# --- Maze Class ---
class Maze:
    def __init__(self, layout):
        self.layout = layout
        self.rows = len(layout)
        self.cols = len(layout[0])
        self.width = self.cols * TILE_SIZE
        self.height = self.rows * TILE_SIZE

    def draw(self, screen):
        """Draws the maze (walls + exit)"""
        for y, row in enumerate(self.layout):
            for x, tile in enumerate(row):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if tile == "1":
                    pygame.draw.rect(screen, BLUE, rect)
                elif tile == "E":
                    pygame.draw.rect(screen, GREEN, rect)

    def is_walkable(self, x, y):
        """Check if the position is not a wall"""
        if 0 <= y < self.rows and 0 <= x < self.cols:
            return self.layout[y][x] != "1"
        return False


# --- Player Class ---
class Player:
    def __init__(self, x, y, color=RED):
        self.x = x
        self.y = y
        self.color = color

    def move(self, dx, dy, maze):
        """Move the player with collision checking"""
        new_x = self.x + dx
        new_y = self.y + dy

        if maze.is_walkable(new_x, new_y):
            self.x, self.y = new_x, new_y

    def draw(self, screen):
        rect = pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, self.color, rect)


# --- Game Class ---
class Game:
    def __init__(self):
        pygame.init()

        # Maze layout
        self.maze_layout = [
            "1111111111",
            "1P000000E1",
            "1011111101",
            "1010000101",
            "1010110101",
            "1000100001",
            "1111111111"
        ]

        # Find player start position
        for y, row in enumerate(self.maze_layout):
            for x, tile in enumerate(row):
                if tile == "P":
                    self.player = Player(x, y)

        # Create maze
        self.maze = Maze(self.maze_layout)
        self.screen = pygame.display.set_mode((self.maze.width, self.maze.height))
        pygame.display.set_caption("OOP Maze Game")

        self.clock = pygame.time.Clock()
        self.running = True

    def handle_input(self):
        """Handle keyboard input"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move(-1, 0, self.maze)
        elif keys[pygame.K_RIGHT]:
            self.player.move(1, 0, self.maze)
        elif keys[pygame.K_UP]:
            self.player.move(0, -1, self.maze)
        elif keys[pygame.K_DOWN]:
            self.player.move(0, 1, self.maze)

    def check_win(self):
        """Check if player reached the exit"""
        if self.maze_layout[self.player.y][self.player.x] == "E":
            print("You reached the exit! 🎉")
            pygame.time.wait(1000)
            self.running = False

    def run(self):
        """Main game loop"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.handle_input()
            self.check_win()

            # Draw everything
            self.screen.fill(BLACK)
            self.maze.draw(self.screen)
            self.player.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


# --- Main ---
if __name__ == "__main__":
    game = Game()
    game.run()
