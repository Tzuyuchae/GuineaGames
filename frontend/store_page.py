import pygame
import os
from api_client import api

# --- Settings & Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
GOLD = (255, 215, 0)

SCREEN_WIDTH = 672
SCREEN_HEIGHT = 864

# Layout Constants
SHELF_START_Y = 185
SHELF_HEIGHT = 120
SHELF_SPACING = 18
FOOD_START_X = 65
PIG_START_X = 375
BTN_OFFSET_Y = 65

# --- Store State ---
font_title = None
font_text = None
background_image = None
store_mode = 'BUY'
user_balance = 0
inventory_items = []
my_pets = []
marketplace_listings = []

FOOD_CATALOG = [
    {"name": "Pellets", "price": 10, "type": "food", "icon": "SP_Pellets.png"},
    {"name": "Hay", "price": 15, "type": "food", "icon": "SP_WaterJug.png"},
    {"name": "Carrot", "price": 25, "type": "food", "icon": "MG_Carrot.png"},
    {"name": "Vitamin C", "price": 50, "type": "medicine", "icon": "MG_Strawberry.png"}
]

class IconLoader:
    def __init__(self):
        self.cache = {}
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Robust recursive search for assets
        self.asset_map = {}
        self._index_assets()

    def _index_assets(self):
        """Walks through the Global Assets folder and maps filenames to full paths"""
        assets_dir = os.path.join(self.base_dir, "Global Assets")
        if not os.path.exists(assets_dir):
            print(f"Warning: Global Assets folder not found at {assets_dir}")
            return

        for root, dirs, files in os.walk(assets_dir):
            for file in files:
                if file.lower().endswith('.png'):
                    self.asset_map[file] = os.path.join(root, file)
        
        print(f"IconLoader: Indexed {len(self.asset_map)} assets.")

    def get_image(self, filename, size=(60, 60)):
        key = (filename, size)
        if key in self.cache:
            return self.cache[key]

        # Look up path in map
        full_path = self.asset_map.get(filename)
        
        if full_path and os.path.exists(full_path):
            try:
                img = pygame.image.load(full_path).convert_alpha()
                img = pygame.transform.scale(img, size)
                self.cache[key] = img
                return img
            except Exception as e:
                print(f"Failed to load {filename}: {e}")
        else:
            # Try generic images folder if not in Global Assets
            alt_path = os.path.join(self.base_dir, "images", filename)
            if os.path.exists(alt_path):
                try:
                    img = pygame.image.load(alt_path).convert_alpha()
                    img = pygame.transform.scale(img, size)
                    self.cache[key] = img
                    return img
                except: pass

        # Fallback
        s = pygame.Surface(size)
        s.fill((150, 100, 50))
        # Draw a little '?'
        pygame.draw.rect(s, (0,0,0), (10,10,40,40), 2)
        self.cache[key] = s
        return s

    def get_pet_image(self, pet_data, size=(80, 80)):
        color = pet_data.get('color_phenotype', pet_data.get('color', 'White')).lower()
        filename = "SH_GP_White_01.png"
        
        if "brown" in color: filename = "SH_GP_Brown_01.png"
        elif "orange" in color: filename = "SH_GP_Orange_01.png"
            
        return self.get_image(filename, size)

icon_loader = None

def store_init(background_path=None):
    global font_title, font_text, background_image, icon_loader
    pygame.font.init()
    font_title = pygame.font.Font(None, 50)
    font_text = pygame.font.Font(None, 24)
    icon_loader = IconLoader()
    
    # Try to load background using the smart loader if direct path fails
    try:
        if background_path and os.path.exists(background_path):
            bg = pygame.image.load(background_path).convert()
            background_image = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        elif background_path:
            # Try finding just the filename
            fname = os.path.basename(background_path)
            bg_img = icon_loader.get_image(fname, (SCREEN_WIDTH, SCREEN_HEIGHT))
            background_image = bg_img
    except:
        pass

def fetch_data(user_id):
    global user_balance, my_pets, marketplace_listings
    try:
        user = api.get_user(user_id)
        user_balance = user.get('balance', 0)
        my_pets = api.get_user_pets(user_id)
        marketplace_listings = api.browse_marketplace(limit=4)
    except Exception as e:
        print(f"Store Fetch Error: {e}")

def draw_button(screen, rect, text, color):
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)
    txt_surf = font_text.render(text, True, BLACK)
    txt_rect = txt_surf.get_rect(center=rect.center)
    screen.blit(txt_surf, txt_rect)

