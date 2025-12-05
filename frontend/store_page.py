import pygame
import os
import random
import time
from api_client import api
from guineapig import GuineaPigSprite

# --- Settings & Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
GOLD = (255, 215, 0)
BLUE = (70, 130, 180)

SCREEN_WIDTH = 672
SCREEN_HEIGHT = 864

# --- Layout Constants ---
SHELF_START_Y = 195  
SHELF_HEIGHT = 120   
SHELF_SPACING = 3    
FOOD_START_X = 70
FOOD_CARD_W = 240
PIG_START_X = 380
PIG_CARD_W = 240
BTN_OFFSET_Y = 55
BUTTON_HEIGHT = 25

# --- Store State ---
font_title = None
font_text = None
background_image = None
store_mode = 'BUY'
user_balance = 0
my_pets = []
marketplace_listings = [] 

# Auto-Refresh Timer logic
last_refresh_time = 0
REFRESH_INTERVAL = 30 * 60 # 30 Minutes

# Button Sprites
btn_buy = None
btn_buy_grey = None
btn_sell = None
btn_sell_grey = None
coin_sprite = None
food_sprites = {}

FOOD_CATALOG = [
    {"name": "Pellets", "price": 10, "type": "food", "icon": "SP_Pellets.png"},
    {"name": "Hay", "price": 15, "type": "food", "icon": "SP_WaterJug.png"},
    {"name": "Carrot", "price": 25, "type": "food", "icon": "MG_Carrot.png"},
    {"name": "Vitamin C", "price": 50, "type": "medicine", "icon": "MG_Strawberry.png"}
]

def load_assets(external_bg_path=None):
    global background_image, btn_buy, btn_buy_grey, btn_sell, btn_sell_grey, coin_sprite, food_sprites
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    def load(path, size=None):
        paths_to_try = [
            os.path.join(base_path, path),
            path,
            os.path.join("frontend", path)
        ]
        for p in paths_to_try:
            if os.path.exists(p):
                try:
                    img = pygame.image.load(p).convert_alpha()
                    if size: img = pygame.transform.scale(img, size)
                    return img
                except: pass
        return None

    # --- BACKGROUND LOGIC ---
    preferred_path = "frontend/images/BG_Store.png"
    
    bg_candidates = [preferred_path]
    if external_bg_path:
        bg_candidates.append(external_bg_path)
    bg_candidates.append("images/BG_Store.png")

    for bg_path in bg_candidates:
        full_bg_path = os.path.join(base_path, bg_path) if not os.path.isabs(bg_path) else bg_path
        if os.path.exists(bg_path):
             try:
                img = pygame.image.load(bg_path).convert()
                background_image = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
                print(f"Loaded Store BG: {bg_path}")
                break
             except: pass
        elif os.path.exists(full_bg_path):
             try:
                img = pygame.image.load(full_bg_path).convert()
                background_image = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
                print(f"Loaded Store BG: {full_bg_path}")
                break
             except: pass

    # Load Buttons
    btn_buy = load("Global Assets/Sprites/Maze/Store buttons/button_buy.png", (85, BUTTON_HEIGHT))
    btn_buy_grey = load("Global Assets/Sprites/Maze/Store buttons/button_buy_grey.png", (85, BUTTON_HEIGHT))
    btn_sell = load("Global Assets/Sprites/Maze/Store buttons/button_sell.png", (70, BUTTON_HEIGHT))
    btn_sell_grey = load("Global Assets/Sprites/Maze/Store buttons/button_sell_grey.png", (70, BUTTON_HEIGHT))
    
    # Load Coin
    coin_sprite = load("Global Assets/Sprites/Global/GL_Coin.png", (40, 40))

    # Load Food Icons
    food_paths = {
        "Pellets": "Global Assets/Sprites/Mini-game/fruit.png",
        "Hay": "Global Assets/Sprites/Mini-game/MG_Cabbage.png",
        "Carrot": "Global Assets/Sprites/Mini-game/MG_Carrot.png",
        "Vitamin C": "Global Assets/Sprites/Mini-game/MG_Strawberry.png"
    }
    for k, v in food_paths.items():
        food_sprites[k] = load(v, (60, 60))

