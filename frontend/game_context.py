# frontend/game_context.py

class GameContext:
    """
    Shared state between frontend screens and the backend.
    Keeps track of the current user and their selected pet.
    """

    def __init__(self):
        # Backend user we’re playing as
        self.user_id = None
        self.username = None
        self.email = None

        # Currently selected pet for the minigame
        self.selected_pet = None  # e.g. dict from API

        # Any coins / points cached locally (optional)
        self.coins = 0


# Single instance you can import everywhere
game_context = GameContext()
