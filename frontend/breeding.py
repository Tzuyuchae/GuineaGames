import pygame
import random
from datetime import datetime, timedelta

# --- CONSTANTS & COLORS ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
GREEN = (34, 139, 34)
RED = (178, 34, 34)
GOLD = (255, 215, 0)
BLUE = (70, 130, 180)

# --- 1. LOGIC CLASSES ---

class GuineaPig:
    def __init__(self, name, genes=None, birth_time=None, score=None):
        self.id = f"gp{random.randint(1000, 9999)}"
        self.name = name
        self.birth_time = birth_time or datetime.now()
        self.last_bred_time = None
        
        # Stats
        self.speed = random.randint(40, 90)
        self.endurance = random.randint(40, 90)
        
        # Calculate Score based on stats (Higher stats = Higher Value)
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
        p = {}
        p['coat_color'] = 'Brown' if 'B' in self.genes['coat_color'] else 'Black'
        p['coat_length'] = 'Short' if 'S' in self.genes['coat_length'] else 'Long'
        p['pattern'] = 'Solid' if 'P' in self.genes['pattern'] else 'Spotted'
        p['eye_color'] = 'Dark' if 'E' in self.genes['eye_color'] else 'Red'
        p['fur_type'] = 'Smooth' if 'R' in self.genes['fur_type'] else 'Rough'
        return p

    def get_age_stage(self):
        age = datetime.now() - self.birth_time
        # Babies mature in 1 minute (real time)
        maturity_time = timedelta(minutes=1) 
        return 'Adult' if age >= maturity_time else 'Baby'
        
    def force_adult(self):
        """Dev Tool: Instantly makes the pig an adult."""
        self.birth_time = datetime.now() - timedelta(minutes=5)

    def calculate_sell_price(self):
        """Calculates sell price based on age and stats."""
        if self.get_age_stage() == 'Baby':
            return 0 # Cannot sell babies
        
        # Base value + stat multiplier
        # E.g. 100 + (60 + 70) = 230 coins
        return self.score + (self.speed + self.endurance)

    def can_breed(self):
        if self.get_age_stage() == 'Baby':
            return False, "Too Young"
        if self.last_bred_time is None:
            return True, "Ready"
        
        cooldown = timedelta(minutes=5)
        time_since_breed = datetime.now() - self.last_bred_time

        if time_since_breed < cooldown:
            remaining = cooldown - time_since_breed
            mins = int(remaining.total_seconds() / 60)
            secs = int(remaining.total_seconds() % 60) 
            return False, f"Wait {mins}m {secs}s"
        return True, "Ready"

# --- 2. PAGE MANAGER ---

