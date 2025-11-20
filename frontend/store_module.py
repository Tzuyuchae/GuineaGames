"""
store_module.py

Single-file implementation of the "Guinea Games Store".

Provides data models for GuineaPig, FoodItem, PlayerInventory and a Store
class that supports adoption (buy/sell) and a food shop, with a CLI-style
console display that mirrors the provided wireframe requirements.

Run directly to see a demo of store display and sample transactions.
"""
import time
import uuid
import random
import math
from typing import List, Dict


# ------------------------- Data Models -------------------------


class GuineaPig:
    """Represents a guinea pig available for adoption.

    Attributes:
        name (str): The guinea pig's name.
        score (int): Randomly generated score used as the buy price.
        id (str): Unique identifier (UUID4 string).
    """

    MIN_PIG_SCORE = 50
    MAX_PIG_SCORE = 500

    def __init__(self, name: str, score: int = None):
        self.name = name
        # If not provided, assign a randomized score between MIN_PIG_SCORE and MAX_PIG_SCORE
        self.score = score if score is not None else random.randint(self.MIN_PIG_SCORE, self.MAX_PIG_SCORE)
        self.id = str(uuid.uuid4())

    def __repr__(self):
        return f"GuineaPig(name={self.name!r}, score={self.score}, id={self.id})"


class FoodItem:
    """Represents a food or buff item sold in the store.

    Attributes:
        name (str): Item name.
        price (int): Cost in coins.
        hunger_boost (int): Hunger boost amount (0 for non-hunger buffs).
        duration_minutes (int): Duration in minutes (0 for 1-round buffs).
        effect_type (str): One of 'SPEED', 'ENDURANCE', or 'HUNGER'.
    """

    def __init__(self, name: str, price: int, hunger_boost: int, duration_minutes: int, effect_type: str):
        self.name = name
        self.price = price
        self.hunger_boost = hunger_boost
        self.duration_minutes = duration_minutes
        self.effect_type = effect_type

    def __repr__(self):
        return f"FoodItem(name={self.name!r}, price={self.price}, effect={self.effect_type})"


class PlayerInventory:
    """Tracks a player's coins, adopted guinea pigs, and owned food items.

    Attributes:
        coins (int): Current coin balance.
        owned_pigs (List[GuineaPig]): Guinea pigs the player has adopted.
        inventory (Dict[str, int]): Mapping from food item name to quantity owned.
    """

    def __init__(self, coins: int = 0):
        self.coins = coins
        self.owned_pigs: List[GuineaPig] = []
        self.inventory: Dict[str, int] = {}

    def add_food(self, item_name: str, qty: int = 1):
        self.inventory[item_name] = self.inventory.get(item_name, 0) + qty

    def remove_food(self, item_name: str, qty: int = 1):
        if self.inventory.get(item_name, 0) >= qty:
            self.inventory[item_name] -= qty
            if self.inventory[item_name] == 0:
                del self.inventory[item_name]
            return True
        return False


# ------------------------- Store Logic -------------------------


