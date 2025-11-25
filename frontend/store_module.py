"""
store_module.py

Implementation of the "Guinea Games Store".
Integrates with breeding.py to ensure purchased pigs have genetics.
"""
import time
import random
import math
from typing import List, Dict

# --- IMPORT THE REAL GUINEA PIG CLASS ---
# We wrap this in a try/except so this file can still run in standalone mode for testing
try:
    from breeding import GuineaPig
except ImportError:
    # Fallback for standalone testing only
    import uuid
    class GuineaPig:
        def __init__(self, name, score=None):
            self.name = name
            self.score = score if score else random.randint(50, 500)
            self.id = str(uuid.uuid4())

# ------------------------- Data Models -------------------------

class FoodItem:
    """Represents a food or buff item sold in the store."""
    def __init__(self, name: str, price: int, hunger_boost: int, duration_minutes: int, effect_type: str):
        self.name = name
        self.price = price
        self.hunger_boost = hunger_boost
        self.duration_minutes = duration_minutes
        self.effect_type = effect_type

    def __repr__(self):
        return f"FoodItem(name={self.name!r}, price={self.price})"


class PlayerInventory:
    """Tracks a player's coins, adopted guinea pigs, and owned food items."""

    def __init__(self, coins: int = 0, food: int = 5):
        self.coins = coins
        self.food = food  # General food counter (for Homescreen HUD)
        self.owned_pigs: List[GuineaPig] = []
        
        # Detailed inventory for specific buffs (Speed/Endurance items)
        self.items: Dict[str, int] = {}

    def add_food(self, item_name: str, qty: int = 1):
        """Adds specific items. If it's food, also increase global food counter."""
        if item_name in ['Banana', 'Carrot']:
            self.food += qty
        
        # Add to detailed inventory
        self.items[item_name] = self.items.get(item_name, 0) + qty

    def remove_food(self, item_name: str, qty: int = 1):
        if self.items.get(item_name, 0) >= qty:
            self.items[item_name] -= qty
            
            # If it's a food item, decrease global counter
            if item_name in ['Banana', 'Carrot']:
                self.food = max(0, self.food - qty)
                
            if self.items[item_name] == 0:
                del self.items[item_name]
            return True
        return False
    
    def add_coins(self, amount):
        self.coins += amount

    def remove_coins(self, amount):
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False


# ------------------------- Store Logic -------------------------


class Store:
    """Represents the in-game store containing pigs for adoption and food items."""

    REFRESH_SECONDS = 30 * 60  # 30 minutes
    MAX_PIGS = 3

    def __init__(self):
        self.pigs_for_sale: List[GuineaPig] = []
        self.last_refresh_time: float = 0.0
        self.food_catalog: Dict[str, FoodItem] = {}
        self._init_food_catalog()
        self.generate_new_pigs()

    def _init_food_catalog(self):
        """Define the food items."""
        self.food_catalog['Banana'] = FoodItem('Banana', 100, 1, 15, 'HUNGER')
        self.food_catalog['Carrot'] = FoodItem('Carrot', 150, 2, 30, 'HUNGER')
        self.food_catalog['Bell Pepper'] = FoodItem('Bell Pepper', 200, 0, 0, 'SPEED')
        self.food_catalog['Cabbage'] = FoodItem('Cabbage', 250, 0, 0, 'ENDURANCE')

    def check_refresh_timer(self):
        """Regenerate pigs if 30 mins passed."""
        now = time.time()
        if (now - self.last_refresh_time) >= Store.REFRESH_SECONDS:
            self.generate_new_pigs()

    def generate_new_pigs(self):
        """Generate new random GuineaPig objects (WITH GENES)."""
        names = ['Nibbles', 'Cocoa', 'Buttons', 'Poppy', 'Widget', 'Pebble', 'Mango', 'Daisy']
        self.pigs_for_sale = []
        
        for _ in range(Store.MAX_PIGS):
            name_base = random.choice(names)
            name = f"{name_base}-{random.randint(100, 999)}"
            
            # Create pig using the class from breeding.py
            pig = GuineaPig(name=name)
            
            # Assign a random price/score if the class doesn't have it
            if not hasattr(pig, 'score'):
                pig.score = random.randint(50, 500)
                
            self.pigs_for_sale.append(pig)
            
        self.last_refresh_time = time.time()

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

    def buy_guinea_pig(self, player: PlayerInventory, pig_index: int) -> bool:
        self.check_refresh_timer()
        
        if pig_index < 0 or pig_index >= len(self.pigs_for_sale):
            return False
            
        pig = self.pigs_for_sale[pig_index]
        # Ensure pig has a score/price
        price = getattr(pig, 'score', 200) 
        
        if player.coins < price:
            return False
            
        player.coins -= price
        player.owned_pigs.append(pig)
        del self.pigs_for_sale[pig_index]
        return True

    def sell_guinea_pig(self, player: PlayerInventory, pig_index: int) -> bool:
        """Sell a guinea pig from player's inventory by index."""
        if pig_index < 0 or pig_index >= len(player.owned_pigs):
            return False
            
        pig = player.owned_pigs[pig_index]
        price = getattr(pig, 'score', 100)
        sell_price = math.floor(price * 0.75)
        
        player.coins += sell_price
        del player.owned_pigs[pig_index]
        return True

    def buy_food(self, player: PlayerInventory, item_name: str, qty: int = 1) -> bool:
        if item_name not in self.food_catalog:
            return False
            
        item = self.food_catalog[item_name]
        total_price = item.price * qty
        
        if player.coins < total_price:
            return False
            
        player.coins -= total_price
        player.add_food(item_name, qty)
        return True

# --- INITIALIZATION HELPER ---
def store_init():
    return Store()