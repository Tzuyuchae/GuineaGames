import pygame
import homescreen
import details_page
import breeding
import minigame.minigame_page
import title
import settings_page
import help_page
import random  # --- NEW ---

# --- NEW: Import all your game classes ---
from minigame.maze_generator import MazeGenerator
from minigame.maze import Maze
from minigame.player import Player
from minigame.enemy import Enemy
from minigame.fruits import Fruit
# from game import Game # We are building the logic here instead
# from guineapig import Guineapig

# Initialize Pygame
pygame.init()

# Set screen dimensions
screen_width = 672
screen_height = 864
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()

# This is your "state machine" variable
currentmenu = "title"


# --- NEW: Function to set up a new game ---
def start_new_game():
    """Initializes and returns all objects needed for a new game."""
    print("Starting new game...")
    # 1. Create generator (use a random seed for variety)
    generator = MazeGenerator(seed=random.randint(0, 9999))

    # 2. Create layout (this includes fruits)
    base_layout = generator.generate()

    # 3. Create player and add to layout
    player = Player()
    layout_with_player = player.add_player(base_layout)

    # 4. Create enemy and add to layout
    enemy = Enemy()
    final_layout = enemy.add_enemies(layout_with_player)

    # 5. Create the Maze object with the final layout
    maze = Maze(final_layout)

    # 6. Create the Fruit object (for drawing and checking)
    fruit_obj = Fruit()

    return maze, player, enemy, fruit_obj


# --- NEW: Initialize game objects ---
# We call this once to have them ready
maze, player, enemy, fruit_obj = start_new_game()


# --- THIS IS THE "MAIN" LOOP ---
running = True
while running:
    # 1. Handle Events
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # 2. Update Game Logic
    if currentmenu == 'homescreen':
        new_state = homescreen.menu_update(events)
        if new_state == 'gameplay':
            # --- NEW: Reset the game every time "PLAY" is clicked ---
            maze, player, enemy, fruit_obj = start_new_game()
            currentmenu = 'gameplay'
        elif new_state:
            currentmenu = new_state

    elif currentmenu == 'details':
        new_state = details_page.details_update(events)
        if new_state:
            currentmenu = new_state

    elif currentmenu == 'breeding':
        new_state = breeding.breeding_update(events)
        if new_state:
            currentmenu = new_state

    elif currentmenu == 'minigame':
        new_state = minigame_page.minigame_update(events)
        if new_state:
            currentmenu = new_state

    elif currentmenu == 'title':
        new_state = title.title_update(events)
        if new_state:
            currentmenu = new_state

    elif currentmenu == 'settings':
        new_state = settings_page.settings_update(events)
        if new_state:
            currentmenu = new_state

    elif currentmenu == 'help':
        new_state = help_page.help_update(events)
        if new_state:
            currentmenu = new_state

    # --- NEW: Added the 'gameplay' update logic ---
    elif currentmenu == 'gameplay':
        # Handle player movement
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.move(0, -1, maze)
                elif event.key == pygame.K_DOWN:
                    player.move(0, 1, maze)
                elif event.key == pygame.K_LEFT:
                    player.move(-1, 0, maze)
                elif event.key == pygame.K_RIGHT:
                    player.move(1, 0, maze)

        # Update enemy movement
        enemy.move_towards_player(player.player_pos(), maze)

        # Check for fruit collection
        # We must update maze.layout because if_collected() MODIFIES it
        maze.layout = fruit_obj.if_collected(player.player_pos(), maze.layout)

        # Check for win/loss conditions
        if player.player_pos() == enemy.enemy_pos():
            print("GAME OVER! You were caught!")
            currentmenu = 'homescreen'  # Go back to menu

        if fruit_obj.all_fruits_collected(maze.layout):
            print("YOU WIN! All fruits collected!")
            currentmenu = 'homescreen'  # Go back to menu

    # 3. Draw to Screen
    screen.fill((20, 20, 20))  # Fill with a dark grey background

    if currentmenu == 'homescreen':
        homescreen.menu_draw(screen)

    elif currentmenu == 'details':
        details_page.details_draw(screen)

    elif currentmenu == 'breeding':
        breeding.breeding_draw(screen)

    elif currentmenu == 'minigame':
        minigame_page.minigame_draw(screen)

    elif currentmenu == 'title':
        title.title_draw(screen)

    elif currentmenu == 'settings':
        settings_page.settings_draw(screen)

    elif currentmenu == 'help':
        help_page.help_draw(screen)

    # --- NEW: Added the 'gameplay' draw logic ---
    elif currentmenu == 'gameplay':
        maze.draw(screen)
        fruit_obj.draw(screen, maze.layout) # Draw fruits
        player.draw(screen)
        enemy.draw(screen)

    # 4. Update the Display
    pygame.display.flip()

    # 5. Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()