import pygame
import sys
import os
import ctypes

# --- 1. FIX WINDOWS SCALING ---
try:
    ctypes.windll.user32.SetProcessDPIAware()
except AttributeError:
    pass

# --- 2. INITIALIZE PYGAME ---
pygame.init()

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
import breeding 
from breeding import GuineaPig # Import the class to create starters

# --- 4. INITIALIZE PAGES & DATA ---
try:
    homescreen.homescreen_init(screen_width, screen_height)
except AttributeError:
    pass

store_page.store_init()
player_inventory = PlayerInventory(coins=500)

# --- CREATE STARTER PIGS ---
# This ensures every new game starts with 2 random pigs
starter_1 = GuineaPig("Starter Alpha")
starter_2 = GuineaPig("Starter Beta")
player_inventory.owned_pigs.extend([starter_1, starter_2])
print(f"Initialized with 2 starter pigs: {starter_1.name}, {starter_2.name}")

minigame_manager = MinigamePage(user_id=1, player_inventory=player_inventory)

# --- 5. MAIN GAME LOOP ---
currentmenu = "title"
running = True

while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    if currentmenu == 'title':
        new_state = title.title_update(events)
        title.title_draw(screen)
        if new_state:
            currentmenu = new_state

    elif currentmenu == 'homescreen':
        new_state = homescreen.homescreen_update(events)
        homescreen.homescreen_draw(screen, player_inventory)
        
        if new_state:
            if new_state == 'mini_games' or new_state == 'gameplay':
                currentmenu = 'minigame'
            elif new_state == 'store':
                currentmenu = 'store'
            elif new_state == 'breeding':
                currentmenu = 'breeding'
            elif new_state == 'details':
                print("Details page coming soon.")
            else:
                currentmenu = new_state

    elif currentmenu == 'store':
        new_state = store_page.store_update(events, player_inventory)
        store_page.store_draw(screen, player_inventory)
        if new_state == 'homescreen':
            currentmenu = 'homescreen'

    elif currentmenu == 'breeding':
        # --- FIX: Pass player_inventory to breeding functions ---
        new_state = breeding.breeding_update(events, player_inventory)
        breeding.breeding_draw(screen, player_inventory)
        if new_state == 'homescreen':
            currentmenu = 'homescreen'

    elif currentmenu == 'minigame':
        result = minigame_manager.update(events)
        minigame_manager.draw(screen)
        if result == 'homescreen':
            currentmenu = 'homescreen'
            screen = pygame.display.set_mode((screen_width, screen_height))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()