"""
Guinea Pig Selector Screen
Allows users to select a guinea pig before starting the minigame.
"""
import pygame
import sys
import os
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from minigame.button import Button
from minigame.settings import *

class GuineaPigSelector:
    """Screen for selecting a guinea pig to use in the minigame."""

    def __init__(self, screen_width=672, screen_height=864, user_id=1, inventory_pigs=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.user_id = user_id
        self.inventory_pigs = inventory_pigs 

        # UI state
        self.selected_pet = None
        self.pets = []
        self.scroll_offset = 0
        self.max_visible_pets = 5

        # Initialize font
        pygame.font.init()
        try:
            self.title_font = pygame.font.SysFont('Arial', 40, bold=True)
            self.pet_font = pygame.font.SysFont('Arial', 24, bold=True)
            self.info_font = pygame.font.SysFont('Arial', 18)
        except:
            self.title_font = pygame.font.Font(None, 50)
            self.pet_font = pygame.font.Font(None, 30)
            self.info_font = pygame.font.Font(None, 22)

        # Load Assets
        self.background_img = self._load_background()
        self.default_sprite = self._load_default_sprite()

        # Create buttons
        button_y = screen_height - 100
        self.button_start = Button(
            screen_width // 2 - 110, button_y, 200, 60, 
            'START', (0, 150, 0), (0, 200, 0)
        )
        self.button_back = Button(
            screen_width // 2 + 110, button_y, 200, 60,
            'BACK', (150, 0, 0), (200, 0, 0)
        )

        # Pet selection buttons
        self.pet_buttons = []

        # Load pets
        self._load_pets()

    def _load_background(self):
        """Loads and scales the title background."""
        base_path = os.path.dirname(os.path.abspath(__file__))
        # Try various relative paths to find the asset
        paths_to_check = [
            os.path.join(base_path, "../../Global Assets/Sprites/More Sprites/BG Art/Title/BG_Title.png"),
            os.path.join(base_path, "../images/BG_Title.png"),
        ]
        
        for p in paths_to_check:
            if os.path.exists(p):
                try:
                    img = pygame.image.load(p).convert()
                    return pygame.transform.scale(img, (self.screen_width, self.screen_height))
                except: pass
        return None

    def _load_default_sprite(self):
        """Loads the default guinea pig sprite for fallback."""
        s = pygame.Surface((60, 60))
        s.fill((150, 75, 0)) # Brown square
        return s

    def _determine_hair_type(self, pig_data):
        """
        Helper to figure out if a pig is Long or Short hair
        based on explicit data OR Breed.
        """
        # 1. Check explicit fields first
        raw_type = pig_data.get('hair_type', pig_data.get('coat_length', None))
        if raw_type:
            rt = str(raw_type).lower()
            if rt in ['long', 'fluffy', 'lh']: return 'Long'
            if rt in ['short', 'smooth', 'sh']: return 'Short'

        # 2. Infer from Species/Breed
        species = pig_data.get('species', 'Guinea Pig')
        # List of known long hair breeds
        long_hair_breeds = [
            "Abyssinian", "Peruvian", "Silkie", "Sheba", 
            "Coronet", "Alpaca", "Lunkarya", "Texel"
        ]
        
        if species in long_hair_breeds:
            return 'Long'
            
        return 'Short'

    def _get_pet_sprite(self, pig_data, hair_type_override=None):
        """Finds and loads the specific sprite based on color AND hair length."""
        
        # 1. Determine Color
        color = "white"
        pig_id = 0
        
        if isinstance(pig_data, dict):
            color = pig_data.get('color_phenotype', pig_data.get('color', 'White'))
            pig_id = pig_data.get('id', 0)
        else:
            pig_id = getattr(pig_data, 'id', 0)
            color = "white"

        if not color: color = "White"
        color = str(color).lower()
        
        # 2. Determine Hair Type (Prefix)
        if hair_type_override:
            h_type = hair_type_override
        else:
            h_type = self._determine_hair_type(pig_data)
            
        is_long = (h_type == 'Long')
        prefix = "LH" if is_long else "SH"

        # 3. Map color to filename keywords
        sprite_color = "White" # Default
        if "brown" in color: sprite_color = "Brown"
        elif "orange" in color: sprite_color = "Orange"
        elif "black" in color: sprite_color = "Brown" # Fallback
        elif "mixed" in color: sprite_color = "Orange" # Fallback
        
        # 4. Pick a variant (01-09) consistently based on ID
        try:
            numeric_id = int(pig_id)
            variant_num = (numeric_id % 9) + 1
        except:
            variant_num = 1
            
        variant_str = f"{variant_num:02d}"
        
        # 5. Build Filename
        filename = f"{prefix}_GP_{sprite_color}_{variant_str}.png"
        
        # 6. Build Path & Load
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
        
        # Construct path variations
        folder_name = f"{prefix}_GP_Sprites"
        possible_paths = [
            os.path.join(base_dir, "Global Assets", "Sprites", "Guinea Pigs", folder_name, folder_name, filename),
            os.path.join(base_dir, "Global Assets", "Sprites", "Guinea Pigs", folder_name, filename)
        ]
        
        for sprite_path in possible_paths:
            if os.path.exists(sprite_path):
                try:
                    img = pygame.image.load(sprite_path).convert_alpha()
                    return pygame.transform.scale(img, (60, 60))
                except Exception as e:
                    print(f"Error loading sprite {filename}: {e}")
                    break 

        # Fallback to variant 01
        fallback_name = f"{prefix}_GP_{sprite_color}_01.png"
        fallback_path = os.path.join(base_dir, "Global Assets", "Sprites", "Guinea Pigs", folder_name, folder_name, fallback_name)
        
        if os.path.exists(fallback_path):
            try:
                img = pygame.image.load(fallback_path).convert_alpha()
                return pygame.transform.scale(img, (60, 60))
            except: pass

        return self.default_sprite

    def _load_pets(self):
        self.pets = []

        if self.inventory_pigs and len(self.inventory_pigs) > 0:
            for pig in self.inventory_pigs:
                
                # --- VITAL: Determine hair type logic BEFORE creating dict ---
                hair_type_val = self._determine_hair_type(pig)
                
                pet_dict = {
                    'id': pig.get('id', random.randint(1000,9999)),
                    'name': pig.get('name', 'Unknown'),
                    'species': pig.get('species', 'Guinea Pig'),
                    'color': pig.get('color_phenotype', pig.get('color', 'Brown')),
                    
                    # Store the determined hair type so the UI text is correct
                    'hair_type': hair_type_val,
                    
                    'speed': pig.get('speed', 50),
                    'health': pig.get('health', 100),
                    
                    # Pass the hair type explicitly to the sprite loader
                    'sprite': self._get_pet_sprite(pig, hair_type_override=hair_type_val)
                }
                self.pets.append(pet_dict)
        else:
            print("No inventory pigs found. Loading Mocks.")
            self.pets = self._get_mock_pets()

        self._create_pet_buttons()

        if self.pets:
            self.selected_pet = self.pets[0]

    def _get_mock_pets(self):
        mock_pigs = [
            {'id': 1, 'name': 'Fluffy (Mock)', 'color': 'brown', 'speed': 55, 'hair_type': 'Long'},
            {'id': 2, 'name': 'Squeaky (Mock)', 'color': 'white', 'speed': 70, 'hair_type': 'Short'},
        ]
        for p in mock_pigs:
            # Mock objects need sprites too
            p['sprite'] = self._get_pet_sprite(p, hair_type_override=p['hair_type'])
        return mock_pigs

    def _create_pet_buttons(self):
        self.pet_buttons = []
        button_width = 500
        button_height = 80
        start_x = (self.screen_width - button_width) // 2
        start_y = 120
        spacing = 10

        for i, pet in enumerate(self.pets):
            y_pos = start_y + i * (button_height + spacing)
            button = Button(
                start_x + button_width // 2,
                y_pos + button_height // 2,
                button_width,
                button_height,
                "", 
                (50, 50, 150),
                (80, 80, 200)
            )
            button.rect.center = (start_x + button_width // 2, y_pos + button_height // 2)
            self.pet_buttons.append(button)

    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if self.button_back.check_click(event):
                return 'back'

            if self.button_start.check_click(event):
                if self.selected_pet:
                    return ('start_game', self.selected_pet)

            for i, button in enumerate(self.pet_buttons):
                if button.check_click(event):
                    self.selected_pet = self.pets[i]

            if event.type == pygame.MOUSEWHEEL:
                self.scroll_offset -= event.y
                self.scroll_offset = max(0, min(self.scroll_offset, max(0, len(self.pets) - self.max_visible_pets)))

        self.button_start.check_hover(mouse_pos)
        self.button_back.check_hover(mouse_pos)
        for button in self.pet_buttons:
            button.check_hover(mouse_pos)

        return None

    def draw(self, screen):
        if self.background_img:
            screen.blit(self.background_img, (0, 0))
        else:
            screen.fill((40, 40, 60))

        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        title_text = self.title_font.render("Select Your Guinea Pig", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 50))
        screen.blit(title_text, title_rect)

        if not self.pets:
            no_pets_text = self.pet_font.render("No guinea pigs found!", True, (255, 100, 100))
            screen.blit(no_pets_text, no_pets_text.get_rect(center=(self.screen_width // 2, 300)))
        else:
            start_index = int(self.scroll_offset)
            end_index = min(len(self.pets), start_index + self.max_visible_pets)
            
            for i in range(start_index, end_index):
                pet = self.pets[i]
                slot_index = i - start_index
                button = self.pet_buttons[i]
                
                base_y = 120 + slot_index * (80 + 10)
                button.rect.y = base_y
                button.y = base_y + 40 

                if pet == self.selected_pet:
                    highlight_rect = button.rect.inflate(6, 6)
                    pygame.draw.rect(screen, (255, 215, 0), highlight_rect, 3, border_radius=15)

                button.draw(screen)

                if pet['sprite']:
                    sprite_rect = pet['sprite'].get_rect(
                        midleft=(button.rect.left + 15, button.rect.centery)
                    )
                    screen.blit(pet['sprite'], sprite_rect)

                name_str = str(pet['name'])
                name_surf = self.pet_font.render(name_str, True, (255, 255, 255))
                screen.blit(name_surf, (button.rect.left + 90, button.rect.top + 15))

                # Display correct hair type info
                h_type = str(pet.get('hair_type', 'Short')).capitalize()
                stats_text = f"Spd: {pet.get('speed', 50)} | {h_type} Hair | {pet.get('color', '?')}"
                info_surf = self.info_font.render(stats_text, True, (200, 200, 200))
                screen.blit(info_surf, (button.rect.left + 90, button.rect.bottom - 30))

        self.button_start.draw(screen)
        self.button_back.draw(screen)