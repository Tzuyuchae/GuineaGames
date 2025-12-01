import pygame
import time
import datetime
import os  # Added to fix file paths
import os
import random

# --- Imports ---
from guineapig import GuineaPigSprite
from details_popup import DetailsPopup

# --- Colors ---
PANEL_GRAY = (235, 235, 235)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# --- Globals ---
font = None
sidebar_font = None
background = None
BG_POS = (0, 0)
house_data = {}  # holds rect, image, mask, glow

# --------------------------
# GAME TIME (5 min = 1 month)
# --------------------------
# --- Logic Globals ---
game_time = {
    "year": 1,
    "month": 1,
    "day": 1,
    "hour": 12,
    "minute": 0,
    "am": True
}

# 5 real minutes = 1 month (30 days)
REAL_SECONDS_PER_GAME_MINUTE = 0.07
last_update = 0

# --- Popup State ---
show_popup = False
popup_manager = None
visual_pigs = [] # List of GuineaPigSprite objects
last_inventory_count = -1 # To detect when to refresh sprites

def make_glow(mask, intensity=22):
    """Soft, translucent Stardew-style glow that fills the silhouette."""
    w, h = mask.get_size()

    glow = pygame.Surface((w + intensity * 2, h + intensity * 2), pygame.SRCALPHA)

    # Create a base surface from the mask
    base = mask.to_surface(setcolor=(255, 240, 150, 5), unsetcolor=(0, 0, 0, 0))
    base = base.convert_alpha()

    # Blur effect manually
    for dx in range(-intensity, intensity + 1):
        for dy in range(-intensity, intensity + 1):
            dist = abs(dx) + abs(dy)
            if dist <= intensity:
                alpha = max(1, 35 - dist * 1.4)
                temp = base.copy()
                temp.fill((255, 240, 150, alpha), special_flags=pygame.BLEND_RGBA_MULT)
                glow.blit(temp, (dx + intensity, dy + intensity))

    return glow


# ----------------------------------------------------------
#  INIT
# ----------------------------------------------------------

def homescreen_init():
    global font, sidebar_font, background, BG_POS, house_data

