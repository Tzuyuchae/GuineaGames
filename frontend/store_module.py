"""
store_module.py

Backend-integrated store + inventory for Guinea Games.
- Uses FastAPI backend for pets / genetics where possible
- Uses local JSON save (save_data.json) for robust persistence of:
  - coins
  - items
  - pigs
  - game time
"""

import time
import random
import math
import json
import os
from typing import List, Dict
from datetime import datetime

from api_client import api

# Single backend status check for the whole module
BACKEND_ONLINE = api.check_connection()
if BACKEND_ONLINE:
    print("[Backend] Online - API reachable at startup.")
else:
    print("[Backend] Offline - running in local-save-only mode.")


try:
    from breeding import GuineaPig
except ImportError:
    # Minimal fallback if breeding module isn't available
    import uuid

    class GuineaPig:
        def __init__(self, name, score=None, **kwargs):
            """
            Fallback GuineaPig that ignores extra kwargs like birth_game_minutes.
            This keeps store_module resilient even if breeding.py is missing.
            """
            self.name = name
            self.score = score if score else random.randint(50, 500)
            self.id = str(uuid.uuid4())
            self.speed = 50
            self.endurance = 50
            self.backend_id = None
            self.birth_time = datetime.now()
            # Optional field so save/load of birth_game_minutes doesn't break
            self.birth_game_minutes = kwargs.get("birth_game_minutes", 0)

        def get_age_stage(self):
            return "Adult"

        def calculate_sell_price(self):
            return self.score


# ============================================================
# ------------------------- FOOD MODEL ------------------------
# ============================================================

class FoodItem:
    def __init__(self, name: str, price: int, hunger_boost: int,
                 duration_minutes: int, effect_type: str):
        self.name = name
        self.price = price
        self.hunger_boost = hunger_boost
        self.duration_minutes = duration_minutes
        self.effect_type = effect_type

    def __repr__(self):
        return f"FoodItem(name={self.name!r}, price={self.price})"


# ============================================================
# -------------------- PLAYER INVENTORY -----------------------
# ============================================================

