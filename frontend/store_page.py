import pygame
import sys
import os

# --- Import Logic ---
from store_module import Store, PlayerInventory

# --- Settings & Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
PANEL_GRAY = (220, 220, 220)
BLUE = (70, 130, 180)

font_title = None
font_text = None
background_image = None  # Will hold the loaded background

# --- Global Store Instance ---
logic_store = Store()

# --- LAYOUT CONSTANTS (Fits 672px Width) ---
SCREEN_WIDTH = 672
SCREEN_HEIGHT = 864

# Background shelf dimensions (matching pixel art)
# Left column: FOOD, Right column: ADOPTION
SHELF_START_Y = 185  # Where shelves start vertically
SHELF_HEIGHT = 120   # Height of each shelf slot
SHELF_SPACING = 18   # Gap between shelves

# Food Layout (Left Column)
FOOD_START_X = 65
FOOD_CARD_W = 260
FOOD_CARD_H = 100

# Pig/Adoption Layout (Right Column)
PIG_START_X = 375
PIG_CARD_W = 260
PIG_CARD_H = 100

# Button offsets within cards
BTN_OFFSET_Y = 65

# State
store_mode = 'BUY' # 'BUY' or 'SELL'

def store_init(background_path=None):
    global font_title, font_text, background_image
    pygame.font.init()
    font_title = pygame.font.Font(None, 50)
    font_text = pygame.font.Font(None, 24)

    # Load background image if path is provided
    if background_path and os.path.exists(background_path):
        try:
            background_image = pygame.image.load(background_path).convert()
            # Scale to fit screen width while maintaining aspect ratio
            original_width = background_image.get_width()
            original_height = background_image.get_height()
            scale_factor = SCREEN_WIDTH / original_width
            new_height = int(original_height * scale_factor)
            background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, new_height))
            print(f"Background loaded: {background_path}")
        except pygame.error as e:
            print(f"Failed to load background: {e}")
            background_image = None

def draw_button(screen, rect, text, color):
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)
    txt_surf = font_text.render(text, True, BLACK)
    txt_rect = txt_surf.get_rect(center=rect.center)
    screen.blit(txt_surf, txt_rect)

