import pygame
import sys
import ctypes

# --- API IMPORT ---
from api_client import api

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

# --- IMPORT MINIGAME (Restored) ---
# Ensure this folder exists and has __init__.py if needed
try:
    from minigame.minigame_page import MinigamePage
except ImportError as e:
    print(f"Minigame Import Error: {e}")
    MinigamePage = None

# --- ONLINE SETUP ---
CURRENT_USER_ID = 1
print("Connecting to backend...")

if api.check_connection():
    print("Backend connected!")
    try:
        user = api.get_user(1)
        CURRENT_USER_ID = user['id']
        print(f"Logged in as {user['username']}")
    except:
        print("Creating User 1...")
        try:
            user = api.create_user("Player1", "p1@game.com", "password")
            CURRENT_USER_ID = user['id']
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
store_page.store_init("frontend/Global Assets/Sprites/More Sprites/BG Art/Store/BG_Store.png")

settings_popup = SettingsPopup(screen_width, screen_height)
settings_active = False 
previous_menu = 'homescreen' 

# --- INIT MINIGAME ---
minigame_manager = None
if MinigamePage:
    # Pass user_id so it can give rewards
    minigame_manager = MinigamePage(user_id=CURRENT_USER_ID)

# --- MAIN LOOP ---
currentmenu = "title"
running = True

while running:
    events = pygame.event.get()
    
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

        if settings_active:
            action = settings_popup.handle_event(event)
            if action == 'quit_game':
                running = False
            elif action == 'help':
                previous_menu = currentmenu 
                currentmenu = 'help'
                settings_active = False
                settings_popup.active = False

    # --- UPDATES & DRAWING ---
    
    if currentmenu == 'title':
        if not settings_active:
            new_state = title.title_update(events)
            if new_state:
                currentmenu = new_state
        title.title_draw(screen)

    elif currentmenu == 'homescreen':
        if not settings_active:
            new_state = homescreen.homescreen_update(events, CURRENT_USER_ID)
            if new_state:
                # FIX: Handle the 'mini_games' string from homescreen
                if new_state == 'mini_games':
                    currentmenu = 'minigame'
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
        breeding.breeding_draw(screen, None, None)

    # --- MINIGAME HANDLER (This was missing!) ---
    elif currentmenu == 'minigame':
        if not settings_active and minigame_manager:
            # Update
            result = minigame_manager.update(events)
            
            # Check for exit
            if result == 'homescreen':
                currentmenu = 'homescreen'
                # Reset screen mode in case minigame changed it
                screen = pygame.display.set_mode((screen_width, screen_height))
        
        # Draw
        if minigame_manager:
            minigame_manager.draw(screen)
        else:
            # Fallback if import failed
            screen.fill((0,0,0))
            font = pygame.font.Font(None, 36)
            txt = font.render("Minigame Failed to Load", True, (255, 255, 255))
            screen.blit(txt, (100, 300))
            
            # Back button fallback
            back_rect = pygame.Rect(10, 10, 100, 50)
            pygame.draw.rect(screen, (255,0,0), back_rect)
            if pygame.mouse.get_pressed()[0] and back_rect.collidepoint(pygame.mouse.get_pos()):
                currentmenu = 'homescreen'

    elif currentmenu == 'help':
        res = help_page.help_update(events)
        help_page.help_draw(screen)
        if res == 'settings':
            currentmenu = previous_menu
            settings_active = True
            settings_popup.active = True

    if settings_active and currentmenu != 'title' and currentmenu != 'help':
        settings_popup.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()