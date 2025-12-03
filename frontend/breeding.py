import pygame
import os
from api_client import api

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

class APIPetWrapper:
    """Wraps API data to look like a local GuineaPig object"""
    def __init__(self, data):
        self.data = data
        self.id = data.get('id')
        self.name = data.get('name', 'Unknown')
        self.speed = data.get('speed', 0)
        self.endurance = data.get('endurance', 0)
        self.rarity = data.get('rarity_tier', 'Common')
        self.age_days = data.get('age_days', 0)
        
        # Safe color logic
        raw_pheno = data.get('color_phenotype')
        raw_color = data.get('color')
        self.phenotype = raw_pheno if raw_pheno else (raw_color if raw_color else 'White')
        
        self.image = self._load_smart_sprite()

    @property
    def is_adult(self):
        # Pet is adult if age >= 1 day (or whatever threshold you set)
        return self.age_days >= 1

    def _load_smart_sprite(self):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            sprite_folder = os.path.join(base_path, "Global Assets", "Sprites", "Guinea Pigs", "SH_GP_Sprites", "SH_GP_Sprites")
            
            filename = "SH_GP_White_01.png"
            c = str(self.phenotype).lower()
            
            if "brown" in c: filename = "SH_GP_Brown_01.png"
            elif "orange" in c: filename = "SH_GP_Orange_01.png"
            
            full_path = os.path.join(sprite_folder, filename)
            if os.path.exists(full_path):
                img = pygame.image.load(full_path).convert_alpha()
                return pygame.transform.scale(img, (120, 120))
        except: pass
        s = pygame.Surface((120, 120))
        s.fill((150, 75, 0))
        return s

