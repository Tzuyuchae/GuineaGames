import pygame
import time
import datetime
import os
import random

# -------------------------------------------------
# Helpers
# -------------------------------------------------

def is_overlapping(rect, others):
    """Check if a rect overlaps ANY rect in a list."""
    for o in others:
        if rect.colliderect(o):
            return True
    return False


# -------------------------------------------------
# Globals
# -------------------------------------------------

PANEL_GRAY = (235, 235, 235)
BLACK = (0,0,0)
WHITE = (255,255,255)

font = None
sidebar_font = None
label_font = None

background = None
BG_POS = (0,0)

house_data = {}
sidebar_icons = {}

pig_walk_data = {}   # holds walk timers + directions

game_time = {
    "year": 1, "month": 1, "day": 1,
    "hour": 12, "minute": 0, "am": True
}


# -------------------------------------------------
# Glow Maker
# -------------------------------------------------

def make_glow(mask, intensity=22):
    w, h = mask.get_size()
    glow = pygame.Surface((w + intensity*2, h + intensity*2), pygame.SRCALPHA)
    base = mask.to_surface(setcolor=(255,240,150,5), unsetcolor=(0,0,0,0)).convert_alpha()

    for dx in range(-intensity, intensity+1):
        for dy in range(-intensity, intensity+1):
            dist = abs(dx) + abs(dy)
            if dist <= intensity:
                alpha = max(1, 35 - dist*1.4)
                tmp = base.copy()
                tmp.fill((255,240,150,alpha), special_flags=pygame.BLEND_RGBA_MULT)
                glow.blit(tmp, (dx+intensity, dy+intensity))

    return glow


# -------------------------------------------------
# Initialization
# -------------------------------------------------

