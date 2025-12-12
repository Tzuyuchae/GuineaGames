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
        def _post(self, url): return {} # Mock post method for reset
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
import homescreen
import title
import store_page
import breeding 
from settings_popup import SettingsPopup
import help_page

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- IMPORT BACKEND TIME LOGIC ---
try:
    from backend.game_time import inc_month, load_clock, save_clock
except ImportError:
    def inc_month(): return []
    def load_clock(): return {"ticks": 0, "year": 1, "month": 1, "day": 1, "hour": 8}
    def save_clock(t, d): pass

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
            api.create_transaction(CURRENT_USER_ID, "gift", 5000, "Starter Test Coins")
            p1 = api.create_pet(CURRENT_USER_ID, "Starter Alpha", "Abyssinian", "Brown")
            api.update_pet(p1['id'], age_days=10)
            p2 = api.create_pet(CURRENT_USER_ID, "Starter Beta", "American", "White")
            api.update_pet(p2['id'], age_days=10)
        except Exception as e:
            print(f"Login Error: {e}")
else:
    print("WARNING: Backend is offline.")

# --- NEW RESTART FUNCTION ---
def hard_reset_game():
    """Wipes all persistent data and resets the user to a fresh game state."""
    global time_passed
    
    print("!!! HARD RESET TRIGGERED !!!")
    
    # 1. DELETE ALL PETS (Wipes all pet-related data including time/calendar)
    try:
        # Assuming your API endpoint is correct for mass deletion
        api._post(f"/pets/delete/all/{CURRENT_USER_ID}") 
        print("All pets deleted successfully.")
    except Exception as e:
        print(f"Error during API mass delete: {e}")
        
    # 2. Reset local time variables
    time_passed = 0
    homescreen.game_time['year'] = 1
    homescreen.game_time['month'] = 1
    homescreen.game_time['day'] = 1
    homescreen.game_time['hour'] = 8
    
    # 3. Create starter pets and coins again
    try:
        api.create_transaction(CURRENT_USER_ID, "gift", 5000, "Hard Reset Gift")
        p1 = api.create_pet(CURRENT_USER_ID, "Starter Alpha", "Abyssinian", "Brown")
        api.update_pet(p1['id'], age_days=10)
        p2 = api.create_pet(CURRENT_USER_ID, "Starter Beta", "American", "White")
        api.update_pet(p2['id'], age_days=10)
        print("Starter pets and coins re-created.")
        
    except Exception as e:
        print(f"Error recreating starter data: {e}")
        
    # 4. Force data refresh and go back to homescreen
    homescreen.needs_refresh = True
    return 'homescreen' 


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

# --- TIME SETUP ---
clock_data = load_clock()

time_passed = clock_data['ticks']

# Inject Date into Homescreen
homescreen.game_time['year'] = clock_data['year']
homescreen.game_time['month'] = clock_data['month']
homescreen.game_time['day'] = clock_data['day']
homescreen.game_time['hour'] = clock_data['hour']

inGameTimerStarted = False
# SETTING FOR TESTING: 5 seconds * 60 FPS = 300 ticks
TICKS_PER_MONTH = 300 

# --- MAIN LOOP ---
currentmenu = "title"
running = True

while running:
    events = pygame.event.get()
    
    old_menu = currentmenu

    for event in events:
        if event.type == pygame.QUIT:
            save_clock(time_passed, homescreen.game_time) 
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
                save_clock(time_passed, homescreen.game_time)
                running = False
            elif action == 'help':
                previous_menu = currentmenu 
                currentmenu = 'help'
                settings_active = False
                settings_popup.active = False
            elif action == 'close': 
                settings_active = False
                settings_popup.active = False
            
            # --- NEW: HANDLE RESTART ---
            elif action == 'confirm_restart':
                currentmenu = hard_reset_game() 
                settings_active = False
                settings_popup.active = False
                settings_popup.confirm_active = False # Should be handled in SettingsPopup, but good safety measure

    # --- UPDATES & DRAWING ---
    
    if currentmenu == 'title':
        if not settings_active:
            new_state = title.title_update(events)
            if new_state == 'settings':
                settings_active = True
                settings_popup.active = True
            elif new_state == 'quit':
                save_clock(time_passed, homescreen.game_time)
                running = False
            elif new_state:
                currentmenu = new_state
        title.title_draw(screen)

    elif currentmenu == 'homescreen':
        if not inGameTimerStarted:   
            inGameTimerStarted = True
        
        if not settings_active:
            new_state = homescreen.homescreen_update(events, CURRENT_USER_ID)
            if new_state:
                if new_state == 'mini_games':
                    currentmenu = 'minigame'
                elif new_state == 'home':
                    settings_active = True
                    settings_popup.active = True
                else:
                    currentmenu = new_state
        homescreen.homescreen_draw(screen, CURRENT_USER_ID, time_passed)

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
        time_passed += 1
        
        if time_passed >= TICKS_PER_MONTH: 
            time_passed = 0
            
            dead_pets = inc_month()
            
            if dead_pets:
                print(f"Main detected deaths: {dead_pets}")
                homescreen.dead_pets_queue.extend(dead_pets)
                homescreen.needs_refresh = True
            
            try:
                store_page.on_month_pass()
            except: pass
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()