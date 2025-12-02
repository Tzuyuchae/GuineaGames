import session  # backend/player session state

import pygame
pygame.init()

from title import title_update, title_draw
from homescreen import homescreen_init, homescreen_update, homescreen_draw

# --- NEW IMPORTS ---
from minigame.game import Game
from minigame.guinea_pig_selector import GuineaPigSelector
import store_page                 # store page UI
from store_module import PlayerInventory


screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Guinea Games")

clock = pygame.time.Clock()
FPS = 60

# Initialize backend session (connect to API, load/create user, load pets)
session.init_session()

current_page = "title"

# --- INITIALIZE PERSISTENT DATA (BACKED BY API WHEN AVAILABLE) ---
if session.api_available and session.current_user:
    # Use the logged-in user's actual balance + pets from the backend.
    player_inventory = PlayerInventory(
        coins=session.current_user.get("balance", 0)
    )
    # Backend returns a list of pet dicts; store them so the UI can use them.
    player_inventory.owned_pigs = list(session.user_pets)
else:
    # Offline / fallback mode – same behavior as before
    player_inventory = PlayerInventory(coins=500)
    player_inventory.owned_pigs = []

homescreen_init(screen_width, screen_height)
store_page.store_init()



# Add a variable to hold the minigame instance
active_minigame = None
guinea_pig_selector = None


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
        # Pass the live inventory so the homescreen can show real pets/coins
        homescreen_draw(screen, player_inventory)
        
        if next_page == "mini_games":
            print("Going to guinea pig selector!")

            # Choose the user ID from the current backend session
            user_id = 1
            if session.current_user is not None:
                user_id = session.current_user["id"]

            guinea_pig_selector = GuineaPigSelector(
                screen_width=screen_width,
                screen_height=screen_height,
                user_id=user_id,
            )
            current_page = "guinea_pig_selector"

        elif next_page == "store":  # <--- THIS CATCHES THE CLICK FROM HOMESCREEN
            print("Going to Store...")
            current_page = "store"
            
        elif next_page:
            print(f"Navigating to {next_page}")


    # --- GUINEA PIG SELECTOR ---
    elif current_page == "guinea_pig_selector":
        # If somehow not initialized, create it now
        if guinea_pig_selector is None:
            user_id = 1
            if session.current_user is not None:
                user_id = session.current_user["id"]

            guinea_pig_selector = GuineaPigSelector(
                screen_width=screen_width,
                screen_height=screen_height,
                user_id=user_id,
            )

        # Update selector (handle clicks, selections, scrolling)
        result = guinea_pig_selector.update(events)
        # Draw selector
        guinea_pig_selector.draw(screen)

        # Navigation based on selector result
        if result == "back":
            current_page = "homescreen"
            guinea_pig_selector = None

        elif isinstance(result, tuple) and result[0] == "start_game":
            selected_guinea_pig = result[1]
            print(f"Starting minigame with guinea pig: {selected_guinea_pig.get('name')}")

            active_minigame = Game(selected_guinea_pig=selected_guinea_pig)

            # Resize the window to match maze dimensions
            screen = pygame.display.set_mode(
                (active_minigame.maze.width, active_minigame.maze.height)
            )

            current_page = "minigame"
            guinea_pig_selector = None


    # --- MINIGAME ---
    elif current_page == "minigame":
        if active_minigame:
            next_page = active_minigame.update(events)
            active_minigame.draw(screen)
            
            if next_page == "homescreen":
                # We’re done with the minigame; go back to homescreen
                current_page = "homescreen"
                active_minigame = None 
                screen = pygame.display.set_mode((screen_width, screen_height))

                # 🔁 NEW: sync coins from backend into player_inventory
                if getattr(session, "api_available", False) and session.current_user is not None:
                    # session.refresh_user() was already called inside the minigame
                    new_balance = session.current_user.get("balance", player_inventory.coins)
                    player_inventory.coins = new_balance
                    print(f"[SYNC] Updated local coins to {player_inventory.coins} from backend balance.")
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