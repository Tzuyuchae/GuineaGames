import pygame
import random
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

class GuineaPig:
    def __init__(self, name, genes=None, birth_time=None, score=None):
        self.id = f"gp{random.randint(1000, 9999)}"
        self.name = name
        self.birth_time = birth_time or datetime.now()
        self.last_bred_time = None
        
        self.speed = random.randint(40, 90)
        self.endurance = random.randint(40, 90)
        
        base_score = score if score else random.randint(50, 150)
        self.score = base_score + int((self.speed + self.endurance) * 0.5)

        if genes is None:
            self.genes = self._generate_random_genes()
        else:
            self.genes = genes
        self.phenotype = self.calculate_phenotype()
    
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
        # Simplified for brevity, same as before
        p = {}
        p['coat_color'] = 'Brown' if 'B' in self.genes['coat_color'] else 'Black'
        p['coat_length'] = 'Short' if 'S' in self.genes['coat_length'] else 'Long'
        p['pattern'] = 'Solid' if 'P' in self.genes['pattern'] else 'Spotted'
        p['eye_color'] = 'Dark' if 'E' in self.genes['eye_color'] else 'Red'
        p['fur_type'] = 'Smooth' if 'R' in self.genes['fur_type'] else 'Rough'
        return p

    def get_age_stage(self):
        age = datetime.now() - self.birth_time
        maturity_time = timedelta(minutes=1) 
        return 'Adult' if age >= maturity_time else 'Baby'
        
    def force_adult(self):
        self.birth_time = datetime.now() - timedelta(minutes=5)

    def calculate_sell_price(self):
        if self.get_age_stage() == 'Baby': return 0
        return self.score + (self.speed + self.endurance)

    def can_breed(self):
        if self.get_age_stage() == 'Baby': return False, "Too Young"
        if self.last_bred_time is None: return True, "Ready"
        
        cooldown = timedelta(minutes=5)
        time_since_breed = datetime.now() - self.last_bred_time

        if time_since_breed < cooldown:
            rem = cooldown - time_since_breed
            return False, f"Wait {int(rem.total_seconds()/60)}m"
        return True, "Ready"

