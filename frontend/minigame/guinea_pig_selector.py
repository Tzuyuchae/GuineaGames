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
        paths_to_check = [
            os.path.join(base_path, "../../Global Assets/Sprites/More Sprites/BG Art/Title/BG_Title.png"),
            os.path.join(base_path, "../../images/BG_Title.png"),
            os.path.join(base_path, "../images/BG_Title.png")
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
        base_path = os.path.dirname(os.path.abspath(__file__))
        paths_to_check = [
            os.path.join(base_path, "../../images/guineapig.png"),
            os.path.join(base_path, "../images/guineapig.png"),
            os.path.join(base_path, "../../Global Assets/guineapig.png")
        ]
        
        for p in paths_to_check:
            if os.path.exists(p):
                try:
                    img = pygame.image.load(p).convert_alpha()
                    return pygame.transform.scale(img, (60, 60))
                except: pass
        
        s = pygame.Surface((60, 60))
        s.fill((150, 75, 0))
        return s

    def _get_pet_sprite(self, pig_data):
        """Finds and loads the specific sprite based on color."""
        # 1. Determine Color
        color = "white"
        if isinstance(pig_data, dict):
            # API Dictionary
            color = pig_data.get('color_phenotype', pig_data.get('color', 'White')).lower()
        else:
            # Legacy Object
            if hasattr(pig_data, 'phenotype') and isinstance(pig_data.phenotype, dict):
                color = pig_data.phenotype.get('coat_color', 'white').lower()
            elif hasattr(pig_data, 'color'):
                color = str(pig_data.color).lower()

        # 2. Pick Filename
        filename = "SH_GP_White_01.png" # Default
        if "brown" in color: filename = "SH_GP_Brown_01.png"
        elif "orange" in color: filename = "SH_GP_Orange_01.png"
        
        # 3. Build Path
        # Base = frontend/minigame -> go up to frontend -> Global Assets
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_dir, "Global Assets", "Sprites", "Guinea Pigs", "SH_GP_Sprites", "SH_GP_Sprites", filename)
        
        # 4. Load
        try:
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (60, 60))
        except: pass
        
        return self.default_sprite

    def _load_pets(self):
        self.pets = []

        if self.inventory_pigs and len(self.inventory_pigs) > 0:
            for pig in self.inventory_pigs:
                # Handle Dictionary (API Data)
                if isinstance(pig, dict):
                    pet_dict = {
                        'id': pig.get('id', random.randint(1000,9999)),
                        'name': pig.get('name', 'Unknown'),
                        'species': pig.get('species', 'guinea_pig'),
                        'color': pig.get('color_phenotype', pig.get('color', 'brown')),
                        'speed': pig.get('speed', 50),
                        'health': pig.get('health', 100),
                        # Load smart sprite here!
                        'sprite': self._get_pet_sprite(pig)
                    }
                # Handle Object (Legacy Data)
                else:
                    pet_dict = {
                        'id': getattr(pig, 'id', random.randint(1000,9999)),
                        'name': getattr(pig, 'name', 'Unknown'),
                        'species': 'guinea_pig',
                        'color': 'brown',
                        'speed': getattr(pig, 'speed', 50),
                        'health': 100,
                        # Load smart sprite here!
                        'sprite': self._get_pet_sprite(pig)
                    }

                self.pets.append(pet_dict)

        # Fallback Mock Data
        else:
            self.pets = self._get_mock_pets()

        self._create_pet_buttons()

        if self.pets:
            self.selected_pet = self.pets[0]

    def _get_mock_pets(self):
        return [
            {'id': 1, 'name': 'Fluffy (Mock)', 'color': 'brown', 'speed': 55, 'sprite': self.default_sprite},
            {'id': 2, 'name': 'Squeaky (Mock)', 'color': 'white', 'speed': 70, 'sprite': self.default_sprite},
            {'id': 3, 'name': 'Nibbles (Mock)', 'color': 'orange', 'speed': 45, 'sprite': self.default_sprite}
        ]

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
                self.scroll_offset = max(0, min(self.scroll_offset, len(self.pets) - self.max_visible_pets))

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

        title_text = self.title_font.render("Select Your Guinea Pig", True, WHITE)
        shadow_text = self.title_font.render("Select Your Guinea Pig", True, BLACK)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 50))
        
        screen.blit(shadow_text, (title_rect.x + 2, title_rect.y + 2))
        screen.blit(title_text, title_rect)

        if not self.pets:
            no_pets_text = self.pet_font.render("No guinea pigs available!", True, (255, 100, 100))
            screen.blit(no_pets_text, no_pets_text.get_rect(center=(self.screen_width // 2, 300)))
        else:
            for i, (pet, button) in enumerate(zip(self.pets, self.pet_buttons)):
                if pet == self.selected_pet:
                    highlight_rect = button.rect.inflate(6, 6)
                    pygame.draw.rect(screen, GOLD, highlight_rect, 3, border_radius=15)

                button.draw(screen)

                # 1. Draw Sprite
                if pet['sprite']:
                    sprite_rect = pet['sprite'].get_rect(
                        midleft=(button.rect.left + 15, button.rect.centery)
                    )
                    screen.blit(pet['sprite'], sprite_rect)

                # 2. Name
                name_str = str(pet['name'])
                if len(name_str) > 20: name_str = name_str[:20] + "..."
                name_surf = self.pet_font.render(name_str, True, WHITE)
                screen.blit(name_surf, (button.rect.left + 90, button.rect.top + 15))

                # 3. Stats
                color_val = str(pet.get('color', 'unknown')).title()
                color_text = self.info_font.render(f"Color: {color_val}", True, (200, 200, 200))
                speed_text = self.info_font.render(f"Speed: {pet.get('speed', 50)}", True, (200, 200, 200))

                screen.blit(color_text, (button.rect.left + 90, button.rect.bottom - 30))
                screen.blit(speed_text, (button.rect.right - speed_text.get_width() - 20, button.rect.bottom - 30))

        # Selected Panel
        if self.selected_pet:
            panel_y = self.screen_height - 200
            panel_rect = pygame.Rect(50, panel_y, self.screen_width - 100, 80)
            
            pygame.draw.rect(screen, (30, 30, 50), panel_rect, border_radius=10)
            pygame.draw.rect(screen, GOLD, panel_rect, 3, border_radius=10)

            selected_text = self.pet_font.render("Selected:", True, GOLD)
            name_text = self.pet_font.render(str(self.selected_pet['name']), True, WHITE)

            screen.blit(selected_text, (panel_rect.x + 20, panel_y + 15))
            screen.blit(name_text, (panel_rect.x + 20, panel_y + 45))
            
            if self.selected_pet['sprite']:
                s_rect = self.selected_pet['sprite'].get_rect(midright=(panel_rect.right - 30, panel_rect.centery))
                screen.blit(self.selected_pet['sprite'], s_rect)

        self.button_start.draw(screen)
        self.button_back.draw(screen)