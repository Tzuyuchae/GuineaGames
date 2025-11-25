import pygame
from minigame.button import Button  # --- FIX: Import from the correct location ---
# Initialize font module
pygame.font.init()

# Define fonts for help page
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

# Colors matching the game theme
TEXT_COLOR = (255, 255, 255)
HEADING_COLOR = (255, 215, 0)  # Gold
BACKGROUND_COLOR = (20, 20, 20)
ACCENT_COLOR = (150, 0, 0)

# Back button
button_back = Button(336, 800, 200, 50, 'BACK', (150, 0, 0), (200, 0, 0))

# Scroll offset
scroll_offset = 0
max_scroll = 0

def create_help_content():
    """Creates all the help content as a list of (type, text, color) tuples."""
    content = [
        ("title", "How to Play: Guinea Gone Wild", HEADING_COLOR),
        ("text", "The goal is to breed, care for and improve your guinea pigs,", TEXT_COLOR),
        ("text", "while managing food, coins, and stats to build the best community you can.", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Starting the Game", HEADING_COLOR),
        ("text", "• When you start the game, a new save is automatically created.", TEXT_COLOR),
        ("text", "• You will start your community with a pair of Common rarity guinea pigs.", TEXT_COLOR),
        ("text", "• Your guinea pigs will start completely Full, with a Hunger Level of 3.", TEXT_COLOR),
        ("text", "• Your game will only be saved when you manually save or when you quit.", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Main Menu", HEADING_COLOR),
        ("text", "When you open the game you will be taken to a Title Screen:", TEXT_COLOR),
        ("text", "• Play means to start your saved game", TEXT_COLOR),
        ("text", "• Quit means exit the game", TEXT_COLOR),
        ("text", "• Settings is where you can adjust volume and/or restart your game", TEXT_COLOR),
        ("text", "• You only have one save file, so the game automatically continues where", TEXT_COLOR),
        ("text", "  you saved it last.", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Home Page", HEADING_COLOR),
        ("text", "What you can do on this page:", TEXT_COLOR),
        ("text", "• View all your guinea pigs", TEXT_COLOR),
        ("text", "• Check your total food and coin balance", TEXT_COLOR),
        ("text", "• Click on the guinea pig to:", TEXT_COLOR),
        ("text", "  - See their details", TEXT_COLOR),
        ("text", "  - Hunger level", TEXT_COLOR),
        ("text", "  - Coat colours and rarity (Common, Uncommon, Rare)", TEXT_COLOR),
        ("text", "  - Speed, Endurance, and overall Score", TEXT_COLOR),
        ("text", "  - Feed them manually", TEXT_COLOR),
        ("text", "  - Sell them for coins", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Breeding Page", HEADING_COLOR),
        ("text", "• Select two adult guinea pigs to breed and create new offspring.", TEXT_COLOR),
        ("text", "• They'll create 2–4 baby guinea pigs.", TEXT_COLOR),
        ("text", "• Breeding cooldown: 30 minutes real-time (= 6 months in-game).", TEXT_COLOR),
        ("text", "• Babies mature into adults after 15 minutes real-time (= 3 months in-game).", TEXT_COLOR),
        ("text", "• Offspring traits are generated using Punnett-square-like genetics", TEXT_COLOR),
        ("text", "  based on parent genes.", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Feeding and Hunger System", HEADING_COLOR),
        ("text", "Each guinea pig has 4 hunger levels:", TEXT_COLOR),
        ("text", "• Full (3)", TEXT_COLOR),
        ("text", "• Hungry (2)", TEXT_COLOR),
        ("text", "• Starving (1)", TEXT_COLOR),
        ("text", "• Dead (0)", TEXT_COLOR),
        ("text", "Hunger decreases one level every 5 minutes in real time.", TEXT_COLOR),
        ("text", "If a guinea pig isn't fed for 15 minutes in real time, it dies.", TEXT_COLOR),
        ("text", "Guinea pigs are automatically fed every 5 minutes (if you have food).", TEXT_COLOR),
        ("text", "If food is limited, the hungriest guinea pigs are prioritized.", TEXT_COLOR),
        ("text", "You can also feed manually at any time.", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Store Page", HEADING_COLOR),
        ("text", "Buy Guinea Pigs:", TEXT_COLOR),
        ("text", "• Up to 3 new guinea pigs are available every 30 minutes.", TEXT_COLOR),
        ("text", "• Prices are based on each guinea pig's score.", TEXT_COLOR),
        ("text", "• Reselling a guinea pig you just bought will lose you coins–", TEXT_COLOR),
        ("text", "  you must first improve their score by keeping them alive as long", TEXT_COLOR),
        ("text", "  as possible and by playing the mini game with them.", TEXT_COLOR),
        ("space", "", None),
        ("text", "Selling Guinea Pigs:", TEXT_COLOR),
        ("text", "• You can sell guinea pigs for coins.", TEXT_COLOR),
        ("text", "• Rarer guinea pigs with higher scores will sell for more money.", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Food Options", HEADING_COLOR),
        ("text", "Basic Food: +1 Hunger Level, Lasts 15 mins, Low Cost", TEXT_COLOR),
        ("text", "Premium Food: +2 Hunger Levels, Lasts 30 mins, Higher Cost", TEXT_COLOR),
        ("text", "Speed Buff: Boosts speed for one mini game, Moderate Cost", TEXT_COLOR),
        ("text", "Endurance Buff: Boosts endurance for one mini game, Moderate Cost", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Mini Games", HEADING_COLOR),
        ("text", "Play the mini game to earn food and coins while improving your", TEXT_COLOR),
        ("text", "guinea pig's stats!", TEXT_COLOR),
        ("text", "• Control your guinea pig using arrow keys or 'WASD'", TEXT_COLOR),
        ("text", "• Your guinea pig runs through a maze while avoiding the dragon", TEXT_COLOR),
        ("text", "• You can exit the maze whenever you like to end the game.", TEXT_COLOR),
        ("text", "• If your guinea pig is caught by the dragon, it will die permanently", TEXT_COLOR),
        ("text", "  in the main game.", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Scoring and Performance", HEADING_COLOR),
        ("text", "• Rewards depend on how long you stay in the maze and how much", TEXT_COLOR),
        ("text", "  food you collect.", TEXT_COLOR),
        ("text", "• Playing the mini game with a specific guinea pig will improve its scores", TEXT_COLOR),
        ("text", "• Speed determines how fast your guinea pig runs", TEXT_COLOR),
        ("text", "• Endurance affects how long it can maintain top speed", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Scores and Lifespan", HEADING_COLOR),
        ("text", "Guinea pig scores depend on:", TEXT_COLOR),
        ("text", "• Speed and endurance stats", TEXT_COLOR),
        ("text", "• Coat rarity", TEXT_COLOR),
        ("text", "• Amount of time alive", TEXT_COLOR),
        ("text", "• Mini game performance", TEXT_COLOR),
        ("text", "Each guinea pig lives for 5 hours real-time (= 5 in game years)", TEXT_COLOR),
        ("text", "Old guinea pigs are slow: speed and endurance are halved in the", TEXT_COLOR),
        ("text", "last 15 minutes of a guinea pig's life.", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Time System", HEADING_COLOR),
        ("text", "• 5 minutes real-time = 1 month in game", TEXT_COLOR),
        ("text", "• 60 minutes real time = 1 in game year", TEXT_COLOR),
        ("text", "• 5 hours real time = full guinea pig lifespan", TEXT_COLOR),
        ("text", "Time only passes when you are actively playing, not while the", TEXT_COLOR),
        ("text", "game is closed.", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Settings and Menu", HEADING_COLOR),
        ("text", "Pause Menu (Press ESC to pause):", TEXT_COLOR),
        ("text", "• Save and Quit (returns to title screen)", TEXT_COLOR),
        ("text", "• Settings", TEXT_COLOR),
        ("text", "• Resume", TEXT_COLOR),
        ("space", "", None),
        ("text", "Settings Page:", TEXT_COLOR),
        ("text", "• Adjust volume levels", TEXT_COLOR),
        ("text", "• Restart the Game", TEXT_COLOR),
        ("text", "• Set the maximum number of guinea pigs shown on the home page", TEXT_COLOR),
        ("text", "• If all your guinea pigs die, you'll have to Restart the game", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Restart the Game", HEADING_COLOR),
        ("text", "• Go to the settings and click Restart.", TEXT_COLOR),
        ("text", "• Confirm 'yes' when asked, 'Are you sure?'", TEXT_COLOR),
        ("text", "• This will reset all progress and start a new save file.", TEXT_COLOR),
        ("space", "", None),

        ("heading", "Tips for Success", HEADING_COLOR),
        ("text", "• Keep an eye on hunger. Food Management is the key!", TEXT_COLOR),
        ("text", "• Play the mini game often to earn rewards and improve stats", TEXT_COLOR),
        ("text", "• Breed strategically to develop stronger, faster offspring", TEXT_COLOR),
        ("text", "• Take Breaks - Time only moves while you're playing", TEXT_COLOR),
        ("space", "", None),

        ("title", "HAVE LOTS OF FUN!", HEADING_COLOR),
        ("space", "", None),
        ("space", "", None),
    ]
    return content

def help_update(events):
    """Handles events for the help page."""
    global scroll_offset
    mouse_pos = pygame.mouse.get_pos()

    for event in events:
        if button_back.check_click(event):
            print("Back button clicked! Returning to settings.")
            return 'settings'

        # Handle scrolling with mouse wheel
        if event.type == pygame.MOUSEWHEEL:
            scroll_offset -= event.y * 20  # Scroll speed
            # Clamp scroll offset
            scroll_offset = max(0, min(scroll_offset, max_scroll))

        # Handle scrolling with arrow keys
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                scroll_offset -= 20
            elif event.key == pygame.K_DOWN:
                scroll_offset += 20
            # Clamp scroll offset
            scroll_offset = max(0, min(scroll_offset, max_scroll))

    button_back.check_hover(mouse_pos)
    return None

def help_draw(screen):
    """Draws the help page with scrolling content."""
    global max_scroll

    # Draw background
    screen.fill(BACKGROUND_COLOR)

    # Create a surface for the scrollable content
    content_surface = pygame.Surface((672, 10000))  # Large surface for all content
    content_surface.fill(BACKGROUND_COLOR)

    # Get help content
    content = create_help_content()

    y_offset = 20

    # Render all content
    for item_type, text, color in content:
        if item_type == "title":
            text_surface = TITLE_FONT.render(text, True, color)
            text_rect = text_surface.get_rect(centerx=336)
            text_rect.y = y_offset
            content_surface.blit(text_surface, text_rect)
            y_offset += 50
        elif item_type == "heading":
            text_surface = HEADING_FONT.render(text, True, color)
            text_rect = text_surface.get_rect(x=40)
            text_rect.y = y_offset
            content_surface.blit(text_surface, text_rect)
            y_offset += 35
        elif item_type == "text":
            text_surface = TEXT_FONT.render(text, True, color)
            text_rect = text_surface.get_rect(x=50)
            text_rect.y = y_offset
            content_surface.blit(text_surface, text_rect)
            y_offset += 25
        elif item_type == "space":
            y_offset += 10

    # Calculate max scroll
    max_scroll = max(0, y_offset - 700)  # Leave room for button at bottom

    # Blit the scrollable content to the main screen
    screen.blit(content_surface, (0, -scroll_offset), (0, 0, 672, 750))

    # Draw a semi-transparent overlay at the bottom for the button
    bottom_overlay = pygame.Surface((672, 100))
    bottom_overlay.fill(BACKGROUND_COLOR)
    bottom_overlay.set_alpha(230)
    screen.blit(bottom_overlay, (0, 764))

    # Draw the back button
    button_back.draw(screen)

    # Draw scroll indicator if there's more content
    if max_scroll > 0:
        scroll_text = SMALL_FONT.render("Use Mouse Wheel or Arrow Keys to Scroll", True, (150, 150, 150))
        scroll_rect = scroll_text.get_rect(centerx=336, y=740)
        screen.blit(scroll_text, scroll_rect)