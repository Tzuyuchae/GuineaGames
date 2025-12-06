import pygame
from .guinea_pig_selector import GuineaPigSelector
from .final_score_screen import FinalScoreScreen
from .game import Game
from .pause_menu import PauseMenu
from api_client import api 

class MinigamePage:
    def __init__(self, user_id=1, player_inventory=None):
        self.state = 'selector'
        self.guinea_pig_selector = None
        self.final_score_screen = None
        self.game_instance = None
        self.selected_guinea_pig = None
        self.user_id = user_id
        self.player_inventory = player_inventory 
        
        self.paused = False
        self.pause_menu = PauseMenu(672, 864) 

    def initialize_selector(self):
        """Fetches fresh data and creates the selector."""
        print("Initializing Minigame Selector - Fetching Pets...")
        try:
            # Fetch user pets from API
            owned_pigs = api.get_user_pets(self.user_id)
            print(f"Found {len(owned_pigs)} pets for minigame.")
        except Exception as e:
            print(f"Error fetching pets for minigame: {e}")
            owned_pigs = []
            
        self.guinea_pig_selector = GuineaPigSelector(
            user_id=self.user_id,
            inventory_pigs=owned_pigs
        )

    def initialize_review_screen(self):
        # Get fruit count from game instance
        fruit_count = getattr(self.game_instance, 'collected_amount', 0)
        
        # Reward Logic
        coin_amount = int(fruit_count * 0.5) # Example: 50% conversion
        if coin_amount < 1 and fruit_count > 0:
            coin_amount = 1 

        if api and fruit_count > 0:
            print(f"Minigame Results: {fruit_count} Fruits, {coin_amount} Coins")
            try:
                # Give Carrots
                api.add_inventory_item(
                    self.user_id, 
                    item_name="Carrot", 
                    item_type="food", 
                    quantity=fruit_count
                )
                
                # Give Coins
                if coin_amount > 0:
                    api.create_transaction(
                        self.user_id, 
                        t_type="reward", 
                        amount=coin_amount, 
                        desc="Minigame Reward"
                    )
                
            except Exception as e:
                print(f"Reward Error: {e}")
        
        self.final_score_screen = FinalScoreScreen(fruit_count, coin_amount)

    def update(self, events):
        # Initialize selector if needed
        if self.state == 'selector' and self.guinea_pig_selector is None:
            self.initialize_selector()

        # --- PLAYING STATE ---
        if self.state == 'playing':
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused

            if self.paused:
                for event in events:
                    action = self.pause_menu.handle_input(event)
                    if action == 'resume':
                        self.paused = False
                    elif action == 'quit':
                        self._reset_state()
                        return 'homescreen'
                return None 

        # --- SELECTOR STATE ---
        if self.state == 'selector':
            result = self.guinea_pig_selector.update(events)

            if result == 'back':
                self._reset_state()
                return 'homescreen'

            elif isinstance(result, (tuple, list)) and len(result) > 0 and result[0] == 'start_game':
                # Unwrap the tuple: ('start_game', pet_data_dict)
                _, self.selected_guinea_pig = result
                
                print(f"Starting game with: {self.selected_guinea_pig['name']}")
                
                # Initialize Game
                self.game_instance = Game(
                    selected_guinea_pig=self.selected_guinea_pig, 
                    player_inventory=self.player_inventory
                )
                self.state = 'playing'
                self.paused = False

        # --- GAME UPDATE ---
        elif self.state == 'playing':
            if self.game_instance:
                if not self.paused:
                    self.game_instance.update(events)
                    
                    if not self.game_instance.running:
                        self.initialize_review_screen()
                        self.state = 'reviewing_score'

        # --- REVIEW STATE ---
        elif self.state == 'reviewing_score':
            if self.final_score_screen:
                result = self.final_score_screen.update(events)
                if result == 'home':
                    self._reset_state()
                    return 'homescreen'

        return None

    def draw(self, screen):
        if self.state == 'selector' and self.guinea_pig_selector:
            self.guinea_pig_selector.draw(screen)
        elif self.state == 'playing' and self.game_instance:
            self.game_instance.draw(screen)
            if self.paused:
                self.pause_menu.draw(screen)
        elif self.state == 'reviewing_score' and self.final_score_screen:
            self.final_score_screen.draw(screen)

    def _reset_state(self):
        """Resets everything so next time we open minigame, it reloads."""
        self.state = 'selector'
        self.game_instance = None
        self.selected_guinea_pig = None
        self.guinea_pig_selector = None # Setting to None forces reload in update()
        self.final_score_screen = None
        self.paused = False