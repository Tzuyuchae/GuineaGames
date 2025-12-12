import pygame
import sys
import ctypes
import os
import random # Added from the second script

# --- API IMPORT ---
try:
    from api_client import api
except ImportError:
    print("API Client not found. Running in offline mode (if supported).")
    class MockApi:
        def check_connection(self): return False
        def _post(self, url): return {} # Mock post method for reset
        # Mock methods needed for user/pet creation to avoid errors in the main logic
        def get_user(self, user_id): return {'id': user_id, 'username': 'OfflineUser', 'balance': 10000}
        def create_transaction(self, *args): pass
        def create_user(self, *args): return {'id': 1, 'username': 'Player1'}
        def create_pet(self, *args): return {'id': random.randint(100, 999)}
        def update_pet(self, *args, **kwargs): pass

    api = MockApi()

# --- FIX WINDOWS SCALING ---
try:
    ctypes.windll.user32.SetProcessDPIAware()
except AttributeError:
    pass

# --- INITIALIZE PYGAME ---
pygame.init()
pygame.mixer.init() # Added from the second script for music

# Screen setup (from first script)
screen_width = 672
screen_height = 864
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Guinea Games - Online")
clock = pygame.time.Clock()
FPS = 60

# --- IMPORT PAGES (Combined list) ---
import homescreen
import title
import store_page
import breeding 
from settings_popup import SettingsPopup
import help_page
# from details_page import details_update, details_draw # Assuming details_page is a typo or not needed if only homescreen uses the list. Included minigame logic instead.
# import settings_page # The first script uses SettingsPopup, which handles settings.
# from volume_settings import get_music_volume, load_settings # Assuming these are available or mocked
try:
    from volume_settings import get_music_volume, load_settings
except ImportError:
    print("Volume Settings not found. Using default volume.")
    def get_music_volume(): return 0.5
    def load_settings(): pass
load_settings() # Load volume settings on startup

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- IMPORT BACKEND TIME LOGIC ---
try:
    from backend.game_time import inc_month, load_clock, save_clock
except ImportError:
    def inc_month(): return []
    def load_clock(): return {"ticks": 0, "year": 1, "month": 1, "day": 1, "hour": 8}
    def save_clock(t, d): pass

# --- IMPORT MINIGAME (Combined Logic) ---
# From first script
try:
    from minigame.minigame_page import MinigamePage
except ImportError as e:
    print(f"MinigamePage Import Error: {e}")
    MinigamePage = None
    
# From second script (These are for the 'gameplay' state)
try:
    from minigame.maze_generator import MazeGenerator
    from minigame.maze import Maze
    from minigame.player import Player
    from minigame.enemy import Enemy
    from minigame.fruits import Fruit
except ImportError as e:
    print(f"Minigame Component Import Error: {e}")
    MazeGenerator, Maze, Player, Enemy, Fruit = None, None, None, None, None


# --- MUSIC MANAGEMENT (From second script) ---
def play_music_with_volume(music_path):
    """Helper function to play music with volume control."""
    try:
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(get_music_volume())
            pygame.mixer.music.play(-1)  # Loop indefinitely
            return True
        else:
            print(f"Music file not found: {music_path}")
            return False
    except Exception as e:
        print(f"Could not load music: {e}")
        return False

# Music flags
gameplay_music_playing = False
title_music_playing = False
home_music_playing = False
breeding_music_playing = False


# --- ONLINE SETUP (From first script) ---
CURRENT_USER_ID = 1
print("Connecting to backend...")

if hasattr(api, 'check_connection') and api.check_connection():
    print("Backend connected!")
    # ... (Login/Create User Logic remains the same)
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