class PlayerInventory:
    """
    Persistent player inventory:
        - coins
        - food/items
        - owned pigs

    Uses:
        - Local JSON save file (save_data.json) if present
        - Otherwise, if backend is online, tries to load from API
        - Otherwise uses constructor defaults
    """

    def __init__(self, user_id=1, coins: int = None, food: int = None):
        # Coerce user_id to int; if anything weird, fall back to 1
        try:
            uid = int(user_id)
        except (ValueError, TypeError):
            print(f"[Inventory] Invalid user_id={user_id!r}, defaulting to 1")
            uid = 1
        self.user_id = uid

        # Local baseline values
        self.coins = coins if coins is not None else 0
        self.food = food if food is not None else 0
        self.items: Dict[str, int] = {}
        self.owned_pigs: List[GuineaPig] = []

        # Saved game_time (if loaded from file)
        self.saved_game_time = None

        # 1) Try local save first
        used_save = self._load_local_save("save_data.json")
        if used_save:
            print("[Inventory] Loaded from local save file.")
        else:
            # 2) If no save, try backend (only if we know it's online)
            self._safe_load_backend_data()

    # ---------------------------------------------------------
    # Local JSON save / load
    # ---------------------------------------------------------
    def _load_local_save(self, path: str) -> bool:
        if not os.path.exists(path):
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[Inventory] Failed to read save file: {e}")
            return False

        try:
            self.coins = int(data.get("coins", self.coins))
        except Exception:
            pass
        self.food = int(data.get("food", self.food))
        self.items = data.get("items", {})

        # Load pigs
        self.owned_pigs = []
        for p in data.get("pigs", []):
            name = p.get("name", "Unnamed")
            score = p.get("score")

            # NEW: restore birth_game_minutes for game-time-based aging
            birth_game_minutes = p.get("birth_game_minutes", 0)

            # Construct GuineaPig with game-time birth
            gp = GuineaPig(
                name=name,
                score=score,
                birth_game_minutes=birth_game_minutes,
            )

            # Restore genes & phenotype
            genes = p.get("genes")
            color = p.get("color")
            if genes:
                gp.genes = genes
                gp.phenotype = gp.calculate_phenotype()
            if color:
                gp.phenotype["coat_color"] = color

            gp.backend_id = p.get("backend_id")
            self.owned_pigs.append(gp)

        # Store game_time for main.py to apply to homescreen
        self.saved_game_time = data.get("game_time")

        return True

    def save_to_file(self, path: str = "save_data.json", game_time: Dict = None):
        """
        Save current inventory, pigs, and optional game_time to a JSON file.
        """
        try:
            pigs_data = []
            for p in self.owned_pigs:
                phenotype = getattr(p, "phenotype", {}) or {}
                pigs_data.append({
                    "name": getattr(p, "name", "Unnamed"),
                    "score": getattr(p, "score", None),
                    "backend_id": getattr(p, "backend_id", None),
                    "color": phenotype.get("coat_color"),
                    "genes": getattr(p, "genes", None),
                    # NEW: persist game-time birth so age is stable across sessions
                    "birth_game_minutes": getattr(p, "birth_game_minutes", 0),
                })

            data = {
                "coins": self.coins,
                "food": self.food,
                "items": self.items,
                "pigs": pigs_data,
                "game_time": game_time,
            }

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print("[Inventory] Saved game state to", path)
        except Exception as e:
            print(f"[Inventory] Failed to save game state: {e}")

    # ---------------------------------------------------------
    # Backend loading wrapper (inventory + pigs + coins)
    # ---------------------------------------------------------
    def _safe_load_backend_data(self):
        if not BACKEND_ONLINE:
            # If backend isn't reachable at all, don't even try endpoints.
            print("[Inventory] Backend offline; using local defaults (no save file).")
            return

        # Inventory items
        try:
            self._load_backend_inventory()
        except Exception:
            print("[Inventory] Backend inventory not available; using local items.")

        # Pigs
        try:
            self._load_backend_pigs()
        except Exception:
            print("[Inventory] Backend pigs not available; starting with local pigs.")

        # Coins
        try:
            self._load_backend_coins()
        except Exception:
            print("[Inventory] Backend transactions not available; using local coins.")

    # ---------------------------------------------------------
    # Load inventory items (food, accessories)
    # ---------------------------------------------------------
    def _load_backend_inventory(self):
        inventory = api.get_user_inventory(self.user_id)
        for item in inventory:
            name = item["item_name"]
            qty = item["quantity"]

            self.items[name] = qty
            if name in ["Banana", "Carrot"]:
                self.food += qty

        print(f"[Inventory] Loaded items from backend: {self.items}")

    # ---------------------------------------------------------
    # Load pigs owned by the user
    # ---------------------------------------------------------
    def _load_backend_pigs(self):
        pets = api.get_user_pets(self.user_id)
        print(f"[Inventory] Loaded {len(pets)} pigs from backend")

        for pet in pets:
            gp = self._convert_backend_pet(pet)
            self.owned_pigs.append(gp)

    def _convert_backend_pet(self, pet_data: Dict) -> GuineaPig:
        """
        Convert backend pet → GuineaPig object.
        Also attempts to pull genetics & recalc phenotype.
        """
        name = pet_data.get("name", "Unnamed")
        color = pet_data.get("color", "Brown")
        pet_id = pet_data.get("pet_id")

        # Backend pigs are treated as "already existing" in game time.
        # You could set birth_game_minutes here if you want them young/old
        # relative to current saved_game_time. For now, default 0.
        gp = GuineaPig(name=name)

        gp.backend_id = pet_id

        # Base coat color from backend
        gp.phenotype["coat_color"] = color
        gp.birth_time = datetime.now()

        # Try to load genetics
        try:
            genetics_list = api.get_pet_genetics(pet_id)
            # genetics_list: [ {"gene": "...", "alleles": ["A","a"]}, ... ]
            converted = {}
            for g in genetics_list:
                gene_name = g["gene"]
                alleles = g["alleles"]
                sorted_alleles = sorted(alleles, reverse=True)
                converted[gene_name] = sorted_alleles

            gp.genes = converted
            gp.phenotype = gp.calculate_phenotype()
        except Exception as e:
            print(f"[Inventory] Failed to load genetics for pet {pet_id}: {e}")
            # keep fallback local genes

        return gp

    # ---------------------------------------------------------
    # Load coin balance based on backend transaction ledger
    # ---------------------------------------------------------
    def _load_backend_coins(self):
        txs = api.get_user_transactions(self.user_id, limit=500)
        balance = 0
        for tx in txs:
            balance += tx.get("amount", 0)
        self.coins = max(0, balance)
        print(f"[Inventory] Loaded coin balance from backend: {self.coins}")

    # ---------------------------------------------------------
    # Coin helpers (local-only to avoid backend schema mismatch)
    # ---------------------------------------------------------
    def add_coins(self, amount: int):
        self.coins += amount

    def remove_coins(self, amount: int) -> bool:
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False

    # ---------------------------------------------------------
    # Food helpers
    # ---------------------------------------------------------
    def add_food(self, item_name: str, qty: int = 1):
        self.items[item_name] = self.items.get(item_name, 0) + qty
        if item_name in ["Banana", "Carrot"]:
            self.food += qty
        # Best-effort call to backend; ignore failures completely
        if BACKEND_ONLINE:
            try:
                api.add_inventory_item(self.user_id, item_name, "food", qty)
            except Exception:
                pass

    def remove_food(self, item_name: str, qty: int = 1) -> bool:
        if self.items.get(item_name, 0) >= qty:
            self.items[item_name] -= qty
            if item_name in ["Banana", "Carrot"]:
                self.food = max(0, self.food - qty)
            if self.items[item_name] == 0:
                del self.items[item_name]
            return True
        return False


