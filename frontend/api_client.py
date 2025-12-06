import requests
from typing import Optional, Dict, List, Any

class APIClient:
    """Singleton API client for Guinea Games backend."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API GET Error [{endpoint}]: {e}")
            raise e

    def _post(self, endpoint: str, json: Optional[Dict] = None) -> Any:
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.post(url, json=json, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API POST Error [{endpoint}]: {e}")
            raise e

    def _delete(self, endpoint: str) -> Any:
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.delete(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API DELETE Error [{endpoint}]: {e}")
            raise e

    # --- USER ---
    def get_user(self, user_id: int):
        return self._get(f"/users/{user_id}")

    def create_user(self, username, email, password):
        return self._post("/users/", json={"username": username, "email": email, "password": password})

    # --- PETS ---
    def get_user_pets(self, user_id: int):
        return self._get(f"/pets/owner/{user_id}")

    def create_pet(self, owner_id, name, species, color, **kwargs):
        """
        Creates a new pet. 
        Accepts **kwargs to pass extra stats (speed, endurance, etc.) 
        if the backend supports them.
        """
        data = {
            "owner_id": owner_id, 
            "name": name, 
            "species": species, 
            "color": color
        }
        # Add any extra stats (speed, endurance, market_value) to the payload
        data.update(kwargs)
        
        return self._post("/pets/", json=data)

    def update_pet(self, pet_id, **kwargs):
        # Used for renaming or updating stats
        return self.session.put(f"{self.base_url}/pets/{pet_id}", json=kwargs).json()

    def delete_pet(self, pet_id: int):
        return self._delete(f"/pets/{pet_id}")

    # --- INVENTORY ---
    def get_user_inventory(self, user_id: int):
        return self._get(f"/inventory/{user_id}")

    def add_inventory_item(self, user_id, item_name, item_type, quantity=1):
        return self._post("/inventory/", json={"user_id": user_id, "item_name": item_name, "quantity": quantity})

    def create_transaction(self, user_id, t_type, amount, desc):
        return self._post("/transactions/", json={"user_id": user_id, "type": t_type, "amount": amount, "description": desc})

    # --- MARKETPLACE ---
    def browse_marketplace(self, limit=10):
        return self._get("/marketplace/listings", params={"limit": limit})
    
    def get_pet_valuation(self, pet_id):
        return self._get(f"/marketplace/valuation/{pet_id}")
    
    def buy_pet(self, pet_id, buyer_id):
        return self._post(f"/marketplace/purchase/{pet_id}", params={"buyer_id": buyer_id})

    # --- GENETICS / BREEDING ---
    def breed_pets(self, parent1_id, parent2_id, child_name, owner_id):
        data = {
            "parent1_id": parent1_id,
            "parent2_id": parent2_id,
            "child_name": child_name,
            "child_species": "Guinea Pig",
            "child_color": "Mixed", 
            "owner_id": owner_id
        }
        return self._post("/genetics/breed", json=data)

    def check_connection(self) -> bool:
        try:
            self.session.get(f"{self.base_url}/", timeout=1)
            return True
        except:
            return False

    # [Insert into APIClient class]

    def feed_pet(self, pet_id: int, item_name: str):
        """Feed a specific pet with an item from inventory."""
        return self._post(f"/pets/{pet_id}/feed", json={"item_name": item_name})

    def trigger_daily_decay(self, user_id: int):
        """Trigger hunger increase and health decrease for a user's pets."""
        return self._post(f"/pets/decay/{user_id}")

api = APIClient()