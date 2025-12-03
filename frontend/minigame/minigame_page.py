import pygame
from minigame.guinea_pig_selector import GuineaPigSelector
from minigame.final_score_screen import FinalScoreScreen
from minigame.game import Game
from minigame.pause_menu import PauseMenu


class MinigamePage:
    def __init__(self, user_id: int, player_inventory):
        self.user_id = user_id
        self.player_inventory = player_inventory

        # Match the main game window size (adjust if your project uses different values)
        self.screen_width = 672
        self.screen_height = 864

        # Basic minigame state
        self.state = "selector"  # 'selector' | 'playing' | 'reviewing_score'
        self.guinea_pig_selector = GuineaPigSelector()
        self.game_instance = None
        self.selected_guinea_pig = None
        self.final_score_screen = None

        # Pause menu needs screen dimensions
        self.pause_menu = PauseMenu(self.screen_width, self.screen_height)
        self.paused = False

    def _reward_player(self, amount: int, reason: str = "minigame reward"):
        """
        Central place to give coins to the player, with persistence/backend.

        NOTE: Right now the Game class already gives coins/food directly
        via player_inventory during play. This helper is currently unused
        to avoid double-paying, but kept for future bonus rewards.
        """
        if not self.player_inventory:
            return

        self.player_inventory.add_coins(amount)

    def update(self, events):
        """
        Main state machine for the minigame page.
        Returns:
            'homescreen' to leave the minigame, or None to stay here.
        """

        # --- STATE: SELECTOR ---
        if self.state == "selector":
            result = self.guinea_pig_selector.update(events)

            if result == "back":
                # Player chose to go back without playing
                self._reset_state()
                return "homescreen"

            elif (
                isinstance(result, (tuple, list))
                and len(result) > 0
                and result[0] == "start_game"
            ):
                # result like ('start_game', selected_guinea_pig)
                _, self.selected_guinea_pig = result

                # Pass inventory into Game so it can spend/reward if needed
                self.game_instance = Game(
                    selected_guinea_pig=self.selected_guinea_pig,
                    player_inventory=self.player_inventory,
                )
                self.state = "playing"
                self.paused = False

        # --- STATE: PLAYING ---
        elif self.state == "playing":
            if self.game_instance:
                if not self.paused:
                    self.game_instance.update(events)

                    # If the game loop has finished (Win, Lose, Back, or Exit)
                    if not getattr(self.game_instance, "running", True):
                        # Move to score review instead of immediately dumping to home
                        self.initialize_review_screen()
                        self.state = "reviewing_score"

        # --- STATE: REVIEWING SCORE ---
        elif self.state == "reviewing_score":
            if self.final_score_screen:
                result = self.final_score_screen.update(events)

                # Case: User clicked Home in the review screen
                if result == "home":
                    # Coins/food have already been applied inside Game.
                    # This screen is purely informational now.
                    self._reset_state()
                    return "homescreen"

        # Optional global quit hook (currently always False)
        if self._player_quit():
            self._reset_state()
            return "homescreen"

        return None  # Stay on this screen

    def draw(self, screen):
        if self.state == "selector" and self.guinea_pig_selector:
            self.guinea_pig_selector.draw(screen)

        elif self.state == "playing" and self.game_instance:
            self.game_instance.draw(screen)
            if self.paused:
                self.pause_menu.draw(screen)

        elif self.state == "reviewing_score" and self.final_score_screen:
            self.final_score_screen.draw(screen)

    def _reset_state(self):
        """Reset the minigame page back to its initial selector state."""
        self.state = "selector"
        self.game_instance = None
        self.selected_guinea_pig = None
        self.final_score_screen = None
        self.paused = False
        # Recreate selector so it doesn't hold stale state
        self.guinea_pig_selector = GuineaPigSelector()

    def initialize_review_screen(self):
        """
        Create and populate the FinalScoreScreen based on the finished game.
        This keeps the score/reward computation in one place.
        """
        # Default values in case the game instance doesn't expose them
        fruits = 0
        coins = 0
        player_won = False

        if self.game_instance:
            fruits = int(getattr(self.game_instance, "fruits_collected", 0) or 0)
            coins = int(getattr(self.game_instance, "coins_earned", 0) or 0)
            player_won = bool(getattr(self.game_instance, "won", False))

        # Build the score screen and pass in the results
        self.final_score_screen = FinalScoreScreen(
            screen_width=self.screen_width,
            screen_height=self.screen_height,
        )
        # score = fruits collected, reward = coins earned
        self.final_score_screen.set_results(
            score=fruits,
            player_won=player_won,
            reward=coins,
        )

    # -------------------------------------------------------------------------
    # Helper predicates (currently simple placeholders, but safe to call)
    # -------------------------------------------------------------------------
    def _player_won_level(self) -> bool:
        """Placeholder for win detection if other code ever calls this."""
        # We prefer the score screen if it's active
        if self.final_score_screen is not None:
            return bool(getattr(self.final_score_screen, "player_won", False))

        if self.game_instance is not None:
            return bool(getattr(self.game_instance, "won", False))

        return False

    def _player_quit(self) -> bool:
        """Placeholder for explicit quit-to-home detection."""
        # If you later add a flag like pause_menu.quit_to_home or game_instance.quit_to_home,
        # check it here.
        return False