def store_update(events, player_inventory):
    global store_mode
    mouse_pos = pygame.mouse.get_pos()
    logic_store.check_refresh_timer()

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            
            # Check 'Back' Button
            back_rect = pygame.Rect((SCREEN_WIDTH - 200)//2, SCREEN_HEIGHT - 110, 200, 50)
            if back_rect.collidepoint(mouse_pos):
                return 'homescreen'

            # Check 'Toggle Mode' Button
            mode_rect = pygame.Rect(SCREEN_WIDTH - 160, 60, 140, 30)
            if mode_rect.collidepoint(mouse_pos):
                store_mode = 'SELL' if store_mode == 'BUY' else 'BUY'
                return None

            if store_mode == 'BUY':
                # --- BUY LOGIC ---
                # 1. Buy Pigs (Right column - Adoption)
                for i, pig in enumerate(logic_store.pigs_for_sale[:4]):
                    card_y = SHELF_START_Y + (i * (SHELF_HEIGHT + SHELF_SPACING))
                    btn_rect = pygame.Rect(PIG_START_X + 10, card_y + BTN_OFFSET_Y, 90, 28)

                    if btn_rect.collidepoint(mouse_pos):
                        if logic_store.buy_guinea_pig(player_inventory, i):
                            print(f"Bought {pig.name}!")
                        return None

                # 2. Buy Food (Left column - Food)
                idx = 0
                for name, item in list(logic_store.food_catalog.items())[:4]:
                    card_y = SHELF_START_Y + (idx * (SHELF_HEIGHT + SHELF_SPACING))
                    btn_rect = pygame.Rect(FOOD_START_X + 10, card_y + BTN_OFFSET_Y, 90, 28)

                    if btn_rect.collidepoint(mouse_pos):
                        if logic_store.buy_food(player_inventory, name):
                            print(f"Bought {name}!")
                        return None
                    idx += 1
            
            else:
                # --- SELL LOGIC ---
                for i, pig in enumerate(player_inventory.owned_pigs[:8]):
                    col = i % 2
                    row = i // 2

                    if col == 0:
                        card_x = FOOD_START_X
                    else:
                        card_x = PIG_START_X

                    card_y = SHELF_START_Y + (row * (SHELF_HEIGHT + SHELF_SPACING))

                    # Sell Button
                    sell_btn = pygame.Rect(card_x + 10, card_y + BTN_OFFSET_Y, 65, 25)

                    # Dev Age Button
                    age_btn = pygame.Rect(card_x + 85, card_y + BTN_OFFSET_Y, 55, 25)

                    if sell_btn.collidepoint(mouse_pos):
                        if logic_store.sell_guinea_pig(player_inventory, i):
                            print(f"Sold {pig.name}!")
                        return None

                    if age_btn.collidepoint(mouse_pos):
                        pig.force_adult()
                        print(f"{pig.name} is now an adult!")
                        return None

    return None

def store_draw(screen, player_inventory):
    # Draw background image if available, otherwise use solid color
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill((50, 50, 70)) 

    # Header
    title = font_title.render("General Store", True, WHITE)
    screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 20))

    coins_text = font_title.render(f"Coins: {player_inventory.coins}", True, GOLD)
    screen.blit(coins_text, (SCREEN_WIDTH - coins_text.get_width() - 20, 20))
    
    # Toggle Button
    mode_rect = pygame.Rect(SCREEN_WIDTH - 160, 60, 140, 30)
    mode_text = "Switch to SELL" if store_mode == 'BUY' else "Switch to BUY"
    mode_color = RED if store_mode == 'BUY' else GREEN
    draw_button(screen, mode_rect, mode_text, mode_color)

    # Refresh Timer
    if store_mode == 'BUY':
        secs = logic_store.get_time_until_refresh()
        timer_txt = font_text.render(f"Restock: {logic_store._format_time(secs)}", True, WHITE)
        screen.blit(timer_txt, (20, 65))
    
    # --- CONTENT AREA ---
    
    if store_mode == 'BUY':
        _draw_buy_mode(screen, player_inventory)
    else:
        _draw_sell_mode(screen, player_inventory)

    # Back Button (positioned at bottom)
    back_rect = pygame.Rect((SCREEN_WIDTH - 200)//2, SCREEN_HEIGHT - 110, 200, 50)
    draw_button(screen, back_rect, "BACK HOME", GOLD)

def _draw_buy_mode(screen, player_inventory):
    # Draw Pigs in RIGHT column (Adoption shelves)
    if not logic_store.pigs_for_sale:
        txt = font_text.render("Sold Out!", True, GRAY)
        txt_rect = txt.get_rect(center=(PIG_START_X + PIG_CARD_W // 2, SHELF_START_Y + 60))
        screen.blit(txt, txt_rect)

    for i, pig in enumerate(logic_store.pigs_for_sale[:4]):  # Max 4 pigs for 4 shelves
        card_y = SHELF_START_Y + (i * (SHELF_HEIGHT + SHELF_SPACING))
        card_rect = pygame.Rect(PIG_START_X, card_y, PIG_CARD_W, PIG_CARD_H)

        # Semi-transparent card background
        card_surface = pygame.Surface((PIG_CARD_W, PIG_CARD_H), pygame.SRCALPHA)
        pygame.draw.rect(card_surface, (240, 240, 240, 200), card_surface.get_rect(), border_radius=8)
        screen.blit(card_surface, (PIG_START_X, card_y))

        name_surf = font_text.render(pig.name[:16], True, BLACK)
        price = getattr(pig, 'score', 200)
        score_surf = font_text.render(f"Cost: {price}", True, BLACK)

        screen.blit(name_surf, (PIG_START_X + 10, card_y + 10))
        screen.blit(score_surf, (PIG_START_X + 10, card_y + 32))

        btn_rect = pygame.Rect(PIG_START_X + 10, card_y + BTN_OFFSET_Y, 90, 28)
        color = GREEN if player_inventory.coins >= price else GRAY
        draw_button(screen, btn_rect, "Buy", color)

    # Draw Food in LEFT column (Food shelves)
    idx = 0
    for name, item in list(logic_store.food_catalog.items())[:4]:  # Max 4 foods for 4 shelves
        card_y = SHELF_START_Y + (idx * (SHELF_HEIGHT + SHELF_SPACING))
        card_rect = pygame.Rect(FOOD_START_X, card_y, FOOD_CARD_W, FOOD_CARD_H)

        # Semi-transparent card background
        card_surface = pygame.Surface((FOOD_CARD_W, FOOD_CARD_H), pygame.SRCALPHA)
        pygame.draw.rect(card_surface, (255, 255, 240, 200), card_surface.get_rect(), border_radius=8)
        screen.blit(card_surface, (FOOD_START_X, card_y))

        display_name = name if len(name) < 14 else name[:12] + ".."
        n_surf = font_text.render(display_name, True, BLACK)
        screen.blit(n_surf, (FOOD_START_X + 10, card_y + 10))

        btn_rect = pygame.Rect(FOOD_START_X + 10, card_y + BTN_OFFSET_Y, 90, 28)
        color = GREEN if player_inventory.coins >= item.price else GRAY
        draw_button(screen, btn_rect, f"${item.price}", color)
        idx += 1

def _draw_sell_mode(screen, player_inventory):
    if not player_inventory.owned_pigs:
        txt = font_text.render("You have no pets!", True, WHITE)
        screen.blit(txt, (SCREEN_WIDTH//2 - 80, 300))
        return

    # Display pigs in a 2-column grid matching the background shelves
    max_visible = 8  # 4 rows x 2 columns
    for i, pig in enumerate(player_inventory.owned_pigs[:max_visible]):
        col = i % 2  # 0 for left, 1 for right
        row = i // 2  # Which shelf row

        if col == 0:
            card_x = FOOD_START_X
            card_w = FOOD_CARD_W
        else:
            card_x = PIG_START_X
            card_w = PIG_CARD_W

        card_y = SHELF_START_Y + (row * (SHELF_HEIGHT + SHELF_SPACING))

        # Semi-transparent card background
        card_surface = pygame.Surface((card_w, FOOD_CARD_H), pygame.SRCALPHA)
        pygame.draw.rect(card_surface, (80, 80, 100, 220), card_surface.get_rect(), border_radius=8)
        pygame.draw.rect(card_surface, (255, 255, 255, 150), card_surface.get_rect(), 2, border_radius=8)
        screen.blit(card_surface, (card_x, card_y))

        # Info
        name_surf = font_text.render(pig.name[:13], True, WHITE)
        age_stage = pig.get_age_stage()
        age_color = GREEN if age_stage == 'Adult' else RED
        age_surf = font_text.render(age_stage, True, age_color)

        sell_val = pig.calculate_sell_price()
        val_surf = font_text.render(f"Val: {sell_val}", True, GOLD)

        screen.blit(name_surf, (card_x + 8, card_y + 8))
        screen.blit(age_surf, (card_x + 8, card_y + 28))
        screen.blit(val_surf, (card_x + 8, card_y + 48))

        # Sell Button
        sell_btn = pygame.Rect(card_x + 10, card_y + BTN_OFFSET_Y, 65, 25)
        can_sell = (age_stage == 'Adult')
        draw_button(screen, sell_btn, "Sell", GREEN if can_sell else GRAY)

        # Dev Age Button
        age_btn = pygame.Rect(card_x + 85, card_y + BTN_OFFSET_Y, 55, 25)
        draw_button(screen, age_btn, "Grow", BLUE)