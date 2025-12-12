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

class BreedingPage:
    def __init__(self, user_id=1):
        self.user_id = user_id
        self.pets = [] 
        
        self.parent1 = None
        self.parent2 = None
        self.message = "Loading pets..."
        self.message_color = WHITE
        
        # --- NAMING QUEUE LOGIC ---
        self.naming_mode = False
        self.babies_to_name = [] # List of babies waiting for names
        self.current_baby_index = 0
        self.input_name = ""
        
        self.is_breeding_anim = False
        
        # --- SCROLLING VARIABLES ---
        self.scroll_offset = 0
        self.max_scroll = 0
        self.item_height = 85
        self.list_start_y = 520
        self.list_height = 320 
        
        # Layout Rects
        self.back_btn_rect = pygame.Rect(20, 20, 100, 40)
        self.refresh_btn_rect = pygame.Rect(550, 20, 100, 40)
        self.breed_btn_rect = pygame.Rect(236, 440, 200, 60)
        self.bar1_rect = pygame.Rect(70, 320, 180, 40)
        self.bar2_rect = pygame.Rect(422, 320, 180, 40)

        # Fonts
        pygame.font.init()
        try:
            self.title_font = pygame.font.SysFont("Arial", 30, bold=True)
            self.text_font = pygame.font.SysFont("Arial", 18)
            self.clock_font = pygame.font.SysFont("Arial", 22, bold=True)
        except:
            self.title_font = pygame.font.Font(None, 36)
            self.text_font = pygame.font.Font(None, 24)
            self.clock_font = pygame.font.Font(None, 28)

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
            paths_to_try = [
                os.path.join(base_path, path),
                os.path.join(base_path, path.replace("Global Assets", "../Global Assets")),
                os.path.join(base_path, "images", os.path.basename(path)),
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
        self.cooldown_img = load("Global Assets/Sprites/breeding_page/BR_Cooldown.png", (30, 30))
        
        if not self.cooldown_img:
            self.cooldown_img = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.cooldown_img, (200, 50, 50), (15, 15), 12)
            pygame.draw.line(self.cooldown_img, WHITE, (15, 15), (15, 5), 2)
            pygame.draw.line(self.cooldown_img, WHITE, (15, 15), (20, 15), 2)

    def refresh_pets(self):
        self.message = "Refreshing..."
        try:
            raw_pets = api.get_user_pets(self.user_id)
            self.pets = []
            
            adult_count = 0
            baby_count = 0
            
            for p in raw_pets:
                # Only Adults can breed
                if p.get('age_days', 0) >= 1: 
                    wrapper = GuineaPigSprite(0, 0, p)
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
            
            total_content_height = len(self.pets) * self.item_height
            self.max_scroll = max(0, total_content_height - self.list_height)
            self.scroll_offset = 0 
            
            # Re-validate slots in case selected pet disappeared
            if self.parent1 and self.parent1 not in self.pets: self.parent1 = None
            if self.parent2 and self.parent2 not in self.pets: self.parent2 = None
            
        except Exception as e:
            self.message = "Connection Error!"
            self.message_color = RED
            print(f"Breeding Fetch Error: {e}")

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_offset -= event.y * 20
                self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

            # --- NAMING MODE INPUT ---
            if self.naming_mode:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self._confirm_baby_name()
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
                        self._trigger_breed_api()
                    else:
                        self.message = "Select 2 parents first!"
                        self.message_color = RED

                if self.bar1_rect.inflate(20, 200).collidepoint(pos): self.parent1 = None
                if self.bar2_rect.inflate(20, 200).collidepoint(pos): self.parent2 = None

                list_viewport = pygame.Rect(0, self.list_start_y, 672, self.list_height)
                if list_viewport.collidepoint(pos):
                    relative_y = pos[1] - self.list_start_y + self.scroll_offset
                    index = relative_y // self.item_height
                    
                    if 0 <= index < len(self.pets):
                        pig = self.pets[int(index)]
                        
                        # --- COOLDOWN CHECK (DB BASED) ---
                        # We now read the cooldown directly from the database field
                        cooldown = pig.data.get('breeding_cooldown', 0)
                        
                        if cooldown > 0:
                            self.message = f"Cooldown: Wait {cooldown}s"
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
        """Sends breed request, THEN starts naming sequence"""
        self.message = "Breeding..."
        self.is_breeding_anim = True
        
        try:
            # Send "Unnamed" initially. We will rename them in the popup.
            data = {
                "parent1_id": self.parent1.data['id'],
                "parent2_id": self.parent2.data['id'],
                "child_name": "Baby", 
                "child_species": "Guinea Pig",
                "child_color": "Mixed", 
                "owner_id": self.user_id
            }
            
            print(f"Sending Breed Request...")
            response = api._post("/genetics/breed", json=data) 
            
            # --- HANDLE RESPONSE FOR NAMING ---
            self.babies_to_name = []
            
            if isinstance(response, list):
                self.babies_to_name = response
            else:
                self.babies_to_name = [response]
                
            count = len(self.babies_to_name)
            self.message = f"{count} Babies Born!"
            self.message_color = GREEN
            
            # Clear parents immediately so we don't double breed
            self.parent1 = None
            self.parent2 = None
            
            # Start Naming Sequence
            self.naming_mode = True
            self.current_baby_index = 0
            self.input_name = ""
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

    def _confirm_baby_name(self):
        """Called when user presses ENTER in the naming popup"""
        new_name = self.input_name.strip()
        if not new_name:
            new_name = "Baby"
            
        current_baby_data = self.babies_to_name[self.current_baby_index]
        baby_id = current_baby_data.get('child_id')
        
        if baby_id:
            try:
                # Call API to update the name
                api.update_pet(baby_id, name=new_name)
                print(f"Renamed baby {baby_id} to {new_name}")
            except Exception as e:
                print(f"Rename failed: {e}")

        # Move to next baby
        self.current_baby_index += 1
        self.input_name = ""
        
        # If we have named everyone, close popup and refresh
        if self.current_baby_index >= len(self.babies_to_name):
            self.naming_mode = False
            self.refresh_pets()
            self.message = "All babies named!"

    def draw(self, screen, game_time=None):
        if self.bg_img: screen.blit(self.bg_img, (0,0))
        else: screen.fill((40, 40, 50))

        # Parent Platforms
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

        # Heart Icon
        heart_x = (self.bar1_rect.right + self.bar2_rect.left) // 2 - 70
        heart_y = self.bar1_rect.top - 110
        if self.is_breeding_anim or (self.parent1 and self.parent2):
            if self.heart_active_img: screen.blit(self.heart_active_img, (heart_x, heart_y))
        else:
            if self.heart_unlit_img: screen.blit(self.heart_unlit_img, (heart_x, heart_y))

        # Breed Button
        btn_color = GREEN if (self.parent1 and self.parent2) else GRAY
        pygame.draw.rect(screen, btn_color, self.breed_btn_rect, border_radius=10)
        btn_txt = self.title_font.render("BREED", True, WHITE)
        screen.blit(btn_txt, btn_txt.get_rect(center=self.breed_btn_rect.center))

        # Messages
        msg_s = self.text_font.render(self.message, True, self.message_color)
        screen.blit(msg_s, (20, 490))
        
        # Navigation Buttons
        pygame.draw.rect(screen, RED, self.back_btn_rect, border_radius=5)
        screen.blit(self.text_font.render("BACK", True, WHITE), (45, 30))

        pygame.draw.rect(screen, BLUE, self.refresh_btn_rect, border_radius=5)
        screen.blit(self.text_font.render("REFRESH", True, WHITE), (560, 30))

        # Game Clock
        if game_time:
            ampm = "AM" if game_time.get("am", True) else "PM"
            time_str = f"{game_time.get('hour', 12)}:{game_time.get('minute', 0):02d} {ampm}"
            date_str = f"Year {game_time.get('year', 1)} | Day {game_time.get('day', 1)}"
            
            t1 = self.clock_font.render(date_str, True, WHITE)
            t2 = self.clock_font.render(time_str, True, GOLD)
            screen.blit(t1, (650 - t1.get_width(), 70))
            screen.blit(t2, (650 - t2.get_width(), 95))

        # Scrollable List
        clip_rect = pygame.Rect(0, self.list_start_y, 672, self.list_height)
        old_clip = screen.get_clip()
        screen.set_clip(clip_rect) 

        start_y = self.list_start_y - self.scroll_offset

        for i, pig in enumerate(self.pets):
            item_y = start_y + (i * self.item_height)
            
            if item_y + self.item_height < self.list_start_y or item_y > self.list_start_y + self.list_height:
                continue

            is_sel = (pig == self.parent1 or pig == self.parent2)
            bg_col = BLUE if is_sel else DARK_GRAY
            rect = pygame.Rect(20, item_y, 632, 80)
            
            pygame.draw.rect(screen, bg_col, rect, border_radius=5)
            
            screen.blit(pig.image, (30, item_y)) 

            # --- DRAW COOLDOWN TIMER ---
            cooldown = pig.data.get('breeding_cooldown', 0)
            if cooldown > 0:
                if self.cooldown_img:
                    screen.blit(self.cooldown_img, (95, item_y + 25))
                    # Draw the countdown number next to the icon
                    cd_text = self.text_font.render(f"{cooldown}s", True, RED)
                    screen.blit(cd_text, (130, item_y + 30))

            screen.blit(self.title_font.render(pig.data['name'], True, WHITE), (120, item_y + 15))
            
            stats = f"Spd:{pig.data.get('speed',0)} | End:{pig.data.get('endurance',0)}"
            screen.blit(self.text_font.render(stats, True, GRAY), (120, item_y + 50))

        screen.set_clip(old_clip)

        # Scrollbar
        if self.max_scroll > 0:
            scrollbar_bg = pygame.Rect(655, self.list_start_y, 10, self.list_height)
            pygame.draw.rect(screen, (30, 30, 30), scrollbar_bg)
            
            visible_ratio = self.list_height / (len(self.pets) * self.item_height)
            handle_h = max(30, self.list_height * visible_ratio)
            scroll_ratio = self.scroll_offset / self.max_scroll
            handle_y = self.list_start_y + (scroll_ratio * (self.list_height - handle_h))
            
            handle_rect = pygame.Rect(655, handle_y, 10, handle_h)
            pygame.draw.rect(screen, GRAY, handle_rect, border_radius=5)

        # --- UPDATED NAMING POPUP ---
        if self.naming_mode and self.babies_to_name:
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0,0,0, 200))
            screen.blit(overlay, (0,0))
            
            box = pygame.Rect(136, 300, 400, 200)
            pygame.draw.rect(screen, (50,50,50), box, border_radius=10)
            pygame.draw.rect(screen, GOLD, box, 3, border_radius=10)
            
            # Show which baby we are naming (1 of 3, 2 of 3, etc.)
            total = len(self.babies_to_name)
            idx = self.current_baby_index + 1
            
            prompt = self.title_font.render(f"Name Baby {idx} of {total}:", True, WHITE)
            screen.blit(prompt, (box.centerx - prompt.get_width()//2, box.y + 40))
            
            inp = self.title_font.render(self.input_name + "_", True, GOLD)
            screen.blit(inp, (box.centerx - inp.get_width()//2, box.y + 100))
            
            hint = self.text_font.render("Press ENTER to Confirm", True, GRAY)
            screen.blit(hint, (box.centerx - hint.get_width()//2, box.y + 160))

manager = None
def breeding_update(events, inv, time):
    global manager
    if not manager: manager = BreedingPage(user_id=1)
    return manager.handle_input(events)

def breeding_draw(screen, inv, time):
    global manager
    if not manager: manager = BreedingPage(user_id=1)
    manager.draw(screen, game_time=time)