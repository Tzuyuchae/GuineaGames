import pygame
import sys
import os

# ------------------------------------------------------------
# Correct package imports — uses minigame package for all deps
# ------------------------------------------------------------
from minigame.maze import Maze
from minigame.player import Player
from minigame.settings import *
from minigame.maze_generator import MazeGenerator
from minigame.enemy import Enemy
from minigame.fruits import Fruit

# Path to assets 
base_path = os.path.dirname(__file__)
assets_path = os.path.join(base_path, "../assets/audio/")


class Game:
    def __init__(self, selected_pig=None):
        pygame.init()
        pygame.mixer.init()

        # Selected guinea pig coming from the selector screen
        self.selected_pig = selected_pig
        self.selected_pig_name = (
            selected_pig.get("name", "Guinea Pig")
            if isinstance(selected_pig, dict)
            else "Guinea Pig"
        )

        self.running = True

        # ------------------------------------------------------------
        # Build maze layout and entities
        # ------------------------------------------------------------
        generator = MazeGenerator(fruit_chance=0.1, seed=42)
        self.PACMAN_MAZE = generator.generate()

        # Player
        self.player = Player(seed=42)
        self.PACMAN_MAZE = self.player.add_player(self.PACMAN_MAZE)

        # Enemy
        self.enemy = Enemy(seed=42)
        self.PACMAN_MAZE = self.enemy.add_enemies(self.PACMAN_MAZE)

        # Fruits
        self.fruit = Fruit(fruit_chance=0.1, seed=42)
        self.PACMAN_MAZE = self.fruit.add_fruits(self.PACMAN_MAZE)

        # Maze renderer / logic object
        self.maze = Maze(self.PACMAN_MAZE)

        # Off-screen surface to draw maze onto; we center this in the main window
        self.maze_surface = pygame.Surface((self.maze.width, self.maze.height))

        pygame.font.init()
        self.ui_font = pygame.font.Font(None, 32)

        # -----------------------
        # Movement / timing state
        # -----------------------
        self.move_dir = (0, 0)       # current direction as (dx, dy)
        self.move_speed = 0.0        # tiles per second
        self.move_progress = 0.0     # accumulated tile-progress this frame

        # Tunable movement parameters — improved acceleration & instant start
        self.BASE_SPEED = 1.6        # was 1.2 — starts moving immediately and a bit quicker
        self.MAX_SPEED = 5         # was 3.0 — slightly higher top speed
        self.ACCELERATION = 3.6      # was 2.0 — accelerates faster but still controlled


        # For dt calculation independent of main loop’s clock
        self.last_time_ms = pygame.time.get_ticks()

        self.clock = pygame.time.Clock()

    # ---------------------------------------------------------
    # INPUT & GAME LOGIC
    # ---------------------------------------------------------

    def handle_player_movement(self, dt):
        """
        Continuous movement with acceleration:
        - Hold a direction -> accelerate up to MAX_SPEED
        - Release / change direction -> speed resets to BASE_SPEED
        - Uses tile steps by calling player.move(dx, dy, maze)
        """
        keys = pygame.key.get_pressed()

        # Determine desired direction based on keys
        desired_dir = (0, 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            desired_dir = (0, -1)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            desired_dir = (0, 1)
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            desired_dir = (-1, 0)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            desired_dir = (1, 0)

        if desired_dir == (0, 0):
            # No movement key pressed: reset speed & progress
            self.move_dir = (0, 0)
            self.move_speed = 0.0
            self.move_progress = 0.0
            return

        # New direction selected
        if desired_dir != self.move_dir:
            self.move_dir = desired_dir
            # Start fresh at base speed
            self.move_speed = self.BASE_SPEED
            self.move_progress = 0.0
        else:
            # Same direction being held: accelerate
            self.move_speed = min(
                self.MAX_SPEED,
                self.move_speed + self.ACCELERATION * dt
            )

        # Convert speed (tiles/sec) into tiles this frame
        self.move_progress += self.move_speed * dt

        # For every whole tile worth of progress, move one step
        while self.move_progress >= 1.0:
            dx, dy = self.move_dir
            self.player.move(dx, dy, self.maze)
            self.move_progress -= 1.0

    def handle_loops(self):
        max_x = self.maze.cols - 1
        max_y = self.maze.rows - 1

        # Horizontal wrap tunnels
        if self.maze.is_loop(max_x, self.player.pos_y, self.PACMAN_MAZE) and self.player.pos_x == max_x:
            self.player.pos_x = 0
        elif self.maze.is_loop(0, self.player.pos_y, self.PACMAN_MAZE) and self.player.pos_x == 0:
            self.player.pos_x = max_x

        # Vertical wrap tunnels (if present)
        if self.maze.is_loop(self.player.pos_x, max_y, self.PACMAN_MAZE) and self.player.pos_y == max_y:
            self.player.pos_y = 0
        elif self.maze.is_loop(self.player.pos_x, 0, self.PACMAN_MAZE) and self.player.pos_y == 0:
            self.player.pos_y = max_y

    def check_lose(self):
        if self.player.player_pos() == self.enemy.enemy_pos():
            print("You Lose!")
            self.running = False

    def check_win(self):
        if self.fruit.all_fruits_collected(self.PACMAN_MAZE):
            print("You Win!")
            self.running = False

    # ---------------------------------------------------------
    # MAIN UPDATE LOOP (called by main.py)
    # ---------------------------------------------------------

    def update(self, events):
        # Compute dt based on wall-clock time, clamp to avoid crazy spikes
        now_ms = pygame.time.get_ticks()
        dt = (now_ms - self.last_time_ms) / 1000.0
        self.last_time_ms = now_ms
        dt = min(dt, 0.05)

        # ESC or Back button -> bail to homescreen
        surf = pygame.display.get_surface()
        back_rect = None
        if surf is not None:
            sw, sh = surf.get_size()
            back_rect = pygame.Rect(sw - 120, 20, 100, 30)

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and back_rect is not None:
                if back_rect.collidepoint(event.pos):
                    self.running = False

        # Continuous movement with acceleration while holding keys
        self.handle_player_movement(dt)

        # ✅ Enemy chases player using the Maze object (has is_wall)
        self.enemy.move_towards_player(
            (self.player.pos_x, self.player.pos_y),
            self.maze
        )

        # Game logic
        self.check_lose()
        self.check_win()
        self.handle_loops()

        if not self.running:
            return "homescreen"

        return None

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------

    def draw(self, screen):
        # Draw maze and entities to the off-screen maze surface
        self.maze_surface.fill(BLACK)
        self.maze.draw(self.maze_surface)
        self.player.draw(self.maze_surface)
        self.enemy.draw(self.maze_surface)

        # Fruit collision & redraw
        self.PACMAN_MAZE = self.fruit.if_collected(
            (self.player.pos_x, self.player.pos_y),
            self.PACMAN_MAZE
        )
        self.fruit.draw(self.maze_surface, self.PACMAN_MAZE)

        # Center maze_surface in the main window
        screen.fill(BLACK)
        sw, sh = screen.get_size()
        mw, mh = self.maze_surface.get_size()
        screen.blit(self.maze_surface, ((sw - mw) // 2, (sh - mh) // 2))

        # Show which pig is being used
        label = self.ui_font.render(
            f"Playing as: {self.selected_pig_name}",
            True,
            (255, 255, 255)
        )
        screen.blit(label, (20, 20))

        # Small BACK button in top-right, out of the maze’s way
        back_rect = pygame.Rect(sw - 120, 20, 100, 30)
        pygame.draw.rect(screen, (60, 60, 60), back_rect, border_radius=6)
        pygame.draw.rect(screen, (200, 200, 200), back_rect, 2, border_radius=6)
        back_text = self.ui_font.render("BACK", True, (255, 255, 255))
        bt_rect = back_text.get_rect(center=back_rect.center)
        screen.blit(back_text, bt_rect)

    # ---------------------------------------------------------
    # OPTIONAL STANDALONE RUNNER
    # ---------------------------------------------------------

    def run(self):
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Pac-Man Maze Game")

        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            result = self.update(events)
            self.draw(screen)

            if result == "homescreen":
                self.running = False

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
