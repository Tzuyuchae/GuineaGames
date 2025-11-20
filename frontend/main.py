import pygame
import sys
import os
import ctypes  # Needed for the screen resolution fix

# --- 1. FIX WINDOWS SCALING (DPI AWARENESS) ---
# This prevents the window from looking zoomed-in or cut off on Windows laptops
try:
    ctypes.windll.user32.SetProcessDPIAware()
except AttributeError:
    pass

# --- 2. INITIALIZE PYGAME ---
# This must happen BEFORE importing custom modules that use fonts/images
pygame.init()

# Setup Screen Dimensions
# These match your standard UI layout (Portrait mode)
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

# Note: These pages are placeholders until you create the files.
# import details_page
# import breeding

# --- 4. INITIALIZE PAGES & DATA ---

# Initialize Homescreen (loads assets)
try:
    homescreen.homescreen_init()
except AttributeError:
    pass

# Initialize Store (loads fonts)
store_page.store_init()

# Create Persistent Player Inventory
# We create it here so coins/items are saved while switching screens
player_inventory = PlayerInventory(coins=500)

# Initialize Minigame Manager
# This handles the transition between the Pet Selector and the Maze
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
            
            elif new_state == 'details':
                print("Details page coming soon.")
                # currentmenu = 'details' # Uncomment when file exists
                
            elif new_state == 'breeding':
                print("Breeding page coming soon.")
                # currentmenu = 'breeding' # Uncomment when file exists
                
            else:
                currentmenu = new_state

    # --- STORE PAGE ---
    elif currentmenu == 'store':
        # Update: We pass 'player_inventory' so the user can spend coins
        new_state = store_page.store_update(events, player_inventory)
        
        # Draw: We pass 'player_inventory' to show current coin balance
        store_page.store_draw(screen, player_inventory)
        
        if new_state == 'homescreen':
            currentmenu = 'homescreen'

    # --- MINIGAME (Selector + Maze) ---
    elif currentmenu == 'minigame':
        # Delegate logic to the Minigame Manager
        result = minigame_manager.update(events)
        minigame_manager.draw(screen)
        
        # If the game ends or user clicks Back
        if result == 'homescreen':
            currentmenu = 'homescreen'
            # FORCE RESET SCREEN SIZE
            # The minigame might resize the window for the maze, so we reset it here.
            screen = pygame.display.set_mode((screen_width, screen_height))

    # --- C. Update Display ---
    pygame.display.flip()
    clock.tick(FPS)

# Quit
pygame.quit()
sys.exit()