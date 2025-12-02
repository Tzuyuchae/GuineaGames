# frontend/main.py

import pygame
import sys

import session
from store_module import PlayerInventory
import homescreen
from homescreen import homescreen_init, homescreen_update, homescreen_draw
from title import title_update, title_draw
from store_page import store_draw, store_update, store_init
from minigame.game import Game as MiniGame
from minigame.guinea_pig_selector import GuineaPigSelector
import save_system


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Guinea Games")

    clock = pygame.time.Clock()

    # -------------------------------
    # INITIALIZATION
    # -------------------------------

    homescreen_init(1280, 720)
    store_init()

    session.init_session()
    save_data = save_system.load_save()

    # Set up inventory from backend if available
    if session.api_available and session.current_user:
        player_inventory = PlayerInventory(
            coins=session.current_user.get("balance", 0)
        )
        player_inventory.owned_pigs = list(session.user_pets)
    else:
        player_inventory = PlayerInventory(coins=500)
        player_inventory.owned_pigs = []

    # Restore food
    food_data = save_data.get("food", {})
    player_inventory.pellets = food_data.get("pellets", 0)
    player_inventory.water = food_data.get("water", 0)

    # Restore homescreen time
    if "game_time" in save_data:
        homescreen.game_time.update(save_data["game_time"])

    current_page = "title"
    current_selector = None
    miniggame_instance = None

    running = True

    # -------------------------------
    # MAIN LOOP
    # -------------------------------
    while running:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False

        next_page = None

        # ---------------------------------------
        # TITLE SCREEN
        # ---------------------------------------
        if current_page == "title":
            next_page = title_update(events)
            title_draw(screen)

        # ---------------------------------------
        # HOMESCREEN
        # ---------------------------------------
        elif current_page == "homescreen":
            result = homescreen_update(events)

            if result == "store":
                current_page = "store"

            elif result == "mini_games":
                # Move to guinea pig selector
                current_selector = GuineaPigSelector(
                    screen_width=1280,
                    screen_height=720,
                    user_id=session.current_user["id"] if session.current_user else 1,
                )
                current_page = "pig_selector"

            homescreen_draw(screen, player_inventory)

        # ---------------------------------------
        # STORE
        # ---------------------------------------
        elif current_page == "store":
            page_return = store_update(events, player_inventory)
            if page_return == "homescreen":
                current_page = "homescreen"

            store_draw(screen, player_inventory)

        # ---------------------------------------
        # GUINEA PIG SELECTOR SCREEN
        # ---------------------------------------
        elif current_page == "pig_selector":
            sel_result = current_selector.update(events)
            current_selector.draw(screen)

            if sel_result == "back":
                current_page = "homescreen"

            elif isinstance(sel_result, tuple) and sel_result[0] == "start_game":
                selected_pet = sel_result[1]
                minigame_instance = MiniGame(selected_pig=selected_pet)
                current_page = "mini_games"

        # ---------------------------------------
        # MINIGAME
        # ---------------------------------------
        elif current_page == "mini_games":
            page_return = minigame_instance.update(events)
            minigame_instance.draw(screen)

            if page_return == "homescreen":
                minigame_instance = None
                current_page = "homescreen"

        if next_page is not None:
            current_page = next_page

        pygame.display.flip()
        clock.tick(60)

    # -------------------------------
    # SAVE ON EXIT
    # -------------------------------
    save_system.save_game_time(save_data, homescreen.game_time)
    save_system.save_food(
        save_data,
        getattr(player_inventory, "pellets", 0),
        getattr(player_inventory, "water", 0)
    )
    save_system.save(save_data)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
