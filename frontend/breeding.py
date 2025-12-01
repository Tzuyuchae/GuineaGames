import pygame
import random
import os
from datetime import datetime, timedelta

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

# 1 Real Minute = ~14.2 Game Minutes (based on 0.07s per game min)
# 30 Real Minutes = 6 Game Months
REAL_SEC_PER_GAME_MIN = 0.07 

def get_total_minutes(gt):
    """Converts game_time dict to total game minutes."""
    # Year 1, Month 1, Day 1 is the start
    # 1 Year = 12 Months, 1 Month = 30 Days, 1 Day = 24 Hours
    total = 0
    total += (gt['year'] - 1) * 12 * 30 * 24 * 60
    total += (gt['month'] - 1) * 30 * 24 * 60
    total += (gt['day'] - 1) * 24 * 60
    total += gt['hour'] * 60
    total += gt['minute']
    return total

class GuineaPig:
    def __init__(self, name, genes=None, birth_time=None, score=None):
        self.id = f"gp{random.randint(1000, 9999)}"
        self.name = name
        self.birth_time = birth_time or datetime.now() # Age still real-time for now
        self.last_bred_game_time = None # Stores total game minutes
        
        self.speed = random.randint(40, 90)
        self.endurance = random.randint(40, 90)
        
        base_score = score if score else random.randint(50, 150)
        self.score = base_score + int((self.speed + self.endurance) * 0.5)

        if genes is None:
            self.genes = self._generate_random_genes()
        else:
            self.genes = genes
        self.phenotype = self.calculate_phenotype()
        
        self.image = self._load_sprite()

    def _load_sprite(self):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_path, "images/guineapig.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (180, 180)) 
        except:
            pass
        s = pygame.Surface((180, 180))
        s.fill((150, 75, 0))
        return s
    
    def _generate_random_genes(self):
        alleles = {
            'coat_color' : random.choices(['B', 'b'], k=2),
            'coat_length' : random.choices(['S', 's'], k=2),
            'pattern' : random.choices(['P', 'p'], k=2),
            'eye_color' : random.choices(['E', 'e'], k=2),
            'fur_type' : random.choices(['R', 'r'], k=2)
        }
        for trait in alleles:
            alleles[trait].sort(reverse=True)
        return alleles

    def calculate_phenotype(self):
        p = {}
        p['coat_color'] = 'Brown' if 'B' in self.genes['coat_color'] else 'Black'
        p['coat_length'] = 'Short' if 'S' in self.genes['coat_length'] else 'Long'
        p['pattern'] = 'Solid' if 'P' in self.genes['pattern'] else 'Spotted'
        p['eye_color'] = 'Dark' if 'E' in self.genes['eye_color'] else 'Red'
        p['fur_type'] = 'Smooth' if 'R' in self.genes['fur_type'] else 'Rough'
        return p

    def get_age_stage(self):
        age = datetime.now() - self.birth_time
        maturity_time = timedelta(minutes=15) 
        return 'Adult' if age >= maturity_time else 'Baby'
        
    def force_adult(self):
        self.birth_time = datetime.now() - timedelta(minutes=20)

    def calculate_sell_price(self):
        if self.get_age_stage() == 'Baby': return 0
        return self.score + (self.speed + self.endurance)

    def can_breed(self, current_game_time):
        """
        Checks if the pig can breed based on GAME TIME.
        Cooldown: 6 Game Months (approx 30 real minutes).
        """
        if self.get_age_stage() == 'Baby': 
            return False, "Too Young"
        
        if self.last_bred_game_time is None: 
            return True, "Ready"
        
        # 6 Game Months in Minutes
        # 6 * 30 days * 24 hours * 60 minutes
        COOLDOWN_GAME_MINS = 6 * 30 * 24 * 60 
        
        current_total = get_total_minutes(current_game_time)
        time_since_breed = current_total - self.last_bred_game_time

        if time_since_breed < COOLDOWN_GAME_MINS:
            rem_game_mins = COOLDOWN_GAME_MINS - time_since_breed
            
            # Convert back to estimated real time for display
            rem_real_seconds = rem_game_mins * REAL_SEC_PER_GAME_MIN
            mins = int(rem_real_seconds // 60)
            secs = int(rem_real_seconds % 60)
            
            return False, f"Cooldown: {mins}m {secs}s"
            
        return True, "Ready"

class BreedingPage:
    def __init__(self):
        self.parent1 = None
        self.parent2 = None
        self.message = "Select two parents to breed."
        self.message_color = WHITE
        
        self.naming_mode = False
        self.temp_babies = []
        self.current_baby_idx = 0
        self.input_name = ""
        
        self.breeding_progress = 0 
        self.is_breeding_anim = False
        
        self.title_font = None
        self.text_font = None
        
        self.bg_img = None
        self.heart_active_img = None
        self.heart_unlit_img = None
        self.cooldown_img = None
        
        self.back_btn_rect = pygame.Rect(20, 20, 100, 40)
        self.breed_btn_rect = pygame.Rect(236, 440, 200, 60)

        self.bar1_rect = pygame.Rect(70, 320, 180, 40)
        self.bar2_rect = pygame.Rect(422, 320, 180, 40)

        self._load_assets()

    def _load_assets(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        def load(path):
            full_path = os.path.join(base_path, path)
            if os.path.exists(full_path):
                return pygame.image.load(full_path).convert_alpha()
            return None

        self.bg_img = load("Global Assets/Sprites/More Sprites/BG Art/Breed/BG_Breed.png")
        self.heart_active_img = load("Global Assets/Sprites/Breeding Page/BR_Active.png")
        self.heart_unlit_img = load("Global Assets/Sprites/Breeding Page/BR_Unlit.png")
        self.cooldown_img = load("Global Assets/Sprites/More Sprites/BG Art/Breed/Wireframe_Breed_Cooldown.png")

        if self.bg_img:
            self.bg_img = pygame.transform.scale(self.bg_img, (672, 864))
            
        if self.heart_active_img:
             self.heart_active_img = pygame.transform.scale(self.heart_active_img, (140, 140))
        if self.heart_unlit_img:
             self.heart_unlit_img = pygame.transform.scale(self.heart_unlit_img, (140, 140))
        
        if self.cooldown_img:
             self.cooldown_img = pygame.transform.scale(self.cooldown_img, (40, 40))

    def handle_input(self, events, player_inventory, current_game_time):
        if not self.title_font:
            self.title_font = pygame.font.SysFont("Arial", 30, bold=True)
            self.text_font = pygame.font.SysFont("Arial", 18)

        for event in events:
            if self.naming_mode:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self._confirm_baby_name(player_inventory)
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
                
                if self.breed_btn_rect.collidepoint(pos):
                    self._attempt_breed(current_game_time)

                list_start_y = 520
                item_height = 80
                for i, pig in enumerate(player_inventory.owned_pigs):
                    pig_y = list_start_y + (i * (item_height + 5))
                    if pig_y > 800: break 
                    
                    pig_rect = pygame.Rect(20, pig_y, 632, item_height)
                    if pig_rect.collidepoint(pos):
                        self._assign_parent(pig, current_game_time)
                        
                p1_click_rect = self.bar1_rect.inflate(20, 200).move(0, -100)
                if p1_click_rect.collidepoint(pos):
                    self.parent1 = None
                    
                p2_click_rect = self.bar2_rect.inflate(20, 200).move(0, -100)
                if p2_click_rect.collidepoint(pos):
                    self.parent2 = None

        return None

    def _assign_parent(self, pig, current_game_time):
        can_breed, reason = pig.can_breed(current_game_time)
        if not can_breed:
            self.message = f"{pig.name}: {reason}"
            self.message_color = RED
            return

        if pig == self.parent1:
            self.parent1 = None
            return
        if pig == self.parent2:
            self.parent2 = None
            return

        if self.parent1 is None:
            self.parent1 = pig
            self.message = f"Selected {pig.name} as Parent 1"
        elif self.parent2 is None:
            self.parent2 = pig
            self.message = f"Selected {pig.name} as Parent 2"
        else:
            self.message = "Slots full! Click a parent to remove first."

    def _attempt_breed(self, current_game_time):
        if not self.parent1 or not self.parent2:
            self.message = "Need two parents!"
            self.message_color = RED
            return
            
        self.is_breeding_anim = True
        self.breeding_progress = 0
        
        # We pass current_game_time to _generate_babies later via stored variable
        # but we can record the time now for logic
        self.breed_time_snapshot = get_total_minutes(current_game_time)

    def update_animation(self):
        if self.is_breeding_anim:
            self.breeding_progress += 2
            if self.breeding_progress >= 100:
                self.is_breeding_anim = False
                self._generate_babies()

    def _generate_babies(self):
        num_babies = random.randint(1, 3)
        self.temp_babies = []
        
        for i in range(num_babies):
            baby_genes = {}
            for trait in self.parent1.genes:
                g1 = random.choice(self.parent1.genes[trait])
                g2 = random.choice(self.parent2.genes[trait])
                baby_genes[trait] = sorted([g1, g2], reverse=True)
            
            baby = GuineaPig("", genes=baby_genes, birth_time=datetime.now())
            self.temp_babies.append(baby)
            
        # Start Cooldown (Using Game Time)
        self.parent1.last_bred_game_time = self.breed_time_snapshot
        self.parent2.last_bred_game_time = self.breed_time_snapshot
        
        self.naming_mode = True
        self.current_baby_idx = 0
        self.input_name = ""

    def _confirm_baby_name(self, player_inventory):
        name = self.input_name.strip()
        if not name: name = f"Baby_{random.randint(100,999)}"
        
        self.temp_babies[self.current_baby_idx].name = name
        self.current_baby_idx += 1
        self.input_name = ""
        
        if self.current_baby_idx >= len(self.temp_babies):
            player_inventory.owned_pigs.extend(self.temp_babies)
            self.message = f"Success! {len(self.temp_babies)} babies born!"
            self.message_color = GREEN
            self.naming_mode = False
            self.parent1 = None
            self.parent2 = None
            self.temp_babies = []

    def draw(self, screen, player_inventory, current_game_time):
        self.update_animation()

        if self.bg_img:
            screen.blit(self.bg_img, (0, 0))
        else:
            screen.fill((40, 40, 50))

        if not self.title_font:
            self.title_font = pygame.font.SysFont("Arial", 30, bold=True)
            self.text_font = pygame.font.SysFont("Arial", 18)

        if self.naming_mode:
            self._draw_naming_overlay(screen)
            return

        # --- PARENT SLOTS ---
        pygame.draw.rect(screen, PLATFORM_COLOR, self.bar1_rect, border_radius=10)
        pygame.draw.rect(screen, PLATFORM_COLOR, self.bar2_rect, border_radius=10)
        pygame.draw.rect(screen, GRAY, self.bar1_rect, 3, border_radius=10)
        pygame.draw.rect(screen, GRAY, self.bar2_rect, 3, border_radius=10)

        p1_sprite_pos = (self.bar1_rect.centerx - 90, self.bar1_rect.top - 170)
        p1_text_pos = (self.bar1_rect.centerx, self.bar1_rect.top - 190)
        
        p2_sprite_pos = (self.bar2_rect.centerx - 90, self.bar2_rect.top - 170)
        p2_text_pos = (self.bar2_rect.centerx, self.bar2_rect.top - 190)

        if self.parent1:
            screen.blit(self.parent1.image, p1_sprite_pos)
            nm = self.text_font.render(self.parent1.name, True, WHITE)
            nm_rect = nm.get_rect(center=p1_text_pos)
            screen.blit(nm, nm_rect)
        else:
            txt = self.text_font.render("Parent 1", True, GRAY)
            txt_rect = txt.get_rect(center=(self.bar1_rect.centerx, self.bar1_rect.top - 50))
            screen.blit(txt, txt_rect)

        if self.parent2:
            screen.blit(self.parent2.image, p2_sprite_pos)
            nm = self.text_font.render(self.parent2.name, True, WHITE)
            nm_rect = nm.get_rect(center=p2_text_pos)
            screen.blit(nm, nm_rect)
        else:
            txt = self.text_font.render("Parent 2", True, GRAY)
            txt_rect = txt.get_rect(center=(self.bar2_rect.centerx, self.bar2_rect.top - 50))
            screen.blit(txt, txt_rect)

        heart_x = (self.bar1_rect.right + self.bar2_rect.left) // 2 - 70
        heart_y = self.bar1_rect.top - 110
        
        if self.is_breeding_anim or (self.parent1 and self.parent2):
            if self.heart_active_img:
                screen.blit(self.heart_active_img, (heart_x, heart_y))
        else:
            if self.heart_unlit_img:
                screen.blit(self.heart_unlit_img, (heart_x, heart_y))

        if self.is_breeding_anim:
            bar_w = 200
            bar_h = 20
            bar_x = 236
            bar_y = 380 
            pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2)
            fill_w = int((self.breeding_progress / 100) * (bar_w - 4))
            pygame.draw.rect(screen, GREEN, (bar_x + 2, bar_y + 2, fill_w, bar_h - 4))

        if not self.is_breeding_anim:
            btn_color = GREEN if (self.parent1 and self.parent2) else GRAY
            pygame.draw.rect(screen, btn_color, self.breed_btn_rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, self.breed_btn_rect, 3, border_radius=10)
            
            btn_txt = self.title_font.render("BREED", True, WHITE)
            btn_rect = btn_txt.get_rect(center=self.breed_btn_rect.center)
            screen.blit(btn_txt, btn_rect)

        # --- BOTTOM SECTION ---
        list_start_y = 520
        item_height = 80
        
        msg_surf = self.text_font.render(self.message, True, self.message_color)
        screen.blit(msg_surf, (20, 490))
        
        pygame.draw.rect(screen, RED, self.back_btn_rect, border_radius=5)
        btn_txt = self.text_font.render("BACK", True, WHITE)
        btn_rect = btn_txt.get_rect(center=self.back_btn_rect.center)
        screen.blit(btn_txt, btn_rect)

        for i, pig in enumerate(player_inventory.owned_pigs):
            pig_y = list_start_y + (i * (item_height + 5))
            if pig_y > screen.get_height() - 20: break

            card_rect = pygame.Rect(20, pig_y, 632, item_height)
            color = DARK_GRAY
            if pig in [self.parent1, self.parent2]:
                color = BLUE
                pygame.draw.rect(screen, GOLD, card_rect.inflate(4,4), border_radius=5)

            pygame.draw.rect(screen, color, card_rect, border_radius=5)
            
            small_sprite = pygame.transform.scale(pig.image, (60, 60))
            screen.blit(small_sprite, (30, pig_y + 10))
            
            name_txt = self.text_font.render(f"{pig.name}", True, WHITE)
            screen.blit(name_txt, (110, pig_y + 15))
            
            stats = f"Speed:{pig.speed} | End:{pig.endurance}"
            screen.blit(self.text_font.render(stats, True, GRAY), (110, pig_y + 45))
            
            can, reason = pig.can_breed(current_game_time)
            
            if not can:
                if "Cooldown" in reason and self.cooldown_img:
                    screen.blit(self.cooldown_img, (560, pig_y + 20))
                    # Clean up text so it fits
                    clean_reason = reason.replace("Cooldown: ", "")
                    screen.blit(self.text_font.render(clean_reason, True, RED), (540, pig_y + 55))
                else:
                    screen.blit(self.text_font.render(reason, True, RED), (550, pig_y + 30))
            else:
                screen.blit(self.text_font.render("Ready", True, GREEN), (550, pig_y + 30))

    def _draw_naming_overlay(self, screen):
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(220)
        overlay.fill(BLACK)
        screen.blit(overlay, (0,0))
        
        w, h = 400, 300
        cx, cy = screen.get_width()//2, screen.get_height()//2
        rect = pygame.Rect(cx - w//2, cy - h//2, w, h)
        
        pygame.draw.rect(screen, (50, 50, 60), rect, border_radius=15)
        pygame.draw.rect(screen, GOLD, rect, 3, border_radius=15)
        
        current = self.current_baby_idx + 1
        total = len(self.temp_babies)
        
        title = self.title_font.render("It's a Baby!", True, WHITE)
        title_rect = title.get_rect(center=(cx, rect.y + 40))
        screen.blit(title, title_rect)
        
        count_txt = self.text_font.render(f"Naming {current} of {total}", True, GRAY)
        count_rect = count_txt.get_rect(center=(cx, rect.y + 80))
        screen.blit(count_txt, count_rect)
        
        baby_sprite = self.temp_babies[self.current_baby_idx].image
        sprite_rect = baby_sprite.get_rect(center=(cx, rect.y + 150))
        screen.blit(baby_sprite, sprite_rect)
        
        input_rect = pygame.Rect(cx - 150, rect.y + 210, 300, 40)
        pygame.draw.rect(screen, WHITE, input_rect)
        
        name_surf = self.title_font.render(self.input_name, True, BLACK)
        screen.blit(name_surf, (input_rect.x + 10, input_rect.y + 5))
        
        hint = self.text_font.render("Type Name + ENTER", True, GOLD)
        hint_rect = hint.get_rect(center=(cx, rect.bottom - 30))
        screen.blit(hint, hint_rect)

breeding_manager = BreedingPage()

def breeding_update(events, player_inventory, current_game_time):
    return breeding_manager.handle_input(events, player_inventory, current_game_time)

def breeding_draw(screen, player_inventory, current_game_time):
    breeding_manager.draw(screen, player_inventory, current_game_time)