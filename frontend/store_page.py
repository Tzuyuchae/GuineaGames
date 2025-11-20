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
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
PANEL_GRAY = (220, 220, 220) # <--- Moved this to the top!

font_title = None
font_text = None

# --- Global Store Instance ---
logic_store = Store()

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
    """
    Handles clicks for buying pigs/food and navigation.
    Returns 'homescreen' if back is clicked, else None.
    """
    mouse_pos = pygame.mouse.get_pos()
    
    # Refresh store timer
    logic_store.check_refresh_timer()

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            
            # 1. Check 'Back' Button (Bottom Center)
            back_rect = pygame.Rect(300, 530, 200, 50)
            if back_rect.collidepoint(mouse_pos):
                return 'homescreen'

            # 2. Check Pig Buy Buttons
            start_x, start_y = 50, 100
            for i, pig in enumerate(logic_store.pigs_for_sale):
                card_x = start_x + (i * 240)
                # This rect must match the one in store_draw
                btn_rect = pygame.Rect(card_x + 20, start_y + 140, 160, 30)
                
                if btn_rect.collidepoint(mouse_pos):
                    if logic_store.buy_guinea_pig(player_inventory, i):
                        print(f"Bought {pig.name}!")
                    else:
                        print("Not enough coins or error!")
                    return None 

            # 3. Check Food Buy Buttons
            food_start_y = 350
            idx = 0
            for name, item in logic_store.food_catalog.items():
                card_x = 30 + (idx * 190)
                btn_rect = pygame.Rect(card_x + 10, food_start_y + 100, 150, 30)
                
                if btn_rect.collidepoint(mouse_pos):
                    if logic_store.buy_food(player_inventory, name):
                        print(f"Bought {name}!")
                    else:
                        print("Not enough coins!")
                    return None
                idx += 1

    return None

def store_draw(screen, player_inventory):
    screen.fill((50, 50, 70)) # Dark blue background

    # --- Header ---
    title = font_title.render("General Store", True, WHITE)
    screen.blit(title, (300, 20))

    # Coins Display
    coins_text = font_title.render(f"Coins: {player_inventory.coins}", True, GOLD)
    screen.blit(coins_text, (600, 20))

    # Refresh Timer
    secs = logic_store.get_time_until_refresh()
    timer_txt = font_text.render(f"New Pigs in: {logic_store._format_time(secs)}", True, WHITE)
    screen.blit(timer_txt, (20, 30))

    # --- SECTION 1: PIGS ---
    start_x, start_y = 50, 100
    
    if not logic_store.pigs_for_sale:
        txt = font_text.render("Sold Out! Check back later.", True, GRAY)
        screen.blit(txt, (300, 150))
    
    for i, pig in enumerate(logic_store.pigs_for_sale):
        card_x = start_x + (i * 240)
        card_rect = pygame.Rect(card_x, start_y, 200, 180)
        
        # Draw Card Background (Now PANEL_GRAY is defined!)
        pygame.draw.rect(screen, PANEL_GRAY, card_rect, border_radius=10)
        
        # Draw Pig details
        name_surf = font_text.render(pig.name, True, BLACK)
        score_surf = font_text.render(f"Score: {pig.score}", True, BLACK)
        
        screen.blit(name_surf, (card_x + 20, start_y + 20))
        screen.blit(score_surf, (card_x + 20, start_y + 50))
        
        # Draw Buy Button
        btn_rect = pygame.Rect(card_x + 20, start_y + 140, 160, 30)
        color = GREEN if player_inventory.coins >= pig.score else GRAY
        draw_button(screen, btn_rect, f"Buy for {pig.score}", color)

    # --- SECTION 2: FOOD ---
    pygame.draw.line(screen, GRAY, (50, 310), (750, 310), 3)
    food_lbl = font_title.render("Food & Buffs", True, WHITE)
    screen.blit(food_lbl, (50, 320))

    food_start_y = 350
    idx = 0
    for name, item in logic_store.food_catalog.items():
        card_x = 30 + (idx * 190)
        card_rect = pygame.Rect(card_x, food_start_y, 170, 140)
        
        pygame.draw.rect(screen, (240, 240, 220), card_rect, border_radius=8)
        
        # Details
        n_surf = font_text.render(name, True, BLACK)
        e_surf = font_text.render(item.effect_type[:10], True, (50, 50, 150))
        
        screen.blit(n_surf, (card_x + 10, food_start_y + 10))
        screen.blit(e_surf, (card_x + 10, food_start_y + 40))

        # Buy Button
        btn_rect = pygame.Rect(card_x + 10, food_start_y + 100, 150, 30)
        color = GREEN if player_inventory.coins >= item.price else GRAY
        draw_button(screen, btn_rect, f"${item.price}", color)
        
        idx += 1

    # --- Back Button ---
    back_rect = pygame.Rect(300, 530, 200, 50)
    draw_button(screen, back_rect, "BACK HOME", GOLD)