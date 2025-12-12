import pygame
import sys
import ctypes
import os

# --- API IMPORT ---
try:
    from api_client import api
except ImportError:
    print("API Client not found. Running in offline mode (if supported).")
    class MockApi:
        def check_connection(self): return False
    api = MockApi()

# --- FIX WINDOWS SCALING ---
try:
    ctypes.windll.user32.SetProcessDPIAware()
except AttributeError:
    pass

# --- INITIALIZE PYGAME ---
pygame.init()

screen_width = 672
screen_height = 864
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Guinea Games - Online")
clock = pygame.time.Clock()
FPS = 60

# --- IMPORT PAGES ---
# Ensure these files exist in the same directory
import homescreen
import title
import store_page
import breeding 
from settings_popup import SettingsPopup
import help_page

# Add the parent directory to path to find backend modules if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Try importing backend logic safely
try:
    from backend.game_time import inc_month 
except ImportError:
    # Fallback if backend file isn't found
    def inc_month(): pass

# --- IMPORT MINIGAME ---
try:
    from minigame.minigame_page import MinigamePage
except ImportError as e:
    print(f"Minigame Import Error: {e}")
    MinigamePage = None

# --- ONLINE SETUP ---
CURRENT_USER_ID = 1
print("Connecting to backend...")

if hasattr(api, 'check_connection') and api.check_connection():
    print("Backend connected!")
    try:
        user = api.get_user(1)
        CURRENT_USER_ID = user['id']
        print(f"Logged in as {user['username']}")

        # --- TEST: ADD STARTER COINS ---
        current_balance = user.get('balance', 0)
        if current_balance < 5000:
            print(f"Balance low ({current_balance}). Adding 5000 test coins...")
            try:
                api.create_transaction(CURRENT_USER_ID, "gift", 5000, "Starter Test Coins")
            except Exception as e:
                print(f"Could not add coins: {e}")

    except:
        print("Creating User 1...")
        try:
            user = api.create_user("Player1", "p1@game.com", "password")
            CURRENT_USER_ID = user['id']
            
            print("Adding 5000 test coins to new user...")
            api.create_transaction(CURRENT_USER_ID, "gift", 5000, "Starter Test Coins")

            # Adult Starters
            p1 = api.create_pet(CURRENT_USER_ID, "Starter Alpha", "Abyssinian", "Brown")
            api.update_pet(p1['id'], age_days=10)
            p2 = api.create_pet(CURRENT_USER_ID, "Starter Beta", "American", "White")
            api.update_pet(p2['id'], age_days=10)
        except Exception as e:
            print(f"Login Error: {e}")
else:
    print("WARNING: Backend is offline.")

# --- PAGE INITIALIZATION ---
homescreen.homescreen_init(screen_width, screen_height)

store_bg_path = "frontend/Global Assets/Sprites/More Sprites/BG Art/Store/BG_Store.png"
if not os.path.exists(store_bg_path):
    store_bg_path = "images/BG_Store.png"
store_page.store_init(store_bg_path)

settings_popup = SettingsPopup(screen_width, screen_height)
settings_active = False 
previous_menu = 'homescreen' 

# --- INIT MINIGAME ---
minigame_manager = None
if MinigamePage:
    minigame_manager = MinigamePage(user_id=CURRENT_USER_ID)

# --- MAIN LOOP ---
currentmenu = "title"
running = True
time_passed = 0 # This variable was misnamed 'secondsPassed' in your snippet
inGameTimerStarted = False

while running:
    events = pygame.event.get()
    
    # Store old menu to detect transitions
    old_menu = currentmenu

    for event in events:
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if currentmenu != 'title':
                    settings_active = not settings_active
                    settings_popup.active = settings_active
                    if not settings_active:
                        settings_popup.active = False

        # Handle events inside the Settings Popup
        if settings_active:
            action = settings_popup.handle_event(event)
            
            if not settings_popup.active:
                settings_active = False

            if action == 'quit_game':
                running = False
            elif action == 'help':
                previous_menu = currentmenu 
                currentmenu = 'help'
                settings_active = False
                settings_popup.active = False
            elif action == 'close': 
                settings_active = False
                settings_popup.active = False

    # --- UPDATES & DRAWING ---
    
    if currentmenu == 'title':
        if not settings_active:
            new_state = title.title_update(events)
            if new_state == 'settings':
                settings_active = True
                settings_popup.active = True
            elif new_state == 'quit':
                running = False
            elif new_state:
                currentmenu = new_state
        title.title_draw(screen)

    elif currentmenu == 'homescreen':
        # FIXED: Use 'not' instead of '!' (Python Syntax)
        if not inGameTimerStarted:   
            inGameTimerStarted = True
        
        if not settings_active:
            new_state = homescreen.homescreen_update(events, CURRENT_USER_ID)
            if new_state:
                if new_state == 'mini_games':
                    currentmenu = 'minigame'
                elif new_state == 'home':
                    # Sometimes 'home' clicks mean settings in legacy code, 
                    # but here we just open settings just in case
                    settings_active = True
                    settings_popup.active = True
                else:
                    currentmenu = new_state
        homescreen.homescreen_draw(screen, CURRENT_USER_ID)

    elif currentmenu == 'store':
        if not settings_active:
            new_state = store_page.store_update(events, CURRENT_USER_ID)
            if new_state == 'homescreen':
                currentmenu = 'homescreen'
        store_page.store_draw(screen, CURRENT_USER_ID)

    elif currentmenu == 'breeding':
        if not settings_active:
            new_state = breeding.breeding_update(events, None, None) 
            if new_state == 'homescreen':
                currentmenu = 'homescreen'
        breeding.breeding_draw(screen, None, homescreen.game_time)

    elif currentmenu == 'minigame':
        if not settings_active and minigame_manager:
            result = minigame_manager.update(events)
            if result == 'homescreen':
                currentmenu = 'homescreen'
                # Reset display mode in case minigame changed it
                screen = pygame.display.set_mode((screen_width, screen_height))
        
        if minigame_manager:
            minigame_manager.draw(screen)
        else:
            screen.fill((0,0,0))

    elif currentmenu == 'help':
        res = help_page.help_update(events)
        help_page.help_draw(screen)
        if res == 'settings':
            currentmenu = previous_menu
            settings_active = True
            settings_popup.active = True

    # --- AUTO-REFRESH LOGIC ---
    if currentmenu == 'homescreen' and old_menu != 'homescreen':
        print("Returning to Homescreen -> Refreshing Data...")
        homescreen.needs_refresh = True

    # --- DRAW SETTINGS POPUP ---
    if settings_active and currentmenu != 'help':
        settings_popup.draw(screen)

    # --- TIME PASSES ---
    if inGameTimerStarted:
        # FIXED: Use 'time_passed' which matches initialization
        time_passed += 1
        if time_passed >= 18000:  # 5 minutes at 60 FPS (300 seconds * 60)
            time_passed = 0
            inc_month()
            try:
                store_page.on_month_pass()
            except: pass
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()