def store_init(background_path=None):
    global font_title, font_text, marketplace_listings
    pygame.font.init()
    font_title = pygame.font.Font(None, 40)
    font_text = pygame.font.Font(None, 22)
    load_assets(background_path)
    
    # --- FORCE CLEAR OLD STOCK ---
    # This ensures no stale "Shorthair" pigs remain from previous runs
    marketplace_listings = [] 
    generate_random_store_stock()

def generate_random_store_stock():
    """Generates random guinea pigs for the store"""
    global marketplace_listings, last_refresh_time
    
    names = ['Nibbles', 'Cocoa', 'Buttons', 'Poppy', 'Widget', 'Pebble', 'Mango', 'Daisy']
    colors = ['Brown', 'Black', 'White', 'Orange']
    
    # --- DEFINE BREEDS ---
    # Maps Breed Name -> Coat Length
    breeds = [
        ("American", "Short"),
        ("Abyssinian", "Long"),
        ("Peruvian", "Long"),
        ("Silkie", "Long"),
        ("Teddy", "Short")
    ]
    
    marketplace_listings = []
    
    for i in range(3): 
        chosen_breed, coat = random.choice(breeds)
        
        fake_data = {
            "id": f"gen_{int(time.time())}_{i}", 
            "name": f"{random.choice(names)}-{random.randint(10,99)}",
            "color": random.choice(colors),
            "species": chosen_breed, # Critical: Sets breed name
            "coat_length": coat,
            "speed": random.randint(30, 80),
            "endurance": random.randint(30, 80),
            "age_days": random.randint(10, 100),
            "market_value": random.randint(100, 300)
        }
        
        listing = {
            "data": fake_data,
            "sprite": GuineaPigSprite(0, 0, fake_data),
            "price": fake_data['market_value']
        }
        marketplace_listings.append(listing)
    
    last_refresh_time = time.time()
    print("Store Restocked with new Guinea Pigs!")

def fetch_user_data(user_id):
    """Updates Balance and Inventory from API"""
    global user_balance, my_pets
    try:
        user = api.get_user(user_id)
        user_balance = user.get('balance', 0)
        
        raw_my_pets = api.get_user_pets(user_id)
        my_pets = [GuineaPigSprite(0,0, p) for p in raw_my_pets]
             
    except Exception as e:
        print(f"Store Fetch Error: {e}")

def draw_simple_btn(screen, rect, text, color):
    pygame.draw.rect(screen, color, rect, border_radius=6)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)
    txt_s = font_text.render(text, True, BLACK)
    screen.blit(txt_s, txt_s.get_rect(center=rect.center))