# ============================================================
# ---------------------- STORE SYSTEM -------------------------
# ============================================================

class Store:
    REFRESH_SECONDS = 30 * 60
    MAX_PIGS = 3

    def __init__(self, user_id: int = 1):
        self.user_id = user_id
        self.pigs_for_sale: List[GuineaPig] = []
        self.last_refresh_time: float = 0.0
        self.food_catalog: Dict[str, FoodItem] = {}

        self._init_food_catalog()
        self.generate_new_pigs()

    # ---------------------------------------------------------
    def _init_food_catalog(self):
        self.food_catalog["Banana"] = FoodItem("Banana", 100, 1, 15, "HUNGER")
        self.food_catalog["Carrot"] = FoodItem("Carrot", 150, 2, 30, "HUNGER")
        self.food_catalog["Bell Pepper"] = FoodItem("Bell Pepper", 200, 0, 0, "SPEED")
        self.food_catalog["Cabbage"] = FoodItem("Cabbage", 250, 0, 0, "ENDURANCE")

    # ---------------------------------------------------------
    def check_refresh_timer(self):
        if time.time() - self.last_refresh_time >= Store.REFRESH_SECONDS:
            self.generate_new_pigs()

    # ---------------------------------------------------------
    def generate_new_pigs(self):
        names = ["Nibbles", "Cocoa", "Buttons", "Poppy",
                 "Widget", "Pebble", "Mango", "Daisy"]

        self.pigs_for_sale = []

        for _ in range(Store.MAX_PIGS):
            base = random.choice(names)
            name = f"{base}-{random.randint(100, 999)}"
            score = random.randint(120, 350)

            pig = GuineaPig(name=name, score=score)
            pig.birth_time = datetime.now()
            self.pigs_for_sale.append(pig)

        self.last_refresh_time = time.time()

    # ---------------------------------------------------------
    def get_time_until_refresh(self) -> int:
        elapsed = int(time.time() - self.last_refresh_time)
        return max(0, Store.REFRESH_SECONDS - elapsed)

    # This is what store_page.store_draw needs
    def _format_time(self, seconds: int) -> str:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    # ---------------------------------------------------------
    def buy_guinea_pig(self, player: PlayerInventory, pig_index: int) -> bool:
        self.check_refresh_timer()

        if pig_index < 0 or pig_index >= len(self.pigs_for_sale):
            return False

        pig = self.pigs_for_sale[pig_index]
        price = getattr(pig, "score", 200)

        if not player.remove_coins(price):
            return False

        # Persist pig to backend; best-effort
        if BACKEND_ONLINE:
            try:
                resp = api.create_pet(
                    owner_id=player.user_id,
                    name=pig.name,
                    species="guinea_pig",
                    color=pig.phenotype.get("coat_color", "Brown"),
                )
                pig.backend_id = resp.get("pet_id")
            except Exception as e:
                print(f"[Store] Backend save failed but purchase continues: {e}")

        player.owned_pigs.append(pig)
        del self.pigs_for_sale[pig_index]
        return True

    # ---------------------------------------------------------
    def sell_guinea_pig(self, player: PlayerInventory, pig_index: int) -> bool:
        if pig_index < 0 or pig_index >= len(player.owned_pigs):
            return False

        pig = player.owned_pigs[pig_index]

        if hasattr(pig, "get_age_stage") and pig.get_age_stage() != "Adult":
            # cannot sell babies
            return False

        if hasattr(pig, "calculate_sell_price"):
            price = pig.calculate_sell_price()
        else:
            price = math.floor(getattr(pig, "score", 100) * 0.7)

        player.add_coins(price)

        # Try to delete from backend if we know its id
        if BACKEND_ONLINE and getattr(pig, "backend_id", None):
            try:
                api.delete_pet(pig.backend_id)
            except Exception as e:
                print(f"[Store] Backend delete failed (non-fatal): {e}")

        del player.owned_pigs[pig_index]
        return True

    # ---------------------------------------------------------
    def buy_food(self, player: PlayerInventory, item_name: str, qty: int = 1) -> bool:
        if item_name not in self.food_catalog:
            return False

        item = self.food_catalog[item_name]
        total_cost = item.price * qty

        if not player.remove_coins(total_cost):
            return False

        player.add_food(item_name, qty)
        return True


# ============================================================
def store_init(user_id: int = 1):
    """
    Entry point used by store_page.py.
    """
    return Store(user_id=user_id)
