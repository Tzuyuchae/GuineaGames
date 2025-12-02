import pygame
import os
from minigame.button import Button

# Initialize font module
pygame.font.init()

# Define fonts
try:
    TITLE_FONT = pygame.font.SysFont('Arial', 36, bold=True)
    HEADING_FONT = pygame.font.SysFont('Arial', 24, bold=True)
    TEXT_FONT = pygame.font.SysFont('Arial', 18)
    SMALL_FONT = pygame.font.SysFont('Arial', 16)
except pygame.error:
    TITLE_FONT = pygame.font.Font(None, 48)
    HEADING_FONT = pygame.font.Font(None, 32)
    TEXT_FONT = pygame.font.Font(None, 24)
    SMALL_FONT = pygame.font.Font(None, 20)

# Colors
TEXT_COLOR = (255, 255, 255)
HEADING_COLOR = (255, 215, 0)  # Gold
OVERLAY_COLOR = (0, 0, 0)      # Black overlay for readability

# Load Background Image
background_img = None
current_dir = os.path.dirname(os.path.abspath(__file__))
bg_path = os.path.join(current_dir, "images", "BG_Title.png")

try:
    raw_bg = pygame.image.load(bg_path)
    # We will scale this in the draw loop or init if we had a specific init function,
    # but scaling every frame is bad. We'll do a lazy load in draw.
except FileNotFoundError:
    print("Warning: BG_Title.png not found for help page.")

# Back button
button_back = Button(336, 800, 200, 50, 'BACK', (150, 0, 0), (200, 0, 0))

# State variables
scroll_offset = 0
max_scroll = 0
content_height = 0
scaled_bg = None

