import pygame
import time
import datetime
import os
import random
import sys

# --- Imports ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from guineapig import GuineaPigSprite
from details_popup import DetailsPopup
from api_client import api

# --- Colors ---
PANEL_GRAY = (235, 235, 235)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (50, 200, 50)
HOVER_GREEN = (70, 220, 70)
BAR_BG = (200, 200, 200)   # Grey background for the time bar
BAR_FILL = (0, 150, 255)   # Blue fill for the time bar

# --- Globals ---
font = None
sidebar_font = None
background = None
BG_POS = (0, 0)
house_data = {}
static_obstacles = []

# --- Logic Globals ---
game_time = {
    "year": 1, 
    "month": 1, 
    "day": 1, 
    "hour": 8, 
    "minute": 0
}

# --- ID LOOKUP ---
pet_id_lookup = {}

# --- SPEED SETTING ---
REAL_SECONDS_PER_GAME_MINUTE = 0.00694444

last_update = 0

# --- State ---
show_popup = False
popup_manager = None
visual_pigs = [] 
selected_pig_stats = None
needs_refresh = True 

# --- DEATH QUEUE ---
dead_pets_queue = [] 

# --- Data Cache ---
cached_user_data = None
cached_inventory = None

# --- UI ELEMENTS ---
feed_all_btn_rect = None

def make_glow(mask, intensity=22):
    """Soft, translucent Stardew-style glow."""
    w, h = mask.get_size()
    glow = pygame.Surface((w + intensity * 2, h + intensity * 2), pygame.SRCALPHA)
    base = mask.to_surface(setcolor=(255, 240, 150, 5), unsetcolor=(0, 0, 0, 0))
    base = base.convert_alpha()
    for dx in range(-intensity, intensity + 1):
        for dy in range(-intensity, intensity + 1):
            dist = abs(dx) + abs(dy)
            if dist <= intensity:
                alpha = max(1, 35 - dist * 1.4)
                temp = base.copy()
                temp.fill((255, 240, 150, alpha), special_flags=pygame.BLEND_RGBA_MULT)
                glow.blit(temp, (dx + intensity, dy + intensity))
    return glow

