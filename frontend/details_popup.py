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
            self.small_font = pygame.font.SysFont('Arial', 18) 
        except:
            self.font = pygame.font.Font(None, 24)
            self.title_font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 20)
            
        self.rect = pygame.Rect(86, 232, 500, 400) 
        
        # Button Layout
        self.button_back = Button(pygame.Rect(350, 550, 100, 50), "BACK")
        self.button_grow = Button(pygame.Rect(86, 550, 100, 50), "GROW")
        self.button_feed = Button(pygame.Rect(200, 550, 140, 50), "FEED")
        
        # Special Button for Death Screen
        self.button_rip = Button(pygame.Rect(186, 550, 300, 50), "SAY GOODBYE")

        self.rename_rect = pygame.Rect(0, 0, 80, 30)
        
        self.is_renaming = False
        self.current_input = ""
        self.active_pig_stats = None 
        
        # Inventory tracking
        self.available_food = None
        self.status_message = ""

    def fetch_food(self, owner_id):
        """Get food items from inventory"""
        try:
            inv = api.get_user_inventory(owner_id)
            self.available_food = [i for i in inv if i['quantity'] > 0]
        except Exception as e:
            print(f"Inventory fetch error: {e}")
            self.available_food = []

    def draw(self, screen, pig_stats):
        self.active_pig_stats = pig_stats

        # 1. Box
        pygame.draw.rect(screen, POPUP_BG, self.rect, border_radius=12)
        pygame.draw.rect(screen, BORDER_COLOR, self.rect, 3, border_radius=12)

        # --- DEATH SCREEN LOGIC ---
        if pig_stats.get("is_dead"):
            # Draw Title
            title = self.title_font.render("R.I.P.", True, (200, 0, 0))
            screen.blit(title, (self.rect.centerx - title.get_width()//2, self.rect.y + 20))
            
            # Draw Name
            name = pig_stats.get("Name", "Unknown")
            name_surf = self.font.render(f"Here lies {name}", True, TEXT_COLOR)
            screen.blit(name_surf, (self.rect.centerx - name_surf.get_width()//2, self.rect.y + 60))

            # Draw Sad Message
            msg = self.font.render("They have passed away.", True, (100, 100, 100))
            screen.blit(msg, (self.rect.centerx - msg.get_width()//2, self.rect.y + 100))

            # Draw Image (Greyscale logic or just normal)
            if "image_surface" in pig_stats and pig_stats["image_surface"]:
                img = pig_stats["image_surface"]
                img = pygame.transform.scale(img, (120, 120))
                # Optional: Make it look ghostly
                img.set_alpha(150) 
                img_rect = img.get_rect(center=(self.rect.centerx, self.rect.y + 200))
                screen.blit(img, img_rect)
            
            # Draw ONLY the Goodbye button
            self.button_rip.draw(screen)
            return
        # ---------------------------

        # Fetch inventory on first draw if alive
        if self.available_food is None and "raw_data" in pig_stats:
             self.fetch_food(pig_stats["raw_data"]["owner_id"])

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
        stats_to_show = ["Age", "Hunger", "Health", "Speed"]
        
        if "Health" not in pig_stats and "raw_data" in pig_stats:
            pig_stats["Health"] = f"{pig_stats['raw_data'].get('health', 0)}/100"

        for i, key in enumerate(stats_to_show):
            val = pig_stats.get(key, "N/A")
            stat_str = f"{key}: {val}"
            text_surf = self.font.render(stat_str, True, TEXT_COLOR)
            screen.blit(text_surf, (self.rect.x + 40, start_y + (i * 35)))

        # 5. Buttons
        self.button_back.draw(screen)
        self.button_grow.draw(screen)

        # Draw Feed Button logic
        if self.available_food:
            item_to_feed = self.available_food[0]
            self.button_feed.text = "FEED" 
            self.button_feed.draw(screen)
            lbl = self.small_font.render(f"Item: {item_to_feed['item_name']} ({item_to_feed['quantity']})", True, (50, 50, 50))
            screen.blit(lbl, (self.button_feed.rect.x, self.button_feed.rect.bottom + 5))
        else:
            lbl = self.small_font.render("No Food!", True, (200, 50, 50))
            screen.blit(lbl, (self.button_feed.rect.x + 20, self.button_feed.rect.y + 15))

        if self.status_message:
            msg = self.font.render(self.status_message, True, (0, 150, 0))
            screen.blit(msg, (self.rect.centerx - msg.get_width()//2, self.rect.bottom - 40))

    def handle_event(self, event):
        # Handle Death Screen Exit
        if self.active_pig_stats and self.active_pig_stats.get("is_dead"):
            if self.button_rip.is_clicked(event):
                return "close"
            return None

        if not self.is_renaming:
            if self.button_back.is_clicked(event):
                self.available_food = None 
                self.status_message = ""
                return "close"
            
            if self.button_grow.is_clicked(event):
                pet_id = self.active_pig_stats.get("pet_id")
                if pet_id:
                    try:
                        api.update_pet(pet_id, age_days=10) 
                        self.active_pig_stats["Age"] = "Adult"
                        if "raw_data" in self.active_pig_stats:
                            self.active_pig_stats["raw_data"]["age_days"] = 10
                    except Exception as e:
                        print(f"Grow failed: {e}")
                return None
            
            if self.button_feed.is_clicked(event) and self.available_food:
                item = self.available_food[0]
                pet_id = self.active_pig_stats.get("pet_id")
                try:
                    res = api.feed_pet(pet_id, item['item_name'])
                    if "raw_data" in self.active_pig_stats:
                        self.active_pig_stats["raw_data"]["hunger"] = res.get('hunger')
                        self.active_pig_stats["raw_data"]["health"] = res.get('health')
                    self.active_pig_stats["Hunger"] = f"{res.get('hunger')}/3"
                    self.active_pig_stats["Health"] = f"{res.get('health')}/100"
                    self.status_message = "Yum!"
                    item['quantity'] -= 1
                    if item['quantity'] <= 0:
                        self.available_food.pop(0)
                except Exception as e:
                    self.status_message = "Error!"
                return None
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.is_renaming and self.rename_rect.collidepoint(event.pos):
                self.is_renaming = True
                self.current_input = self.active_pig_stats.get("Name", "")
                return None

        if self.is_renaming and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                new_name = self.current_input.strip()
                pet_id = self.active_pig_stats.get("pet_id")
                if new_name and pet_id:
                    try:
                        api.update_pet(pet_id, name=new_name)
                        self.active_pig_stats["Name"] = new_name
                        if "raw_data" in self.active_pig_stats:
                            self.active_pig_stats["raw_data"]["name"] = new_name
                    except: pass
                self.is_renaming = False
            elif event.key == pygame.K_BACKSPACE:
                self.current_input = self.current_input[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.is_renaming = False
            else:
                if len(self.current_input) < 12:
                    self.current_input += event.unicode
        return None