import pygame
pygame.init()

from guineapig import Guineapig
from title import title_update, title_draw
from homescreen import homescreen_init, homescreen_update, homescreen_draw

# --- NEW IMPORTS ---
from minigame.game import Game 
import store_page                 # <--- Just import the file name
from store_module import PlayerInventory

# Original screen size
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Guinea Games")

clock = pygame.time.Clock()
FPS = 60
current_page = "title"

# --- INITIALIZE PERSISTENT DATA ---
# We create the inventory HERE so it survives between page changes
# Giving the player 500 coins to start so you can test buying things
player_inventory = PlayerInventory(coins=500) 

# Initialize pages
homescreen_init()
store_page.store_init() # Init fonts for store

# Add a variable to hold the minigame instance
active_minigame = None

running = True 
while running:
    events = pygame.event.get()
    
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # --- TITLE ---
    if current_page == "title":
        screen = pygame.display.set_mode((screen_width, screen_height))
        next_page = title_update(events)
        title_draw(screen)
        if next_page == "homescreen":
            current_page = "homescreen"

    # --- HOMESCREEN ---
    elif current_page == "homescreen":
        screen = pygame.display.set_mode((screen_width, screen_height))
        
        next_page = homescreen_update(events)
        homescreen_draw(screen)
        
        # Draw HUD using real inventory data
        # (Optional: You can eventually link the homescreen sidebar to player_inventory.coins)
        
        if next_page == "mini_games":
            print("Starting minigame!")
            active_minigame = Game()
            screen = pygame.display.set_mode((active_minigame.maze.width, active_minigame.maze.height))
            current_page = "minigame"
            
        elif next_page == "store": # <--- THIS CATCHES THE CLICK FROM HOMESCREEN
            print("Going to Store...")
            current_page = "store"
            
        elif next_page:
            print(f"Navigating to {next_page}")

    # --- MINIGAME ---
    elif current_page == "minigame":
        if active_minigame:
            next_page = active_minigame.update(events)
            active_minigame.draw(screen)
            
            if next_page == "homescreen":
                current_page = "homescreen"
                active_minigame = None 
                screen = pygame.display.set_mode((screen_width, screen_height))
        else:
            current_page = "homescreen"
            screen = pygame.display.set_mode((screen_width, screen_height))

    # --- NEW: STORE PAGE ---
    elif current_page == "store":
        # 1. Update
        # We pass 'player_inventory' so we can spend coins
        next_page = store_page.store_update(events, player_inventory)
        
        # 2. Draw
        store_page.store_draw(screen, player_inventory)
        
        # 3. Navigation
        if next_page == "homescreen":
            current_page = "homescreen"

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()