import pygame
from minigame.guinea_pig_selector import GuineaPigSelector
from minigame.game import Game
from minigame.pause_menu import PauseMenu

class MinigamePage:
    def __init__(self, user_id=1, player_inventory=None):
        self.state = 'selector'
        self.guinea_pig_selector = None
        self.game_instance = None
        self.selected_guinea_pig = None
        self.user_id = user_id
        self.player_inventory = player_inventory # Store inventory reference
        
        self.paused = False
        self.pause_menu = PauseMenu(672, 864) 

    def initialize_selector(self):
        owned_pigs = self.player_inventory.owned_pigs if self.player_inventory else []
        self.guinea_pig_selector = GuineaPigSelector(
            user_id=self.user_id,
            inventory_pigs=owned_pigs
        )

    def update(self, events):
        if self.guinea_pig_selector is None:
            self.initialize_selector()

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
                    elif action == 'settings':
                        print("Settings clicked")
                return None 

        if self.state == 'selector':
            result = self.guinea_pig_selector.update(events)

            if result == 'back':
                self._reset_state()
                return 'homescreen'

            elif isinstance(result, (tuple, list)) and len(result) > 0 and result[0] == 'start_game':
                _, self.selected_guinea_pig = result
                
                # --- PASS INVENTORY HERE ---
                self.game_instance = Game(
                    selected_guinea_pig=self.selected_guinea_pig, 
                    player_inventory=self.player_inventory
                )
                self.state = 'playing'
                self.paused = False

        elif self.state == 'playing':
            if self.game_instance:
                if not self.paused:
                    self.game_instance.update(events)
                    if not self.game_instance.running:
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

    def _reset_state(self):
        self.state = 'selector'
        self.game_instance = None
        self.selected_guinea_pig = None
        self.guinea_pig_selector = None
        self.paused = False