class Store:
    """Represents the in-game store containing pigs for adoption and food items.

    Attributes:
        pigs_for_sale (List[GuineaPig]): Up to three guinea pigs available.
        last_refresh_time (float): Timestamp of when pigs were last generated.
        food_catalog (Dict[str, FoodItem]): Available food/buff items.
    """

    REFRESH_SECONDS = 30 * 60  # 30 minutes
    MAX_PIGS = 3

    def __init__(self):
        self.pigs_for_sale: List[GuineaPig] = []
        self.last_refresh_time: float = 0.0
        self.food_catalog: Dict[str, FoodItem] = {}
        self._init_food_catalog()
        self.generate_new_pigs()

    def _init_food_catalog(self):
        """Define the 4 required food items and add them to the catalog."""
        # Low Hunger Food (Banana): Price: ~100 coins. +1 Hunger, 15 minutes
        self.food_catalog['Banana'] = FoodItem(
            name='Banana', price=100, hunger_boost=1, duration_minutes=15, effect_type='HUNGER'
        )
        # High Hunger Food (Carrot): Price: ~150 coins. +2 Hunger, 30 minutes
        self.food_catalog['Carrot'] = FoodItem(
            name='Carrot', price=150, hunger_boost=2, duration_minutes=30, effect_type='HUNGER'
        )
        # Speed Buff (Bell Pepper): Price: ~200 coins. Buff for 1 mini-game round
        self.food_catalog['Bell Pepper'] = FoodItem(
            name='Bell Pepper', price=200, hunger_boost=0, duration_minutes=0, effect_type='SPEED'
        )
        # Endurance Buff (Cabbage): Price: ~250 coins. Buff for 1 mini-game round
        self.food_catalog['Cabbage'] = FoodItem(
            name='Cabbage', price=250, hunger_boost=0, duration_minutes=0, effect_type='ENDURANCE'
        )

    def check_refresh_timer(self):
        """Check whether 30 minutes have passed since the last refresh.

        If the refresh timer has expired, generate a new set of pigs and update
        `last_refresh_time`.
        """
        now = time.time()
        if (now - self.last_refresh_time) >= Store.REFRESH_SECONDS:
            self.generate_new_pigs()

    def generate_new_pigs(self):
        """Generate up to three new random GuineaPig objects and reset timer.

        Names are generated from a small list with a random suffix to keep them
        unique-looking.
        """
        names = ['Nibbles', 'Cocoa', 'Buttons', 'Poppy', 'Widget', 'Pebble', 'Mango', 'Daisy']
        self.pigs_for_sale = []
        for _ in range(Store.MAX_PIGS):
            name = random.choice(names) + '-' + str(random.randint(1, 999))
            pig = GuineaPig(name=name)
            self.pigs_for_sale.append(pig)
        self.last_refresh_time = time.time()

    def buy_guinea_pig(self, player: PlayerInventory, pig_index: int) -> bool:
        """Attempt to buy a guinea pig from `pigs_for_sale` by index (0-based).

        The purchase price equals the pig's score. On success, deduct coins,
        add pig to player's `owned_pigs`, and remove it from `pigs_for_sale`.

        Returns True on success, False on failure (invalid index or insufficient coins).
        """
        self.check_refresh_timer()
        if pig_index < 0 or pig_index >= len(self.pigs_for_sale):
            return False
        pig = self.pigs_for_sale[pig_index]
        price = pig.score
        if player.coins < price:
            return False
        player.coins -= price
        player.owned_pigs.append(pig)
        # Remove purchased pig from the store
        del self.pigs_for_sale[pig_index]
        return True

    def sell_guinea_pig(self, player: PlayerInventory, pig_id: str) -> bool:
        """Sell a guinea pig from player's `owned_pigs` by id.

        The sell price is floor(score * 0.75). On success, add coins and remove
        the pig from player's collection. Returns True on success.
        """
        for i, pig in enumerate(player.owned_pigs):
            if pig.id == pig_id:
                sell_price = math.floor(pig.score * 0.75)
                player.coins += sell_price
                del player.owned_pigs[i]
                return True
        return False

    def buy_food(self, player: PlayerInventory, item_name: str, qty: int = 1) -> bool:
        """Buy `qty` units of `item_name` from the food catalog.

        Returns True if purchase succeeded, False otherwise.
        """
        if item_name not in self.food_catalog:
            return False
        item = self.food_catalog[item_name]
        total_price = item.price * qty
        if player.coins < total_price:
            return False
        player.coins -= total_price
        player.add_food(item_name, qty)
        return True

    def get_time_until_refresh(self) -> int:
        """Return seconds remaining until next pig refresh."""
        now = time.time()
        elapsed = now - self.last_refresh_time
        remaining = max(0, Store.REFRESH_SECONDS - int(elapsed))
        return remaining

    def _format_time(self, seconds: int) -> str:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def display_store_cli(self, player: PlayerInventory):
        """Print a console representation of the store that mirrors the wireframe.

        Shows header with coin balance and refresh timer, an Adoption section
        listing up to 3 guinea pigs with Name/Score and a buy label, and a Food
        Shop section listing all defined food items with price and buy label.
        """
        # Ensure pigs are fresh
        self.check_refresh_timer()

        coins_line = f"[Coins: {player.coins}]"
        refresh_seconds = self.get_time_until_refresh()
        refresh_line = f"[Refresh: {self._format_time(refresh_seconds)}]"

        # Header
        print("=" * 60)
        print(f"GUINEA GAMES STORE".center(60))
        print(f"{coins_line}  {refresh_line}".center(60))
        print("=" * 60)

        # Adoption Section
        print("Guinea Pig Adoption".center(60, ' '))
        print("-" * 60)
        if not self.pigs_for_sale:
            print("No guinea pigs available right now. Come back later.".center(60))
        else:
            # Present each pig in a simple 3-column layout (index, name, price)
            for idx, pig in enumerate(self.pigs_for_sale):
                buy_label = f"[Buy #{idx}]"
                print(f"{idx+1}. Name: {pig.name:25} Price: {pig.score:4} {buy_label}")
        print("\n")

        # Food Shop Section
        print("Food Shop".center(60, ' '))
        print("-" * 60)
        # Format: Name | Price | Effect | Duration | [Buy]
        for item in self.food_catalog.values():
            duration = (f"{item.duration_minutes}m" if item.duration_minutes > 0 else "1 round")
            effect = (
                f"Hunger+{item.hunger_boost}" if item.effect_type == 'HUNGER' else item.effect_type
            )
            buy_label = f"[Buy {item.name}]"
            print(f"{item.name:12} Price: {item.price:4}  Effect: {effect:12} Duration: {duration:8} {buy_label}")

        print("=" * 60)


