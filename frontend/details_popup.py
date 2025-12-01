import pygame
from frontend_button import Button 

# Settings
POPUP_BG = (245, 245, 245)
BORDER_COLOR = (0, 0, 0)
TEXT_COLOR = (0, 0, 0)
INPUT_BG = (255, 255, 255)
INPUT_BORDER = (70, 130, 180) # Blue

class DetailsPopup:
    def __init__(self):
        try:
            self.font = pygame.font.SysFont('Arial', 24)
            self.title_font = pygame.font.SysFont('Arial', 30, bold=True)
        except:
            self.font = pygame.font.Font(None, 24)
            self.title_font = pygame.font.Font(None, 32)
            
        # Center popup
        self.rect = pygame.Rect(86, 232, 500, 400) 
        
        # Buttons
        self.button_back = Button(pygame.Rect(236, 550, 200, 50), "BACK")
        
        # Rename button (Small button next to name)
        self.rename_rect = pygame.Rect(0, 0, 80, 30) # Positioned dynamically
        
        # State
        self.is_renaming = False
        self.current_input = ""
        self.active_pig_data = None # Logic reference to modify name

    def draw(self, screen, pig_data):
        # Store reference to allow renaming
        self.active_pig_data = pig_data

        # 1. Draw Popup Box
        pygame.draw.rect(screen, POPUP_BG, self.rect, border_radius=12)
        pygame.draw.rect(screen, BORDER_COLOR, self.rect, 3, border_radius=12)

        # 2. Handle Name / Renaming
        name = pig_data.get("Name", "Unknown")
        
        if self.is_renaming:
            # Draw Input Box
            input_rect = pygame.Rect(self.rect.centerx - 100, self.rect.y + 20, 200, 40)
            pygame.draw.rect(screen, INPUT_BG, input_rect)
            pygame.draw.rect(screen, INPUT_BORDER, input_rect, 2)
            
            # Draw typing text
            txt_surf = self.title_font.render(self.current_input, True, TEXT_COLOR)
            screen.blit(txt_surf, (input_rect.x + 5, input_rect.y + 5))
            
            # Instruction
            hint = self.font.render("Press ENTER to save", True, (100, 100, 100))
            screen.blit(hint, (input_rect.centerx - hint.get_width()//2, input_rect.bottom + 5))
            
        else:
            # Draw Title (Name)
            name_text = self.title_font.render(name, True, TEXT_COLOR)
            text_x = self.rect.centerx - (name_text.get_width() // 2)
            screen.blit(name_text, (text_x, self.rect.y + 20))
            
            # Draw Rename Button ('Pencil' icon or text)
            self.rename_rect.topleft = (text_x + name_text.get_width() + 15, self.rect.y + 25)
            # Simple "Edit" text button
            pygame.draw.rect(screen, (200, 200, 200), self.rename_rect, border_radius=5)
            edit_txt = self.font.render("Edit", True, (50, 50, 50))
            screen.blit(edit_txt, (self.rename_rect.x + 20, self.rename_rect.y))

        # 3. Draw Image
        if "image_surface" in pig_data and pig_data["image_surface"]:
            img = pig_data["image_surface"]
            img = pygame.transform.scale(img, (120, 120))
            img_rect = img.get_rect(center=(self.rect.centerx, self.rect.y + 120))
            screen.blit(img, img_rect)

        # 4. Draw Stats
        start_y = self.rect.y + 200
        stats_to_show = ["Age", "Hunger", "Speed", "Endurance"]
        
        for i, key in enumerate(stats_to_show):
            val = pig_data.get(key, "N/A")
            stat_str = f"{key}: {val}"
            text_surf = self.font.render(stat_str, True, TEXT_COLOR)
            screen.blit(text_surf, (self.rect.x + 40, start_y + (i * 35)))

        # 5. Draw Back Button
        self.button_back.draw(screen)

    def handle_event(self, event):
        # 1. Handle Back Button (if not renaming)
        if not self.is_renaming and self.button_back.is_clicked(event):
            return "close"
        
        # 2. Handle Rename Click
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.is_renaming and self.rename_rect.collidepoint(event.pos):
                self.is_renaming = True
                # Pre-fill with current name
                self.current_input = self.active_pig_data.get("Name", "")
                return None

        # 3. Handle Typing
        if self.is_renaming and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Save Name
                new_name = self.current_input.strip()
                if new_name and self.active_pig_data:
                    # Update the actual pig object referenced in the dict
                    # (This requires the pig object to be passed in the dict)
                    if "object" in self.active_pig_data:
                         self.active_pig_data["object"].name = new_name
                         self.active_pig_data["Name"] = new_name # Update display immediately
                
                self.is_renaming = False
                
            elif event.key == pygame.K_BACKSPACE:
                self.current_input = self.current_input[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.is_renaming = False
            else:
                # Limit length
                if len(self.current_input) < 12:
                    self.current_input += event.unicode

        return None