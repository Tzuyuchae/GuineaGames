"""
Guinea Pig Selector Screen
Allows users to select a guinea pig before starting the minigame.
"""
import pygame
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from button import Button
from minigame.settings import *

# Try to import the API client, but handle case where backend is not available
try:
    from frontend.api_client import APIClient
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    print("Warning: API client not available. Using mock data.")


class GuineaPigSelector:
    """Screen for selecting a guinea pig to use in the minigame."""

    def __init__(self, screen_width=672, screen_height=864, user_id=1):
        """
        Initialize the guinea pig selector.
        
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
            user_id: ID of the user whose pets to fetch
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.user_id = user_id

        # UI state
        self.selected_pet = None
        self.pets = []
        self.scroll_offset = 0
        self.max_visible_pets = 5

        # Initialize font
        pygame.font.init()
        try:
            self.title_font = pygame.font.SysFont('Arial', 40, bold=True)
            self.pet_font = pygame.font.SysFont('Arial', 24)
            self.info_font = pygame.font.SysFont('Arial', 18)
        except:
            self.title_font = pygame.font.Font(None, 50)
            self.pet_font = pygame.font.Font(None, 30)
            self.info_font = pygame.font.Font(None, 22)

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

        # Pet selection buttons (will be created dynamically)
        self.pet_buttons = []

        # Load pets
        self._load_pets()

    def _load_pets(self):
        """Load pets from the backend API or use mock data."""
        if API_AVAILABLE:
            try:
                api = APIClient()
                self.pets = api.get_user_pets(self.user_id)
                if not self.pets:
                    print(f"No pets found for user {self.user_id}. Using mock data.")
                    self.pets = self._get_mock_pets()
            except Exception as e:
                print(f"Error loading pets from API: {e}. Using mock data.")
                self.pets = self._get_mock_pets()
        else:
            self.pets = self._get_mock_pets()

        # Create buttons for each pet
        self._create_pet_buttons()

        # Auto-select first pet if available
        if self.pets:
            self.selected_pet = self.pets[0]

    def _get_mock_pets(self):
        """Return mock pet data for testing."""
        return [
            {
                'id': 1,
                'name': 'Fluffy',
                'species': 'guinea_pig',
                'color': 'brown',
                'speed': 55,
                'health': 90,
                'happiness': 85
            },
            {
                'id': 2,
                'name': 'Squeaky',
                'species': 'guinea_pig',
                'color': 'white',
                'speed': 70,
                'health': 80,
                'happiness': 95
            },
            {
                'id': 3,
                'name': 'Nibbles',
                'species': 'guinea_pig',
                'color': 'orange',
                'speed': 45,
                'health': 100,
                'happiness': 75
            }
        ]

    def _create_pet_buttons(self):
        """Create selection buttons for each pet."""
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
                pet['name'],
                (50, 50, 150),
                (80, 80, 200)
            )
            self.pet_buttons.append(button)

    def update(self, events):
        """
        Handle events and update selector state.
        
        Args:
            events: List of pygame events
            
        Returns:
            'start_game' with selected pet data if start clicked
            'back' if back button clicked
            None to stay on selector
        """
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            # Check back button
            if self.button_back.check_click(event):
                return 'back'

            # Check start button
            if self.button_start.check_click(event):
                if self.selected_pet:
                    return ('start_game', self.selected_pet)

            # Check pet selection buttons
            for i, button in enumerate(self.pet_buttons):
                if button.check_click(event):
                    self.selected_pet = self.pets[i]

            # Handle scroll wheel for many pets
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_offset -= event.y
                self.scroll_offset = max(0, min(self.scroll_offset, 
                                                len(self.pets) - self.max_visible_pets))

        # Update hover states
        self.button_start.check_hover(mouse_pos)
        self.button_back.check_hover(mouse_pos)
        for button in self.pet_buttons:
            button.check_hover(mouse_pos)

        return None

    def draw(self, screen):
        """
        Draw the selector screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Background
        screen.fill((40, 40, 60))

        # Title
        title_text = self.title_font.render("Select Your Guinea Pig", True, WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 50))
        screen.blit(title_text, title_rect)

        # Draw pet list
        if not self.pets:
            no_pets_text = self.pet_font.render("No guinea pigs available!", True, (255, 100, 100))
            no_pets_rect = no_pets_text.get_rect(center=(self.screen_width // 2, 300))
            screen.blit(no_pets_text, no_pets_rect)
        else:
            # Draw each pet button with info
            for i, (pet, button) in enumerate(zip(self.pets, self.pet_buttons)):
                # Highlight selected pet
                if pet == self.selected_pet:
                    # Draw selection highlight
                    highlight_rect = pygame.Rect(
                        button.rect.x - 5, button.rect.y - 5,
                        button.rect.width + 10, button.rect.height + 10
                    )
                    pygame.draw.rect(screen, GOLD, highlight_rect, 3, border_radius=15)

                # Draw button
                button.draw(screen)

                # Draw pet stats on the button
                stats_y = button.rect.y + 35
                color_text = self.info_font.render(
                    f"Color: {pet.get('color', 'unknown').title()}", 
                    True, WHITE
                )
                speed_text = self.info_font.render(
                    f"Speed: {pet.get('speed', 50)}", 
                    True, WHITE
                )

                screen.blit(color_text, (button.rect.x + 10, stats_y))
                screen.blit(speed_text, (button.rect.x + 250, stats_y))

        # Draw selected pet info panel
        if self.selected_pet:
            panel_y = self.screen_height - 200
            panel_height = 80
            panel_rect = pygame.Rect(50, panel_y, self.screen_width - 100, panel_height)
            pygame.draw.rect(screen, (30, 30, 50), panel_rect, border_radius=10)
            pygame.draw.rect(screen, GOLD, panel_rect, 3, border_radius=10)

            selected_text = self.pet_font.render("Selected:", True, GOLD)
            name_text = self.pet_font.render(self.selected_pet['name'], True, WHITE)

            screen.blit(selected_text, (panel_rect.x + 20, panel_y + 15))
            screen.blit(name_text, (panel_rect.x + 20, panel_y + 45))

        # Draw buttons
        self.button_start.draw(screen)
        self.button_back.draw(screen)

        # Draw instruction text
        if not self.selected_pet:
            instruction_text = self.info_font.render(
                "Click on a guinea pig to select it!", 
                True, (255, 200, 100)
            )
            instruction_rect = instruction_text.get_rect(
                center=(self.screen_width // 2, self.screen_height - 140)
            )
            screen.blit(instruction_text, instruction_rect)