def store_update(events, user_id):
    global store_mode, last_refresh_time
    mouse_pos = pygame.mouse.get_pos()
    
    if user_balance == 0 and not my_pets: 
        fetch_user_data(user_id)
        
    if time.time() - last_refresh_time > REFRESH_INTERVAL:
        generate_random_store_stock()

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            
            back_rect = pygame.Rect((SCREEN_WIDTH - 200)//2, SCREEN_HEIGHT - 110, 200, 50)
            if back_rect.collidepoint(mouse_pos): return 'homescreen'

            mode_rect = pygame.Rect(SCREEN_WIDTH - 160, 60, 140, 30)
            if mode_rect.collidepoint(mouse_pos):
                store_mode = 'SELL' if store_mode == 'BUY' else 'BUY'
                fetch_user_data(user_id)
                return None

            if store_mode == 'BUY':
                # --- BUY FOOD ---
                for i, item in enumerate(FOOD_CATALOG):
                    extra = 18 if i == 0 else (10 if i == 1 else 0)
                    y = SHELF_START_Y + (i * (SHELF_HEIGHT + SHELF_SPACING)) + extra
                    btn_rect = pygame.Rect(FOOD_START_X + 8, y + BTN_OFFSET_Y, 85, BUTTON_HEIGHT)
                    
                    if btn_rect.collidepoint(mouse_pos):
                        if user_balance >= item['price']:
                            try:
                                api.create_transaction(user_id, "purchase", -item['price'], f"Bought {item['name']}")
                                api.add_inventory_item(user_id, item['name'], item['type'], 1)
                                fetch_user_data(user_id)
                            except Exception as e: print(f"Buy Error: {e}")

                # --- BUY PETS (Randomly Generated) ---
                for i, listing in enumerate(marketplace_listings):
                    if i >= 4: break
                    extra = 18 if i == 0 else (10 if i == 1 else 0)
                    y = SHELF_START_Y + (i * (SHELF_HEIGHT + SHELF_SPACING)) + extra
                    btn_rect = pygame.Rect(PIG_START_X + 8, y + BTN_OFFSET_Y, 85, BUTTON_HEIGHT)
                    
                    if btn_rect.collidepoint(mouse_pos):
                        if user_balance >= listing['price']:
                            try:
                                p_data = listing['data']
                                api.create_transaction(user_id, "purchase", -listing['price'], f"Adopted {p_data['name']}")
                                
                                # --- DEBUG: Print what we are sending ---
                                breed_to_send = p_data.get('species', 'American')
                                print(f"Adopting Pet. Name: {p_data['name']}, Breed: {breed_to_send}")

                                api.create_pet(
                                    # Positional Arguments (Order Matters!)
                                    user_id,                                # 1. Owner
                                    p_data['name'],                         # 2. Name
                                    breed_to_send,                          # 3. Species (e.g. Abyssinian)
                                    p_data['color'],                        # 4. Color
                                    
                                    # Keyword Arguments
                                    coat_length=p_data.get('coat_length', 'Short'), 
                                    speed=p_data['speed'],
                                    endurance=p_data['endurance'],
                                    market_value=p_data['market_value']
                                )
                                
                                marketplace_listings.pop(i)
                                fetch_user_data(user_id)
                                print("Pet saved successfully!")
                                
                            except Exception as e: 
                                print(f"Adopt Error: {e}")

            else:
                # --- SELL PETS ---
                for i, pet in enumerate(my_pets[:4]):
                    extra = 18 if i == 0 else (10 if i == 1 else 0)
                    y = SHELF_START_Y + (i * (SHELF_HEIGHT + SHELF_SPACING)) + extra
                    btn_rect = pygame.Rect(PIG_START_X + 8, y + BTN_OFFSET_Y, 70, BUTTON_HEIGHT)
                    
                    if btn_rect.collidepoint(mouse_pos):
                        try:
                            val = pet.data.get('market_value', 50)
                            api.create_transaction(user_id, "sale", val, f"Sold {pet.data['name']}")
                            api.delete_pet(pet.data['id'])
                            fetch_user_data(user_id)
                        except Exception as e: print(f"Sell Error: {e}")

    return None

def store_draw(screen, user_id):
    if background_image: 
        screen.blit(background_image, (0,0))
    else: 
        screen.fill((60, 60, 70))

    title = font_title.render("General Store", True, WHITE)
    screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 20))

    bal_txt = font_title.render(str(user_balance), True, GOLD)
    if coin_sprite:
        screen.blit(coin_sprite, (SCREEN_WIDTH - 120, 20))
        screen.blit(bal_txt, (SCREEN_WIDTH - 75, 25))
    else:
        screen.blit(bal_txt, (SCREEN_WIDTH - 100, 25))

    mode_rect = pygame.Rect(SCREEN_WIDTH - 160, 60, 140, 30)
    mode_txt = "Switch to SELL" if store_mode == 'BUY' else "Switch to BUY"
    mode_col = RED if store_mode == 'BUY' else GREEN
    draw_simple_btn(screen, mode_rect, mode_txt, mode_col)

    if store_mode == 'BUY':
        for i, item in enumerate(FOOD_CATALOG):
            extra = 18 if i == 0 else (10 if i == 1 else 0)
            y = SHELF_START_Y + (i * (SHELF_HEIGHT + SHELF_SPACING)) + extra
            
            bg = pygame.Surface((FOOD_CARD_W, 85), pygame.SRCALPHA)
            pygame.draw.rect(bg, (255, 255, 240, 220), bg.get_rect(), border_radius=6)
            screen.blit(bg, (FOOD_START_X, y))
            
            screen.blit(font_text.render(item['name'], True, BLACK), (FOOD_START_X + 8, y + 8))
            screen.blit(font_text.render(f"${item['price']}", True, BLACK), (FOOD_START_X + 8, y + 28))
            
            if item['name'] in food_sprites and food_sprites[item['name']]:
                 screen.blit(food_sprites[item['name']], (FOOD_START_X + 160, y + 10))

            btn_rect = pygame.Rect(FOOD_START_X + 8, y + BTN_OFFSET_Y, 85, BUTTON_HEIGHT)
            can_afford = user_balance >= item['price']
            
            if can_afford and btn_buy: screen.blit(btn_buy, btn_rect)
            elif not can_afford and btn_buy_grey: screen.blit(btn_buy_grey, btn_rect)
            else: draw_simple_btn(screen, btn_rect, "Buy", GREEN if can_afford else GRAY)

        for i, listing in enumerate(marketplace_listings):
            if i >= 4: break
            extra = 18 if i == 0 else (10 if i == 1 else 0)
            y = SHELF_START_Y + (i * (SHELF_HEIGHT + SHELF_SPACING)) + extra
            
            bg = pygame.Surface((PIG_CARD_W, 85), pygame.SRCALPHA)
            pygame.draw.rect(bg, (240, 240, 240, 220), bg.get_rect(), border_radius=6)
            screen.blit(bg, (PIG_START_X, y))
            
            p_data = listing['data']
            screen.blit(font_text.render(p_data.get('name', 'Unknown')[:12], True, BLACK), (PIG_START_X + 8, y + 8))
            
            # --- SHOW BREED ON CARD ---
            breed_txt = p_data.get('species', 'Guinea Pig')
            screen.blit(font_text.render(breed_txt, True, BLACK), (PIG_START_X + 8, y + 25))
            
            screen.blit(font_text.render(f"${listing['price']}", True, BLACK), (PIG_START_X + 8, y + 42))
            
            if listing['sprite']:
                listing['sprite'].rect.bottomleft = (PIG_START_X + 160, y + 80)
                screen.blit(listing['sprite'].image, listing['sprite'].rect)

            btn_rect = pygame.Rect(PIG_START_X + 8, y + BTN_OFFSET_Y, 85, BUTTON_HEIGHT)
            can_afford = user_balance >= listing['price']
            
            if can_afford and btn_buy: screen.blit(btn_buy, btn_rect)
            elif not can_afford and btn_buy_grey: screen.blit(btn_buy_grey, btn_rect)
            else: draw_simple_btn(screen, btn_rect, "Buy", GREEN if can_afford else GRAY)
            
    else:
        if not my_pets:
             screen.blit(font_title.render("No Pets to Sell", True, WHITE), (PIG_START_X, SHELF_START_Y))

        for i, pet in enumerate(my_pets[:4]):
            extra = 18 if i == 0 else (10 if i == 1 else 0)
            y = SHELF_START_Y + (i * (SHELF_HEIGHT + SHELF_SPACING)) + extra
            
            bg = pygame.Surface((PIG_CARD_W, 85), pygame.SRCALPHA)
            pygame.draw.rect(bg, (240, 240, 240, 220), bg.get_rect(), border_radius=6)
            screen.blit(bg, (PIG_START_X, y))
            
            screen.blit(font_text.render(pet.data['name'][:10], True, BLACK), (PIG_START_X + 8, y + 8))
            val = pet.data.get('market_value', 50)
            screen.blit(font_text.render(f"Value: ${val}", True, BLACK), (PIG_START_X + 8, y + 28))
            
            pet.rect.bottomleft = (PIG_START_X + 160, y + 80)
            screen.blit(pet.image, pet.rect)

            btn_rect = pygame.Rect(PIG_START_X + 8, y + BTN_OFFSET_Y, 70, BUTTON_HEIGHT)
            if btn_sell: screen.blit(btn_sell, btn_rect)
            else: draw_simple_btn(screen, btn_rect, "Sell", GREEN)

    back_rect = pygame.Rect((SCREEN_WIDTH - 200)//2, SCREEN_HEIGHT - 110, 200, 50)
    draw_simple_btn(screen, back_rect, "BACK HOME", GOLD)