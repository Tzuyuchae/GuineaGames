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
    # --- THIS WAS THE FIX ---
    # We must pass screen_width and screen_height here now!
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

    # --- HOMESCREEN ---
    elif currentmenu == 'homescreen':
        new_state = homescreen.homescreen_update(events)
        homescreen.homescreen_draw(screen)
        
        if new_state:
            # Navigation Logic
            if new_state == 'mini_games' or new_state == 'gameplay':
                currentmenu = 'minigame'
            
            elif new_state == 'store':
                currentmenu = 'store'
            
            elif new_state == 'breeding':
                currentmenu = 'breeding'

            elif new_state == 'details':
                print("Details page coming soon.")
                # currentmenu = 'details'
                
            else:
                currentmenu = new_state

    # --- STORE PAGE ---
    elif currentmenu == 'store':
        new_state = store_page.store_update(events, player_inventory)
        store_page.store_draw(screen, player_inventory)
        
        if new_state == 'homescreen':
            currentmenu = 'homescreen'

    # --- BREEDING PAGE ---
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
            # Force Reset Screen Size (fixes minigame resize issues)
            screen = pygame.display.set_mode((screen_width, screen_height))

    # --- C. Update Display ---
    pygame.display.flip()
    clock.tick(FPS)

# Quit
pygame.quit()
sys.exit()