def store_update(events, user_id):
    global store_mode
    mouse_pos = pygame.mouse.get_pos()
    
    if user_balance == 0 and not my_pets: 
        fetch_data(user_id)

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            
            back_rect = pygame.Rect((SCREEN_WIDTH - 200)//2, SCREEN_HEIGHT - 110, 200, 50)
            if back_rect.collidepoint(mouse_pos):
                return 'homescreen'

            mode_rect = pygame.Rect(SCREEN_WIDTH - 160, 60, 140, 30)
            if mode_rect.collidepoint(mouse_pos):
                store_mode = 'SELL' if store_mode == 'BUY' else 'BUY'
                fetch_data(user_id)
                return None

            if store_mode == 'BUY':
                # BUY FOOD
                for i, item in enumerate(FOOD_CATALOG):
                    card_y = SHELF_START_Y + (i * (SHELF_HEIGHT + SHELF_SPACING))
                    btn_rect = pygame.Rect(FOOD_START_X + 10, card_y + BTN_OFFSET_Y, 90, 28)
                    
                    if btn_rect.collidepoint(mouse_pos):
                        if user_balance >= item['price']:
                            try:
                                api.create_transaction(user_id, "purchase", -item['price'], f"Bought {item['name']}")
                                api.add_inventory_item(user_id, item['name'], item['type'], 1)
                                print(f"Bought {item['name']}")
                                fetch_data(user_id)
                            except Exception as e:
                                print(f"Buy Error: {e}")

                # BUY PETS
                for i, listing in enumerate(marketplace_listings[:4]):
                    card_y = SHELF_START_Y + (i * (SHELF_HEIGHT + SHELF_SPACING))
                    btn_rect = pygame.Rect(PIG_START_X + 10, card_y + BTN_OFFSET_Y, 90, 28)
                    
                    if btn_rect.collidepoint(mouse_pos):
                        price = listing['asking_price']
                        if user_balance >= price:
                            try:
                                api.buy_pet(listing['pet_id'], user_id)
                                print("Pet adopted!")
                                fetch_data(user_id)
                            except Exception as e:
                                print(f"Adoption Error: {e}")

            else:
                # SELL PETS
                for i, pet in enumerate(my_pets[:8]):
                    col = i % 2
                    row = i // 2
                    card_x = FOOD_START_X if col == 0 else PIG_START_X
                    card_y = SHELF_START_Y + (row * (SHELF_HEIGHT + SHELF_SPACING))
                    
                    btn_rect = pygame.Rect(card_x + 10, card_y + BTN_OFFSET_Y, 80, 28)
                    
                    if btn_rect.collidepoint(mouse_pos):
                        try:
                            val = pet.get('market_value', 100)
                            api.create_transaction(user_id, "sale", val, f"Sold {pet['name']}")
                            api.delete_pet(pet['id'])
                            print(f"Sold {pet['name']}")
                            fetch_data(user_id)
                        except Exception as e:
                            print(f"Sell Error: {e}")

    return None

def store_draw(screen, user_id):
    if background_image:
        screen.blit(background_image, (0,0))
    else:
        screen.fill((60, 60, 80))

    title = font_title.render("General Store", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))
    
    coins = font_title.render(f"Coins: {user_balance}", True, GOLD)
    screen.blit(coins, (SCREEN_WIDTH - 200, 20))

    mode_rect = pygame.Rect(SCREEN_WIDTH - 160, 60, 140, 30)
    mode_text = "Switch to SELL" if store_mode == 'BUY' else "Switch to BUY"
    mode_color = RED if store_mode == 'BUY' else GREEN
    draw_button(screen, mode_rect, mode_text, mode_color)

    if store_mode == 'BUY':
        # Food Column
        for i, item in enumerate(FOOD_CATALOG):
            y = SHELF_START_Y + (i * (SHELF_HEIGHT + SHELF_SPACING))
            
            if icon_loader:
                icon = icon_loader.get_image(item['icon'])
                screen.blit(icon, (FOOD_START_X + 150, y + 10))
            
            name = font_text.render(item['name'], True, BLACK)
            screen.blit(name, (FOOD_START_X + 10, y + 10))
            
            btn_rect = pygame.Rect(FOOD_START_X + 10, y + BTN_OFFSET_Y, 90, 28)
            col = GREEN if user_balance >= item['price'] else GRAY
            draw_button(screen, btn_rect, f"${item['price']}", col)

        # Pet Column
        for i, listing in enumerate(marketplace_listings[:4]):
            y = SHELF_START_Y + (i * (SHELF_HEIGHT + SHELF_SPACING))
            
            if icon_loader:
                img = icon_loader.get_pet_image(listing, size=(60,60))
                screen.blit(img, (PIG_START_X + 150, y + 10))
            
            name = font_text.render(f"{listing['name'][:10]}..", True, BLACK)
            screen.blit(name, (PIG_START_X + 10, y + 10))
            
            price = listing['asking_price']
            btn_rect = pygame.Rect(PIG_START_X + 10, y + BTN_OFFSET_Y, 90, 28)
            col = GREEN if user_balance >= price else GRAY
            draw_button(screen, btn_rect, f"${price}", col)

    else:
        # Sell Grid
        for i, pet in enumerate(my_pets[:8]):
            col = i % 2
            row = i // 2
            x = FOOD_START_X if col == 0 else PIG_START_X
            y = SHELF_START_Y + (row * (SHELF_HEIGHT + SHELF_SPACING))
            
            if icon_loader:
                img = icon_loader.get_pet_image(pet, size=(60,60))
                screen.blit(img, (x + 150, y + 10))
            
            name = font_text.render(pet['name'][:10], True, BLACK)
            screen.blit(name, (x + 10, y + 10))
            
            val = pet.get('market_value', 100)
            val_txt = font_text.render(f"Val: {val}", True, GOLD)
            screen.blit(val_txt, (x + 10, y + 35))
            
            btn_rect = pygame.Rect(x + 10, y + BTN_OFFSET_Y, 80, 28)
            draw_button(screen, btn_rect, "Sell", GREEN)

    back_rect = pygame.Rect((SCREEN_WIDTH - 200)//2, SCREEN_HEIGHT - 110, 200, 50)
    draw_button(screen, back_rect, "BACK", GOLD)