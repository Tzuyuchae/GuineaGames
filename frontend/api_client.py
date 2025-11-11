"""
Guinea Games API Client
A comprehensive client for interacting with the Guinea Games FastAPI backend.

Usage:
    from api_client import api

    # Create a user
    user = api.create_user("john_doe", "john@example.com", "password123")

    # Create a pet
    pet = api.create_pet(user['user_id'], "Fluffy", "brown")

    # Get marketplace valuation
    valuation = api.get_pet_valuation(pet['pet_id'])
"""

import requests
from typing import Optional, Dict, List, Any
from datetime import datetime


class APIClient:
    """Singleton API client for Guinea Games backend."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the API client.

        Args:
            base_url: Base URL of the backend API (default: http://localhost:8000)
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a GET request to the API.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            requests.RequestException: If request fails
        """
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Cannot connect to backend at {self.base_url}. Is the server running?")
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request to {endpoint} timed out")
        except requests.exceptions.HTTPError as e:
            error_detail = "Unknown error"
            try:
                error_detail = response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            raise Exception(f"HTTP {response.status_code}: {error_detail}")

    def _post(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a POST request to the API.

        Args:
            endpoint: API endpoint path
            data: Form data
            json: JSON data

        Returns:
            JSON response as dictionary

        Raises:
            requests.RequestException: If request fails
        """
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.post(url, data=data, json=json, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Cannot connect to backend at {self.base_url}. Is the server running?")
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request to {endpoint} timed out")
        except requests.exceptions.HTTPError as e:
            error_detail = "Unknown error"
            try:
                error_detail = response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            raise Exception(f"HTTP {response.status_code}: {error_detail}")

    def _put(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a PUT request to the API.

        Args:
            endpoint: API endpoint path
            data: Form data
            json: JSON data

        Returns:
            JSON response as dictionary

        Raises:
            requests.RequestException: If request fails
        """
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.put(url, data=data, json=json, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Cannot connect to backend at {self.base_url}. Is the server running?")
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request to {endpoint} timed out")
        except requests.exceptions.HTTPError as e:
            error_detail = "Unknown error"
            try:
                error_detail = response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            raise Exception(f"HTTP {response.status_code}: {error_detail}")

    def _delete(self, endpoint: str) -> Dict[str, Any]:
        """
        Make a DELETE request to the API.

        Args:
            endpoint: API endpoint path

        Returns:
            JSON response as dictionary

        Raises:
            requests.RequestException: If request fails
        """
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.delete(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Cannot connect to backend at {self.base_url}. Is the server running?")
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request to {endpoint} timed out")
        except requests.exceptions.HTTPError as e:
            error_detail = "Unknown error"
            try:
                error_detail = response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            raise Exception(f"HTTP {response.status_code}: {error_detail}")

    # ==================== USER ENDPOINTS ====================

    def create_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """
        Create a new user.

        Args:
            username: User's username
            email: User's email address
            password: User's password (will be hashed by backend)

        Returns:
            Dictionary containing user data with user_id

        Example:
            user = api.create_user("john_doe", "john@example.com", "password123")
            print(user['user_id'])
        """
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        return self._post("/users/", json=data)

    def get_users(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get list of all users.

        Args:
            skip: Number of users to skip (for pagination)
            limit: Maximum number of users to return

        Returns:
            List of user dictionaries
        """
        params = {"skip": skip, "limit": limit}
        return self._get("/users/", params=params)

    def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        Get a specific user by ID.

        Args:
            user_id: ID of the user

        Returns:
            User dictionary
        """
        return self._get(f"/users/{user_id}")

    # ==================== PET ENDPOINTS ====================

    def create_pet(self, user_id: int, name: str, color: str) -> Dict[str, Any]:
        """
        Create a new pet for a user.

        Args:
            user_id: ID of the pet owner
            name: Pet's name
            color: Pet's color

        Returns:
            Dictionary containing pet data with pet_id

        Example:
            pet = api.create_pet(1, "Fluffy", "brown")
            print(pet['pet_id'])
        """
        data = {
            "user_id": user_id,
            "name": name,
            "color": color
        }
        return self._post("/pets/", json=data)

    def get_pets(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get list of all pets.

        Args:
            skip: Number of pets to skip (for pagination)
            limit: Maximum number of pets to return

        Returns:
            List of pet dictionaries
        """
        params = {"skip": skip, "limit": limit}
        return self._get("/pets/", params=params)

    def get_user_pets(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all pets owned by a specific user.

        Args:
            user_id: ID of the user

        Returns:
            List of pet dictionaries
        """
        return self._get(f"/pets/user/{user_id}")

    def get_pet(self, pet_id: int) -> Dict[str, Any]:
        """
        Get a specific pet by ID.

        Args:
            pet_id: ID of the pet

        Returns:
            Pet dictionary with all stats
        """
        return self._get(f"/pets/{pet_id}")

    def update_pet(self, pet_id: int, **kwargs) -> Dict[str, Any]:
        """
        Update pet attributes.

        Args:
            pet_id: ID of the pet
            **kwargs: Pet attributes to update (name, health, happiness, hunger, cleanliness)

        Returns:
            Updated pet dictionary

        Example:
            api.update_pet(1, health=100, happiness=95)
        """
        return self._put(f"/pets/{pet_id}", json=kwargs)

    def delete_pet(self, pet_id: int) -> Dict[str, Any]:
        """
        Delete a pet.

        Args:
            pet_id: ID of the pet to delete

        Returns:
            Success message
        """
        return self._delete(f"/pets/{pet_id}")

    def feed_pet(self, pet_id: int, food_item_id: int) -> Dict[str, Any]:
        """
        Feed a pet with a food item.

        Args:
            pet_id: ID of the pet
            food_item_id: ID of the food item from inventory

        Returns:
            Updated pet dictionary
        """
        data = {"food_item_id": food_item_id}
        return self._post(f"/pets/{pet_id}/feed", json=data)

    # ==================== INVENTORY ENDPOINTS ====================

    def add_inventory_item(self, user_id: int, item_name: str, item_type: str, quantity: int = 1) -> Dict[str, Any]:
        """
        Add an item to user's inventory.

        Args:
            user_id: ID of the user
            item_name: Name of the item
            item_type: Type of item (food, toy, accessory, etc.)
            quantity: Number of items to add

        Returns:
            Inventory item dictionary
        """
        data = {
            "user_id": user_id,
            "item_name": item_name,
            "item_type": item_type,
            "quantity": quantity
        }
        return self._post("/inventory/", json=data)

    def get_user_inventory(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all items in user's inventory.

        Args:
            user_id: ID of the user

        Returns:
            List of inventory item dictionaries
        """
        return self._get(f"/inventory/user/{user_id}")

    def update_inventory_item(self, inventory_id: int, quantity: int) -> Dict[str, Any]:
        """
        Update quantity of an inventory item.

        Args:
            inventory_id: ID of the inventory item
            quantity: New quantity

        Returns:
            Updated inventory item dictionary
        """
        data = {"quantity": quantity}
        return self._put(f"/inventory/{inventory_id}", json=data)

    # ==================== TRANSACTION ENDPOINTS ====================

    def create_transaction(self, user_id: int, transaction_type: str, amount: int,
                          description: str = "") -> Dict[str, Any]:
        """
        Create a new transaction.

        Args:
            user_id: ID of the user
            transaction_type: Type of transaction (purchase, sale, reward, etc.)
            amount: Transaction amount (positive or negative)
            description: Optional description

        Returns:
            Transaction dictionary
        """
        data = {
            "user_id": user_id,
            "transaction_type": transaction_type,
            "amount": amount,
            "description": description
        }
        return self._post("/transactions/", json=data)

    def get_user_transactions(self, user_id: int, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get transaction history for a user.

        Args:
            user_id: ID of the user
            skip: Number of transactions to skip
            limit: Maximum number of transactions to return

        Returns:
            List of transaction dictionaries
        """
        params = {"skip": skip, "limit": limit}
        return self._get(f"/transactions/user/{user_id}", params=params)

    def get_transactions_by_type(self, transaction_type: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get all transactions of a specific type.

        Args:
            transaction_type: Type of transaction to filter by
            skip: Number of transactions to skip
            limit: Maximum number of transactions to return

        Returns:
            List of transaction dictionaries
        """
        params = {"skip": skip, "limit": limit}
        return self._get(f"/transactions/type/{transaction_type}", params=params)

    # ==================== LEADERBOARD ENDPOINTS ====================

    def get_leaderboard(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the global leaderboard.

        Args:
            skip: Number of entries to skip
            limit: Maximum number of entries to return

        Returns:
            List of leaderboard entries with user data
        """
        params = {"skip": skip, "limit": limit}
        return self._get("/leaderboard/", params=params)

    def get_user_rank(self, user_id: int) -> Dict[str, Any]:
        """
        Get a user's rank on the leaderboard.

        Args:
            user_id: ID of the user

        Returns:
            Dictionary with user rank and score
        """
        return self._get(f"/leaderboard/user/{user_id}")

    def update_user_score(self, user_id: int, score: int) -> Dict[str, Any]:
        """
        Update a user's leaderboard score.

        Args:
            user_id: ID of the user
            score: New score

        Returns:
            Updated leaderboard entry
        """
        data = {"score": score}
        return self._post(f"/leaderboard/user/{user_id}", json=data)

    # ==================== MINI-GAME ENDPOINTS ====================

    def get_mini_games(self) -> List[Dict[str, Any]]:
        """
        Get list of all mini-games.

        Returns:
            List of mini-game dictionaries
        """
        return self._get("/mini-games/")

    def create_mini_game(self, name: str, description: str, reward_coins: int) -> Dict[str, Any]:
        """
        Create a new mini-game.

        Args:
            name: Name of the mini-game
            description: Description of the mini-game
            reward_coins: Coins rewarded for completing the game

        Returns:
            Mini-game dictionary
        """
        data = {
            "name": name,
            "description": description,
            "reward_coins": reward_coins
        }
        return self._post("/mini-games/", json=data)

    # ==================== MARKETPLACE ENDPOINTS ====================

    def get_pet_valuation(self, pet_id: int) -> Dict[str, Any]:
        """
        Get AI-calculated valuation for a pet based on genetics.

        Args:
            pet_id: ID of the pet

        Returns:
            Dictionary with base_price, genetics_multiplier, final_price, and breakdown

        Example:
            valuation = api.get_pet_valuation(1)
            print(f"Pet worth: {valuation['final_price']} coins")
            print(f"Genetics multiplier: {valuation['genetics_multiplier']}x")
        """
        return self._get(f"/marketplace/valuation/{pet_id}")

    def list_pet_for_sale(self, pet_id: int, asking_price: int) -> Dict[str, Any]:
        """
        List a pet for sale on the marketplace.

        Args:
            pet_id: ID of the pet
            asking_price: Price in coins

        Returns:
            Marketplace listing dictionary
        """
        data = {"asking_price": asking_price}
        return self._post(f"/marketplace/list/{pet_id}", json=data)

    def unlist_pet(self, pet_id: int) -> Dict[str, Any]:
        """
        Remove a pet from the marketplace.

        Args:
            pet_id: ID of the pet

        Returns:
            Success message
        """
        return self._post(f"/marketplace/unlist/{pet_id}")

    def buy_pet(self, pet_id: int, buyer_id: int) -> Dict[str, Any]:
        """
        Purchase a pet from the marketplace.

        Args:
            pet_id: ID of the pet to purchase
            buyer_id: ID of the buyer

        Returns:
            Transaction dictionary
        """
        data = {"buyer_id": buyer_id}
        return self._post(f"/marketplace/purchase/{pet_id}", json=data)

    def browse_marketplace(self, min_price: Optional[int] = None, max_price: Optional[int] = None,
                          color: Optional[str] = None, sort_by: str = "price_asc",
                          skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Browse pets for sale on the marketplace with filters.

        Args:
            min_price: Minimum price filter
            max_price: Maximum price filter
            color: Color filter
            sort_by: Sort order (price_asc, price_desc, newest, genetics_high, genetics_low)
            skip: Number of listings to skip
            limit: Maximum number of listings to return

        Returns:
            List of marketplace listing dictionaries

        Example:
            # Get expensive brown pets
            listings = api.browse_marketplace(min_price=5000, color="brown", sort_by="price_desc")
        """
        params = {
            "skip": skip,
            "limit": limit,
            "sort_by": sort_by
        }
        if min_price is not None:
            params["min_price"] = min_price
        if max_price is not None:
            params["max_price"] = max_price
        if color is not None:
            params["color"] = color

        return self._get("/marketplace/browse", params=params)

    def get_user_portfolio(self, user_id: int) -> Dict[str, Any]:
        """
        Get user's portfolio summary including total pet value.

        Args:
            user_id: ID of the user

        Returns:
            Dictionary with total_pets, total_value, average_value, and pet list

        Example:
            portfolio = api.get_user_portfolio(1)
            print(f"Total portfolio value: {portfolio['total_value']} coins")
        """
        return self._get(f"/marketplace/portfolio/{user_id}")

    # ==================== GENETICS/BREEDING ENDPOINTS ====================

    def get_genes(self) -> List[Dict[str, Any]]:
        """
        Get list of all available genes.

        Returns:
            List of gene dictionaries with name, trait, and dominance
        """
        return self._get("/genetics/genes/")

    def get_gene(self, gene_id: int) -> Dict[str, Any]:
        """
        Get details of a specific gene.

        Args:
            gene_id: ID of the gene

        Returns:
            Gene dictionary
        """
        return self._get(f"/genetics/genes/{gene_id}")

    def get_pet_genetics(self, pet_id: int) -> List[Dict[str, Any]]:
        """
        Get genetic makeup of a pet.

        Args:
            pet_id: ID of the pet

        Returns:
            List of pet genetics (allele pairs) with gene information
        """
        return self._get(f"/genetics/pet-genetics/{pet_id}")

    def breed_pets(self, parent1_id: int, parent2_id: int,
                   offspring_name: str, offspring_color: str) -> Dict[str, Any]:
        """
        Breed two pets to create offspring with inherited genetics.

        Args:
            parent1_id: ID of first parent
            parent2_id: ID of second parent
            offspring_name: Name for the offspring
            offspring_color: Color for the offspring

        Returns:
            Dictionary with offspring pet data and inherited genetics

        Example:
            offspring = api.breed_pets(1, 2, "Baby Fluffy", "brown")
            print(f"New pet ID: {offspring['pet_id']}")
            print(f"Inherited genes: {offspring['genetics']}")
        """
        data = {
            "parent1_id": parent1_id,
            "parent2_id": parent2_id,
            "offspring_name": offspring_name,
            "offspring_color": offspring_color
        }
        return self._post("/genetics/breed/", json=data)

    def get_breeding_history(self, pet_id: int) -> Dict[str, Any]:
        """
        Get breeding history of a pet (parents and offspring).

        Args:
            pet_id: ID of the pet

        Returns:
            Dictionary with parents, offspring, and generation info
        """
        return self._get(f"/genetics/breeding-history/{pet_id}")

    def calculate_punnett_square(self, parent1_id: int, parent2_id: int,
                                gene_id: int) -> Dict[str, Any]:
        """
        Calculate Punnett square for a specific gene from two parents.

        Args:
            parent1_id: ID of first parent
            parent2_id: ID of second parent
            gene_id: ID of the gene to analyze

        Returns:
            Dictionary with Punnett square grid and probability percentages

        Example:
            punnett = api.calculate_punnett_square(1, 2, 1)
            print(punnett['probabilities'])  # {'AA': 25, 'Aa': 50, 'aa': 25}
        """
        return self._get(f"/genetics/punnett-square/{parent1_id}/{parent2_id}/{gene_id}")

    def get_pet_stats(self, pet_id: int) -> Dict[str, Any]:
        """
        Get calculated stats for a pet based on genetics.

        Args:
            pet_id: ID of the pet

        Returns:
            Dictionary with speed, strength, intelligence, cuteness scores
        """
        return self._get(f"/genetics/pet-stats/{pet_id}")

    def compare_pets(self, pet1_id: int, pet2_id: int) -> Dict[str, Any]:
        """
        Compare stats of two pets side by side.

        Args:
            pet1_id: ID of first pet
            pet2_id: ID of second pet

        Returns:
            Dictionary with both pets' stats and comparison

        Example:
            comparison = api.compare_pets(1, 2)
            print(f"Pet 1 speed: {comparison['pet1_stats']['speed']}")
            print(f"Pet 2 speed: {comparison['pet2_stats']['speed']}")
        """
        return self._get(f"/genetics/compare-stats/{pet1_id}/{pet2_id}")

    def check_connection(self) -> bool:
        """
        Check if the backend API is reachable.

        Returns:
            True if connected, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/docs", timeout=2)
            return response.status_code == 200
        except:
            return False


# Singleton instance
api = APIClient()