# --- NEW RESTART FUNCTION (From first script) ---
def hard_reset_game():
    """Wipes all persistent data and resets the user to a fresh game state."""
    global time_passed, home_music_playing
    
    print("!!! HARD RESET TRIGGERED !!!")
    
    # 1. DELETE ALL PETS
    try:
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
    
    # Stop any music and ensure home music starts next loop
    pygame.mixer.music.stop()
    globals()['title_music_playing'] = False
    globals()['home_music_playing'] = False
    globals()['breeding_music_playing'] = False
    globals()['gameplay_music_playing'] = False

    return 'homescreen' 


# --- MINIGAME LOGIC (From second script) ---
def start_new_game():
    """Initializes the components for the 'gameplay' minigame state."""
    print("Starting new maze minigame...")
    if not all([MazeGenerator, Maze, Player, Enemy, Fruit]):
        print("Minigame classes not available. Cannot start.")
        return None, None, None, None

    generator = MazeGenerator(seed=random.randint(0, 9999))
    base_layout = generator.generate()

    player = Player()
    layout_with_player = player.add_player(base_layout)

    enemy = Enemy()
    final_layout = enemy.add_enemies(layout_with_player)

    maze = Maze(final_layout)
    fruit_obj = Fruit()

    return maze, player, enemy, fruit_obj

# Initialize minigame components for 'gameplay' state
maze, player, enemy, fruit_obj = start_new_game() if all([MazeGenerator, Maze, Player, Enemy, Fruit]) else (None, None, None, None)


# --- PAGE INITIALIZATION (From first script) ---
homescreen.homescreen_init(screen_width, screen_height)

store_bg_path = "frontend/Global Assets/Sprites/More Sprites/BG Art/Store/BG_Store.png"
if not os.path.exists(store_bg_path):
    store_bg_path = "images/BG_Store.png"
store_page.store_init(store_bg_path)

settings_popup = SettingsPopup(screen_width, screen_height)
settings_active = False 
previous_menu = 'homescreen' 

# --- INIT MINIGAME MANAGER (From first script, for 'minigame' state) ---
minigame_manager = None
if MinigamePage:
    minigame_manager = MinigamePage(user_id=CURRENT_USER_ID)

# --- TIME SETUP (From first script) ---
clock_data = load_clock()
time_passed = clock_data['ticks']

# Inject Date into Homescreen
homescreen.game_time['year'] = clock_data['year']
homescreen.game_time['month'] = clock_data['month']
homescreen.game_time['day'] = clock_data['day']
homescreen.game_time['hour'] = clock_data['hour']

