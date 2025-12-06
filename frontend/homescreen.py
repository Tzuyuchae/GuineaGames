import pygame
import time
import datetime
import os
import random

# --- Imports ---
from guineapig import GuineaPigSprite
from details_popup import DetailsPopup
from api_client import api

# --- Colors ---
PANEL_GRAY = (235, 235, 235)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# --- Globals ---
font = None
sidebar_font = None
background = None
BG_POS = (0, 0)
house_data = {}
static_obstacles = []

# --- Logic Globals ---
# Start at 8:00 AM
game_time = {
    "year": 1, "month": 1, "day": 1, "hour": 8, "minute": 0
}

# --- SPEED SETTING ---
# 0.005 = Super Fast (Dev Mode)
# 0.05  = Playable Fast (1 Game Day = ~1 min 12 sec)
# 0.1   = Relaxed (1 Game Day = ~2 min 24 sec)
REAL_SECONDS_PER_GAME_MINUTE = 0.05 

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
    global font, sidebar_font, background, BG_POS, house_data, popup_manager, static_obstacles

    pygame.font.init()
    font = pygame.font.Font(None, 40)
    sidebar_font = pygame.font.Font(None, 26)
    
    popup_manager = DetailsPopup()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    bg_path = os.path.join(current_dir, "images", "BG_Home.png")

    try:
        raw_bg = pygame.image.load(bg_path).convert_alpha()
    except FileNotFoundError:
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
        house_img = raw_bg.subsurface(pygame.Rect(ox, oy, ow, oh)).copy()
        sw, sh = int(ow * scale), int(oh * scale)
        house_img = pygame.transform.scale(house_img, (sw, sh))
        mask = pygame.mask.from_surface(house_img)
        glow = make_glow(mask, intensity=22)
        
        sx = int(ox * scale) + BG_POS[0]
        sy = int(oy * scale) + BG_POS[1]
        
        rect = pygame.Rect(sx, sy, sw, sh)
        house_data[name] = {"rect": rect, "img": house_img, "mask": mask, "glow": glow}

    # --- DEFINING EXTRA OBSTACLES (Trees, Fences) ---
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
    """
    Fetches ALL data from API at once.
    Only called when necessary (Startup, Popup Close, Day Change).
    """
    global visual_pigs, house_data, static_obstacles, cached_user_data, cached_inventory
    
    print("Refreshing game state...") 

    # 1. Fetch User Data (Sidebar)
    try:
        cached_user_data = api.get_user(user_id)
        cached_inventory = api.get_user_inventory(user_id)
    except Exception as e:
        # print(f"Sidebar update failed: {e}")
        pass

    # 2. Fetch Pets (Visuals)
    try:
        my_pets = api.get_user_pets(user_id)
    except Exception:
        return

    existing_sprites = {s.data['id']: s for s in visual_pigs}
    new_visual_pigs = []
    
    screen = pygame.display.get_surface()
    sw, sh = screen.get_size()

    pad = 20
    yard_min_x, yard_max_x = pad, sw - 60 - pad 
    yard_min_y, yard_max_y = 300, sh - 60 - pad
    
    for pet_data in my_pets:
        pid = pet_data['id']
        sprite = None
        needs_new_spot = True

        if pid in existing_sprites:
            sprite = existing_sprites[pid]
            sprite.data = pet_data # Update stats in existing sprite
            
            is_safe = True
            for house_info in house_data.values():
                if sprite.rect.colliderect(house_info["rect"].inflate(-10, -10)):
                    is_safe = False
                    break
            
            if is_safe:
                for obs in static_obstacles:
                    if sprite.rect.colliderect(obs):
                        is_safe = False
                        break

            if is_safe:
                for other_pig in new_visual_pigs:
                    if sprite.rect.colliderect(other_pig.rect):
                        is_safe = False
                        break
            
            if is_safe:
                needs_new_spot = False 
                new_visual_pigs.append(sprite)

        if needs_new_spot:
            final_pos = None
            for _ in range(100): 
                rx = random.randint(yard_min_x, yard_max_x)
                ry = random.randint(yard_min_y, yard_max_y)
                potential_rect = pygame.Rect(rx, ry, 60, 50)
                collision = False
                
                for house_info in house_data.values():
                    if potential_rect.colliderect(house_info["rect"]):
                        collision = True
                        break
                if not collision:
                    for obs in static_obstacles:
                        if potential_rect.colliderect(obs):
                            collision = True
                            break
                if not collision:
                    for existing_pig in new_visual_pigs:
                        if potential_rect.colliderect(existing_pig.rect.inflate(10, 10)):
                            collision = True
                            break
                if not collision:
                    final_pos = (rx, ry)
                    break 
            
            if final_pos is None:
                safe_x = pad + (len(new_visual_pigs) * 65) % (sw - 100)
                safe_y = sh - 70 
                final_pos = (safe_x, safe_y)

            if sprite:
                sprite.rect.topleft = final_pos
                if hasattr(sprite, 'x'): sprite.x = final_pos[0]
                if hasattr(sprite, 'y'): sprite.y = final_pos[1]
                new_visual_pigs.append(sprite)
            else:
                new_sprite = GuineaPigSprite(final_pos[0], final_pos[1], pet_data)
                new_visual_pigs.append(new_sprite)

    visual_pigs = new_visual_pigs

