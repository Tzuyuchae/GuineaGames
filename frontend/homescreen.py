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
static_obstacles = [] # New list for trees, fences, etc.

# --- Logic Globals ---
game_time = {
    "year": 1, "month": 1, "day": 1, "hour": 12, "minute": 0, "am": True
}
REAL_SECONDS_PER_GAME_MINUTE = 0.07
last_update = 0

# --- State ---
show_popup = False
popup_manager = None
visual_pigs = [] 
selected_pig_stats = None

# --- API Caching ---
last_api_fetch_time = 0
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
        print("Background loaded successfully.")
    except FileNotFoundError:
        print("ERROR: BG_Home.png not found. Creating placeholder.")
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
    # These are approximations based on the background image 800x600 reference
    obstacles_original = [
        (30, 480, 120, 100),   # The Big Tree on the left
        (220, 580, 100, 40),   # Fence bottom left
        (120, 650, 150, 40),   # Fence bottom center
    ]
    
    static_obstacles = []
    for (ox, oy, ow, oh) in obstacles_original:
        sx = int(ox * scale) + BG_POS[0]
        sy = int(oy * scale) + BG_POS[1]
        sw = int(ow * scale)
        sh = int(oh * scale)
        static_obstacles.append(pygame.Rect(sx, sy, sw, sh))


def refresh_visual_pigs(user_id):
    """
    Fetch pets and update sprites.
    Strictly ensures pigs do not overlap buildings, trees, or each other.
    """
    global visual_pigs, house_data, static_obstacles
    
    try:
        my_pets = api.get_user_pets(user_id)
    except Exception:
        return

    existing_sprites = {s.data['id']: s for s in visual_pigs}
    new_visual_pigs = []
    
    screen = pygame.display.get_surface()
    sw, sh = screen.get_size()

    # Define the yard area
    pad = 20
    yard_min_x, yard_max_x = pad, sw - 60 - pad 
    yard_min_y, yard_max_y = 300, sh - 60 - pad
    
    for pet_data in my_pets:
        pid = pet_data['id']
        sprite = None
        needs_new_spot = True

        # 1. Check if we already have this pig
        if pid in existing_sprites:
            sprite = existing_sprites[pid]
            sprite.data = pet_data # Update stats
            
            # CRITICAL FIX: Check if the EXISTING pig is currently in a bad spot.
            # If they are overlapping something, we force them to move.
            is_safe = True
            
            # Check overlap with buildings
            for house_info in house_data.values():
                if sprite.rect.colliderect(house_info["rect"].inflate(-10, -10)):
                    is_safe = False
                    break
            
            # Check overlap with static obstacles (trees)
            if is_safe:
                for obs in static_obstacles:
                    if sprite.rect.colliderect(obs):
                        is_safe = False
                        break

            # Check overlap with pigs processed SO FAR in this loop
            if is_safe:
                for other_pig in new_visual_pigs:
                    if sprite.rect.colliderect(other_pig.rect):
                        is_safe = False
                        break
            
            if is_safe:
                needs_new_spot = False # It's safe, leave it alone
                new_visual_pigs.append(sprite)

        # 2. If it's a new pig OR the old pig was in a bad spot, find a new spot
        if needs_new_spot:
            final_pos = None
            
            # Create a new sprite instance if needed, or reuse old one to keep image cache
            if sprite is None:
                # Temp sprite just to get rect size? We'll assume 60x60 for calculation
                pass

            # Attempt 100 times to find a clear spot
            for _ in range(100): 
                rx = random.randint(yard_min_x, yard_max_x)
                ry = random.randint(yard_min_y, yard_max_y)
                
                # Assume Pig is roughly 60x50
                potential_rect = pygame.Rect(rx, ry, 60, 50)
                
                collision = False
                
                # Check Buildings (Inflate check to keep distance)
                for house_info in house_data.values():
                    if potential_rect.colliderect(house_info["rect"]):
                        collision = True
                        break
                
                # Check Trees/Fences
                if not collision:
                    for obs in static_obstacles:
                        if potential_rect.colliderect(obs):
                            collision = True
                            break

                # Check Other Pigs
                if not collision:
                    for existing_pig in new_visual_pigs:
                        # Inflate strictly to give them "personal space"
                        if potential_rect.colliderect(existing_pig.rect.inflate(10, 10)):
                            collision = True
                            break
                
                if not collision:
                    final_pos = (rx, ry)
                    break 
            
            # Fallback if map is too full
            if final_pos is None:
                safe_x = pad + (len(new_visual_pigs) * 65) % (sw - 100)
                safe_y = sh - 70 
                final_pos = (safe_x, safe_y)

            # Create or Move Sprite
            if sprite:
                sprite.rect.topleft = final_pos # Move existing
                # Ensure we update the internal x,y if the sprite uses them
                if hasattr(sprite, 'x'): sprite.x = final_pos[0]
                if hasattr(sprite, 'y'): sprite.y = final_pos[1]
                new_visual_pigs.append(sprite)
            else:
                new_sprite = GuineaPigSprite(final_pos[0], final_pos[1], pet_data)
                new_visual_pigs.append(new_sprite)

    visual_pigs = new_visual_pigs

