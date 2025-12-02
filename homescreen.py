import pygame
import time

import datetime
now = datetime.datetime.now()
real_clock = now.strftime("%I:%M %p")


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
game_time = {
    "year": 1,
    "month": 1,
    "day": 1,
    "hour": 12,
    "minute": 0,
    "am": True
}

# 5 real minutes = 1 month (30 days)
# 300 real seconds / (30 days * 1440 min) = 1 min every ~0.07 sec
REAL_SECONDS_PER_GAME_MINUTE = 0.07
last_update = 0

def make_glow(mask, intensity=22):
    """Soft, translucent Stardew-style glow that fills the silhouette."""
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


# ----------------------------------------------------------
#  INIT
# ----------------------------------------------------------

def homescreen_init():
    global font, sidebar_font, background, BG_POS, house_data

    pygame.font.init()
    font = pygame.font.Font(None, 40)
    sidebar_font = pygame.font.Font(None, 26)

    # Load background PNG
    raw_bg = pygame.image.load("images/BG_Home.png").convert_alpha()
    raw_w, raw_h = raw_bg.get_width(), raw_bg.get_height()

    # Scale background proportionally
    screen_w, screen_h = 800, 600
    scale = screen_h / raw_h
    new_w = int(raw_w * scale)

    background = pygame.transform.scale(raw_bg, (new_w, screen_h))
    BG_POS = ((screen_w - new_w) // 2, 0)

    # House coordinates from PNG
    houses_original = {
        "home":       (132, 83, 215, 232),
        "mini_games": (348, 331, 202, 215),
        "store":      (423, 624, 195, 178),
        "training":   (50,  328, 198, 183),   # adjusted from 0 → 50 to stop left glow
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

        house_data[name] = {
            "rect": rect,
            "img": house_img,
            "mask": mask,
            "glow": glow,
        }


# ----------------------------------------------------------
#  UPDATE (clock + clicks)
# ----------------------------------------------------------

def homescreen_update(events):
    global last_update, game_time

    # --- Time system ---
    now = time.time()
    if now - last_update >= REAL_SECONDS_PER_GAME_MINUTE:
        last_update = now

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
    screen.blit(background, BG_POS)

    mouse_pos = pygame.mouse.get_pos()

    # Hover glow
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

    # Sidebar UI
    pygame.draw.rect(screen, PANEL_GRAY, (620, 20, 160, 220))

    sidebar_lines = [
        f"Year: {game_time['year']}",
        f"Month: {game_time['month']}",
        f"Day: {game_time['day']}",
        "",
        f"🕒 {real_clock}",
        "",
        "🪙 Coins: 5",
        "🍎 Food: 5",
        "",
        "T1 x19",
    ]

    y = 40
    for line in sidebar_lines:
        text_surface = sidebar_font.render(line, True, BLACK)