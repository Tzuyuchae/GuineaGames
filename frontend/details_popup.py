import pygame
from frontend_button import Button
from api_client import api 

# Settings
POPUP_BG = (245, 245, 245)
BORDER_COLOR = (0, 0, 0)
TEXT_COLOR = (0, 0, 0)
INPUT_BG = (255, 255, 255)
INPUT_BORDER = (70, 130, 180) 

class DetailsPopup:
    def __init__(self):
        try:
            self.font = pygame.font.SysFont('Arial', 24)
            self.title_font = pygame.font.SysFont('Arial', 30, bold=True)
        except:
            self.font = pygame.font.Font(None, 24)
            self.title_font = pygame.font.Font(None, 32)
            
        self.rect = pygame.Rect(86, 232, 500, 400) 
        
        self.button_back = Button(pygame.Rect(236, 550, 200, 50), "BACK")
        self.button_grow = Button(pygame.Rect(86, 550, 140, 50), "GROW (Dev)") # New Button
        self.rename_rect = pygame.Rect(0, 0, 80, 30)
        
        self.is_renaming = False
        self.current_input = ""
        self.active_pig_stats = None 

    def draw(self, screen, pig_stats):
        self.active_pig_stats = pig_stats

        # 1. Box
        pygame.draw.rect(screen, POPUP_BG, self.rect, border_radius=12)
        pygame.draw.rect(screen, BORDER_COLOR, self.rect, 3, border_radius=12)

        # 2. Name / Rename UI
        name = pig_stats.get("Name", "Unknown")
        
        if self.is_renaming:
            input_rect = pygame.Rect(self.rect.centerx - 100, self.rect.y + 20, 200, 40)
            pygame.draw.rect(screen, INPUT_BG, input_rect)
            pygame.draw.rect(screen, INPUT_BORDER, input_rect, 2)
            
            txt_surf = self.title_font.render(self.current_input, True, TEXT_COLOR)
            screen.blit(txt_surf, (input_rect.x + 5, input_rect.y + 5))
            
            hint = self.font.render("Press ENTER to save", True, (100, 100, 100))
            screen.blit(hint, (input_rect.centerx - hint.get_width()//2, input_rect.bottom + 5))
            
        else:
            name_text = self.title_font.render(name, True, TEXT_COLOR)
            text_x = self.rect.centerx - (name_text.get_width() // 2)
            screen.blit(name_text, (text_x, self.rect.y + 20))
            
            self.rename_rect.topleft = (text_x + name_text.get_width() + 15, self.rect.y + 25)
            pygame.draw.rect(screen, (200, 200, 200), self.rename_rect, border_radius=5)
            edit_txt = self.font.render("Edit", True, (50, 50, 50))
            screen.blit(edit_txt, (self.rename_rect.x + 20, self.rename_rect.y))

        # 3. Image
        if "image_surface" in pig_stats and pig_stats["image_surface"]:
            img = pig_stats["image_surface"]
            img = pygame.transform.scale(img, (120, 120))
            img_rect = img.get_rect(center=(self.rect.centerx, self.rect.y + 120))
            screen.blit(img, img_rect)

        # 4. Stats
        start_y = self.rect.y + 200
        stats_to_show = ["Age", "Hunger", "Speed", "Endurance"]
        
        for i, key in enumerate(stats_to_show):
            val = pig_stats.get(key, "N/A")
            stat_str = f"{key}: {val}"
            text_surf = self.font.render(stat_str, True, TEXT_COLOR)
            screen.blit(text_surf, (self.rect.x + 40, start_y + (i * 35)))

        # 5. Buttons
        self.button_back.draw(screen)
        self.button_grow.draw(screen)

    def handle_event(self, event):
        if not self.is_renaming:
            if self.button_back.is_clicked(event):
                return "close"
            
            # --- HANDLE GROW CLICK ---
            if self.button_grow.is_clicked(event):
                pet_id = self.active_pig_stats.get("pet_id")
                if pet_id:
                    print(f"Growing pet {pet_id}...")
                    try:
                        api.update_pet(pet_id, age_days=10) # Instant Adult
                        # Update local display
                        self.active_pig_stats["Age"] = "Adult"
                        if "raw_data" in self.active_pig_stats:
                            self.active_pig_stats["raw_data"]["age_days"] = 10
                    except Exception as e:
                        print(f"Grow failed: {e}")
                return None
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.is_renaming and self.rename_rect.collidepoint(event.pos):
                self.is_renaming = True
                self.current_input = self.active_pig_stats.get("Name", "")
                return None

        if self.is_renaming and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # SAVE RENAME
                new_name = self.current_input.strip()
                pet_id = self.active_pig_stats.get("pet_id")
                
                if new_name and pet_id:
                    print(f"Renaming pet {pet_id} to {new_name}...")
                    try:
                        api.update_pet(pet_id, name=new_name)
                        self.active_pig_stats["Name"] = new_name
                        if "raw_data" in self.active_pig_stats:
                            self.active_pig_stats["raw_data"]["name"] = new_name
                    except Exception as e:
                        print(f"Rename failed: {e}")
                
                self.is_renaming = False
                
            elif event.key == pygame.K_BACKSPACE:
                self.current_input = self.current_input[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.is_renaming = False
            else:
                if len(self.current_input) < 12:
                    self.current_input += event.unicode

        return None