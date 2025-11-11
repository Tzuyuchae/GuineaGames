import pygame

# --- Colors ---
GRASS_GREEN = (132, 196, 108)
BUTTON_BROWN = (150, 111, 51)
HOVER_BROWN = (184, 138, 72)
TEXT_WHITE = (255, 255, 255)
PANEL_GRAY = (235, 235, 235)
BLACK = (0, 0, 0)

# --- Globals ---
font = None
buttons = {}
sidebar_font = None

# --- Helper class ---
class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.base_color = BUTTON_BROWN
        self.hover_color = HOVER_BROWN

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.base_color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        text_surface = font.render(self.text, True, TEXT_WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(pygame.mouse.get_pos())


# --- Initialization ---
def homescreen_init():
    global font, sidebar_font, buttons
    font = pygame.font.Font(None, 40)
    sidebar_font = pygame.font.Font(None, 26)

    buttons = {
        "mini_games": Button((100, 100, 200, 100), "Mini-games"),
        "breeding": Button((500, 100, 200, 100), "Breeding"),
        "training": Button((100, 400, 200, 100), "Training"),
        "store": Button((350, 350, 200, 100), "Store"),
        "home": Button((600, 350, 150, 100), "Home")
    }


# --- Event Handling ---
def homescreen_update(events):
    for event in events:
        for name, button in buttons.items():
            if button.is_clicked(event):
                print(f"{name} button clicked!")
                return name  # later connect to those pages
    return None


# --- Drawing ---
def homescreen_draw(screen):
    # Make the whole background green
    screen.fill(GRASS_GREEN)

    # Draw all buttons
    for button in buttons.values():
        button.draw(screen)

    # Sidebar info panel (top-right)
    pygame.draw.rect(screen, PANEL_GRAY, (620, 20, 160, 220))
    sidebar_lines = [
        "Year: 1",
        "Month: 2",
        "Day: 1",
        "",
        "🕒 12:15 AM",
        "",
        "🪙 Coins: 5",
        "🍎 Food: 5",
        "",
        "T1 x19"
    ]
    y = 40
    for line in sidebar_lines:
        text_surface = sidebar_font.render(line, True, BLACK)
        screen.blit(text_surface, (630, y))
        y += 20