def create_help_content():
    """Creates all the help content."""
    return [
        ("title", "How to Play: Guinea Gone Wild", HEADING_COLOR),
        ("text", "The goal is to breed, care for and improve your guinea pigs,", TEXT_COLOR),
        ("text", "while managing food, coins, and stats to build the best community.", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Starting the Game", HEADING_COLOR),
        ("text", "• When you start, you get a pair of Common guinea pigs.", TEXT_COLOR),
        ("text", "• Your guinea pigs start fully fed (Hunger Level 3).", TEXT_COLOR),
        ("text", "• Progress is saved automatically when you quit.", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Home Page & The Yard", HEADING_COLOR),
        ("text", "Your guinea pigs now roam freely in the yard!", TEXT_COLOR),
        ("text", "• Click on any guinea pig to open the Details Popup.", TEXT_COLOR),
        ("text", "• In the Popup, you can:", TEXT_COLOR),
        ("text", "  - View Stats (Speed, Endurance, Age).", TEXT_COLOR),
        ("text", "  - Check Hunger Level.", TEXT_COLOR),
        ("text", "  - Rename your pig by clicking the 'Edit' button.", TEXT_COLOR),
        ("text", "• Check the sidebar for total food and coin balance.", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Breeding Page", HEADING_COLOR),
        ("text", "• Select two adult parents to create offspring.", TEXT_COLOR),
        ("text", "• Naming Phase: You must name each baby before they join the yard!", TEXT_COLOR),
        ("text", "• Breeding cooldown: 30 minutes real-time.", TEXT_COLOR),
        ("text", "• Babies take 15 minutes to grow into adults.", TEXT_COLOR),
        ("text", "• Offspring inherit traits via genetics (Punnett Squares).", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Feeding and Hunger", HEADING_COLOR),
        ("text", "Hunger Levels: Full(3) -> Hungry(2) -> Starving(1) -> Dead(0)", TEXT_COLOR),
        ("text", "• Hunger drops every 5 minutes.", TEXT_COLOR),
        ("text", "• Pigs are auto-fed if you have food in inventory.", TEXT_COLOR),
        ("text", "• If you run out of food, pigs may die after 15 mins!", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Store Page", HEADING_COLOR),
        ("text", "• Buy new pigs with randomized genetics (Restocks every 30m).", TEXT_COLOR),
        ("text", "• Buy Food (Carrots, Bananas) to keep your herd alive.", TEXT_COLOR),
        ("text", "• Buy Buffs (Peppers, Cabbage) to boost minigame performance.", TEXT_COLOR),
        ("text", "• Sell adult pigs for coins based on their stats and rarity.", TEXT_COLOR),
        ("text", "• Rare/Legendary pigs sell for much more!", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Mini Games", HEADING_COLOR),
        ("text", "Run through the maze to earn coins and food!", TEXT_COLOR),
        ("text", "• Controls: Arrow Keys or WASD.", TEXT_COLOR),
        ("text", "• Objective: Collect fruit and avoid the Dragon.", TEXT_COLOR),
        ("text", "• Win: Collect all fruit.", TEXT_COLOR),
        ("text", "• Lose: Get caught by the Dragon.", TEXT_COLOR),
        ("text", "• Stats: High Speed = Faster movement.", TEXT_COLOR),
        ("text", "• Stats: High Endurance = Run longer without tiring.", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Time System", HEADING_COLOR),
        ("text", "• 5 minutes real-time = 1 month in-game.", TEXT_COLOR),
        ("text", "• 60 minutes real-time = 1 year in-game.", TEXT_COLOR),
        ("text", "• Lifespan: Approx 5 hours real-time.", TEXT_COLOR),
        ("text", "• Time pauses when the game is closed.", TEXT_COLOR),
        ("space", "", None),
        
        ("heading", "Settings and Menu", HEADING_COLOR),
        ("text", "• Press ESC to open the Pause/Settings menu.", TEXT_COLOR),
        ("text", "• You can adjust volume or Quit from there.", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Tips for Success", HEADING_COLOR),
        ("text", "• Keep an eye on hunger. Food Management is key!", TEXT_COLOR),
        ("text", "• Play the mini game often to earn free food and coins.", TEXT_COLOR),
        ("text", "• Breed strategically to get 'Fluffy' or 'Speed' traits.", TEXT_COLOR),
        ("text", "• Take Breaks - Time only moves while you're playing.", TEXT_COLOR),
        ("space", "", None),

        ("title", "HAVE FUN!", HEADING_COLOR),
        ("space", "", None),
        ("space", "", None),
        ("space", "", None),
        ("space", "", None),
    ]

def get_item_height(item_type):
    """Returns the vertical space required for a specific item type."""
    if item_type == "title": return 60
    if item_type == "heading": return 45
    if item_type == "text": return 30
    if item_type == "space": return 15
    return 30

def help_update(events):
    """Handles scrolling and back button."""
    global scroll_offset
    mouse_pos = pygame.mouse.get_pos()

    for event in events:
        if button_back.check_click(event):
            return 'settings'

        if event.type == pygame.MOUSEWHEEL:
            scroll_offset -= event.y * 30
            scroll_offset = max(0, min(scroll_offset, max_scroll))

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                scroll_offset -= 30
            elif event.key == pygame.K_DOWN:
                scroll_offset += 30
            scroll_offset = max(0, min(scroll_offset, max_scroll))

    button_back.check_hover(mouse_pos)
    return None

def help_draw(screen):
    global max_scroll, content_height, scaled_bg

    screen_w, screen_h = screen.get_size()

    # 1. Draw Background Image (Scaled once)
    if raw_bg:
        if scaled_bg is None or scaled_bg.get_size() != (screen_w, screen_h):
            scaled_bg = pygame.transform.scale(raw_bg, (screen_w, screen_h))
        screen.blit(scaled_bg, (0, 0))
    else:
        screen.fill((20, 20, 30)) # Fallback color

    # 2. Draw Dark Overlay (for text readability)
    overlay = pygame.Surface((screen_w, screen_h))
    overlay.set_alpha(200) # 0-255, higher is darker
    overlay.fill(OVERLAY_COLOR)
    screen.blit(overlay, (0, 0))

    # 3. Calculate Total Content Height
    content = create_help_content()
    if content_height == 0:
        total_h = 40 # Initial top padding
        for item_type, _, _ in content:
            total_h += get_item_height(item_type)
        # Add generous bottom padding so last items scroll up nicely
        content_height = total_h + 300 

    # 4. Calculate Max Scroll
    # Allow scrolling until the bottom of content hits roughly the middle of the screen
    max_scroll = max(0, content_height - (screen_h - 150))

    # 5. Create Transparent Content Surface
    # SRCALPHA makes the background transparent so we see the image behind
    content_surface = pygame.Surface((screen_w, content_height), pygame.SRCALPHA)

    # 6. Render Content onto Surface
    y_pos = 20
    for item_type, text, color in content:
        height = get_item_height(item_type)
        
        text_surf = None
        if item_type == "title":
            text_surf = TITLE_FONT.render(text, True, color)
            # Center Titles
            dest_x = (screen_w - text_surf.get_width()) // 2
        elif item_type == "heading":
            text_surf = HEADING_FONT.render(text, True, color)
            dest_x = 40
        elif item_type == "text":
            text_surf = TEXT_FONT.render(text, True, color)
            dest_x = 50
        
        if text_surf:
            content_surface.blit(text_surf, (dest_x, y_pos))
        
        y_pos += height

    # 7. Blit the Content Surface (Scrolled)
    screen.blit(content_surface, (0, -scroll_offset))

    # 8. Draw Bottom UI Overlay (for Back Button area)
    bottom_bar = pygame.Surface((screen_w, 100))
    bottom_bar.fill(OVERLAY_COLOR)
    bottom_bar.set_alpha(230) # Slightly more opaque
    screen.blit(bottom_bar, (0, screen_h - 100))

    # 9. Draw Back Button
    button_back.rect.y = screen_h - 75 # Ensure it's always at bottom
    button_back.text_rect.center = button_back.rect.center
    button_back.draw(screen)

    # 10. Scroll Indicator
    if max_scroll > 0:
        pct = int((scroll_offset / max_scroll) * 100) if max_scroll > 0 else 0
        scroll_text = SMALL_FONT.render(f"Scroll: {pct}%", True, (150, 150, 150))
        scroll_rect = scroll_text.get_rect(center=(screen_w // 2, screen_h - 90))
        screen.blit(scroll_text, scroll_rect)