import pygame
import random
import os
from datetime import datetime, timedelta

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

# --- GAME TIME / COOLDOWN LOGIC ---
# 6 Game Months Cooldown
GAME_MIN_PER_REAL_SEC = 1 / 0.07  # Real Seconds to 1 Game Minute
GAME_MIN_PER_YEAR = 12 * 30 * 24 * 60
GAME_MIN_PER_MONTH = 30 * 24 * 60
GAME_MIN_PER_DAY = 24 * 60
COOLDOWN_GAME_MINS = 6 * GAME_MIN_PER_MONTH  # 6 Game Months
REAL_SEC_PER_GAME_MIN = 0.07

# NEW: how long (in game minutes) until a pig is considered Adult
MATURITY_GAME_MINS = 3 * GAME_MIN_PER_MONTH  # 3 game months to adulthood


def get_total_minutes(gt):
    """Converts game_time dict to total game minutes."""
    # Year 1, Month 1, Day 1 is the start
    # 1 Year = 12 Months, 1 Month = 30 Days, 1 Day = 24 Hours
    total = 0
    total += (gt["year"] - 1) * GAME_MIN_PER_YEAR
    total += (gt["month"] - 1) * GAME_MIN_PER_MONTH
    total += (gt["day"] - 1) * GAME_MIN_PER_DAY
    total += gt["hour"] * 60
    total += gt["minute"]
    return total