class BreedingPage:
    def __init__(self):
        # Selection State
        self.parent1 = None
        self.parent2 = None
        self.message = "Select two parents to breed."
        self.message_color = WHITE
        
        # Rects
        self.back_btn_rect = pygame.Rect(20, 20, 100, 40)
        self.breed_btn_rect = pygame.Rect(380, 600, 200, 60)
        self.p1_slot_rect = pygame.Rect(360, 150, 240, 150)
        self.p2_slot_rect = pygame.Rect(360, 350, 240, 150)
        
        # Naming Phase State
        self.naming_mode = False
        self.temp_babies = []
        self.current_baby_idx = 0
        self.input_name = ""
        
        # Fonts
        self.title_font = None
        self.text_font = None

    def handle_input(self, events, player_inventory):
        # Init fonts if needed
        if not self.title_font:
            self.title_font = pygame.font.SysFont("Arial", 30, bold=True)
            self.text_font = pygame.font.SysFont("Arial", 18)

        for event in events:
            # --- NAMING PHASE INPUT ---
            if self.naming_mode:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self._confirm_baby_name(player_inventory)
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_name = self.input_name[:-1]
                    else:
                        if len(self.input_name) < 12:
                            self.input_name += event.unicode
                return None # Block other inputs

            # --- NORMAL PHASE INPUT ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                
                if self.back_btn_rect.collidepoint(pos):
                    return 'homescreen'
                    
                if self.p1_slot_rect.collidepoint(pos):
                    self.parent1 = None
                    self.message = "Parent 1 removed."
                if self.p2_slot_rect.collidepoint(pos):
                    self.parent2 = None
                    self.message = "Parent 2 removed."

                if self.breed_btn_rect.collidepoint(pos):
                    self._attempt_breed()

                # Check inventory clicks
                list_start_y = 100
                item_height = 80
                for i, pig in enumerate(player_inventory.owned_pigs):
                    pig_y = list_start_y + (i * (item_height + 5))
                    if pig_y > 800: break 
                    
                    pig_rect = pygame.Rect(20, pig_y, 300, item_height)
                    if pig_rect.collidepoint(pos):
                        self._assign_parent(pig)
                        
        return None

    def _assign_parent(self, pig):
        can_breed, reason = pig.can_breed()
        if not can_breed:
            self.message = f"{pig.name}: {reason}"
            self.message_color = RED
            return

        if self.parent1 is None:
            if pig == self.parent2: self.message = "Already selected!"
            else:
                self.parent1 = pig
                self.message = f"Selected {pig.name}"
                self.message_color = WHITE
        elif self.parent2 is None:
            if pig == self.parent1: self.message = "Already selected!"
            else:
                self.parent2 = pig
                self.message = f"Selected {pig.name}"
                self.message_color = WHITE
        else:
            self.message = "Slots full! Click slot to remove."

    def _attempt_breed(self):
        if not self.parent1 or not self.parent2:
            self.message = "Need two parents!"
            self.message_color = RED
            return
            
        # Generate Data but DO NOT add to inventory yet
        num_babies = random.randint(1, 3)
        self.temp_babies = []
        
        for i in range(num_babies):
            baby_genes = {}
            for trait in self.parent1.genes:
                g1 = random.choice(self.parent1.genes[trait])
                g2 = random.choice(self.parent2.genes[trait])
                baby_genes[trait] = sorted([g1, g2], reverse=True)
            
            # Create pig with placeholder name
            baby = GuineaPig("", genes=baby_genes, birth_time=datetime.now())
            self.temp_babies.append(baby)
            
        # Enter Naming Mode
        self.naming_mode = True
        self.current_baby_idx = 0
        self.input_name = ""
        self.parent1.last_bred_time = datetime.now()
        self.parent2.last_bred_time = datetime.now()

    def _confirm_baby_name(self, player_inventory):
        name = self.input_name.strip()
        if not name: name = f"Baby_{random.randint(100,999)}"
        
        # Set Name
        self.temp_babies[self.current_baby_idx].name = name
        
        # Move to next baby or Finish
        self.current_baby_idx += 1
        self.input_name = ""
        
        if self.current_baby_idx >= len(self.temp_babies):
            # All named, finish up
            player_inventory.owned_pigs.extend(self.temp_babies)
            self.message = f"Success! {len(self.temp_babies)} babies born!"
            self.message_color = GREEN
            self.naming_mode = False
            self.parent1 = None
            self.parent2 = None
            self.temp_babies = []

    def draw(self, screen, player_inventory):
        if not self.title_font:
            self.title_font = pygame.font.SysFont("Arial", 30, bold=True)
            self.text_font = pygame.font.SysFont("Arial", 18)

        # If Naming, draw naming overlay
        if self.naming_mode:
            self._draw_naming_overlay(screen)
            return

        # --- Normal Draw Code ---
        screen.fill((40, 40, 50))
        title_surf = self.title_font.render("Breeding Center", True, GOLD)
        screen.blit(title_surf, (screen.get_width()//2 - title_surf.get_width()//2, 20))

        pygame.draw.rect(screen, RED, self.back_btn_rect, border_radius=5)
        screen.blit(self.text_font.render("BACK", True, WHITE), (45, 30))

        msg_surf = self.text_font.render(self.message, True, self.message_color)
        screen.blit(msg_surf, (20, 70))

        # Draw Inventory List
        list_start_y = 100
        item_height = 80
        for i, pig in enumerate(player_inventory.owned_pigs):
            pig_y = list_start_y + (i * (item_height + 5))
            if pig_y > screen.get_height() - 100: break

            color = BLUE if pig in [self.parent1, self.parent2] else DARK_GRAY
            pygame.draw.rect(screen, color, (20, pig_y, 320, item_height), border_radius=5)
            
            name_txt = self.text_font.render(f"{pig.name}", True, WHITE)
            screen.blit(name_txt, (30, pig_y + 10))
            
            # Stats snippet
            stats = f"Speed:{pig.speed} | End:{pig.endurance}"
            screen.blit(self.text_font.render(stats, True, GRAY), (30, pig_y + 35))
            
            # Status
            can, reason = pig.can_breed()
            col = GREEN if can else RED
            screen.blit(self.text_font.render(reason if not can else "Ready", True, col), (30, pig_y + 55))

        # Draw Slots
        self._draw_slot(screen, "Parent 1", self.p1_slot_rect, self.parent1)
        self._draw_slot(screen, "Parent 2", self.p2_slot_rect, self.parent2)

        # Breed Button
        btn_color = GREEN if (self.parent1 and self.parent2) else GRAY
        pygame.draw.rect(screen, btn_color, self.breed_btn_rect, border_radius=10)
        btn_txt = self.title_font.render("BREED", True, WHITE)
        screen.blit(btn_txt, (self.breed_btn_rect.centerx - btn_txt.get_width()//2, 
                              self.breed_btn_rect.centery - btn_txt.get_height()//2))

    def _draw_slot(self, screen, label, rect, pig):
        pygame.draw.rect(screen, (30,30,30), rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
        screen.blit(self.text_font.render(label, True, GRAY), (rect.x+10, rect.y+10))
        
        if pig:
            nm = self.title_font.render(pig.name, True, GOLD)
            screen.blit(nm, (rect.centerx - nm.get_width()//2, rect.centery - 15))

    def _draw_naming_overlay(self, screen):
        # Darken BG
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0,0))
        
        # Box
        w, h = 400, 300
        cx, cy = screen.get_width()//2, screen.get_height()//2
        rect = pygame.Rect(cx - w//2, cy - h//2, w, h)
        pygame.draw.rect(screen, (50, 50, 60), rect, border_radius=15)
        pygame.draw.rect(screen, GOLD, rect, 3, border_radius=15)
        
        # Text
        total = len(self.temp_babies)
        current = self.current_baby_idx + 1
        
        title = self.title_font.render("It's a Baby!", True, WHITE)
        screen.blit(title, (cx - title.get_width()//2, rect.y + 30))
        
        count_txt = self.text_font.render(f"Naming baby {current} of {total}", True, GRAY)
        screen.blit(count_txt, (cx - count_txt.get_width()//2, rect.y + 80))
        
        # Input Box
        input_rect = pygame.Rect(cx - 150, rect.y + 130, 300, 50)
        pygame.draw.rect(screen, WHITE, input_rect)
        
        # Input Text
        name_surf = self.title_font.render(self.input_name, True, BLACK)
        screen.blit(name_surf, (input_rect.x + 10, input_rect.y + 10))
        
        # Footer
        hint = self.text_font.render("Type name and press ENTER", True, GOLD)
        screen.blit(hint, (cx - hint.get_width()//2, rect.bottom - 50))


breeding_manager = BreedingPage()

def breeding_update(events, player_inventory):
    return breeding_manager.handle_input(events, player_inventory)

def breeding_draw(screen, player_inventory):
    breeding_manager.draw(screen, player_inventory)