def homescreen_init(screen_w, screen_h):
    global font, sidebar_font, label_font
    global background, BG_POS, house_data, sidebar_icons

    pygame.font.init()
    font = pygame.font.Font(None, 40)
    label_font = pygame.font.Font(None, 32)
    sidebar_font = pygame.font.Font(None, 26)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    bg_path = os.path.join(current_dir, "images", "BG_Home.png")

    try:
        raw_bg = pygame.image.load(bg_path).convert_alpha()
    except:
        raw_bg = pygame.Surface((800,600))
        raw_bg.fill((100,100,200))

    # scale background to full height
    raw_w, raw_h = raw_bg.get_width(), raw_bg.get_height()
    scale = screen_h / raw_h
    new_w = int(raw_w * scale)
    new_h = int(raw_h * scale)

    background = pygame.transform.scale(raw_bg, (new_w,new_h))
    BG_POS = ((screen_w - new_w)//2, 0)

    # House rects from original sprite sheet
    houses_original = {
        "home":       (150,83,215,232),
        "training":   (20,328,198,183),
        "mini_games": (370,331,202,215),
        "breeding":   (250,535,120,200),
        "store":      (443,624,195,178),
    }

    # build scaled rects + masks
    house_data = {}
    for name,(ox,oy,ow,oh) in houses_original.items():
        sprite = raw_bg.subsurface(pygame.Rect(ox,oy,ow,oh)).copy()
        sw,sh = int(ow*scale), int(oh*scale)
        sprite = pygame.transform.scale(sprite, (sw,sh))

        mask = pygame.mask.from_surface(sprite)
        glow = make_glow(mask,22)

        sx = int(ox*scale) + BG_POS[0]
        sy = int(oy*scale) + BG_POS[1]

        house_data[name] = {
            "rect": pygame.Rect(sx,sy,sw,sh),
            "img": sprite,
            "mask": mask,
            "glow": glow
        }

    # Sidebar icons
    clock_icon_path = os.path.join(current_dir,"images","HP_In-Game_Time.png")
    coin_icon_path  = os.path.join(current_dir,"images","GL_Coin.png")

    try:
        clock_icon = pygame.image.load(clock_icon_path).convert_alpha()
        coin_icon  = pygame.image.load(coin_icon_path).convert_alpha()
    except:
        clock_icon = pygame.Surface((32,32))
        coin_icon  = pygame.Surface((32,32))

    sidebar_icons = {
        "clock": pygame.transform.scale(clock_icon,(32,32)),
        "coin": pygame.transform.scale(coin_icon,(50,50)),
    }

    # Load pig sprites
    pig_sprites = {}

    short_dir = os.path.join(current_dir,"images","Guinea Pigs","SH_GP_Sprites","SH_GP_Sprites")
    long_dir  = os.path.join(current_dir,"images","Guinea Pigs","LH_GP_Sprites","LH_GP_Sprites")

    short_files = [f for f in os.listdir(short_dir) if f.endswith(".png")]
    long_files  = [f for f in os.listdir(long_dir) if f.endswith(".png")]

    pig_sprites["short"] = pygame.image.load(os.path.join(short_dir, short_files[0])).convert_alpha()
    pig_sprites["long"]  = pygame.image.load(os.path.join(long_dir,  long_files[0])).convert_alpha()

    # scale pigs smaller
    for k in pig_sprites:
        pig_sprites[k] = pygame.transform.scale(pig_sprites[k], (45,45))  # half size

    house_data["pig_sprites"] = pig_sprites

    print("Homescreen initialized.")


# -------------------------------------------------
# Time update
# -------------------------------------------------

def homescreen_update(events):
    # simple game clock
    game_time["minute"] += 1
    if game_time["minute"] >= 60:
        game_time["minute"] = 0
        game_time["hour"] += 1
    if game_time["hour"] >= 24:
        game_time["hour"] = 0
        game_time["day"] += 1
    if game_time["day"] > 30:
        game_time["day"] = 1
        game_time["month"] += 1
    if game_time["month"] > 12:
        game_time["month"] = 1
        game_time["year"] += 1


# -------------------------------------------------
# Labels
# -------------------------------------------------

HOUSE_LABELS = {
    "home":"Home",
    "training":"Training",
    "mini_games":"Mini Games",
    "breeding":"Breeding",
    "store":"Store"
}


# -------------------------------------------------
# Pig Movement Helpers
# -------------------------------------------------
def begin_walk(pig_id):
    """Assign a random direction & next timer for a pig."""
    dirs = [
        (1,0), (-1,0),
        (0,1), (0,-1),
        (1,1), (-1,1),
        (1,-1), (-1,-1),
        (0,0), (0,0), (0,0)   # more stopping
    ]
    dx,dy = random.choice(dirs)
    pig_walk_data[pig_id] = {
        "dx":dx, "dy":dy,
        "timer": time.time() + random.uniform(2.5,5.0)  # slower change rate
    }




def move_pig(rect, pig_id, forbidden, others):
    """Try to move pig smoothly; if collision, choose new direction."""
    if pig_id not in pig_walk_data:
        begin_walk(pig_id)

    info = pig_walk_data[pig_id]

    # change direction?
    if time.time() > info["timer"]:
        begin_walk(pig_id)
        info = pig_walk_data[pig_id]

    new_rect = rect.move(info["dx"], info["dy"])

    # check collisions
    if is_overlapping(new_rect, forbidden) or is_overlapping(new_rect, others):
        begin_walk(pig_id)
        return rect   # stay still this frame

    return new_rect



# -------------------------------------------------
# Main Draw
# -------------------------------------------------

def homescreen_draw(screen, player_inventory=None, pigs=None):
    screen.fill(BLACK)
    screen.blit(background, BG_POS)

    mouse_pos = pygame.mouse.get_pos()

    # hover glow
    for name,data in house_data.items():
        if name=="pig_sprites": continue
        rect = data["rect"]
        mask = data["mask"]
        glow = data["glow"]

        lx = mouse_pos[0] - rect.x
        ly = mouse_pos[1] - rect.y

        if 0<=lx<rect.width and 0<=ly<rect.height and mask.get_at((lx,ly)):
            gx = rect.x - (glow.get_width()-rect.width)//2
            gy = rect.y - (glow.get_height()-rect.height)//2
            screen.blit(glow,(gx,gy))

    # Labels
    label_rects = []
    for name,data in house_data.items():
        if name=="pig_sprites": continue
        rect = data["rect"]
        label = HOUSE_LABELS.get(name,"")
        surf = label_font.render(label, True, WHITE)
        text_rect = surf.get_rect(center=(rect.centerx, rect.bottom+20))
        screen.blit(surf, text_rect)
        label_rects.append(text_rect.inflate(40,20))

    # -------------------------------------------------
    # Forbidden Zones (houses + labels + tree)
    # -------------------------------------------------
    forbidden = [house_data[n]["rect"] for n in house_data if n!="pig_sprites"]
    forbidden.extend(label_rects)
    forbidden.append(pygame.Rect(70,380,120,150))  # tree area

    # -------------------------------------------------
    # Pigs wandering
    # -------------------------------------------------
    if pigs:
        pig_sprites = house_data["pig_sprites"]

        home_rect = house_data["home"]["rect"]
        walk_area = pygame.Rect(
            home_rect.centerx - 200,
            home_rect.bottom + 10,
            400,
            250
        )

        pig_rects = []
        for i,pig in enumerate(pigs):
            coat_len = pig.phenotype.get("coat_length","Short")
            sprite_key = "long" if coat_len.lower()=="long" else "short"
            sprite = pig_sprites[sprite_key]

            # initialize pigs at center bottom of home
            if not hasattr(pig, "screen_rect"):
                pig.screen_rect = sprite.get_rect()
                pig.screen_rect.midtop = (home_rect.centerx, home_rect.bottom+40)

            # movement
            new_rect = move_pig(pig.screen_rect, pig.id, forbidden, pig_rects)

            # clamp to walk area
            if not walk_area.contains(new_rect):
                begin_walk(pig.id)

            pig.screen_rect = new_rect
            pig_rects.append(new_rect)

            screen.blit(sprite, new_rect.topleft)

    # -------------------------------------------------
    # Sidebar
    # -------------------------------------------------
    w,h = screen.get_size()
    panel = pygame.Rect(w-180,20,160,260)
    pygame.draw.rect(screen, PANEL_GRAY, panel)

    real_clock = datetime.datetime.now().strftime("%I:%M %p")
    coins = player_inventory.coins if player_inventory else 0
    food  = player_inventory.food if player_inventory else 0

    tx = w-170
    ty = 40

    for line in [
        f"Year: {game_time['year']}",
        f"Month: {game_time['month']}",
        f"Day: {game_time['day']}",
    ]:
        screen.blit(sidebar_font.render(line,True,BLACK),(tx,ty))
        ty += 20

    screen.blit(sidebar_icons["clock"], (tx, ty))
    screen.blit(sidebar_font.render(real_clock,True,BLACK),(tx+40,ty+8))
    ty+=30

    screen.blit(sidebar_icons["coin"], (tx-10,ty))
    screen.blit(sidebar_font.render(f"Coins: {coins}",True,BLACK),(tx+40,ty+15))
    ty+=55

    screen.blit(sidebar_font.render("Food Inventory",True,BLACK),(tx,ty))
    ty+=15
    screen.blit(sidebar_font.render("---------------------",True,BLACK),(tx,ty))
    ty+=20
    screen.blit(sidebar_font.render(f"Basic: {food}",True,BLACK),(tx,ty))
    ty+=20
    screen.blit(sidebar_font.render(f"Premium: {food}",True,BLACK),(tx,ty))