class BreedingPage:
    def __init__(self, user_id=1):
        self.user_id = user_id
        self.pets = [] 
        
        self.parent1 = None
        self.parent2 = None
        self.message = "Loading pets..."
        self.message_color = WHITE
        
        self.naming_mode = False
        self.input_name = ""
        self.is_breeding_anim = False
        
        self.bg_img = None
        self.heart_active = None
        self.heart_unlit = None
        self._load_assets()
        
        self.back_btn_rect = pygame.Rect(20, 20, 100, 40)
        self.refresh_btn_rect = pygame.Rect(550, 20, 100, 40)
        self.breed_btn_rect = pygame.Rect(236, 440, 200, 60)
        self.bar1_rect = pygame.Rect(70, 320, 180, 40)
        self.bar2_rect = pygame.Rect(422, 320, 180, 40)

        self.title_font = pygame.font.SysFont("Arial", 30, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 18)

        self.refresh_pets()

    def _load_assets(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        def load(rel_path, size=None):
            path = os.path.join(base_path, rel_path)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    if size: img = pygame.transform.scale(img, size)
                    return img
                except: return None
            return None

        self.bg_img = load("Global Assets/Sprites/More Sprites/BG Art/Breed/BG_Breed.png", (672, 864))
        self.heart_active = load("Global Assets/Sprites/Breeding Page/BR_Active.png", (140, 140))
        self.heart_unlit = load("Global Assets/Sprites/Breeding Page/BR_Unlit.png", (140, 140))

    def refresh_pets(self):
        self.message = "Refreshing..."
        try:
            raw_pets = api.get_user_pets(self.user_id)
            self.pets = []
            
            adult_count = 0
            baby_count = 0
            
            for p in raw_pets:
                try:
                    wrapper = APIPetWrapper(p)
                    # Filter logic: Only show Adults
                    if wrapper.is_adult: 
                        self.pets.append(wrapper)
                        adult_count += 1
                    else:
                        baby_count += 1
                except: pass
            
            if not self.pets:
                if baby_count > 0:
                    self.message = f"Only babies found ({baby_count}). Grow them first!"
                else:
                    self.message = "No adult pets found."
                self.message_color = RED
            else:
                self.message = "Select two parents."
                self.message_color = WHITE
            
            # Reset slots if they hold invalid pets
            if self.parent1 and self.parent1 not in self.pets: self.parent1 = None
            if self.parent2 and self.parent2 not in self.pets: self.parent2 = None
            
        except Exception as e:
            self.message = "Connection Error!"
            self.message_color = RED
            print(f"Breeding Fetch Error: {e}")

    def handle_input(self, events):
        for event in events:
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

                if self.bar1_rect.inflate(20, 200).collidepoint(pos): self.parent1 = None
                if self.bar2_rect.inflate(20, 200).collidepoint(pos): self.parent2 = None

                list_start_y = 520
                item_height = 80
                for i, pig in enumerate(self.pets):
                    pig_y = list_start_y + (i * (item_height + 5))
                    if pig_y > 800: break 
                    
                    pig_rect = pygame.Rect(20, pig_y, 632, item_height)
                    if pig_rect.collidepoint(pos):
                        self._select_parent(pig)

        return None

    def _select_parent(self, pig):
        # Strict Double Check
        if not pig.is_adult:
            self.message = "That's a baby!"
            self.message_color = RED
            return

        if pig == self.parent1: self.parent1 = None; return
        if pig == self.parent2: self.parent2 = None; return
        if not self.parent1: self.parent1 = pig
        elif not self.parent2: self.parent2 = pig

    def _trigger_breed_api(self):
        self.message = "Breeding..."
        self.is_breeding_anim = True
        name = self.input_name if self.input_name else "Baby"
        
        try:
            data = {
                "parent1_id": self.parent1.id,
                "parent2_id": self.parent2.id,
                "child_name": name,
                "child_species": "Guinea Pig",
                "child_color": "Mixed",
                "owner_id": self.user_id
            }
            
            response = api._post("/genetics/breed/", json=data)
            
            self.message = f"Born: {response.get('child_name')}!"
            self.message_color = GREEN
            self.naming_mode = False
            self.parent1 = None
            self.parent2 = None
            self.refresh_pets()
            self.is_breeding_anim = False
            
        except Exception as e:
            # Display the actual error code from the server
            err_msg = str(e)
            if "500" in err_msg:
                self.message = "Server Error (Check DB)"
            elif "400" in err_msg:
                self.message = "Cannot Breed (Cooldown?)"
            else:
                self.message = "Error: " + err_msg[:20]
                
            self.message_color = RED
            print(f"BREED ERROR: {e}")
            self.naming_mode = False
            self.is_breeding_anim = False

    def draw(self, screen):
        if self.bg_img: screen.blit(self.bg_img, (0,0))
        else: screen.fill((40, 40, 50))

        pygame.draw.rect(screen, PLATFORM_COLOR, self.bar1_rect, border_radius=10)
        pygame.draw.rect(screen, PLATFORM_COLOR, self.bar2_rect, border_radius=10)
        
        if self.parent1:
            screen.blit(self.parent1.image, (self.bar1_rect.centerx - 60, self.bar1_rect.top - 130))
            nm = self.text_font.render(self.parent1.name, True, WHITE)
            screen.blit(nm, nm.get_rect(center=(self.bar1_rect.centerx, self.bar1_rect.top - 145)))
        else:
            txt = self.text_font.render("Select Parent 1", True, GRAY)
            screen.blit(txt, txt.get_rect(center=self.bar1_rect.center))

        if self.parent2:
            screen.blit(self.parent2.image, (self.bar2_rect.centerx - 60, self.bar2_rect.top - 130))
            nm = self.text_font.render(self.parent2.name, True, WHITE)
            screen.blit(nm, nm.get_rect(center=(self.bar2_rect.centerx, self.bar2_rect.top - 145)))
        else:
            txt = self.text_font.render("Select Parent 2", True, GRAY)
            screen.blit(txt, txt.get_rect(center=self.bar2_rect.center))

        heart_x = (self.bar1_rect.right + self.bar2_rect.left) // 2 - 70
        heart_y = self.bar1_rect.top - 110
        if self.is_breeding_anim or (self.parent1 and self.parent2):
            if self.heart_active: screen.blit(self.heart_active, (heart_x, heart_y))
        else:
            if self.heart_unlit: screen.blit(self.heart_unlit, (heart_x, heart_y))

        btn_color = GREEN if (self.parent1 and self.parent2) else GRAY
        pygame.draw.rect(screen, btn_color, self.breed_btn_rect, border_radius=10)
        btn_txt = self.title_font.render("BREED", True, WHITE)
        screen.blit(btn_txt, btn_txt.get_rect(center=self.breed_btn_rect.center))

        msg_s = self.text_font.render(self.message, True, self.message_color)
        screen.blit(msg_s, (20, 490))
        
        pygame.draw.rect(screen, RED, self.back_btn_rect, border_radius=5)
        screen.blit(self.text_font.render("BACK", True, WHITE), (35, 30))

        pygame.draw.rect(screen, BLUE, self.refresh_btn_rect, border_radius=5)
        screen.blit(self.text_font.render("REFRESH", True, WHITE), (560, 30))

        list_y = 520
        for pig in self.pets:
            is_sel = (pig == self.parent1 or pig == self.parent2)
            bg_col = BLUE if is_sel else DARK_GRAY
            rect = pygame.Rect(20, list_y, 632, 80)
            pygame.draw.rect(screen, bg_col, rect, border_radius=5)
            
            small = pygame.transform.scale(pig.image, (60, 60))
            screen.blit(small, (30, list_y + 10))
            screen.blit(self.title_font.render(pig.name, True, WHITE), (100, list_y + 15))
            stats = f"{pig.phenotype} | Spd:{pig.speed} | End:{pig.endurance} | Age:{pig.age_days}"
            screen.blit(self.text_font.render(stats, True, GRAY), (100, list_y + 50))
            list_y += 85

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

manager = None
def breeding_update(events, inv, time):
    global manager
    if not manager: manager = BreedingPage(user_id=1)
    return manager.handle_input(events)

def breeding_draw(screen, inv, time):
    global manager
    if not manager: manager = BreedingPage(user_id=1)
    manager.draw(screen)