def homescreen_update(events, user_id):
    global last_update, game_time, show_popup, selected_pig_stats

    # Check for updates (renames, new pets)
    refresh_visual_pigs(user_id)

    if show_popup:
        for event in events:
            action = popup_manager.handle_event(event)
            if action == "close":
                show_popup = False
        return None

    # Time Logic
    now = time.time()
    if last_update == 0: last_update = now
    if now - last_update >= REAL_SECONDS_PER_GAME_MINUTE:
        last_update = now
        game_time["minute"] += 1
        if game_time["minute"] >= 60:
            game_time["minute"] = 0
            game_time["hour"] += 1
        game_time["day"] += 1 
        if game_time["day"] > 30:
            game_time["day"] = 1
            game_time["month"] += 1
        if game_time["month"] > 12:
            game_time["month"] = 1
            game_time["year"] += 1

    mouse_pos = pygame.mouse.get_pos()
    
    # Handle Clicks
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 1. Check Guinea Pig Clicks
            clicked_pig = False
            for sprite in reversed(visual_pigs):
                if sprite.is_clicked(mouse_pos):
                    selected_pig_stats = sprite.get_stats()
                    show_popup = True
                    clicked_pig = True
                    break 
            
            if clicked_pig:
                return None

            # 2. Check Building Clicks
            for name, data in house_data.items():
                rect = data["rect"]
                if rect.collidepoint(mouse_pos):
                    return name
    
    # --- KEEP PIGS ON SCREEN ---
    screen = pygame.display.get_surface()
    screen_rect = screen.get_rect()
    
    for sprite in visual_pigs:
        if hasattr(sprite, 'update'):
            sprite.update()
        sprite.rect.clamp_ip(screen_rect)

    return None

def homescreen_draw(screen, user_id):
    global last_api_fetch_time, cached_user_data, cached_inventory

    # 1. Fetch Sidebar Data (API check)
    now = time.time()
    if now - last_api_fetch_time > 2.0:
        try:
            cached_user_data = api.get_user(user_id)
            cached_inventory = api.get_user_inventory(user_id)
            last_api_fetch_time = now
        except:
            pass

    # 2. Draw Background
    screen.fill(BLACK)
    screen.blit(background, BG_POS)
    
    # 3. Draw Houses & Labels
    mouse_pos = pygame.mouse.get_pos()

    for name, data in house_data.items():
        rect = data["rect"]
        glow = data["glow"]
        
        # Check if mouse is over the building
        hovering = False
        if not show_popup:
            if rect.collidepoint(mouse_pos):
                hovering = True

        if hovering:
            # --- DRAW GLOW ---
            gx = rect.x - (glow.get_width() - rect.width) // 2
            gy = rect.y - (glow.get_height() - rect.height) // 2
            screen.blit(glow, (gx, gy))

            # --- DRAW LABELS ---
            display_name = name.replace("_", " ").title()
            
            text_surf = font.render(display_name, True, (255, 255, 255))
            shadow_surf = font.render(display_name, True, (0, 0, 0))
            
            text_rect = text_surf.get_rect(center=rect.center)
            
            screen.blit(shadow_surf, (text_rect.x + 2, text_rect.y + 2))
            screen.blit(text_surf, text_rect)

    # 4. Draw Pigs
    visual_pigs.sort(key=lambda p: p.rect.centery)
    for sprite in visual_pigs:
        sprite.draw(screen)

    # 5. Draw Sidebar
    w, h = screen.get_size()
    pygame.draw.rect(screen, PANEL_GRAY, (w - 180, 20, 160, 220))
    real_clock = datetime.datetime.now().strftime("%I:%M %p")

    coins = cached_user_data['balance'] if cached_user_data else 0
    food_count = sum(item['quantity'] for item in cached_inventory) if cached_inventory else 0
    
    sidebar_lines = [
        f"Year: {game_time['year']}",
        f"Month: {game_time['month']}",
        f"Day: {game_time['day']}",
        "",
        f"{real_clock}",
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

    # 6. Draw Popup
    if show_popup and popup_manager and selected_pig_stats:
        overlay = pygame.Surface((w, h))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        popup_manager.draw(screen, selected_pig_stats)