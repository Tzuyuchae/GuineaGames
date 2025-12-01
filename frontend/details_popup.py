import pygame
# Assumes frontend_button.py is in the same directory (frontend/)
from frontend_button import Button 

# Settings
POPUP_BG = (245, 245, 245)
BORDER_COLOR = (0, 0, 0)
TEXT_COLOR = (0, 0, 0)

class DetailsPopup:
    def __init__(self):
        try:
            self.font = pygame.font.SysFont('Arial', 24)
            self.title_font = pygame.font.SysFont('Arial', 30, bold=True)
        except:
            self.font = pygame.font.Font(None, 24)
            self.title_font = pygame.font.Font(None, 32)
            
        # Position the popup in the center of a 672x864 screen
        self.rect = pygame.Rect(86, 232, 500, 400) 
        
        # Back button inside the popup
        # x, y, width, height
        self.button_back = Button(pygame.Rect(236, 550, 200, 50), "BACK")

    def draw(self, screen, pig_data):
        # 1. Draw Popup Box
        pygame.draw.rect(screen, POPUP_BG, self.rect, border_radius=12)
        pygame.draw.rect(screen, BORDER_COLOR, self.rect, 3, border_radius=12)

        # 2. Draw Title (Name)
        name_text = self.title_font.render(pig_data.get("Name", "Unknown"), True, TEXT_COLOR)
        # Center text horizontally in popup
        text_x = self.rect.centerx - (name_text.get_width() // 2)
        screen.blit(name_text, (text_x, self.rect.y + 20))

        # 3. Draw Image (if available in the object passed)
        # We look for a 'visual_surface' key, or pass the image directly
        if "image_surface" in pig_data and pig_data["image_surface"]:
            img = pig_data["image_surface"]
            # Scale up for detail view
            img = pygame.transform.scale(img, (120, 120))
            img_rect = img.get_rect(center=(self.rect.centerx, self.rect.y + 100))
            screen.blit(img, img_rect)

        # 4. Draw Stats
        # We start drawing stats below the image
        start_y = self.rect.y + 180
        stats_to_show = ["Age", "Hunger", "Speed", "Endurance"]
        
        for i, key in enumerate(stats_to_show):
            val = pig_data.get(key, "N/A")
            stat_str = f"{key}: {val}"
            text_surf = self.font.render(stat_str, True, TEXT_COLOR)
            screen.blit(text_surf, (self.rect.x + 40, start_y + (i * 35)))

        # 5. Draw Back Button
        self.button_back.draw(screen)

    def handle_event(self, event):
        if self.button_back.is_clicked(event):
            return "close"
        return None