"""
store_module.py

Implementation of the "Guinea Games Store".
Integrates with breeding.py to ensure purchased pigs have genetics.
"""
import time
import random
import math
from typing import List, Dict

try:
    from breeding import GuineaPig
except ImportError:
    import uuid
    class GuineaPig:
        def __init__(self, name, score=None):
            self.name = name
            self.score = score if score else random.randint(50, 500)
            self.id = str(uuid.uuid4())
            self.speed = 50
            self.endurance = 50
        def get_age_stage(self): return 'Adult'
        def calculate_sell_price(self): return self.score

# ------------------------- Data Models -------------------------

class FoodItem:
    def __init__(self, name: str, price: int, hunger_boost: int, duration_minutes: int, effect_type: str):
        self.name = name
        self.price = price
        self.hunger_boost = hunger_boost
        self.duration_minutes = duration_minutes
        self.effect_type = effect_type

    def __repr__(self):
        return f"FoodItem(name={self.name!r}, price={self.price})"


class PlayerInventory:
    def __init__(self, coins: int = 0, food: int = 5):
        self.coins = coins
        self.food = food 
        self.owned_pigs: List[GuineaPig] = []
        self.items: Dict[str, int] = {}

    def add_food(self, item_name: str, qty: int = 1):
        if item_name in ['Banana', 'Carrot']:
            self.food += qty
        self.items[item_name] = self.items.get(item_name, 0) + qty

    def remove_food(self, item_name: str, qty: int = 1):
        if self.items.get(item_name, 0) >= qty:
            self.items[item_name] -= qty
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
    REFRESH_SECONDS = 30 * 60  # 30 minutes
    MAX_PIGS = 3

    def __init__(self):
        self.pigs_for_sale: List[GuineaPig] = []
        self.last_refresh_time: float = 0.0
        self.food_catalog: Dict[str, FoodItem] = {}
        self._init_food_catalog()
        self.generate_new_pigs()

    def _init_food_catalog(self):
        self.food_catalog['Banana'] = FoodItem('Banana', 100, 1, 15, 'HUNGER')
        self.food_catalog['Carrot'] = FoodItem('Carrot', 150, 2, 30, 'HUNGER')
        self.food_catalog['Bell Pepper'] = FoodItem('Bell Pepper', 200, 0, 0, 'SPEED')
        self.food_catalog['Cabbage'] = FoodItem('Cabbage', 250, 0, 0, 'ENDURANCE')

    def check_refresh_timer(self):
        now = time.time()
        if (now - self.last_refresh_time) >= Store.REFRESH_SECONDS:
            self.generate_new_pigs()

    def generate_new_pigs(self):
        names = ['Nibbles', 'Cocoa', 'Buttons', 'Poppy', 'Widget', 'Pebble', 'Mango', 'Daisy']
        self.pigs_for_sale = []
        
        for _ in range(Store.MAX_PIGS):
            name_base = random.choice(names)
            name = f"{name_base}-{random.randint(100, 999)}"
            
            # Create pig using the class from breeding.py
            # Random score for buying price
            buy_score = random.randint(100, 300)
            pig = GuineaPig(name=name, score=buy_score)
                
            self.pigs_for_sale.append(pig)
            
        self.last_refresh_time = time.time()

    def get_time_until_refresh(self) -> int:
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
        price = getattr(pig, 'score', 200) 
        
        if player.coins < price:
            return False
            
        player.coins -= price
        # Reset birth time so they aren't instantly adults when bought? 
        # Or keep them as is? Let's reset to simulate adoption.
        if hasattr(pig, 'birth_time'):
             from datetime import datetime
             pig.birth_time = datetime.now()
             
        player.owned_pigs.append(pig)
        del self.pigs_for_sale[pig_index]
        return True

    def sell_guinea_pig(self, player: PlayerInventory, pig_index: int) -> bool:
        """Sell a guinea pig from player's inventory by index."""
        if pig_index < 0 or pig_index >= len(player.owned_pigs):
            return False
            
        pig = player.owned_pigs[pig_index]
        
        # Check Age
        if hasattr(pig, 'get_age_stage'):
            if pig.get_age_stage() != 'Adult':
                return False # Cannot sell babies
        
        # Calculate dynamic price
        if hasattr(pig, 'calculate_sell_price'):
            sell_price = pig.calculate_sell_price()
        else:
            # Fallback
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

def store_init():
    return Store()