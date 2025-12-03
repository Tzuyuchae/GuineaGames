import pygame
import sys
import ctypes  # Needed for the screen resolution fix

# --- 1. FIX WINDOWS SCALING (DPI AWARENESS) ---
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

# Simple UI font for buttons
ui_font = pygame.font.SysFont(None, 28)

# Back button for sub-pages (we only use it on breeding right now)
BACK_BUTTON_RECT = pygame.Rect(20, 20, 100, 40)

# --- 3. IMPORT CUSTOM MODULES ---
import homescreen
import title
import store_page
import breeding
from breeding import GuineaPig
from store_module import PlayerInventory
from minigame.minigame_page import MinigamePage
from settings_popup import SettingsPopup
import help_page
from api_client import api

# --- 4. BACKEND STATUS ---
backend_online = api.check_connection()
print(f"[Backend] Online: {backend_online}")

# --- 5. INITIALIZE PAGES & DATA ---

# Initialize homescreen layout
try:
    homescreen.homescreen_init(screen_width, screen_height)
except AttributeError:
    # If homescreen_init has a different signature, just ignore
    pass

# Initialize store (uses store_module.store_init internally)
store_page.store_init()

# Persistent inventory:
# - If save_data.json exists, it will load from there
# - Otherwise (and backend is on), it will try backend
# - Otherwise falls back to defaults
player_inventory = PlayerInventory(user_id=1)

# If a saved game_time exists from file, apply it to homescreen
if getattr(player_inventory, "saved_game_time", None):
    try:
        homescreen.game_time.update(player_inventory.saved_game_time)
        print("[Main] Restored game_time from save.")
    except Exception as e:
        print(f"[Main] Failed to apply saved game_time: {e}")

# Optional: give some starter coins if completely empty (fresh game, no save)
if player_inventory.coins == 0 and not getattr(player_inventory, "saved_game_time", None):
    player_inventory.add_coins(500)

# Settings popup
settings_popup = SettingsPopup(screen_width, screen_height)
settings_active = False
previous_menu = "homescreen"

# --- CREATE STARTER PIGS (ONLY IF NONE EXIST) ---
if not player_inventory.owned_pigs:
    starter_1 = GuineaPig("Starter Alpha")
    starter_2 = GuineaPig("Starter Beta")

    # Try to persist starters to backend so they become real pets
    if backend_online:
        for pig in (starter_1, starter_2):
            try:
                resp = api.create_pet(
                    owner_id=player_inventory.user_id,
                    name=pig.name,
                    species="guinea_pig",
                    color=pig.phenotype.get("coat_color", "Brown"),
                )
                pig.backend_id = resp.get("pet_id")
            except Exception as e:
                print(f"[Main] Failed to persist starter pig {pig.name}: {e}")

    player_inventory.owned_pigs.extend([starter_1, starter_2])

# Minigame manager gets both user_id and inventory for rewards, etc.
minigame_manager = MinigamePage(user_id=1, player_inventory=player_inventory)

# --- 6. MAIN GAME LOOP ---
currentmenu = "title"
running = True

while running:
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

        # ESC key toggles settings popup in most menus
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if currentmenu != "title":
                    settings_active = not settings_active
                    settings_popup.active = settings_active
                    if not settings_active:
                        settings_popup.active = False

        # If settings is active, route events to it
        if settings_active:
            action = settings_popup.handle_event(event)
            if action == "quit_game":
                running = False
            elif action == "help":
                previous_menu = currentmenu
                currentmenu = "help"
                settings_active = False
                settings_popup.active = False

        # --- HANDLE BREEDING BACK BUTTON CLICK HERE ---
        if (
            not settings_active
            and currentmenu == "breeding"
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):
            if BACK_BUTTON_RECT.collidepoint(event.pos):
                # Go back to homescreen when the back button is clicked
                currentmenu = "homescreen"

    # --- STATE UPDATES & DRAWING ---

    # TITLE SCREEN
    if currentmenu == "title":
        if not settings_active:
            new_state = title.title_update(events)
            if new_state:
                currentmenu = new_state
        title.title_draw(screen)

    # HOME SCREEN
    elif currentmenu == "homescreen":
        if not settings_active:
            new_state = homescreen.homescreen_update(events)
            if new_state:
                if new_state in ("mini_games", "gameplay"):
                    currentmenu = "minigame"
                elif new_state == "store":
                    currentmenu = "store"
                elif new_state == "breeding":
                    currentmenu = "breeding"
                elif new_state == "details":
                    print("Details page coming soon.")
                else:
                    currentmenu = new_state
        homescreen.homescreen_draw(screen, player_inventory)

    # STORE
    elif currentmenu == "store":
        if not settings_active:
            new_state = store_page.store_update(events, player_inventory)
            if new_state == "homescreen":
                currentmenu = "homescreen"
        store_page.store_draw(screen, player_inventory)

    # BREEDING
    elif currentmenu == "breeding":
        # Pass homescreen.game_time so breeding cooldown uses in-game time
        if not settings_active:
            new_state = breeding.breeding_update(
                events, player_inventory, homescreen.game_time
            )
            if new_state == "homescreen":
                currentmenu = "homescreen"

        breeding.breeding_draw(screen, player_inventory, homescreen.game_time)

        # --- DRAW BACK BUTTON OVER THE BREEDING UI ---
        pygame.draw.rect(screen, (200, 200, 200), BACK_BUTTON_RECT, border_radius=8)
        pygame.draw.rect(screen, (60, 60, 60), BACK_BUTTON_RECT, width=2, border_radius=8)
        back_text = ui_font.render("Back", True, (0, 0, 0))
        text_rect = back_text.get_rect(center=BACK_BUTTON_RECT.center)
        screen.blit(back_text, text_rect)

    # MINIGAME
    elif currentmenu == "minigame":
        if not settings_active:
            result = minigame_manager.update(events)
            if result == "homescreen":
                currentmenu = "homescreen"
                # Reset screen size in case minigame changed it
                screen = pygame.display.set_mode((screen_width, screen_height))
        minigame_manager.draw(screen)

    # HELP SCREEN
    elif currentmenu == "help":
        res = help_page.help_update(events)
        help_page.help_draw(screen)
        if res == "settings":
            currentmenu = previous_menu
            settings_active = True
            settings_popup.active = True

    # Overlay settings popup on top of current screen
    if settings_active and currentmenu not in ("title", "help"):
        settings_popup.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

# --- On clean exit: save game state (inventory + pigs + time) ---
try:
    player_inventory.save_to_file("save_data.json", game_time=homescreen.game_time)
except Exception as e:
    print(f"[Main] Failed to save game state: {e}")

pygame.quit()
sys.exit()