inGameTimerStarted = False
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
            if event.key == pygame.K_ESCAPE and currentmenu != 'title':
                # Toggle settings popup
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
            
            elif action == 'confirm_restart':
                currentmenu = hard_reset_game() 
                settings_active = False
                settings_popup.active = False
                settings_popup.confirm_active = False 
        
        # Minigame ('gameplay' state) input handling from second script
        if currentmenu == 'gameplay':
             if event.type == pygame.KEYDOWN and player and maze:
                 if event.key == pygame.K_UP:
                     player.move(0, -1, maze)
                 elif event.key == pygame.K_DOWN:
                     player.move(0, 1, maze)
                 elif event.key == pygame.K_LEFT:
                     player.move(-1, 0, maze)
                 elif event.key == pygame.K_RIGHT:
                     player.move(1, 0, maze)


    # --- UPDATES & DRAWING ---
    
    # Music cleanup for state transitions
    if currentmenu != old_menu:
        pygame.mixer.music.stop()
        title_music_playing = False
        home_music_playing = False
        breeding_music_playing = False
        gameplay_music_playing = False

    if currentmenu == 'title':
        if not title_music_playing:
            start_music_path = os.path.join("music", "start.wav")
            if play_music_with_volume(start_music_path):
                title_music_playing = True

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
        if not home_music_playing:
            journey_music_path = os.path.join("music", "journey.wav")
            if play_music_with_volume(journey_music_path):
                home_music_playing = True

        if not inGameTimerStarted:  
            inGameTimerStarted = True
        
        if not settings_active:
            new_state = homescreen.homescreen_update(events, CURRENT_USER_ID)
            if new_state:
                if new_state == 'mini_games':
                    # This maps to the MinigamePage from the first script
                    currentmenu = 'minigame'
                elif new_state == 'start_maze': # Added a state to start the second script's minigame
                    maze, player, enemy, fruit_obj = start_new_game() # Re-initialize the maze
                    currentmenu = 'gameplay'
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
        if not breeding_music_playing:
            breeding_music_path = os.path.join("music", "yeahhhhh yuh.wav")
            if play_music_with_volume(breeding_music_path):
                breeding_music_playing = True

        if not settings_active:
            # Note: The first script passes None, None for pets/data. Adjust if your actual breeding module needs it.
            new_state = breeding.breeding_update(events, None, None) 
            if new_state == 'homescreen':
                currentmenu = 'homescreen'
        # Pass required arguments for breeding_draw if necessary. The first script suggests None, homescreen.game_time
        breeding.breeding_draw(screen, None, homescreen.game_time) 

    elif currentmenu == 'minigame':
        # This is the MinigamePage from the first script
        if not settings_active and minigame_manager:
            result = minigame_manager.update(events)
            if result == 'homescreen':
                currentmenu = 'homescreen'
                screen = pygame.display.set_mode((screen_width, screen_height))
        
        if minigame_manager:
            minigame_manager.draw(screen)
        else:
            screen.fill((0,0,0)) # Fallback if MinigamePage is missing
            
    elif currentmenu == 'help':
        res = help_page.help_update(events)
        help_page.help_draw(screen)
        if res == 'settings':
            currentmenu = previous_menu
            settings_active = True
            settings_popup.active = True

    elif currentmenu == 'gameplay':
        # This is the maze minigame from the second script
        if not gameplay_music_playing:
            boss_music_path = os.path.join("music", "boss battle.wav")
            if play_music_with_volume(boss_music_path):
                gameplay_music_playing = True
        
        if player and enemy and maze and fruit_obj:
            # Update Logic
            enemy.move_towards_player(player.player_pos(), maze)
            maze.layout = fruit_obj.if_collected(player.player_pos(), maze.layout)

            # Game Over / Win Conditions
            if player.player_pos() == enemy.enemy_pos():
                print("GAME OVER! You were caught!")
                currentmenu = 'homescreen'
            elif fruit_obj.all_fruits_collected(maze.layout):
                print("YOU WIN! All fruits collected!")
                currentmenu = 'homescreen'

            # DRAWING
            maze.draw(screen)
            fruit_obj.draw(screen, maze.layout)
            player.draw(screen)
            enemy.draw(screen)
        else:
            # Fallback if minigame components are missing
            screen.fill((0,0,0))
            currentmenu = 'homescreen' # Auto-exit if game cannot run


    # --- AUTO-REFRESH LOGIC ---
    if currentmenu == 'homescreen' and old_menu != 'homescreen':
        print("Returning to Homescreen -> Refreshing Data...")
        homescreen.needs_refresh = True

    # --- DRAW SETTINGS POPUP ---
    if settings_active and currentmenu != 'help':
        settings_popup.draw(screen)

    # --- TIME PASSES (Game Clock) ---
    if inGameTimerStarted and not settings_active: # Only advance time if not in settings
        time_passed += 1
        
        if time_passed >= TICKS_PER_MONTH: 
            time_passed = 0
            
            dead_pets = inc_month()
            
            if dead_pets:
                print(f"Main detected deaths: {dead_pets}")
                homescreen.dead_pets_queue.extend(dead_pets)
                homescreen.needs_refresh = True
            
            try:
                # Store page monthly update logic (from first script)
                store_page.on_month_pass()
            except: 
                pass
    
    pygame.display.flip()
    clock.tick(FPS)

# --- CLEANUP ---
save_clock(time_passed, homescreen.game_time)
pygame.quit()
sys.exit()