# ------------------------- Demo / CLI Execution -------------------------


if __name__ == "__main__":
    # Initialize a demo player with 420 coins per requirements
    player = PlayerInventory(coins=420)
    store = Store()

    print("Initial store display:")
    store.display_store_cli(player)

    # Sample transactions demonstration
    print("\nDemo transactions:\n")

    # Attempt to buy the first available pig (index 0)
    if store.pigs_for_sale:
        first_pig = store.pigs_for_sale[0]
        print(f"Attempting to buy pig '{first_pig.name}' priced {first_pig.score} coins...")
        success = store.buy_guinea_pig(player, 0)
        if success:
            print(f"Purchased {first_pig.name} for {first_pig.score} coins.")
        else:
            print("Purchase failed (insufficient coins or invalid index).")
    else:
        print("No pigs to buy in demo.")

    # If player now owns a pig, demonstrate selling it
    if player.owned_pigs:
        to_sell = player.owned_pigs[0]
        sell_price = math.floor(to_sell.score * 0.75)
        print(f"Selling owned pig '{to_sell.name}' for {sell_price} coins...")
        sold = store.sell_guinea_pig(player, to_sell.id)
        if sold:
            print(f"Sold {to_sell.name} for {sell_price} coins.")
        else:
            print("Sell failed (pig not found in inventory).")
    else:
        print("No owned pigs to sell in demo.")

    # Demonstrate buying a food item
    print("\nAttempting to buy 1 'Banana' (100 coins)...")
    bought_food = store.buy_food(player, 'Banana', qty=1)
    if bought_food:
        print("Banana purchased and added to inventory.")
    else:
        print("Failed to purchase Banana (insufficient coins or item missing).")

    # Final state
    print("\nFinal store display after demo transactions:")
    store.display_store_cli(player)

    print("Player inventory summary:")
    print(f"Coins: {player.coins}")
    print(f"Owned pigs: {len(player.owned_pigs)}")
    if player.owned_pigs:
        for p in player.owned_pigs:
            print(f" - {p.name} (score={p.score})")
    print(f"Food inventory: {player.inventory}")