class GuineaPig:
    def __init__(self, name, genes=None, birth_time=None, score=None,
                 birth_game_minutes: int | None = None):
        """
        Logical guinea pig data model.

        birth_game_minutes:
            - If provided, used for game-time-based aging.
            - If None, defaults to 0 (start of time), so pigs will
              quickly end up as Adults once game_time advances.
        """
        self.id = f"gp{random.randint(1000, 9999)}"
        self.name = name
        # Backend Pet.id if this pig has been saved to the API
        self.backend_id: int | None = None

        # Keep real-time birth_time for backwards-compatibility / debug
        self.birth_time = birth_time or datetime.now()

        # NEW: game-time birth minute (used for age stage in gameplay)
        self.birth_game_minutes = birth_game_minutes if birth_game_minutes is not None else 0

        # When this pig last bred (in total game minutes)
        self.last_bred_game_time = None  # Stores total game minutes

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
        """
        Loads the correct sprite based on phenotype.
        If the specific sprite doesn't exist yet (probably right now),
        it falls back to pig_default.png so the game never breaks.
        """

        base_path = os.path.dirname(os.path.abspath(__file__))

        # --- Extract phenotype traits (with safe defaults) ---
        coat = (self.phenotype.get("coat_color") or "brown").lower()
        length = (self.phenotype.get("coat_length") or "short").lower()
        pattern = (self.phenotype.get("pattern") or "solid").lower()

        # Build expected filename for future sprite variants
        sprite_name = f"pig_{coat}_{length}_{pattern}.png"
        sprite_path = os.path.join(base_path, "images", sprite_name)

        # --- Fallback to default sprite ---
        default_path = os.path.join(base_path, "images", "pig_default.png")

        # Decide which file to load
        if os.path.exists(sprite_path):
            use_path = sprite_path
        else:
            use_path = default_path  # safe fallback (which you already have)

        # --- Load and scale safely ---
        try:
            img = pygame.image.load(use_path).convert_alpha()
            img = pygame.transform.scale(img, (180, 180))
            return img
        except Exception as e:
            print(f"[GuineaPig] Failed loading sprite at {use_path}: {e}")
            # Emergency final fallback: plain colored square
            fallback = pygame.Surface((180, 180), pygame.SRCALPHA)
            fallback.fill((200, 100, 100, 255))
            return fallback

    def _generate_random_genes(self):
        alleles = {
            "coat_color": random.choices(["B", "b"], k=2),
            "coat_length": random.choices(["S", "s"], k=2),
            "pattern": random.choices(["P", "p"], k=2),
            "eye_color": random.choices(["E", "e"], k=2),
            "fur_type": random.choices(["R", "r"], k=2),
        }
        for trait in alleles:
            alleles[trait].sort(reverse=True)
        return alleles

    def calculate_phenotype(self):
        p = {}
        p["coat_color"] = "Brown" if "B" in self.genes["coat_color"] else "Black"
        p["coat_length"] = "Short" if "S" in self.genes["coat_length"] else "Long"
        p["pattern"] = "Solid" if "P" in self.genes["pattern"] else "Spotted"
        p["eye_color"] = "Dark" if "E" in self.genes["eye_color"] else "Red"
        p["fur_type"] = "Smooth" if "R" in self.genes["fur_type"] else "Rough"
        return p

    def get_age_stage(self, current_game_time: dict | None = None):
        """
        Determine if the guinea pig is a Baby or Adult.

        - If current_game_time is provided -> use game-time-based aging.
        - If not provided -> fall back to old real-time behavior so
          existing callers (e.g., popup details) don't explode.
        """
        if current_game_time is not None:
            current_total = get_total_minutes(current_game_time)
            age_game_minutes = current_total - self.birth_game_minutes
            return "Adult" if age_game_minutes >= MATURITY_GAME_MINS else "Baby"

        # Fallback: old behavior (real-time age)
        age = datetime.now() - self.birth_time
        maturity_time = timedelta(minutes=15)
        return "Adult" if age >= maturity_time else "Baby"

    def force_adult(self, current_game_time: dict | None = None):
        """
        Debug helper: instantly make pig an Adult.

        - If current_game_time is given, set birth_game_minutes so that
          age >= MATURITY_GAME_MINS.
        - Otherwise, fall back to old real-time hack.
        """
        if current_game_time is not None:
            current_total = get_total_minutes(current_game_time)
            self.birth_game_minutes = current_total - MATURITY_GAME_MINS
        else:
            # Old real-time hack
            self.birth_time = datetime.now() - timedelta(minutes=20)

    def can_breed(self, current_game_time):
        """
        Checks if the pig can breed based on GAME TIME.
        Cooldown: 6 Game Months (~30 real minutes).
        """
        # NEW: age check uses game-time-based age stage
        if self.get_age_stage(current_game_time) == "Baby":
            return False, "Too Young"

        if self.last_bred_game_time is None:
            return True, "Ready"

        current_total = get_total_minutes(current_game_time)
        time_since_breed = current_total - self.last_bred_game_time

        if time_since_breed < COOLDOWN_GAME_MINS:
            rem_game_mins = COOLDOWN_GAME_MINS - time_since_breed

            # Convert remaining game minutes back to real seconds
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

        self.is_breeding_anim = False
        self.breeding_progress = 0
        self.breed_time_snapshot = None  # total game minutes at breeding

        # Layout rectangles
        self.bar1_rect = pygame.Rect(60, 220, 200, 80)
        self.bar2_rect = pygame.Rect(412, 220, 200, 80)

        self.heart_rect = pygame.Rect(264, 260, 140, 140)

        self.message_rect = pygame.Rect(40, 450, 592, 60)
        self.pig_list_rect = pygame.Rect(40, 540, 592, 260)

        # Fonts & images
        pygame.font.init()
        self.title_font = pygame.font.SysFont("arial", 36, bold=True)
        self.text_font = pygame.font.SysFont("arial", 22)
        self.small_font = pygame.font.SysFont("arial", 18)

        # Name input box
        self.name_box_rect = pygame.Rect(160, 420, 320, 40)
        self.confirm_button_rect = pygame.Rect(230, 480, 180, 40)

        # Load background & icons
        self.bg_img = None
        self.heart_active_img = None
        self.heart_unlit_img = None
        self.cooldown_img = None

        try:
            base_path = os.path.dirname(os.path.abspath(__file__))

            def load(rel):
                full = os.path.join(base_path, rel)
                return pygame.image.load(full).convert_alpha() if os.path.exists(full) else None

            self.bg_img = load("Global Assets/Sprites/Breeding Page/Breeding_BG.png")
            self.heart_active_img = load("Global Assets/Sprites/Breeding Page/BR_Active.png")
            self.heart_unlit_img = load("Global Assets/Sprites/Breeding Page/BR_Unlit.png")
            self.cooldown_img = load("Global Assets/Sprites/More Sprites/BG Art/Breed/Wireframe_Breed_Cooldown.png")
        except:
            pass

        if self.bg_img:
            self.bg_img = pygame.transform.scale(self.bg_img, (672, 864))

        if self.heart_active_img:
            self.heart_active_img = pygame.transform.scale(self.heart_active_img, (140, 140))
        if self.heart_unlit_img:
            self.heart_unlit_img = pygame.transform.scale(self.heart_unlit_img, (140, 140))

        if self.cooldown_img:
            self.cooldown_img = pygame.transform.scale(self.cooldown_img, (40, 40))

    def handle_input(self, events, player_inventory, current_game_time):
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            # --- NEW: ESCAPE to go back to homescreen ---
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "homescreen"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.naming_mode:
                    # In naming overlay, handle text and confirm
                    if self.name_box_rect.collidepoint(mouse_pos):
                        pass
                    if self.confirm_button_rect.collidepoint(mouse_pos):
                        self._confirm_baby_name(player_inventory)
                    continue

                # Click detection for selecting parents
                if self.bar1_rect.collidepoint(mouse_pos):
                    if self.parent1 is not None:
                        self.parent1 = None
                    else:
                        self._pick_parent_from_list(player_inventory, current_game_time, index=0)
                    return None

                if self.bar2_rect.collidepoint(mouse_pos):
                    if self.parent2 is not None:
                        self.parent2 = None
                    else:
                        self._pick_parent_from_list(player_inventory, current_game_time, index=1)
                    return None

                if self.heart_rect.collidepoint(mouse_pos):
                    self._attempt_breed(current_game_time)
                    return None

                # Click on pig list to select parents
                self._handle_pig_list_click(mouse_pos, player_inventory, current_game_time)

            elif event.type == pygame.KEYDOWN:
                if self.naming_mode:
                    if event.key == pygame.K_BACKSPACE:
                        self.input_name = self.input_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        self._confirm_baby_name(player_inventory)
                    else:
                        ch = event.unicode
                        if len(ch) == 1 and ch.isprintable() and len(self.input_name) < 20:
                            self.input_name += ch

        return None

    def _pick_parent_from_list(self, player_inventory, current_game_time, index):
        """
        Simple parent selection: choose first or second available adult pig,
        based on GAME-TIME age.
        """
        candidates = [
            p for p in player_inventory.owned_pigs
            if p.get_age_stage(current_game_time) == "Adult"
        ]
        if not candidates:
            self.message = "No adult pigs available!"
            self.message_color = RED
            return

        if index == 0:
            self.parent1 = candidates[0]
            self.message = f"Selected {self.parent1.name} as Parent 1"
        elif index == 1:
            self.parent2 = candidates[1] if len(candidates) > 1 else candidates[0]
            self.message = f"Selected {self.parent2.name} as Parent 2"

    def _handle_pig_list_click(self, mouse_pos, player_inventory, current_game_time):
        """
        Click in scrolling list of pigs to pick parents.
        """
        if not self.pig_list_rect.collidepoint(mouse_pos):
            return

        rel_y = mouse_pos[1] - self.pig_list_rect.y
        index = rel_y // 40
        if index < 0 or index >= len(player_inventory.owned_pigs):
            return

        pig = player_inventory.owned_pigs[index]
        if pig.get_age_stage(current_game_time) == "Baby":
            self.message = "That pig is still a baby!"
            self.message_color = RED
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

        # Check individual cooldowns (uses game-time age/cooldown)
        can1, msg1 = self.parent1.can_breed(current_game_time)
        can2, msg2 = self.parent2.can_breed(current_game_time)

        if not can1 or not can2:
            if not can1 and not can2:
                self.message = f"Parents on cooldown: {msg1}, {msg2}"
            elif not can1:
                self.message = f"{self.parent1.name}: {msg1}"
            else:
                self.message = f"{self.parent2.name}: {msg2}"
            self.message_color = RED
            return

        self.is_breeding_anim = True
        self.breeding_progress = 0

        # Store game-time snapshot for cooldown tracking AND baby birth time
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

        for _ in range(num_babies):
            baby_genes = {}
            for trait in self.parent1.genes:
                g1 = random.choice(self.parent1.genes[trait])
                g2 = random.choice(self.parent2.genes[trait])
                baby_genes[trait] = sorted([g1, g2], reverse=True)

            # NEW: use game-time birth minute instead of real datetime
            baby = GuineaPig(
                "",
                genes=baby_genes,
                birth_game_minutes=self.breed_time_snapshot,
            )
            self.temp_babies.append(baby)

        # Start Cooldown (Using Game Time)
        self.parent1.last_bred_game_time = self.breed_time_snapshot
        self.parent2.last_bred_game_time = self.breed_time_snapshot

        self.naming_mode = True
        self.current_baby_idx = 0
        self.input_name = ""

    def _draw_naming_overlay(self, screen):
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = self.title_font.render("Name Your New Baby!", True, GOLD)
        title_rect = title.get_rect(center=(screen.get_width() // 2, 200))
        screen.blit(title, title_rect)

        # Current baby preview
        if self.temp_babies:
            baby = self.temp_babies[self.current_baby_idx]
            img_rect = baby.image.get_rect(center=(screen.get_width() // 2, 320))
            screen.blit(baby.image, img_rect)

        pygame.draw.rect(screen, WHITE, self.name_box_rect, border_radius=8)
        pygame.draw.rect(screen, DARK_GRAY, self.name_box_rect, 2, border_radius=8)

        txt_surface = self.text_font.render(self.input_name or "Type a name...", True, BLACK)
        txt_rect = txt_surface.get_rect(midleft=(self.name_box_rect.x + 10, self.name_box_rect.centery))
        screen.blit(txt_surface, txt_rect)

        pygame.draw.rect(screen, GREEN, self.confirm_button_rect, border_radius=8)
        btn_txt = self.text_font.render("Confirm", True, WHITE)
        btn_rect = btn_txt.get_rect(center=self.confirm_button_rect.center)
        screen.blit(btn_txt, btn_rect)

    def _confirm_baby_name(self, player_inventory):
        """
        Handles naming a baby AND integrates backend genetics if possible.
        """
        name = self.input_name.strip()
        if not name:
            name = f"Baby_{random.randint(100,999)}"

        # Local baby object (created earlier during generate_babies)
        baby = self.temp_babies[self.current_baby_idx]
        baby.name = name

        # ----------------------------------------------
        # 🔥 Try backend genetics inheritance
        # ----------------------------------------------
        backend_success = False

        try:
            # Both parents MUST have backend IDs for real breeding
            if baby.backend_id is None and \
               self.parent1.backend_id is not None and \
               self.parent2.backend_id is not None:

                # Using phenotype coat_color as offspring base color
                phenotype_color = baby.phenotype.get("coat_color", "Brown")

                resp = api.breed_pets(
                    parent1_id=self.parent1.backend_id,
                    parent2_id=self.parent2.backend_id,
                    offspring_name=name,
                    offspring_color=phenotype_color
                )

                # Backend returns: pet_id + genetics + color
                pet_id = resp.get("pet_id")
                genetics = resp.get("genetics", [])
                color = resp.get("color", phenotype_color)

                if pet_id is not None:
                    # Assign backend_id so the pig becomes persistent
                    baby.backend_id = pet_id

                    # Convert backend genetics (list of {"gene": "...", "alleles": ["A","a"]})
                    # into your local format {trait: [dom, rec]}
                    converted = {}
                    for g in genetics:
                        gene_name = g["gene"]
                        alleles = g["alleles"]
                        # Sort so dominant allele first
                        sorted_alleles = sorted(alleles, reverse=True)
                        converted[gene_name] = sorted_alleles

                    # Apply real genetics
                    baby.genes = converted
                    baby.phenotype["coat_color"] = color

                    backend_success = True

        except Exception as e:
            print(f"[Breeding] Backend genetics failed, falling back to local genetics: {e}")

        # ----------------------------------------------
        # Fallback: keep your existing local gene version
        # ----------------------------------------------
        if not backend_success:
            print("[Breeding] Using local genetics inheritance.")

        # Move on to next baby
        self.current_baby_idx += 1
        self.input_name = ""

        # If all babies done → finalize
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

        # Title
        title = self.title_font.render("Breeding Center", True, GOLD)
        title_rect = title.get_rect(center=(screen.get_width() // 2, 60))
        screen.blit(title, title_rect)

        # Parent slots
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

        # Heart / breeding button
        heart_img = self.heart_active_img if self.is_breeding_anim else self.heart_unlit_img
        if heart_img:
            screen.blit(heart_img, self.heart_rect.topleft)
        else:
            pygame.draw.ellipse(screen, RED, self.heart_rect)

        # Message area
        pygame.draw.rect(screen, (30, 30, 40), self.message_rect, border_radius=10)
        pygame.draw.rect(screen, GRAY, self.message_rect, 2, border_radius=10)

        msg_surf = self.text_font.render(self.message, True, self.message_color)
        msg_rect = msg_surf.get_rect(center=self.message_rect.center)
        screen.blit(msg_surf, msg_rect)

        # Pig list
        pygame.draw.rect(screen, (30, 30, 40), self.pig_list_rect, border_radius=10)
        pygame.draw.rect(screen, GRAY, self.pig_list_rect, 2, border_radius=10)

        list_title = self.small_font.render("Your Pigs", True, GOLD)
        lt_rect = list_title.get_rect(midleft=(self.pig_list_rect.x + 10, self.pig_list_rect.y + 15))
        screen.blit(list_title, lt_rect)

        start_y = self.pig_list_rect.y + 40
        line_height = 40

        for i, pig in enumerate(player_inventory.owned_pigs):
            y = start_y + i * line_height
            if y + line_height > self.pig_list_rect.bottom:
                break

            rect = pygame.Rect(self.pig_list_rect.x + 10, y, self.pig_list_rect.width - 20, line_height - 4)
            pygame.draw.rect(screen, (50, 50, 70), rect, border_radius=6)

            # NEW: age and breedability based on game time
            stage = pig.get_age_stage(current_game_time)
            can_breed, reason = pig.can_breed(current_game_time)
            color = GREEN if can_breed and stage == "Adult" else GRAY

            label = f"{pig.name} ({stage})"
            txt = self.small_font.render(label, True, color)
            screen.blit(txt, (rect.x + 8, rect.y + 8))

        # Cooldown icon + text (if a parent is on cooldown)
        if self.parent1:
            can1, msg1 = self.parent1.can_breed(current_game_time)
        else:
            can1, msg1 = True, ""

        if self.parent2:
            can2, msg2 = self.parent2.can_breed(current_game_time)
        else:
            can2, msg2 = True, ""

        cd_msgs = []
        if not can1:
            cd_msgs.append(f"{self.parent1.name}: {msg1}")
        if not can2:
            cd_msgs.append(f"{self.parent2.name}: {msg2}")

        if cd_msgs and self.cooldown_img:
            screen.blit(self.cooldown_img, (self.message_rect.x + 10, self.message_rect.y - 50))
            cd_text = self.small_font.render(" / ".join(cd_msgs), True, WHITE)
            cd_rect = cd_text.get_rect(
                midleft=(self.message_rect.x + 60, self.message_rect.y - 30)
            )
            screen.blit(cd_text, cd_rect)

        # Breeding animation progress bar
        if self.is_breeding_anim:
            bar_w = 300
            bar_h = 20
            bar_x = (screen.get_width() - bar_w) // 2
            bar_y = self.heart_rect.bottom + 20
            pygame.draw.rect(screen, (50, 50, 70), (bar_x, bar_y, bar_w, bar_h), border_radius=10)
            fill_w = int(bar_w * (self.breeding_progress / 100))
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_w, bar_h), border_radius=10)

        if self.naming_mode:
            self._draw_naming_overlay(screen)


breeding_manager = BreedingPage()


def breeding_update(events, player_inventory, current_game_time):
    return breeding_manager.handle_input(events, player_inventory, current_game_time)


def breeding_draw(screen, player_inventory, current_game_time):
    breeding_manager.draw(screen, player_inventory, current_game_time)
