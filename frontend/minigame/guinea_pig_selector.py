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
        # Check multiple locations
        paths_to_check = [
            os.path.join(base_path, "../../images/BG_Title.png"),
            os.path.join(base_path, "../images/BG_Title.png"),
            os.path.join(base_path, "../../Global Assets/Sprites/More Sprites/BG Art/Title/BG_Title.png")
        ]
        
        for p in paths_to_check:
            if os.path.exists(p):
                try:
                    img = pygame.image.load(p).convert()
                    return pygame.transform.scale(img, (self.screen_width, self.screen_height))
                except:
                    pass
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
                except:
                    pass
        
        # Fallback surface if image fails
        s = pygame.Surface((60, 60))
        s.fill((150, 75, 0))
        return s

    def _load_pets(self):
        self.pets = []

        # 1. Check Local Inventory
        if self.inventory_pigs and len(self.inventory_pigs) > 0:
            for pig_obj in self.inventory_pigs:
                # Basic Info
                pet_dict = {
                    'id': getattr(pig_obj, 'id', random.randint(1000,9999)),
                    'name': getattr(pig_obj, 'name', 'Unknown'),
                    'species': 'guinea_pig',
                    'color': 'brown', 
                    'speed': 50,      
                    'health': 100,
                    'happiness': 100,
                    'sprite': None
                }

                # Get Sprite: Check if object already has one, else use default
                if hasattr(pig_obj, 'image') and pig_obj.image:
                    # Scale existing image to button size
                    pet_dict['sprite'] = pygame.transform.scale(pig_obj.image, (60, 60))
                else:
                    pet_dict['sprite'] = self.default_sprite

                # Extract Stats
                if hasattr(pig_obj, 'phenotype') and isinstance(pig_obj.phenotype, dict):
                    pet_dict['color'] = pig_obj.phenotype.get('coat_color', 'brown')
                
                if hasattr(pig_obj, 'score'):
                    # Simple logic: Score 100->40 speed, 500->80 speed
                    pet_dict['speed'] = int(40 + (pig_obj.score / 500) * 40)
                elif hasattr(pig_obj, 'speed'):
                    pet_dict['speed'] = pig_obj.speed

                self.pets.append(pet_dict)

        # 2. Fallback Mock Data
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
        # 1. Draw Background
        if self.background_img:
            screen.blit(self.background_img, (0, 0))
        else:
            screen.fill((40, 40, 60))

        # 2. Draw Semi-Transparent Overlay for Readability
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # 3. Draw Title with Shadow
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
                # Highlight selected
                if pet == self.selected_pet:
                    highlight_rect = button.rect.inflate(6, 6)
                    pygame.draw.rect(screen, GOLD, highlight_rect, 3, border_radius=15)

                button.draw(screen)

                # --- DRAW CONTENT ON BUTTON ---
                
                # 1. Draw Sprite (Left Side)
                if pet['sprite']:
                    sprite_rect = pet['sprite'].get_rect(
                        midleft=(button.rect.left + 15, button.rect.centery)
                    )
                    screen.blit(pet['sprite'], sprite_rect)

                # 2. Name (Top Right - Shifted to avoid sprite)
                name_str = pet['name'][:20] + "..." if len(pet['name']) > 20 else pet['name']
                name_surf = self.pet_font.render(name_str, True, WHITE)
                # Position text starting after the sprite (approx 90px in)
                screen.blit(name_surf, (button.rect.left + 90, button.rect.top + 15))

                # 3. Stats (Bottom Right)
                color_val = str(pet.get('color', 'unknown')).title()
                color_text = self.info_font.render(f"Color: {color_val}", True, (200, 200, 200))
                speed_text = self.info_font.render(f"Speed: {pet.get('speed', 50)}", True, (200, 200, 200))

                screen.blit(color_text, (button.rect.left + 90, button.rect.bottom - 30))
                screen.blit(speed_text, (button.rect.right - speed_text.get_width() - 20, button.rect.bottom - 30))

        # Selected Panel (Bottom)
        if self.selected_pet:
            panel_y = self.screen_height - 200
            panel_rect = pygame.Rect(50, panel_y, self.screen_width - 100, 80)
            
            pygame.draw.rect(screen, (30, 30, 50), panel_rect, border_radius=10)
            pygame.draw.rect(screen, GOLD, panel_rect, 3, border_radius=10)

            # Draw selected info
            selected_text = self.pet_font.render("Selected:", True, GOLD)
            name_text = self.pet_font.render(self.selected_pet['name'], True, WHITE)

            screen.blit(selected_text, (panel_rect.x + 20, panel_y + 15))
            screen.blit(name_text, (panel_rect.x + 20, panel_y + 45))
            
            # Draw sprite in panel too
            if self.selected_pet['sprite']:
                s_rect = self.selected_pet['sprite'].get_rect(midright=(panel_rect.right - 30, panel_rect.centery))
                screen.blit(self.selected_pet['sprite'], s_rect)

        self.button_start.draw(screen)
        self.button_back.draw(screen)