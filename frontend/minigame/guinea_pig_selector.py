import pygame
import os
import sys

# Ensure the module can find api_client when running from /frontend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ----------------------------------------------------------
#  IMPORTS
# ----------------------------------------------------------
# Use the existing minigame Button implementation
from .button import Button

# API client import (works in both execution modes)
try:
    from api_client import APIClient         # running: python frontend/main.py
except ImportError:
    from frontend.api_client import APIClient


class GuineaPigSelector:
    """
    Screen that lets the player choose one of their guinea pigs.

    Integration points:
      - Loads pets from backend via APIClient.get_user_pets(user_id)
      - Returns:
          ('start_game', selected_pet_dict)  when Start is clicked
          'back'                             when Back is clicked
          None                               otherwise
    """

    def __init__(self, screen_width: int, screen_height: int, user_id: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.user_id = user_id

        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)

        # Layout for the scrollable list
        self.margin_top = 100
        self.margin_left = 80
        self.item_height = 70
        self.item_width = screen_width - 2 * self.margin_left
        self.scroll_offset = 0
        self.scroll_speed = 25

        # Buttons at bottom
        self.start_button = Button(
            60,
            screen_height - 80,
            200,
            60,
            "Start",
        )
        self.back_button = Button(
            screen_width - 260,
            screen_height - 80,
            200,
            60,
            "Back",
        )

        self.api = APIClient()

        # Data
        self.pets = []           # list of dicts from backend
        self.pet_rects = []      # list of pygame.Rect for clickable rows
        self.selected_index = None

        self._load_pets()

    # ------------------------------------------------------
    def _load_pets(self):
        """Load pets from backend or fallback to mock data."""
        try:
            pets = self.api.get_user_pets(self.user_id)
            if not pets:
                print("No backend pets found; using mock pets.")
                pets = self._mock_pets()
        except Exception as e:
            print(f"Error loading pets from API: {e}")
            pets = self._mock_pets()

        self.pets = pets
        self._build_pet_rects()

    # ------------------------------------------------------
    def _mock_pets(self):
        return [
            {"name": "Fluffy", "type": "guinea_pig"},
            {"name": "Squeaky", "type": "guinea_pig"},
            {"name": "Nibbles", "type": "guinea_pig"},
        ]

    # ------------------------------------------------------
    def _build_pet_rects(self):
        """Create a list of rectangles representing each pet row."""
        self.pet_rects = []
        y = self.margin_top
        for _ in self.pets:
            rect = pygame.Rect(self.margin_left, y, self.item_width, self.item_height)
            self.pet_rects.append(rect)
            y += self.item_height + 10

    # ------------------------------------------------------
    def update(self, events):
        """
        Handles input and scroll.

        Returns:
          - ('start_game', pet_dict) when Start is clicked with a selection
          - 'back' when Back is clicked
          - None otherwise
        """

        # Scroll using arrow keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.scroll_offset = min(self.scroll_offset + self.scroll_speed, 0)
        if keys[pygame.K_DOWN]:
            self.scroll_offset -= self.scroll_speed

        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # Check clicks on pet rows
                for i, rect in enumerate(self.pet_rects):
                    shifted_rect = rect.move(0, self.scroll_offset)
                    if shifted_rect.collidepoint(mx, my):
                        self.selected_index = i

            # Use the real Button API: check_click(event)
            if self.start_button.check_click(event):
                if self.selected_index is not None:
                    return ("start_game", self.pets[self.selected_index])

            if self.back_button.check_click(event):
                return "back"

        # Hover effects for buttons (optional)
        self.start_button.check_hover(mouse_pos)
        self.back_button.check_hover(mouse_pos)

        return None

    # ------------------------------------------------------
    def draw(self, screen):
        """Render the selector screen."""
        screen.fill((40, 40, 60))

        # Title
        title_surf = self.title_font.render("Choose Your Guinea Pig", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, 50))
        screen.blit(title_surf, title_rect)

        # Draw pet rows
        for i, rect in enumerate(self.pet_rects):
            shifted_rect = rect.move(0, self.scroll_offset)

            # Background color depending on selection
            if i == self.selected_index:
                color = (255, 215, 0)  # selected
            else:
                color = (200, 200, 200)

            pygame.draw.rect(screen, color, shifted_rect, border_radius=10)

            # Pet name text
            pet = self.pets[i]
            name_text = pet.get("name", "Unnamed")
            text_surf = self.font.render(name_text, True, (0, 0, 0))
            text_rect = text_surf.get_rect(midleft=(shifted_rect.x + 15, shifted_rect.centery))
            screen.blit(text_surf, text_rect)

        # Draw buttons
        self.start_button.draw(screen)
        self.back_button.draw(screen)