class BreedingPage:
    def __init__(self):
        self.parent1 = None
        self.parent2 = None
        self.message = "Select two parents to breed."
        self.message_color = WHITE
        
        self.back_btn_rect = pygame.Rect(20, 20, 100, 40)
        self.breed_btn_rect = pygame.Rect(380, 600, 200, 60)
        self.p1_slot_rect = pygame.Rect(360, 150, 240, 150)
        self.p2_slot_rect = pygame.Rect(360, 350, 240, 150)
        
        self.title_font = None
        self.text_font = None
        self.small_font = None

    def handle_click(self, pos, player_inventory):
        x, y = pos
        
        if self.back_btn_rect.collidepoint(pos):
            return 'homescreen'
            
        if self.p1_slot_rect.collidepoint(pos):
            self.parent1 = None
            self.message = "Parent 1 removed."
        if self.p2_slot_rect.collidepoint(pos):
            self.parent2 = None
            self.message = "Parent 2 removed."

        list_start_y = 100
        item_height = 80
        owned_pigs = player_inventory.owned_pigs
        
        for i, pig in enumerate(owned_pigs):
            pig_y = list_start_y + (i * (item_height + 5))
            if pig_y > 800: break 

            pig_rect = pygame.Rect(20, pig_y, 300, item_height)
            if pig_rect.collidepoint(pos):
                self._assign_parent(pig)
                
        if self.breed_btn_rect.collidepoint(pos):
            self._attempt_breed(player_inventory)

        return None

    def _assign_parent(self, pig):
        can_breed, reason = pig.can_breed()
        if not can_breed:
            self.message = f"{pig.name}: {reason}"
            self.message_color = RED
            return

        if self.parent1 is None:
            if pig == self.parent2:
                self.message = "Already selected as Parent 2!"
            else:
                self.parent1 = pig
                self.message = f"Selected {pig.name} as Parent 1."
                self.message_color = WHITE
        elif self.parent2 is None:
            if pig == self.parent1:
                self.message = "Already selected as Parent 1!"
            else:
                self.parent2 = pig
                self.message = f"Selected {pig.name} as Parent 2."
                self.message_color = WHITE
        else:
            self.message = "Slots full! Click a slot to clear it."
            self.message_color = GOLD

    def _attempt_breed(self, player_inventory):
        if not self.parent1 or not self.parent2:
            self.message = "Need two parents!"
            self.message_color = RED
            return
            
        num_babies = random.randint(1, 3)
        new_babies = []
        for i in range(num_babies):
            baby_genes = {}
            for trait in self.parent1.genes:
                g1 = random.choice(self.parent1.genes[trait])
                g2 = random.choice(self.parent2.genes[trait])
                baby_genes[trait] = sorted([g1, g2], reverse=True)
            
            name = f"Baby_{random.randint(100,999)}"
            baby = GuineaPig(name, genes=baby_genes, birth_time=datetime.now())
            new_babies.append(baby)
            
        self.parent1.last_bred_time = datetime.now()
        self.parent2.last_bred_time = datetime.now()
        
        player_inventory.owned_pigs.extend(new_babies)
        
        self.parent1 = None
        self.parent2 = None
        
        self.message = f"Success! {num_babies} new babies born!"
        self.message_color = GREEN

    def draw(self, screen, player_inventory):
        if not self.title_font:
            self.title_font = pygame.font.SysFont("Arial", 30, bold=True)
            self.text_font = pygame.font.SysFont("Arial", 18)
            self.small_font = pygame.font.SysFont("Arial", 14)

        screen.fill((40, 40, 50))

        title_surf = self.title_font.render("Breeding Center", True, GOLD)
        screen.blit(title_surf, (screen.get_width()//2 - title_surf.get_width()//2, 20))

        pygame.draw.rect(screen, RED, self.back_btn_rect, border_radius=5)
        back_text = self.text_font.render("BACK", True, WHITE)
        screen.blit(back_text, (self.back_btn_rect.x + 25, self.back_btn_rect.y + 10))

        msg_surf = self.text_font.render(self.message, True, self.message_color)
        screen.blit(msg_surf, (20, 70))

        list_start_y = 100
        item_height = 80
        owned_pigs = player_inventory.owned_pigs
        
        if not owned_pigs:
            empty_txt = self.text_font.render("No Guinea Pigs owned!", True, GRAY)
            screen.blit(empty_txt, (50, 200))

        for i, pig in enumerate(owned_pigs):
            pig_y = list_start_y + (i * (item_height + 5))
            if pig_y > screen.get_height() - 100: break

            card_rect = pygame.Rect(20, pig_y, 320, item_height)
            color = DARK_GRAY
            if pig == self.parent1 or pig == self.parent2:
                color = BLUE
                pygame.draw.rect(screen, GOLD, card_rect.inflate(4,4), border_radius=5)
            
            pygame.draw.rect(screen, color, card_rect, border_radius=5)

            name_txt = self.text_font.render(f"{pig.name}", True, WHITE)
            screen.blit(name_txt, (30, pig_y + 5))
            
            pheno = f"{pig.phenotype.get('coat_color', '?')} | {pig.phenotype.get('pattern', '?')}"
            desc_txt = self.small_font.render(pheno, True, GRAY)
            screen.blit(desc_txt, (30, pig_y + 30))
            
            can_breed, reason = pig.can_breed()
            status_color = GREEN if can_breed else RED
            status_txt = self.small_font.render(reason, True, status_color)
            screen.blit(status_txt, (30, pig_y + 50))
            
            stage_txt = self.small_font.render(pig.get_age_stage(), True, WHITE)
            screen.blit(stage_txt, (250, pig_y + 5))

        self._draw_slot(screen, "Parent 1", self.p1_slot_rect, self.parent1)
        self._draw_slot(screen, "Parent 2", self.p2_slot_rect, self.parent2)

        btn_color = GREEN if (self.parent1 and self.parent2) else GRAY
        pygame.draw.rect(screen, btn_color, self.breed_btn_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.breed_btn_rect, 3, border_radius=10)
        
        breed_txt = self.title_font.render("BREED", True, WHITE if (self.parent1 and self.parent2) else DARK_GRAY)
        screen.blit(breed_txt, (self.breed_btn_rect.centerx - breed_txt.get_width()//2, 
                                self.breed_btn_rect.centery - breed_txt.get_height()//2))

    def _draw_slot(self, screen, label, rect, pig):
        pygame.draw.rect(screen, (30,30,30), rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
        
        lbl = self.text_font.render(label, True, GRAY)
        screen.blit(lbl, (rect.x + 10, rect.y + 10))
        
        if pig:
            name = self.title_font.render(pig.name, True, GOLD)
            screen.blit(name, (rect.centerx - name.get_width()//2, rect.centery - 20))
            
            stats = f"{pig.phenotype.get('coat_color', '?')}, {pig.phenotype.get('coat_length', '?')}"
            s_txt = self.small_font.render(stats, True, WHITE)
            screen.blit(s_txt, (rect.centerx - s_txt.get_width()//2, rect.centery + 15))
            
            click_txt = self.small_font.render("(Click to remove)", True, RED)
            screen.blit(click_txt, (rect.centerx - click_txt.get_width()//2, rect.centery + 40))
        else:
            empty = self.text_font.render("Empty", True, DARK_GRAY)
            screen.blit(empty, (rect.centerx - empty.get_width()//2, rect.centery))


breeding_manager = BreedingPage()

def breeding_update(events, player_inventory):
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            result = breeding_manager.handle_click(event.pos, player_inventory)
            if result:
                return result
    return None

def breeding_draw(screen, player_inventory):
    breeding_manager.draw(screen, player_inventory)