def homescreen_update(events, user_id):
    global last_update, game_time, show_popup, selected_pig_stats, needs_refresh, dead_pets_queue

    # --- 1. HANDLE DEATH QUEUE ---
    # If there are dead pets pending, show popup for the first one
    if dead_pets_queue and not show_popup:
        dead_name = dead_pets_queue.pop(0)
        
        # Try to find its sprite to get the image before it vanishes
        img = None
        for p in visual_pigs:
            if p.data['name'] == dead_name:
                img = p.image
                break
        
        selected_pig_stats = {
            "Name": dead_name,
            "is_dead": True,
            "image_surface": img
        }
        show_popup = True
        return None

    # --- 2. HANDLE REFRESH ---
    if needs_refresh and not show_popup:
        refresh_game_state(user_id)
        needs_refresh = False

    # --- 3. POPUP LOGIC ---
    if show_popup:
        for event in events:
            action = popup_manager.handle_event(event)
            if action == "close":
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
                print(f"Queueing death popups for: {result['dead_pets']}")
            
            if not result.get("dead_pets"):
                needs_refresh = True
                
        except Exception as e:
            print(f"Error processing decay: {e}")

    # --- 5. INTERACTION ---
    mouse_pos = pygame.mouse.get_pos()
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            # === DEBUG: Press 'T' to skip a day (Kept for manual testing) ===
            if event.key == pygame.K_t:
                print("DEBUG: Skipping Day...")
                game_time["day"] += 1
                game_time["hour"] = 8 
                needs_refresh = True 

        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked_pig = False
            for sprite in reversed(visual_pigs):
                if sprite.is_clicked(mouse_pos):
                    selected_pig_stats = sprite.get_stats()
                    show_popup = True
                    clicked_pig = True
                    break 
            
            if clicked_pig:
                return None

            for name, data in house_data.items():
                rect = data["rect"]
                if rect.collidepoint(mouse_pos):
                    return name
    
    # --- 6. ANIMATION ---
    screen = pygame.display.get_surface()
    screen_rect = screen.get_rect()
    
    for sprite in visual_pigs:
        if hasattr(sprite, 'update'):
            sprite.update()
        sprite.rect.clamp_ip(screen_rect)

    return None

def homescreen_draw(screen, user_id):
    screen.fill(BLACK)
    screen.blit(background, BG_POS)
    
    mouse_pos = pygame.mouse.get_pos()

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

    visual_pigs.sort(key=lambda p: p.rect.centery)
    for sprite in visual_pigs:
        sprite.draw(screen)

    w, h = screen.get_size()
    pygame.draw.rect(screen, PANEL_GRAY, (w - 180, 20, 160, 220))
    
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
    for line in sidebar_lines:
        text_surface = sidebar_font.render(line, True, BLACK)
        screen.blit(text_surface, (w - 170, y))
        y += 20

    if show_popup and popup_manager and selected_pig_stats:
        overlay = pygame.Surface((w, h))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        popup_manager.draw(screen, selected_pig_stats)