def homescreen_init(screen_w, screen_h):
    global font, sidebar_font, background, BG_POS, house_data, popup_manager, static_obstacles, feed_all_btn_rect

    pygame.font.init()
    font = pygame.font.Font(None, 40)
    sidebar_font = pygame.font.Font(None, 26)
    
    popup_manager = DetailsPopup()

    # --- SETUP FEED BUTTON ---
    feed_all_btn_rect = pygame.Rect(screen_w - 170, 250, 140, 40)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    bg_path = os.path.join(current_dir, "images", "BG_Home.png")

    try:
        raw_bg = pygame.image.load(bg_path).convert_alpha()
    except FileNotFoundError:
        print(f"Background not found at {bg_path}, using placeholder.")
        raw_bg = pygame.Surface((800, 600))
        raw_bg.fill((100, 100, 200)) 

    raw_w, raw_h = raw_bg.get_width(), raw_bg.get_height()
    scale = screen_h / raw_h
    new_w = int(raw_w * scale)
    new_h = int(raw_h * scale)

    background = pygame.transform.scale(raw_bg, (new_w, new_h))
    BG_POS = ((screen_w - new_w) // 2, 0)

    # --- DEFINING BUILDINGS ---
    houses_original = {
        "home":       (132, 83, 215, 232),
        "mini_games": (348, 331, 202, 215),
        "store":      (423, 624, 195, 178),
        "training":   (50,  328, 198, 183), 
        "breeding":   (156, 535, 218, 200),
    }

    house_data = {}
    for name, (ox, oy, ow, oh) in houses_original.items():
        try:
            house_img = raw_bg.subsurface(pygame.Rect(ox, oy, ow, oh)).copy()
            sw, sh = int(ow * scale), int(oh * scale)
            house_img = pygame.transform.scale(house_img, (sw, sh))
            mask = pygame.mask.from_surface(house_img)
            glow = make_glow(mask, intensity=22)
            
            sx = int(ox * scale) + BG_POS[0]
            sy = int(oy * scale) + BG_POS[1]
            
            rect = pygame.Rect(sx, sy, sw, sh)
            house_data[name] = {"rect": rect, "img": house_img, "mask": mask, "glow": glow}
        except ValueError:
            print(f"Warning: Could not extract sprite for {name}. Check coordinates.")

    # --- DEFINING EXTRA OBSTACLES ---
    obstacles_original = [
        (30, 480, 120, 100),   
        (220, 580, 100, 40),   
        (120, 650, 150, 40),   
    ]
    
    static_obstacles = []
    for (ox, oy, ow, oh) in obstacles_original:
        sx = int(ox * scale) + BG_POS[0]
        sy = int(oy * scale) + BG_POS[1]
        sw = int(ow * scale)
        sh = int(oh * scale)
        static_obstacles.append(pygame.Rect(sx, sy, sw, sh))

def refresh_game_state(user_id):
    """Fetches ALL data from API at once."""
    global visual_pigs, house_data, static_obstacles, cached_user_data, cached_inventory, pet_id_lookup
    
    print("Refreshing game state...") 

    # 1. Fetch User Data (Sidebar)
    try:
        cached_user_data = api.get_user(user_id)
        cached_inventory = api.get_user_inventory(user_id)
    except Exception as e:
        print(f"API Error fetching user data: {e}")

    # 2. Fetch Pets (Visuals)
    try:
        my_pets = api.get_user_pets(user_id)
    except Exception as e:
        print(f"API Error fetching pets: {e}")
        return

    # --- STEP 2.5: Build ID Lookup & Filter Dead ---
    pet_id_lookup.clear()
    
    existing_sprites = {s.data['id']: s for s in visual_pigs}
    new_visual_pigs = []
    
    screen = pygame.display.get_surface()
    if screen: sw, sh = screen.get_size()
    else: sw, sh = 800, 600

    pad = 20
    yard_min_x, yard_max_x = pad, sw - 60 - pad 
    yard_min_y, yard_max_y = 300, sh - 60 - pad
    
    for pet_data in my_pets:
        # Save ID for lookup (even if dead)
        p_name = pet_data.get('name')
        p_id = pet_data.get('id')
        if p_name:
            pet_id_lookup[p_name] = p_id

        # SKIP VISUALS IF DEAD
        if pet_data.get('health', 100) <= 0:
            continue

        # ... Create Sprite Logic ...
        sprite = None
        needs_new_spot = True

        if p_id in existing_sprites:
            sprite = existing_sprites[p_id]
            sprite.data = pet_data
            
            is_safe = True
            for house_info in house_data.values():
                if sprite.rect.colliderect(house_info["rect"].inflate(-10, -10)):
                    is_safe = False; break
            
            if is_safe:
                needs_new_spot = False 
                new_visual_pigs.append(sprite)

        if needs_new_spot:
            final_pos = None
            for _ in range(100): 
                rx = random.randint(int(yard_min_x), int(yard_max_x))
                ry = random.randint(int(yard_min_y), int(yard_max_y))
                potential_rect = pygame.Rect(rx, ry, 60, 50)
                collision = False
                
                for house_info in house_data.values():
                    if potential_rect.colliderect(house_info["rect"]): collision = True; break
                if not collision:
                    for obs in static_obstacles:
                        if potential_rect.colliderect(obs): collision = True; break
                if not collision:
                    for existing_pig in new_visual_pigs:
                        if potential_rect.colliderect(existing_pig.rect.inflate(10, 10)): collision = True; break
                if not collision:
                    final_pos = (rx, ry); break 
            
            if final_pos is None:
                safe_x = pad + (len(new_visual_pigs) * 65) % (sw - 100)
                safe_y = sh - 70 
                final_pos = (safe_x, safe_y)

            if sprite:
                sprite.rect.topleft = final_pos
                new_visual_pigs.append(sprite)
            else:
                new_sprite = GuineaPigSprite(final_pos[0], final_pos[1], pet_data)
                new_visual_pigs.append(new_sprite)

    visual_pigs = new_visual_pigs

def homescreen_update(events, user_id):
    global last_update, game_time, show_popup, selected_pig_stats, needs_refresh, dead_pets_queue, pet_id_lookup

    # --- 1. HANDLE DEATH QUEUE ---
    while dead_pets_queue and not show_popup:
        dead_name = dead_pets_queue.pop(0)
        
        # Try to find the image from visual pigs
        img = None
        for p in visual_pigs:
            if p.data['name'] == dead_name:
                img = p.image
                break
        
        # Try to find ID from global lookup
        pid = pet_id_lookup.get(dead_name)

        selected_pig_stats = {
            "Name": dead_name,
            "is_dead": True,
            "image_surface": img,
            "id": pid  # Pass ID to popup stats
        }
        show_popup = True
        break

    # --- 2. HANDLE REFRESH ---
    if needs_refresh and not show_popup:
        refresh_game_state(user_id)
        needs_refresh = False

    # --- 3. POPUP LOGIC ---
    if show_popup:
        for event in events:
            action = popup_manager.handle_event(event)
            if action == "close":
                
                # --- NEW: DELETE PET ON CLOSE ---
                if selected_pig_stats.get('is_dead') and selected_pig_stats.get('id'):
                    pid_to_delete = selected_pig_stats['id']
                    print(f"User acknowledged death. Deleting pet {pid_to_delete}...")
                    try:
                        # Attempt to call delete_pet on api
                        if hasattr(api, 'delete_pet'):
                            api.delete_pet(pid_to_delete)
                        else:
                            # Fallback if specific method doesn't exist
                            api._post(f"/pets/{pid_to_delete}/delete") 
                        print("Pet deleted successfully.")
                    except Exception as e:
                        print(f"Error deleting pet: {e}")

                show_popup = False
                needs_refresh = True 
        return None

    # --- 4. CLOCK LOGIC ---
    now = time.time()
    if last_update == 0: last_update = now
    
    day_change_triggered = False

    while now - last_update >= REAL_SECONDS_PER_GAME_MINUTE:
        last_update += REAL_SECONDS_PER_GAME_MINUTE
        game_time["minute"] += 1
        if game_time["minute"] >= 60:
            game_time["minute"] = 0
            game_time["hour"] += 1
        if game_time["hour"] >= 24:
            game_time["hour"] = 0
            game_time["day"] += 1 
            day_change_triggered = True
            
            if game_time["day"] > 30:
                game_time["day"] = 1
                game_time["month"] += 1
            if game_time["month"] > 12:
                game_time["month"] = 1
                game_time["year"] += 1

    if day_change_triggered:
        print(f"Day changed to {game_time['day']}. Processing decay...")
        try:
            result = api.trigger_daily_decay(user_id)
            if result.get("dead_pets"):
                dead_pets_queue.extend(result['dead_pets'])
            needs_refresh = True
        except Exception as e:
            print(f"Error processing decay: {e}")

    # --- 5. INTERACTION ---
    mouse_pos = pygame.mouse.get_pos()
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t: # Debug Time Skip
                game_time["day"] += 1
                game_time["hour"] = 8 
                needs_refresh = True 

        if event.type == pygame.MOUSEBUTTONDOWN:
            if feed_all_btn_rect and feed_all_btn_rect.collidepoint(mouse_pos):
                print("Attempting to feed all pets...")
                try:
                    response = api._post(f"/pets/feed/all/{user_id}")
                    if isinstance(response, dict) and not response.get('success', True):
                         print(f"Feed Failed: {response.get('message', 'Unknown error')}")
                    else:
                         print(f"Feed Success: {response.get('message', 'Pets fed')}")
                    needs_refresh = True 
                except Exception as e:
                    print(f"Feed All Error: {e}")
                return None

            # Check Pigs
            clicked_pig = False
            for sprite in reversed(visual_pigs):
                if sprite.is_clicked(mouse_pos):
                    selected_pig_stats = sprite.get_stats()
                    show_popup = True
                    clicked_pig = True
                    break 
            
            if clicked_pig: return None

            # Check Buildings
            for name, data in house_data.items():
                if data["rect"].collidepoint(mouse_pos): 
                    # --- CHANGE: Training building now returns 'help' ---
                    if name == 'training':
                        return 'help'
                    else:
                        return name
    
    # --- 6. ANIMATION ---
    screen = pygame.display.get_surface()
    if screen:
        screen_rect = screen.get_rect()
        for sprite in visual_pigs:
            if hasattr(sprite, 'update'): sprite.update()
            sprite.rect.clamp_ip(screen_rect)

    return None

def homescreen_draw(screen, user_id, current_ticks=0):
    if not background: screen.fill(BLACK)
    else:
        screen.fill(BLACK)
        screen.blit(background, BG_POS)
    
    mouse_pos = pygame.mouse.get_pos()

    # Draw Buildings
    for name, data in house_data.items():
        rect = data["rect"]
        glow = data["glow"]
        hovering = False
        if not show_popup:
            if rect.collidepoint(mouse_pos): hovering = True

        if hovering:
            gx = rect.x - (glow.get_width() - rect.width) // 2
            gy = rect.y - (glow.get_height() - rect.height) // 2
            screen.blit(glow, (gx, gy))

            display_name = name.replace("_", " ").title()
            text_surf = font.render(display_name, True, (255, 255, 255))
            shadow_surf = font.render(display_name, True, (0, 0, 0))
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(shadow_surf, (text_rect.x + 2, text_rect.y + 2))
            screen.blit(text_surf, text_rect)

    # Draw Pigs
    visual_pigs.sort(key=lambda p: p.rect.centery)
    for sprite in visual_pigs:
        sprite.draw(screen)

    # --- DRAW SIDEBAR ---
    w, h = screen.get_size()
    pygame.draw.rect(screen, PANEL_GRAY, (w - 180, 20, 160, 280)) 
    
    h_24 = game_time['hour']
    m = game_time['minute']
    ampm = "AM" if h_24 < 12 else "PM"
    h_12 = h_24 % 12
    if h_12 == 0: h_12 = 12
    game_clock_str = f"{h_12}:{m:02d} {ampm}"
    
    coins = cached_user_data['balance'] if cached_user_data else 0
    food_count = sum(item['quantity'] for item in cached_inventory) if cached_inventory else 0
    
    sidebar_lines = [
        f"Year: {game_time['year']}",
        f"Month: {game_time['month']}",
        f"Day: {game_time['day']}",
        "",
        f"{game_clock_str}", 
        "",
        f"Coins: {coins}",
        f"Food: {food_count}",
        "",
        f"Pets: {len(visual_pigs)}",
    ]

    y = 40
    for i, line in enumerate(sidebar_lines):
        text_surface = sidebar_font.render(line, True, BLACK)
        screen.blit(text_surface, (w - 170, y))
        
        # Draw Time Progress Bar under the Clock (index 4)
        if i == 4:
            MAX_TICKS = 18000 # Use default production value, main.py overrides for testing
            bar_w = 140
            bar_h = 6
            bar_x = w - 170
            bar_y = y + 22
            
            fill_pct = min(current_ticks / MAX_TICKS, 1.0)
            fill_w = int(bar_w * fill_pct)
            
            pygame.draw.rect(screen, BAR_BG, (bar_x, bar_y, bar_w, bar_h))
            if fill_w > 0:
                pygame.draw.rect(screen, BAR_FILL, (bar_x, bar_y, fill_w, bar_h))
            
            y += 10 # Extra spacing for bar

        y += 20

    # --- DRAW AUTOFEED BUTTON ---
    if feed_all_btn_rect:
        hover = feed_all_btn_rect.collidepoint(mouse_pos)
        col = HOVER_GREEN if hover else GREEN
        pygame.draw.rect(screen, col, feed_all_btn_rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, feed_all_btn_rect, 2, border_radius=8)
        
        btn_txt = sidebar_font.render("AUTOFEED ALL", True, WHITE)
        txt_rect = btn_txt.get_rect(center=feed_all_btn_rect.center)
        screen.blit(btn_txt, txt_rect)

    # Draw Popup if active
    if show_popup and popup_manager and selected_pig_stats:
        overlay = pygame.Surface((w, h))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        popup_manager.draw(screen, selected_pig_stats)