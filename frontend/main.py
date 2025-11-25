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
from breeding import GuineaPig 
from settings_popup import SettingsPopup # Import the settings popup
import help_page # Import the help page

# --- 4. INITIALIZE PAGES & DATA ---
try:
    homescreen.homescreen_init(screen_width, screen_height)
except AttributeError:
    pass

store_page.store_init()
player_inventory = PlayerInventory(coins=500)

# Initialize Global Settings Popup
settings_popup = SettingsPopup(screen_width, screen_height)
settings_active = False # Flag to check if settings are open
previous_menu = 'homescreen' # Logic to return to previous screen from help

# --- CREATE STARTER PIGS ---
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
    
    # --- GLOBAL EVENT HANDLING ---
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            
        # Global Toggle for Settings Popup
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # If we are in the title screen, we might not want the popup, 
                # but typically games allow it. Let's allow it everywhere except title if desired.
                # For now, allow everywhere.
                if currentmenu != 'title':
                    settings_active = not settings_active
                    settings_popup.active = settings_active
                    # If we just closed it, ensure active is False
                    if not settings_active:
                        settings_popup.active = False

        # If settings are active, handle interactions inside the popup
        if settings_active:
            action = settings_popup.handle_event(event)
            if action == 'quit_game':
                running = False
            elif action == 'help':
                previous_menu = currentmenu # Remember where we were
                currentmenu = 'help'
                settings_active = False # Close popup to show full screen help
                settings_popup.active = False

    # --- STATE UPDATES & DRAWING ---
    
    # If settings are active, we generally PAUSE the underlying game loop
    # So we simply DRAW the current state, then DRAW the settings overlay.
    # We DO NOT call the update functions of the underlying state.
    
    if currentmenu == 'title':
        # Title usually handles its own updates, and maybe we don't want settings popup here?
        # If you want settings on title, handle it. If not, just run normally.
        # Assuming we run normally on title, and settings only available inside game.
        if not settings_active:
            new_state = title.title_update(events)
            if new_state:
                currentmenu = new_state
        title.title_draw(screen)

    elif currentmenu == 'homescreen':
        if not settings_active:
            new_state = homescreen.homescreen_update(events)
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
        homescreen.homescreen_draw(screen, player_inventory)

    elif currentmenu == 'store':
        if not settings_active:
            new_state = store_page.store_update(events, player_inventory)
            if new_state == 'homescreen':
                currentmenu = 'homescreen'
        store_page.store_draw(screen, player_inventory)

    elif currentmenu == 'breeding':
        if not settings_active:
            new_state = breeding.breeding_update(events, player_inventory)
            if new_state == 'homescreen':
                currentmenu = 'homescreen'
        breeding.breeding_draw(screen, player_inventory)

    elif currentmenu == 'minigame':
        # Minigame might have its own internal pause, but the global settings 
        # basically overrides it by stopping updates.
        if not settings_active:
            result = minigame_manager.update(events)
            if result == 'homescreen':
                currentmenu = 'homescreen'
                screen = pygame.display.set_mode((screen_width, screen_height))
        minigame_manager.draw(screen)

    elif currentmenu == 'help':
        # Help page logic
        res = help_page.help_update(events)
        help_page.help_draw(screen)
        
        # When returning from help, we go back to the previous menu 
        # AND reopen the settings popup (since we came from there)
        if res == 'settings':
            currentmenu = previous_menu
            settings_active = True
            settings_popup.active = True

    # --- DRAW SETTINGS OVERLAY ---
    if settings_active and currentmenu != 'title' and currentmenu != 'help':
        settings_popup.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()