def homescreen_init(screen_w, screen_h):
    global font, sidebar_font, background, BG_POS, house_data, popup_manager

    pygame.font.init()
    font = pygame.font.Font(None, 40)
    sidebar_font = pygame.font.Font(None, 26)
    
    # Initialize the popup manager
    popup_manager = DetailsPopup()

    # --- FIX: Dynamic Path Loading ---
    # This finds the folder where homescreen.py lives, then looks for 'images' inside it
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bg_path = os.path.join(current_dir, "images", "BG_Home.png")

    try:
        raw_bg = pygame.image.load(bg_path).convert_alpha()
    except FileNotFoundError:
        print(f"CRITICAL ERROR: Could not find image at: {bg_path}")
        print("Ensure 'images' folder is inside the 'frontend' folder.")
        # Create a fallback surface so the game doesn't crash immediately
        raw_bg = pygame.Surface((800, 600))
        raw_bg.fill((100, 100, 200)) 

    raw_w, raw_h = raw_bg.get_width(), raw_bg.get_height()

    # Scale background proportionally
    screen_w, screen_h = 800, 600
    # Scale background to fill height
    scale = screen_h / raw_h
    new_w = int(raw_w * scale)

    background = pygame.transform.scale(raw_bg, (new_w, screen_h))
    BG_POS = ((screen_w - new_w) // 2, 0)

    # House coordinates from PNG
    # Defined areas for buildings
    houses_original = {
        "home":       (132, 83, 215, 232),
        "mini_games": (348, 331, 202, 215),
        "store":      (423, 624, 195, 178),
        "training":   (50,  328, 198, 183), 
        "breeding":   (156, 535, 218, 200),
    }

    house_data = {}

    for name, (ox, oy, ow, oh) in houses_original.items():
        # Create subsurface for specific house
        # Extract sub-image from original BG for glowing effect
        house_img = raw_bg.subsurface(pygame.Rect(ox, oy, ow, oh)).copy()

        sw, sh = int(ow * scale), int(oh * scale)
        house_img = pygame.transform.scale(house_img, (sw, sh))

        mask = pygame.mask.from_surface(house_img)
        glow = make_glow(mask, intensity=22)

        sx = int(ox * scale) + BG_POS[0]
        sy = int(oy * scale) + BG_POS[1]

        rect = pygame.Rect(sx, sy, sw, sh)

        house_data[name] = {
            "rect": rect,
            "img": house_img,
            "mask": mask,
            "glow": glow,
        }


# ----------------------------------------------------------
#  UPDATE (clock + clicks)
# ----------------------------------------------------------

def refresh_visual_pigs(inventory_list):
    """Rebuilds the list of visual sprites based on inventory data."""
    global visual_pigs
    visual_pigs = []
    
    # Define boundaries for the "Yard" where pigs can walk
    yard_min_x, yard_max_x = 50, 600
    yard_min_y, yard_max_y = 400, 800
    
    for pig_data in inventory_list:
        # Random position in the yard
        rx = random.randint(yard_min_x, yard_max_x)
        ry = random.randint(yard_min_y, yard_max_y)
        sprite = GuineaPigSprite(rx, ry, pig_data)
        visual_pigs.append(sprite)

def homescreen_update(events):
    global last_update, game_time

    # --- Time system ---
    global last_update, game_time, show_popup, selected_pig_stats

    # --- Handle Popup Events First ---
    if show_popup:
        for event in events:
            action = popup_manager.handle_event(event)
            if action == "close":
                show_popup = False
        # Block other inputs while popup is open
        return None

    # --- Time system ---
    now = time.time()
    
    # Ensure last_update is set on first run
    if last_update == 0:
        last_update = now

    if now - last_update >= REAL_SECONDS_PER_GAME_MINUTE:
        last_update = now
        
        # Increment minute (optional, if you want minutes)
        game_time["minute"] += 1
        if game_time["minute"] >= 60:
            game_time["minute"] = 0
            game_time["hour"] += 1

        # For now, based on your code, just incrementing day/month logic:
        # Note: You might want to link day incrementing to hours passing
        # But sticking to your original logic loop:
        
        # Increment Days periodically? 
        # (Currently your math increments this very fast, 1 min real time = ~14 days)
        # Adjusting strictly to your loop request:
        game_time["day"] += 1 

        if game_time["day"] > 30:
            game_time["day"] = 1
            game_time["month"] += 1

        if game_time["month"] > 12:
            game_time["month"] = 1
            game_time["year"] += 1

    # --- Button clicks ---
    mouse_pos = pygame.mouse.get_pos()

    
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            
            # 1. Check Guinea Pig Clicks
            clicked_pig = False
            # Iterate in reverse so we click the one "on top"
            for sprite in reversed(visual_pigs):
                if sprite.is_clicked(mouse_pos):
                    selected_pig_stats = sprite.get_stats()
                    show_popup = True
                    clicked_pig = True
                    break # Stop checking
            
            if clicked_pig:
                return None

            # 2. Check Building Clicks
            for name, data in house_data.items():
                rect = data["rect"]
                mask = data["mask"]

                lx = mouse_pos[0] - rect.x
                ly = mouse_pos[1] - rect.y

                if 0 <= lx < rect.width and 0 <= ly < rect.height:
                    if mask.get_at((lx, ly)):
                        print(f"{name} clicked!")
                        return name

    return None


# ----------------------------------------------------------
#  DRAW
# ----------------------------------------------------------

def homescreen_draw(screen):
def homescreen_draw(screen, player_inventory=None):
    global last_inventory_count

    # Sync Visuals with Inventory
    if player_inventory:
        current_count = len(player_inventory.owned_pigs)
        if current_count != last_inventory_count:
            refresh_visual_pigs(player_inventory.owned_pigs)
            last_inventory_count = current_count

    screen.fill(BLACK)
    screen.blit(background, BG_POS)

    mouse_pos = pygame.mouse.get_pos()

    # Draw Buildings & Glow
    for name, data in house_data.items():
        rect = data["rect"]
        mask = data["mask"]
        glow = data["glow"]

        lx = mouse_pos[0] - rect.x
        ly = mouse_pos[1] - rect.y

        hovering = (
            0 <= lx < rect.width and
            0 <= ly < rect.height and
            mask.get_at((lx, ly))
        )

        if hovering:
        
        # Only calculate expensive mask collision if popup is NOT showing
        hovering = False
        if not show_popup:
            lx = mouse_pos[0] - rect.x
            ly = mouse_pos[1] - rect.y
            if 0 <= lx < rect.width and 0 <= ly < rect.height and mask.get_at((lx, ly)):
                hovering = True

        if hovering:
            gx = rect.x - (glow.get_width() - rect.width) // 2
            gy = rect.y - (glow.get_height() - rect.height) // 2

            glow_rect = pygame.Rect(gx, gy, glow.get_width(), glow.get_height())
            clipped = glow_rect.clip(screen.get_rect())

            if clipped.width > 0 and clipped.height > 0:
                screen.blit(
                    glow,
                    clipped.topleft,
                    pygame.Rect(
                        clipped.x - gx,
                        clipped.y - gy,
                        clipped.width,
                        clipped.height
                    )
                )

    # --- NEW: Draw Guinea Pigs ---
    # Sort by Y position so lower pigs appear in front of higher pigs (2.5D effect)
    visual_pigs.sort(key=lambda p: p.rect.centery)
    for sprite in visual_pigs:
        sprite.draw(screen)

    # Sidebar UI
    pygame.draw.rect(screen, PANEL_GRAY, (620, 20, 160, 220))

    # --- FIX: Update Real Clock Here ---
    real_clock = datetime.datetime.now().strftime("%I:%M %p")


    coins = player_inventory.coins if player_inventory else 0
    food = player_inventory.food if player_inventory else 0
    
    sidebar_lines = [
        f"Year: {game_time['year']}",
        f"Month: {game_time['month']}",
        f"Day: {game_time['day']}",
        "",
        f"{real_clock}",
        "",
        "Coins: 5",
        "Food: 5",
        "",
        "T1 x19",
        f"Pets: {len(visual_pigs)}",
    ]

    y = 40
    for line in sidebar_lines:
        # Simple check to support emoji if font supports it, otherwise remove emoji
        # Pygame default fonts struggle with emojis.
        text_surface = sidebar_font.render(line, True, BLACK)
        screen.blit(text_surface, (630, y))
        y += 20

    # --- NEW: Draw Popup Overlay ---
    if show_popup and popup_manager and selected_pig_stats:
        # Darken background
        overlay = pygame.Surface((w, h))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Draw popup content
        popup_manager.draw(screen, selected_pig_stats)