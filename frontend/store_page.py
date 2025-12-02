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

# --- Global Store Instance ---
logic_store = Store()

# --- LAYOUT CONSTANTS (Fits 672px Width) ---
SCREEN_WIDTH = 672

# Pig Layout
PIG_START_X = 25
PIG_START_Y = 100
PIG_CARD_W = 200
PIG_CARD_H = 180
PIG_SPACING = 215
PIG_BTN_OFFSET_Y = 140

# Food Layout
FOOD_START_X = 25
FOOD_START_Y = 350
FOOD_CARD_W = 145
FOOD_CARD_H = 140
FOOD_SPACING = 155
FOOD_BTN_OFFSET_Y = 100

# State
store_mode = 'BUY' # 'BUY' or 'SELL'

def store_init():
    global font_title, font_text
    pygame.font.init()
    font_title = pygame.font.Font(None, 50)
    font_text = pygame.font.Font(None, 24)

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
            back_rect = pygame.Rect((SCREEN_WIDTH - 200)//2, 530, 200, 50)
            if back_rect.collidepoint(mouse_pos):
                return 'homescreen'

            # Check 'Toggle Mode' Button
            mode_rect = pygame.Rect(SCREEN_WIDTH - 160, 60, 140, 30)
            if mode_rect.collidepoint(mouse_pos):
                store_mode = 'SELL' if store_mode == 'BUY' else 'BUY'
                return None

            if store_mode == 'BUY':
                # --- BUY LOGIC ---
                # 1. Buy Pigs
                for i, pig in enumerate(logic_store.pigs_for_sale):
                    card_x = PIG_START_X + (i * PIG_SPACING)
                    btn_rect = pygame.Rect(card_x + 20, PIG_START_Y + PIG_BTN_OFFSET_Y, 160, 30)
                    
                    if btn_rect.collidepoint(mouse_pos):
                        if logic_store.buy_guinea_pig(player_inventory, i):
                            print(f"Bought {pig.name}!")
                        return None 

                # 2. Buy Food
                idx = 0
                for name, item in logic_store.food_catalog.items():
                    card_x = FOOD_START_X + (idx * FOOD_SPACING)
                    btn_rect = pygame.Rect(card_x + 10, FOOD_START_Y + FOOD_BTN_OFFSET_Y, FOOD_CARD_W - 20, 30)
                    
                    if btn_rect.collidepoint(mouse_pos):
                        if logic_store.buy_food(player_inventory, name):
                            print(f"Bought {name}!")
                        return None
                    idx += 1
            
            else:
                # --- SELL LOGIC ---
                for i, pig in enumerate(player_inventory.owned_pigs):
                    row = i // 3
                    col = i % 3
                    card_x = PIG_START_X + (col * PIG_SPACING)
                    card_y = PIG_START_Y + (row * (PIG_CARD_H + 20))
                    
                    # Sell Button
                    sell_btn = pygame.Rect(card_x + 20, card_y + PIG_BTN_OFFSET_Y, 80, 30)
                    
                    # Dev Age Button
                    age_btn = pygame.Rect(card_x + 110, card_y + PIG_BTN_OFFSET_Y, 70, 30)
                    
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

    # Back Button
    back_rect = pygame.Rect((SCREEN_WIDTH - 200)//2, 530, 200, 50)
    draw_button(screen, back_rect, "BACK HOME", GOLD)

def _draw_buy_mode(screen, player_inventory):
    # Pigs
    if not logic_store.pigs_for_sale:
        txt = font_text.render("Sold Out! Check back later.", True, GRAY)
        txt_rect = txt.get_rect(center=(SCREEN_WIDTH // 2, PIG_START_Y + 90))
        screen.blit(txt, txt_rect)
    
    for i, pig in enumerate(logic_store.pigs_for_sale):
        card_x = PIG_START_X + (i * PIG_SPACING)
        card_rect = pygame.Rect(card_x, PIG_START_Y, PIG_CARD_W, PIG_CARD_H)
        pygame.draw.rect(screen, PANEL_GRAY, card_rect, border_radius=10)
        
        name_surf = font_text.render(pig.name[:12], True, BLACK)
        price = getattr(pig, 'score', 200)
        score_surf = font_text.render(f"Cost: {price}", True, BLACK)
        
        screen.blit(name_surf, (card_x + 20, PIG_START_Y + 20))
        screen.blit(score_surf, (card_x + 20, PIG_START_Y + 50))
        
        btn_rect = pygame.Rect(card_x + 20, PIG_START_Y + PIG_BTN_OFFSET_Y, 160, 30)
        color = GREEN if player_inventory.coins >= price else GRAY
        draw_button(screen, btn_rect, "Buy", color)

    # Food
    separator_y = FOOD_START_Y - 40
    pygame.draw.line(screen, GRAY, (50, separator_y), (SCREEN_WIDTH - 50, separator_y), 3)
    food_lbl = font_title.render("Food & Buffs", True, WHITE)
    screen.blit(food_lbl, (50, separator_y + 10))

    idx = 0
    for name, item in logic_store.food_catalog.items():
        card_x = FOOD_START_X + (idx * FOOD_SPACING)
        card_rect = pygame.Rect(card_x, FOOD_START_Y, FOOD_CARD_W, FOOD_CARD_H)
        pygame.draw.rect(screen, (240, 240, 220), card_rect, border_radius=8)
        
        display_name = name if len(name) < 11 else name[:9] + ".."
        n_surf = font_text.render(display_name, True, BLACK)
        
        screen.blit(n_surf, (card_x + 10, FOOD_START_Y + 10))
        
        btn_rect = pygame.Rect(card_x + 10, FOOD_START_Y + FOOD_BTN_OFFSET_Y, FOOD_CARD_W - 20, 30)
        color = GREEN if player_inventory.coins >= item.price else GRAY
        draw_button(screen, btn_rect, f"${item.price}", color)
        idx += 1

def _draw_sell_mode(screen, player_inventory):
    subtitle = font_text.render("Your Pets (Sell Adults)", True, WHITE)
    screen.blit(subtitle, (20, 65))
    
    if not player_inventory.owned_pigs:
        txt = font_text.render("You have no pets!", True, GRAY)
        screen.blit(txt, (SCREEN_WIDTH//2 - 80, 200))
        return

    for i, pig in enumerate(player_inventory.owned_pigs):
        # Grid layout
        row = i // 3
        col = i % 3
        
        card_x = PIG_START_X + (col * PIG_SPACING)
        card_y = PIG_START_Y + (row * (PIG_CARD_H + 20))
        
        # Clip if too many
        if card_y > 450: break 

        card_rect = pygame.Rect(card_x, card_y, PIG_CARD_W, PIG_CARD_H)
        pygame.draw.rect(screen, (60, 60, 80), card_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, card_rect, 2, border_radius=10)
        
        # Info
        name_surf = font_text.render(pig.name[:12], True, WHITE)
        age_stage = pig.get_age_stage()
        age_color = GREEN if age_stage == 'Adult' else RED
        age_surf = font_text.render(age_stage, True, age_color)
        
        sell_val = pig.calculate_sell_price()
        val_surf = font_text.render(f"Value: {sell_val}", True, GOLD)

        screen.blit(name_surf, (card_x + 10, card_y + 10))
        screen.blit(age_surf, (card_x + 10, card_y + 40))
        screen.blit(val_surf, (card_x + 10, card_y + 70))
        
        # Sell Button
        sell_btn = pygame.Rect(card_x + 20, card_y + PIG_BTN_OFFSET_Y, 80, 30)
        can_sell = (age_stage == 'Adult')
        draw_button(screen, sell_btn, "Sell", GREEN if can_sell else GRAY)
        
        # Dev Age Button
        age_btn = pygame.Rect(card_x + 110, card_y + PIG_BTN_OFFSET_Y, 70, 30)
        draw_button(screen, age_btn, "Grow", BLUE)