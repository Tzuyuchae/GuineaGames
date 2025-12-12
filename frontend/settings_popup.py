import pygame

# Colors
OVERLAY_COLOR = (0, 0, 0, 180)
PANEL_COLOR = (50, 50, 60)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
GOLD = (255, 215, 0) 
BLACK = (0, 0, 0) # <--- ADD THIS LINE

class SettingsPopup:
    def __init__(self, screen_width, screen_height):
        self.screen_w = screen_width
        self.screen_h = screen_height
        self.active = False
        
        # Panel sizing (increased height for new button)
        self.panel_w = 400
        self.panel_h = 420 
        self.panel_x = (screen_width - self.panel_w) // 2
        self.panel_y = (screen_height - self.panel_h) // 2
        
        # State
        self.music_on = True
        self.sfx_on = True
        self.confirm_active = False # NEW: State for the confirmation screen
        
        # Fonts
        try:
            pygame.font.init()
            self.font = pygame.font.SysFont("Arial", 24, bold=True)
            self.font_small = pygame.font.SysFont("Arial", 20, bold=True)
        except:
            self.font = pygame.font.Font(None, 30)
            self.font_small = pygame.font.Font(None, 24)

        # UI Element Rects
        self.rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_w, self.panel_h)
        self.close_btn = pygame.Rect(self.panel_x + self.panel_w - 40, self.panel_y + 10, 30, 30)
        
        self.music_btn = pygame.Rect(self.panel_x + 50, self.panel_y + 80, 300, 40)
        self.sfx_btn = pygame.Rect(self.panel_x + 50, self.panel_y + 140, 300, 40)
        
        self.help_btn = pygame.Rect(self.panel_x + 50, self.panel_y + 200, 300, 40)
        
        # NEW: Restart Game Button
        self.restart_btn = pygame.Rect(self.panel_x + 50, self.panel_y + 260, 300, 40)
        
        self.quit_btn = pygame.Rect(self.panel_x + 50, self.panel_y + 340, 300, 40)

        # Confirmation Rects (Will be drawn dynamically on top of main panel)
        self.confirm_message = "ARE YOU SURE? All progress will be LOST."
        self.btn_confirm_yes = pygame.Rect(0, 0, 100, 40) # Placeholder, positions calculated in draw
        self.btn_confirm_no = pygame.Rect(0, 0, 100, 40)


    def toggle(self):
        self.active = not self.active
        self.confirm_active = False # Reset confirmation state on toggle

    def handle_event(self, event):
        if not self.active:
            return None
        
        mouse_pos = event.pos if event.type == pygame.MOUSEBUTTONDOWN else None

        # --- CONFIRMATION SCREEN LOGIC ---
        if self.confirm_active:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check confirmation buttons (Yes/No)
                if self.btn_confirm_yes.collidepoint(mouse_pos):
                    # Signal main.py to handle the restart
                    self.confirm_active = False
                    self.active = False
                    return 'confirm_restart'
                elif self.btn_confirm_no.collidepoint(mouse_pos):
                    self.confirm_active = False
                    return 'close' # Revert to normal settings view
            return None # Consume event, don't process main settings buttons

        # --- MAIN SETTINGS LOGIC ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.close_btn.collidepoint(mouse_pos):
                self.active = False
                return 'close'
            
            elif self.music_btn.collidepoint(mouse_pos):
                self.music_on = not self.music_on
                
            elif self.sfx_btn.collidepoint(mouse_pos):
                self.sfx_on = not self.sfx_on

            elif self.help_btn.collidepoint(mouse_pos):
                return 'help' # Handled by main.py
            
            # NEW: Restart Button Click
            elif self.restart_btn.collidepoint(mouse_pos):
                self.confirm_active = True
                return None # Stay in settings, but switch to confirmation view
                
            elif self.quit_btn.collidepoint(mouse_pos):
                return 'quit_game' # Handled by main.py
                
        return None

    def draw(self, screen):
        if not self.active:
            return

        # Overlay
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        screen.blit(overlay, (0, 0))

        # Panel
        pygame.draw.rect(screen, PANEL_COLOR, self.rect, border_radius=15)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=15)
        
        # Title
        title = self.font.render("SETTINGS", True, WHITE)
        screen.blit(title, (self.panel_x + 20, self.panel_y + 20))
        
        # Close X
        pygame.draw.rect(screen, RED, self.close_btn, border_radius=5)
        x_txt = self.font.render("X", True, WHITE)
        screen.blit(x_txt, (self.close_btn.x + 8, self.close_btn.y + 2))

        # Music Toggle
        color = GREEN if self.music_on else RED
        pygame.draw.rect(screen, color, self.music_btn, border_radius=8)
        txt = f"Music: {'ON' if self.music_on else 'OFF'}"
        surf = self.font.render(txt, True, WHITE)
        screen.blit(surf, (self.music_btn.x + 100, self.music_btn.y + 8))

        # SFX Toggle
        color = GREEN if self.sfx_on else RED
        pygame.draw.rect(screen, color, self.sfx_btn, border_radius=8)
        txt = f"SFX: {'ON' if self.sfx_on else 'OFF'}"
        surf = self.font.render(txt, True, WHITE)
        screen.blit(surf, (self.sfx_btn.x + 100, self.sfx_btn.y + 8))

        # Help Button
        pygame.draw.rect(screen, GOLD, self.help_btn, border_radius=8)
        h_txt = self.font.render("Help / How to Play", True, (50, 50, 50)) 
        screen.blit(h_txt, (self.help_btn.x + 60, self.help_btn.y + 8))
        
        # NEW: Restart Game Button
        pygame.draw.rect(screen, RED, self.restart_btn, border_radius=8)
        r_txt = self.font.render("RESTART GAME", True, WHITE)
        screen.blit(r_txt, (self.restart_btn.x + 80, self.restart_btn.y + 8))

        # Quit Button
        pygame.draw.rect(screen, GRAY, self.quit_btn, border_radius=8)
        q_txt = self.font.render("Quit to Desktop", True, WHITE)
        screen.blit(q_txt, (self.quit_btn.x + 70, self.quit_btn.y + 8))
        
        # --- NEW: DRAW CONFIRMATION SCREEN ---
        if self.confirm_active:
            # Draw dark overlay over the settings panel
            confirm_overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
            confirm_overlay.fill(OVERLAY_COLOR)
            screen.blit(confirm_overlay, (0, 0))

            # Confirmation Box
            box_w, box_h = 350, 180
            box_x = (self.screen_w - box_w) // 2
            box_y = (self.screen_h - box_h) // 2
            box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
            
            pygame.draw.rect(screen, WHITE, box_rect, border_radius=15)
            pygame.draw.rect(screen, RED, box_rect, 4, border_radius=15)

            # Draw text
            text_surf = self.font.render(self.confirm_message, True, BLACK)
            text_rect = text_surf.get_rect(center=(box_rect.centerx, box_y + 40))
            screen.blit(text_surf, text_rect)

            # Define and draw Yes/No buttons
            btn_w, btn_h = 100, 40
            
            # Position the buttons (Yes on left, No on right)
            self.btn_confirm_yes.topleft = (box_x + 50, box_y + 100)
            self.btn_confirm_yes.size = (btn_w, btn_h)
            
            self.btn_confirm_no.topleft = (box_x + box_w - btn_w - 50, box_y + 100)
            self.btn_confirm_no.size = (btn_w, btn_h)
            
            # Draw the buttons
            pygame.draw.rect(screen, GREEN, self.btn_confirm_yes, border_radius=8)
            pygame.draw.rect(screen, RED, self.btn_confirm_no, border_radius=8)
            
            yes_txt = self.font.render("YES", True, WHITE)
            no_txt = self.font.render("NO", True, WHITE)
            
            screen.blit(yes_txt, yes_txt.get_rect(center=self.btn_confirm_yes.center))
            screen.blit(no_txt, no_txt.get_rect(center=self.btn_confirm_no.center))