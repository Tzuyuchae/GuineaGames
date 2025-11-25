import pygame
import sys
import os
import ctypes  # Needed for the screen resolution fix

# --- 1. FIX WINDOWS SCALING (DPI AWARENESS) ---
try:
    ctypes.windll.user32.SetProcessDPIAware()
except AttributeError:
    pass

# --- 2. INITIALIZE PYGAME ---
pygame.init()

# Setup Screen Dimensions
screen_width = 672
screen_height = 864
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Guinea Games")
clock = pygame.time.Clock()
FPS = 60

# --- 3. IMPORT CUSTOM MODULES ---
import homescreen
import title
import store_page
from store_module import PlayerInventory
from minigame.minigame_page import MinigamePage

# Make sure breeding.py exists in your folder!
import breeding 
# import details_page # Keep this commented until you have the file

# --- 4. INITIALIZE PAGES & DATA ---

# Initialize Homescreen
try:
    # FIX: Pass the actual screen width/height so it scales correctly
    homescreen.homescreen_init(screen_width, screen_height)
except AttributeError:
    pass

# Initialize Store
store_page.store_init()

# Initialize Inventory
player_inventory = PlayerInventory(coins=500)

# Initialize Minigame Manager
minigame_manager = MinigamePage(user_id=1)

# --- 5. MAIN GAME LOOP ---
currentmenu = "title"
running = True

while running:
    # A. Event Handling
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # B. State Machine (Update & Draw)
    
    # --- TITLE SCREEN ---
    if currentmenu == 'title':
        new_state = title.title_update(events)
        title.title_draw(screen)
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
        new_state = breeding.breeding_update(events)
        breeding.breeding_draw(screen)
        
        if new_state == 'homescreen':
            currentmenu = 'homescreen'

    # --- MINIGAME (Selector + Maze) ---
    elif currentmenu == 'minigame':
        result = minigame_manager.update(events)
        minigame_manager.draw(screen)
        
        if result == 'homescreen':
            currentmenu = 'homescreen'
            # Force Reset Screen Size (fixes minigame resize issues if any)
            screen = pygame.display.set_mode((screen_width, screen_height))

    # --- C. Update Display ---
    pygame.display.flip()
    clock.tick(FPS)

# Quit
pygame.quit()
sys.exit()