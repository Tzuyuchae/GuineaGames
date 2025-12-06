import pygame
import os
import time
from api_client import api
from guineapig import GuineaPigSprite 

# --- CONSTANTS ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
GREEN = (34, 139, 34)
RED = (178, 34, 34)
GOLD = (255, 215, 0)
BLUE = (70, 130, 180)
PLATFORM_COLOR = (100, 100, 120)

BREEDING_COOLDOWN_SECONDS = 180 # 3 Minutes

class BreedingPage:
    def __init__(self, user_id=1):
        self.user_id = user_id
        self.pets = [] 
        
        # Local cache for cooldowns to ensure they show up immediately
        # Format: {pet_id: timestamp_when_bred}
        self.local_cooldowns = {} 
        
        self.parent1 = None
        self.parent2 = None
        self.message = "Loading pets..."
        self.message_color = WHITE
        
        self.naming_mode = False
        self.input_name = ""
        self.is_breeding_anim = False
        self.breeding_progress = 0
        
        # --- SCROLLING VARIABLES ---
        self.scroll_offset = 0
        self.max_scroll = 0
        self.item_height = 85  # Height of one pet card + spacing
        self.list_start_y = 520
        self.list_height = 320 # Height of the visible list area
        
        # Layout Rects
        self.back_btn_rect = pygame.Rect(20, 20, 100, 40)
        self.refresh_btn_rect = pygame.Rect(550, 20, 100, 40)
        self.breed_btn_rect = pygame.Rect(236, 440, 200, 60)
        self.bar1_rect = pygame.Rect(70, 320, 180, 40)
        self.bar2_rect = pygame.Rect(422, 320, 180, 40)

        # Fonts
        pygame.font.init()
        self.title_font = pygame.font.SysFont("Arial", 30, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 18)
        self.clock_font = pygame.font.SysFont("Arial", 22, bold=True)

        # Visuals
        self.bg_img = None
        self.heart_active_img = None
        self.heart_unlit_img = None
        self.cooldown_img = None
        self._load_assets()
        
        self.refresh_pets()

    def _load_assets(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        def load(path, size=None):
            # Try multiple path variations to be safe
            paths_to_try = [
                os.path.join(base_path, path),
                os.path.join(base_path, path.replace("Global Assets", "../Global Assets")),
                os.path.join(base_path, "images", os.path.basename(path)),
                # Handle case sensitivity/spacing differences
                os.path.join(base_path, path.replace("breeding_page", "Breeding Page")),
            ]
            
            for p in paths_to_try:
                if os.path.exists(p):
                    try:
                        img = pygame.image.load(p).convert_alpha()
                        if size: img = pygame.transform.scale(img, size)
                        return img
                    except: pass
            return None

        self.bg_img = load("Global Assets/Sprites/More Sprites/BG Art/Breed/BG_Breed.png", (672, 864))
        self.heart_active_img = load("Global Assets/Sprites/Breeding Page/BR_Active.png", (140, 140))
        self.heart_unlit_img = load("Global Assets/Sprites/Breeding Page/BR_Unlit.png", (140, 140))
        
        # Load Cooldown Icon
        self.cooldown_img = load("Global Assets/Sprites/breeding_page/BR_Cooldown.png", (30, 30))
        
        # Fallback if cooldown image missing
        if not self.cooldown_img:
            self.cooldown_img = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.cooldown_img, (200, 50, 50), (15, 15), 12)
            pygame.draw.line(self.cooldown_img, WHITE, (15, 15), (15, 5), 2)
            pygame.draw.line(self.cooldown_img, WHITE, (15, 15), (20, 15), 2)

    def refresh_pets(self):
        """Fetches pets from API"""
        self.message = "Refreshing..."
        try:
            raw_pets = api.get_user_pets(self.user_id)
            self.pets = []
            
            adult_count = 0
            baby_count = 0
            
            for p in raw_pets:
                pid = p['id']
                wrapper = GuineaPigSprite(0, 0, p)
                
                # --- APPLY LOCAL COOLDOWN OVERRIDE ---
                # If we bred this pig locally recently, enforce that timestamp
                # This fixes the issue where the API might be slow to update
                if pid in self.local_cooldowns:
                    wrapper.data['last_bred_timestamp'] = self.local_cooldowns[pid]

                if p.get('age_days', 0) >= 1: 
                    self.pets.append(wrapper)
                    adult_count += 1
                else:
                    baby_count += 1
            
            if not self.pets:
                if baby_count > 0:
                    self.message = f"Only babies found ({baby_count}). Grow them first!"
                else:
                    self.message = "No adult pets found."
                self.message_color = RED
            else:
                self.message = "Select two parents."
                self.message_color = WHITE
            
            # Recalculate max scroll
            total_content_height = len(self.pets) * self.item_height
            self.max_scroll = max(0, total_content_height - self.list_height)
            self.scroll_offset = 0 # Reset scroll
            
            # Validate slots
            if self.parent1 and self.parent1 not in self.pets: self.parent1 = None
            if self.parent2 and self.parent2 not in self.pets: self.parent2 = None
            
        except Exception as e:
            self.message = "Connection Error!"
            self.message_color = RED
            print(f"Breeding Fetch Error: {e}")

    def handle_input(self, events):
        for event in events:
            # Scroll Wheel Handling
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_offset -= event.y * 20  # Scroll speed
                self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

            if self.naming_mode:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self._trigger_breed_api()
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_name = self.input_name[:-1]
                    else:
                        if len(self.input_name) < 12:
                            self.input_name += event.unicode
                return None 

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                
                if self.back_btn_rect.collidepoint(pos):
                    return 'homescreen'
                
                if self.refresh_btn_rect.collidepoint(pos):
                    self.refresh_pets()
                    return None
                
                if self.breed_btn_rect.collidepoint(pos):
                    if self.parent1 and self.parent2:
                        self.naming_mode = True
                        self.input_name = ""
                        self.message = "Name your baby:"
                    else:
                        self.message = "Select 2 parents first!"
                        self.message_color = RED

                # Clear slots
                if self.bar1_rect.inflate(20, 200).collidepoint(pos): self.parent1 = None
                if self.bar2_rect.inflate(20, 200).collidepoint(pos): self.parent2 = None

                # Select from list (Adjusted for Scroll)
                # Check if click is within the list viewport area
                list_viewport = pygame.Rect(0, self.list_start_y, 672, self.list_height)
                if list_viewport.collidepoint(pos):
                    # Calculate which item was clicked based on scroll
                    relative_y = pos[1] - self.list_start_y + self.scroll_offset
                    index = relative_y // self.item_height
                    
                    if 0 <= index < len(self.pets):
                        pig = self.pets[int(index)]
                        
                        # --- COOLDOWN CHECK ---
                        last_bred = pig.data.get('last_bred_timestamp', 0)
                        now = time.time()
                        if last_bred > 0 and (now - last_bred < BREEDING_COOLDOWN_SECONDS):
                            remaining = int(BREEDING_COOLDOWN_SECONDS - (now - last_bred))
                            self.message = f"Cooldown: Wait {remaining}s"
                            self.message_color = RED
                        else:
                            self._select_parent(pig)

        return None

    def _select_parent(self, pig):
        if pig == self.parent1: self.parent1 = None; return
        if pig == self.parent2: self.parent2 = None; return
        
        if not self.parent1: 
            self.parent1 = pig
        elif not self.parent2: 
            self.parent2 = pig
        
        self.message = "Select parents."
        self.message_color = WHITE

    def _trigger_breed_api(self):
        """Sends breed request to server"""
        self.message = "Breeding..."
        self.is_breeding_anim = True
        self.breeding_progress = 50 
        
        # --- FIX: Ensure name is captured safely ---
        # .strip() removes accidental spaces
        final_name = self.input_name.strip()
        if not final_name:
            final_name = "Baby"
        
        try:
            data = {
                "parent1_id": self.parent1.data['id'],
                "parent2_id": self.parent2.data['id'],
                "child_name": final_name, # <--- Use the cleaned name
                "child_species": "Guinea Pig",
                "child_color": "Mixed", 
                "owner_id": self.user_id
            }
            
            # Debug print to see what we are sending
            print(f"Sending Breed Request: {data}")

            response = api._post("/genetics/breed", json=data) # Removed trailing slash just in case
            
            # Force local update
            now = time.time()
            self.local_cooldowns[self.parent1.data['id']] = now
            self.local_cooldowns[self.parent2.data['id']] = now
            
            # Use response name to confirm what server saved
            server_name = response.get('child_name', final_name)
            self.message = f"Born: {server_name}!"
            
            self.message_color = GREEN
            self.naming_mode = False
            self.parent1 = None
            self.parent2 = None
            self.refresh_pets() 
            self.is_breeding_anim = False
            
        except Exception as e:
            err_msg = str(e)
            if "500" in err_msg: self.message = "Server Error"
            elif "400" in err_msg: self.message = "Cooldown active!"
            else: self.message = f"Error: {err_msg[:15]}..."
            self.message_color = RED
            print(f"BREED ERROR: {e}")
            self.naming_mode = False
            self.is_breeding_anim = False

    def draw(self, screen, game_time=None):
        # 1. Background
        if self.bg_img: screen.blit(self.bg_img, (0,0))
        else: screen.fill((40, 40, 50))

        # 2. Parent Platforms
        pygame.draw.rect(screen, PLATFORM_COLOR, self.bar1_rect, border_radius=10)
        pygame.draw.rect(screen, PLATFORM_COLOR, self.bar2_rect, border_radius=10)
        
        if self.parent1:
            big_img = pygame.transform.scale(self.parent1.image, (150, 150))
            screen.blit(big_img, (self.bar1_rect.centerx - 75, self.bar1_rect.top - 140))
            nm = self.text_font.render(self.parent1.data['name'], True, WHITE)
            screen.blit(nm, nm.get_rect(center=(self.bar1_rect.centerx, self.bar1_rect.top - 160)))
        else:
            txt = self.text_font.render("Select Parent 1", True, GRAY)
            screen.blit(txt, txt.get_rect(center=(self.bar1_rect.centerx, self.bar1_rect.top - 50)))

        if self.parent2:
            big_img = pygame.transform.scale(self.parent2.image, (150, 150))
            screen.blit(big_img, (self.bar2_rect.centerx - 75, self.bar2_rect.top - 140))
            nm = self.text_font.render(self.parent2.data['name'], True, WHITE)
            screen.blit(nm, nm.get_rect(center=(self.bar2_rect.centerx, self.bar2_rect.top - 160)))
        else:
            txt = self.text_font.render("Select Parent 2", True, GRAY)
            screen.blit(txt, txt.get_rect(center=(self.bar2_rect.centerx, self.bar2_rect.top - 50)))

        # 3. Heart Icon
        heart_x = (self.bar1_rect.right + self.bar2_rect.left) // 2 - 70
        heart_y = self.bar1_rect.top - 110
        if self.is_breeding_anim or (self.parent1 and self.parent2):
            if self.heart_active_img: screen.blit(self.heart_active_img, (heart_x, heart_y))
        else:
            if self.heart_unlit_img: screen.blit(self.heart_unlit_img, (heart_x, heart_y))

        # 4. Breed Button
        btn_color = GREEN if (self.parent1 and self.parent2) else GRAY
        pygame.draw.rect(screen, btn_color, self.breed_btn_rect, border_radius=10)
        btn_txt = self.title_font.render("BREED", True, WHITE)
        screen.blit(btn_txt, btn_txt.get_rect(center=self.breed_btn_rect.center))

        # 5. UI Elements
        msg_s = self.text_font.render(self.message, True, self.message_color)
        screen.blit(msg_s, (20, 490))
        
        pygame.draw.rect(screen, RED, self.back_btn_rect, border_radius=5)
        screen.blit(self.text_font.render("BACK", True, WHITE), (45, 30))

        pygame.draw.rect(screen, BLUE, self.refresh_btn_rect, border_radius=5)
        screen.blit(self.text_font.render("REFRESH", True, WHITE), (560, 30))

        # --- DRAW IN-GAME CLOCK (New Request) ---
        if game_time:
            # Format: Year 1 | Day 5 | 12:30 PM
            ampm = "AM" if game_time.get("am", True) else "PM"
            time_str = f"{game_time.get('hour', 12)}:{game_time.get('minute', 0):02d} {ampm}"
            date_str = f"Year {game_time.get('year', 1)} | Day {game_time.get('day', 1)}"
            
            # Draw bg box for clock
            clock_box = pygame.Rect(450, 70, 200, 50)
            # pygame.draw.rect(screen, (0, 0, 0, 150), clock_box, border_radius=5) # semi-transparent if surface
            
            t1 = self.clock_font.render(date_str, True, WHITE)
            t2 = self.clock_font.render(time_str, True, GOLD)
            
            # Align right
            screen.blit(t1, (650 - t1.get_width(), 70))
            screen.blit(t2, (650 - t2.get_width(), 95))

        # --- 6. SCROLLABLE Inventory List ---
        clip_rect = pygame.Rect(0, self.list_start_y, 672, self.list_height)
        old_clip = screen.get_clip()
        screen.set_clip(clip_rect) 

        start_y = self.list_start_y - self.scroll_offset
        current_time = time.time()

        for i, pig in enumerate(self.pets):
            item_y = start_y + (i * self.item_height)
            
            if item_y + self.item_height < self.list_start_y or item_y > self.list_start_y + self.list_height:
                continue

            is_sel = (pig == self.parent1 or pig == self.parent2)
            bg_col = BLUE if is_sel else DARK_GRAY
            rect = pygame.Rect(20, item_y, 632, 80)
            
            pygame.draw.rect(screen, bg_col, rect, border_radius=5)
            
            screen.blit(pig.image, (30, item_y)) 

            # --- DRAW COOLDOWN ICON ---
            last_bred = pig.data.get('last_bred_timestamp', 0)
            if last_bred > 0 and (current_time - last_bred < BREEDING_COOLDOWN_SECONDS):
                if self.cooldown_img:
                    # Draw TO THE RIGHT of the pig icon (x=30 + width ~60 + padding)
                    screen.blit(self.cooldown_img, (95, item_y + 25))

            screen.blit(self.title_font.render(pig.data['name'], True, WHITE), (120, item_y + 15))
            
            stats = f"Spd:{pig.data.get('speed',0)} | End:{pig.data.get('endurance',0)}"
            screen.blit(self.text_font.render(stats, True, GRAY), (120, item_y + 50))

        screen.set_clip(old_clip)

        # Draw Scrollbar
        if self.max_scroll > 0:
            scrollbar_bg = pygame.Rect(655, self.list_start_y, 10, self.list_height)
            pygame.draw.rect(screen, (30, 30, 30), scrollbar_bg)
            
            visible_ratio = self.list_height / (len(self.pets) * self.item_height)
            handle_h = max(30, self.list_height * visible_ratio)
            scroll_ratio = self.scroll_offset / self.max_scroll
            handle_y = self.list_start_y + (scroll_ratio * (self.list_height - handle_h))
            
            handle_rect = pygame.Rect(655, handle_y, 10, handle_h)
            pygame.draw.rect(screen, GRAY, handle_rect, border_radius=5)

        # 7. Naming Overlay
        if self.naming_mode:
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0,0,0, 200))
            screen.blit(overlay, (0,0))
            
            box = pygame.Rect(136, 300, 400, 200)
            pygame.draw.rect(screen, (50,50,50), box, border_radius=10)
            pygame.draw.rect(screen, GOLD, box, 3, border_radius=10)
            
            prompt = self.title_font.render("Name your Baby:", True, WHITE)
            screen.blit(prompt, (box.centerx - 100, box.y + 40))
            
            inp = self.title_font.render(self.input_name + "_", True, GOLD)
            screen.blit(inp, (box.centerx - 100, box.y + 100))
            
            hint = self.text_font.render("Press ENTER to Confirm", True, GRAY)
            screen.blit(hint, (box.centerx - 80, box.y + 160))

manager = None
def breeding_update(events, inv, time):
    global manager
    if not manager: manager = BreedingPage(user_id=1)
    return manager.handle_input(events)

def breeding_draw(screen, inv, time):
    global manager
    if not manager: manager = BreedingPage(user_id=1)
    # Pass the game time to the draw function
    manager.draw(screen, game_time=time)