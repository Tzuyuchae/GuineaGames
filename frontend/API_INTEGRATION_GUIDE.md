# Guinea Games API Integration Guide

Complete guide for integrating the FastAPI backend with your Pygame frontend.

## Table of Contents

1. [Quick Start](#quick-start)
2. [API Client Overview](#api-client-overview)
3. [Complete Endpoint Reference](#complete-endpoint-reference)
4. [Integration Examples by Page](#integration-examples-by-page)
5. [Error Handling Patterns](#error-handling-patterns)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Prerequisites

Make sure you have the `requests` library installed:

```bash
pip install requests
```

### 2. Start the Backend

```bash
cd backend
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

### 3. Test the Connection

```bash
cd frontend
python test_api_connection.py
```

This will verify:
- Backend connection
- User creation
- Pet creation
- Marketplace valuation

### 4. Basic Usage

```python
from api_client import api

# Create a user
user = api.create_user("username", "email@example.com", "password")

# Create a pet
pet = api.create_pet(user['user_id'], "Fluffy", "brown")

# Get pet valuation
valuation = api.get_pet_valuation(pet['pet_id'])
print(f"Pet is worth {valuation['final_price']} coins")
```

---

## API Client Overview

The `api_client.py` provides a singleton instance `api` that handles all backend communication.

### Architecture

```
api_client.py
    └── APIClient class
        ├── Base methods: _get, _post, _put, _delete
        ├── User endpoints (create, get, list)
        ├── Pet endpoints (create, update, delete, feed)
        ├── Inventory endpoints (add, get, update)
        ├── Transaction endpoints (create, get history)
        ├── Leaderboard endpoints (get ranks, update scores)
        ├── Mini-game endpoints (list, create)
        ├── Marketplace endpoints (list, buy, browse, valuate)
        └── Genetics endpoints (breed, get stats, compare)
```

### Error Handling

All methods automatically handle:
- Connection errors (server offline)
- Timeout errors (slow network)
- HTTP errors (404, 500, etc.)
- JSON parsing errors

Errors are raised as Python exceptions with descriptive messages.

---

## Complete Endpoint Reference

### User Endpoints

#### Create User
```python
user = api.create_user(username, email, password)
```
- **Returns**: `{'user_id': int, 'username': str, 'email': str, ...}`
- **Raises**: Exception if username/email already exists

#### Get All Users
```python
users = api.get_users(skip=0, limit=100)
```
- **Returns**: List of user dictionaries
- **Use for**: Leaderboards, user search

#### Get Specific User
```python
user = api.get_user(user_id)
```
- **Returns**: User dictionary with balance, stats
- **Raises**: Exception if user not found

---

### Pet Endpoints

#### Create Pet
```python
pet = api.create_pet(user_id, name, color)
```
- **Returns**: `{'pet_id': int, 'name': str, 'color': str, 'health': int, ...}`
- **Note**: Initial stats (health, happiness) are set by backend

#### Get User's Pets
```python
pets = api.get_user_pets(user_id)
```
- **Returns**: List of all pets owned by user
- **Use for**: Pet selection screens, inventory display

#### Get Single Pet
```python
pet = api.get_pet(pet_id)
```
- **Returns**: Complete pet data including stats
- **Use for**: Pet detail pages, status displays

#### Update Pet
```python
updated_pet = api.update_pet(pet_id, health=100, happiness=95, hunger=20)
```
- **Parameters**: Any combination of: `name`, `health`, `happiness`, `hunger`, `cleanliness`
- **Returns**: Updated pet dictionary
- **Use for**: After feeding, playing, cleaning

#### Delete Pet
```python
result = api.delete_pet(pet_id)
```
- **Returns**: Success message
- **Use for**: Releasing/removing pets

#### Feed Pet
```python
updated_pet = api.feed_pet(pet_id, food_item_id)
```
- **Parameters**: `pet_id`, `food_item_id` (from inventory)
- **Returns**: Updated pet with increased stats
- **Note**: Decrements food item in inventory

---

### Inventory Endpoints

#### Add Item
```python
item = api.add_inventory_item(user_id, "Premium Pellets", "food", quantity=5)
```
- **Types**: `food`, `toy`, `accessory`, `medicine`
- **Returns**: Inventory item dictionary

#### Get User Inventory
```python
inventory = api.get_user_inventory(user_id)
```
- **Returns**: List of all items owned by user
- **Use for**: Inventory screens, shop purchases

#### Update Item Quantity
```python
updated_item = api.update_inventory_item(inventory_id, new_quantity)
```
- **Use for**: After using/consuming items
- **Note**: Set quantity to 0 to effectively remove item

---

### Transaction Endpoints

#### Create Transaction
```python
txn = api.create_transaction(
    user_id=1,
    transaction_type="purchase",
    amount=-100,
    description="Bought food"
)
```
- **Types**: `purchase`, `sale`, `reward`, `breeding`, `marketplace`
- **Amount**: Negative for spending, positive for earning
- **Returns**: Transaction record

#### Get User Transaction History
```python
transactions = api.get_user_transactions(user_id, skip=0, limit=50)
```
- **Returns**: List of transactions, newest first
- **Use for**: Transaction history pages, balance calculation

#### Get Transactions by Type
```python
purchases = api.get_transactions_by_type("purchase", limit=20)
```
- **Returns**: All transactions of specified type
- **Use for**: Analytics, filtering

---

### Leaderboard Endpoints

#### Get Global Leaderboard
```python
leaderboard = api.get_leaderboard(skip=0, limit=10)
```
- **Returns**: Top players sorted by score
- **Use for**: Leaderboard displays, rankings

#### Get User Rank
```python
rank_data = api.get_user_rank(user_id)
```
- **Returns**: `{'rank': int, 'score': int, 'username': str}`
- **Use for**: Showing player's current rank

#### Update User Score
```python
updated_rank = api.update_user_score(user_id, new_score)
```
- **Use for**: After mini-games, achievements
- **Note**: Automatically updates leaderboard position

---

### Mini-Game Endpoints

#### Get All Mini-Games
```python
games = api.get_mini_games()
```
- **Returns**: List of available mini-games with descriptions
- **Use for**: Game selection menus

#### Create Mini-Game
```python
game = api.create_mini_game(
    name="Maze Runner",
    description="Navigate the maze to find treats",
    reward_coins=50
)
```
- **Use for**: Adding new mini-games dynamically

---

### Marketplace Endpoints

#### Get Pet Valuation
```python
valuation = api.get_pet_valuation(pet_id)
```
- **Returns**:
  ```python
  {
      'base_price': 1000,
      'genetics_multiplier': 1.5,
      'final_price': 1500,
      'breakdown': {
          'speed_bonus': 200,
          'rarity_bonus': 300
      }
  }
  ```
- **Use for**: Before listing, pricing guidance

#### List Pet for Sale
```python
listing = api.list_pet_for_sale(pet_id, asking_price=2000)
```
- **Returns**: Marketplace listing data
- **Note**: Pet becomes unavailable to owner until unlisted

#### Unlist Pet
```python
result = api.unlist_pet(pet_id)
```
- **Returns**: Success message
- **Use for**: Canceling listings

#### Buy Pet
```python
transaction = api.buy_pet(pet_id, buyer_id)
```
- **Returns**: Transaction record
- **Side effects**:
  - Deducts coins from buyer
  - Transfers coins to seller
  - Changes pet ownership
  - Creates transaction records

#### Browse Marketplace
```python
listings = api.browse_marketplace(
    min_price=1000,
    max_price=5000,
    color="brown",
    sort_by="price_asc",  # price_asc, price_desc, newest, genetics_high, genetics_low
    skip=0,
    limit=20
)
```
- **Returns**: List of marketplace listings with pet data
- **Filters**: All optional
- **Use for**: Marketplace browsing pages

#### Get User Portfolio
```python
portfolio = api.get_user_portfolio(user_id)
```
- **Returns**:
  ```python
  {
      'total_pets': 5,
      'total_value': 7500,
      'average_value': 1500,
      'pets': [...]
  }
  ```
- **Use for**: Portfolio/collection views

---

### Genetics/Breeding Endpoints

#### Get All Genes
```python
genes = api.get_genes()
```
- **Returns**: List of all genes in system
- **Use for**: Genetics info pages, breeding UI

#### Get Specific Gene
```python
gene = api.get_gene(gene_id)
```
- **Returns**: Gene details (name, trait, dominance)

#### Get Pet Genetics
```python
genetics = api.get_pet_genetics(pet_id)
```
- **Returns**: List of allele pairs for pet
- **Example**:
  ```python
  [
      {'gene_name': 'Fur Length', 'allele1': 'L', 'allele2': 'l', 'expressed': 'Long'},
      {'gene_name': 'Speed', 'allele1': 'S', 'allele2': 'S', 'expressed': 'Fast'}
  ]
  ```

#### Breed Pets
```python
offspring = api.breed_pets(
    parent1_id=1,
    parent2_id=2,
    offspring_name="Baby",
    offspring_color="mixed"
)
```
- **Returns**: New pet with inherited genetics
- **Side effects**:
  - Creates new pet
  - Records breeding history
  - May charge breeding fee (if implemented)

#### Get Breeding History
```python
history = api.get_breeding_history(pet_id)
```
- **Returns**:
  ```python
  {
      'parents': [parent1_data, parent2_data],
      'offspring': [offspring1_data, offspring2_data],
      'generation': 2
  }
  ```

#### Calculate Punnett Square
```python
punnett = api.calculate_punnett_square(parent1_id, parent2_id, gene_id)
```
- **Returns**:
  ```python
  {
      'gene_name': 'Fur Color',
      'parent1_genotype': 'Bb',
      'parent2_genotype': 'bb',
      'grid': [['Bb', 'bb'], ['Bb', 'bb']],
      'probabilities': {'Bb': 50, 'bb': 50}
  }
  ```
- **Use for**: Educational displays, breeding predictions

#### Get Pet Stats
```python
stats = api.get_pet_stats(pet_id)
```
- **Returns**:
  ```python
  {
      'speed': 85,
      'strength': 70,
      'intelligence': 90,
      'cuteness': 95
  }
  ```
- **Note**: Stats calculated from genetics

#### Compare Pets
```python
comparison = api.compare_pets(pet1_id, pet2_id)
```
- **Returns**:
  ```python
  {
      'pet1_stats': {'speed': 85, ...},
      'pet2_stats': {'speed': 78, ...},
      'differences': {'speed': +7, ...}
  }
  ```
- **Use for**: Breeding decisions, competition previews

---

## Integration Examples by Page

### Example 1: Homescreen/Main Menu

```python
# homescreen.py

import pygame
from button import Button

# Optional API integration
try:
    from api_client import api
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    print("API client not available. Running in offline mode.")

# Global state
current_user = None
user_pets = []
api_status = "Disconnected"

def homescreen_init():
    """Initialize homescreen and load user data."""
    global current_user, user_pets, api_status

    if API_AVAILABLE:
        try:
            # Check connection
            if api.check_connection():
                api_status = "Connected"

                # Load or create user (example: auto-login as user 1)
                try:
                    current_user = api.get_user(1)
                    user_pets = api.get_user_pets(1)
                except:
                    # User doesn't exist, create one
                    current_user = api.create_user(
                        "Player1",
                        "player1@game.com",
                        "password"
                    )
                    user_pets = []
            else:
                api_status = "Server Offline"
        except Exception as e:
            api_status = f"Error: {str(e)}"
            print(f"API Error: {e}")

def homescreen_update(events):
    """Handle homescreen events."""
    # ... your existing event handling ...
    pass

def homescreen_draw(screen):
    """Draw homescreen with API status."""
    # ... your existing drawing ...

    # Optional: Display connection status
    if API_AVAILABLE:
        font = pygame.font.Font(None, 24)
        status_text = font.render(f"API: {api_status}", True, (0, 0, 0))
        screen.blit(status_text, (10, 10))

        if current_user:
            balance_text = font.render(
                f"Balance: {current_user.get('balance', 0)} coins",
                True, (0, 128, 0)
            )
            screen.blit(balance_text, (10, 35))

            pets_text = font.render(
                f"Pets: {len(user_pets)}",
                True, (0, 0, 128)
            )
            screen.blit(pets_text, (10, 60))
```

---

### Example 2: Pet Selection Screen

```python
# pet_selection.py

import pygame
from api_client import api

class PetSelectionScreen:
    def __init__(self, user_id):
        self.user_id = user_id
        self.pets = []
        self.selected_pet = None
        self.loading = True
        self.error_message = None

        self.load_pets()

    def load_pets(self):
        """Load user's pets from backend."""
        try:
            self.pets = api.get_user_pets(self.user_id)
            self.loading = False
        except ConnectionError:
            self.error_message = "Cannot connect to server"
            self.loading = False
        except Exception as e:
            self.error_message = f"Error loading pets: {str(e)}"
            self.loading = False

    def select_pet(self, pet_id):
        """Select a pet and load its full details."""
        try:
            self.selected_pet = api.get_pet(pet_id)
            return self.selected_pet
        except Exception as e:
            self.error_message = f"Error loading pet: {str(e)}"
            return None

    def create_new_pet(self, name, color):
        """Create a new pet for the user."""
        try:
            new_pet = api.create_pet(self.user_id, name, color)
            self.pets.append(new_pet)
            return new_pet
        except Exception as e:
            self.error_message = f"Error creating pet: {str(e)}"
            return None

    def draw(self, screen):
        """Draw the pet selection screen."""
        if self.loading:
            # Show loading indicator
            font = pygame.font.Font(None, 36)
            loading_text = font.render("Loading pets...", True, (0, 0, 0))
            screen.blit(loading_text, (300, 250))

        elif self.error_message:
            # Show error message
            font = pygame.font.Font(None, 28)
            error_text = font.render(self.error_message, True, (255, 0, 0))
            screen.blit(error_text, (200, 250))

        else:
            # Draw pets
            y_offset = 100
            for pet in self.pets:
                font = pygame.font.Font(None, 24)
                text = font.render(
                    f"{pet['name']} ({pet['color']}) - Health: {pet['health']}",
                    True, (0, 0, 0)
                )
                screen.blit(text, (50, y_offset))
                y_offset += 30
```

---

### Example 3: Marketplace Browser

```python
# marketplace.py

import pygame
from api_client import api

class MarketplaceBrowser:
    def __init__(self):
        self.listings = []
        self.filters = {
            'min_price': 0,
            'max_price': 10000,
            'color': None,
            'sort_by': 'price_asc'
        }
        self.current_page = 0
        self.items_per_page = 10

        self.refresh_listings()

    def refresh_listings(self):
        """Refresh marketplace listings with current filters."""
        try:
            self.listings = api.browse_marketplace(
                min_price=self.filters['min_price'],
                max_price=self.filters['max_price'],
                color=self.filters['color'],
                sort_by=self.filters['sort_by'],
                skip=self.current_page * self.items_per_page,
                limit=self.items_per_page
            )
        except Exception as e:
            print(f"Error loading marketplace: {e}")
            self.listings = []

    def get_pet_value(self, pet_id):
        """Get estimated value of a pet."""
        try:
            valuation = api.get_pet_valuation(pet_id)
            return valuation['final_price']
        except:
            return None

    def purchase_pet(self, pet_id, buyer_id):
        """Purchase a pet from marketplace."""
        try:
            transaction = api.buy_pet(pet_id, buyer_id)
            self.refresh_listings()  # Refresh after purchase
            return {
                'success': True,
                'message': f"Purchased pet for {transaction.get('amount', 0)} coins!"
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Purchase failed: {str(e)}"
            }

    def list_my_pet(self, pet_id):
        """List one of your pets for sale."""
        try:
            # Get valuation first
            valuation = api.get_pet_valuation(pet_id)
            suggested_price = valuation['final_price']

            # List at 120% of estimated value
            asking_price = int(suggested_price * 1.2)

            listing = api.list_pet_for_sale(pet_id, asking_price)
            return {
                'success': True,
                'listing_id': listing.get('listing_id'),
                'price': asking_price
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
```

---

### Example 4: Breeding Interface

```python
# breeding.py

import pygame
from api_client import api

class BreedingInterface:
    def __init__(self, user_id):
        self.user_id = user_id
        self.parent1 = None
        self.parent2 = None
        self.available_pets = []
        self.punnett_squares = {}

        self.load_available_pets()

    def load_available_pets(self):
        """Load user's pets available for breeding."""
        try:
            self.available_pets = api.get_user_pets(self.user_id)
        except Exception as e:
            print(f"Error loading pets: {e}")

    def select_parent(self, slot, pet):
        """Select a parent for breeding."""
        if slot == 1:
            self.parent1 = pet
        else:
            self.parent2 = pet

        # Calculate Punnett squares if both parents selected
        if self.parent1 and self.parent2:
            self.calculate_all_punnett_squares()

    def calculate_all_punnett_squares(self):
        """Calculate Punnett squares for all genes."""
        try:
            genes = api.get_genes()
            self.punnett_squares = {}

            for gene in genes:
                punnett = api.calculate_punnett_square(
                    self.parent1['pet_id'],
                    self.parent2['pet_id'],
                    gene['gene_id']
                )
                self.punnett_squares[gene['name']] = punnett
        except Exception as e:
            print(f"Error calculating Punnett squares: {e}")

    def compare_parents(self):
        """Compare stats of both parents."""
        if not (self.parent1 and self.parent2):
            return None

        try:
            comparison = api.compare_pets(
                self.parent1['pet_id'],
                self.parent2['pet_id']
            )
            return comparison
        except Exception as e:
            print(f"Error comparing pets: {e}")
            return None

    def breed(self, offspring_name, offspring_color):
        """Breed the two selected parents."""
        if not (self.parent1 and self.parent2):
            return {'success': False, 'message': 'Select both parents first'}

        try:
            offspring = api.breed_pets(
                self.parent1['pet_id'],
                self.parent2['pet_id'],
                offspring_name,
                offspring_color
            )

            # Get offspring stats
            stats = api.get_pet_stats(offspring['pet_id'])

            return {
                'success': True,
                'pet': offspring,
                'stats': stats,
                'message': f"Successfully bred {offspring_name}!"
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Breeding failed: {str(e)}"
            }

    def draw_punnett_square(self, screen, gene_name, x, y):
        """Draw a Punnett square for a specific gene."""
        if gene_name not in self.punnett_squares:
            return

        punnett = self.punnett_squares[gene_name]
        font = pygame.font.Font(None, 20)

        # Draw gene name
        title = font.render(gene_name, True, (0, 0, 0))
        screen.blit(title, (x, y))

        # Draw probabilities
        y_offset = y + 25
        for genotype, probability in punnett.get('probabilities', {}).items():
            text = font.render(f"{genotype}: {probability}%", True, (0, 100, 0))
            screen.blit(text, (x, y_offset))
            y_offset += 20
```

---

### Example 5: Mini-Game Rewards

```python
# minigame.py

import pygame
from api_client import api

class MiniGame:
    def __init__(self, user_id, game_name):
        self.user_id = user_id
        self.game_name = game_name
        self.reward_coins = 0
        self.game_completed = False

        self.load_game_info()

    def load_game_info(self):
        """Load mini-game information."""
        try:
            games = api.get_mini_games()
            for game in games:
                if game['name'] == self.game_name:
                    self.reward_coins = game.get('reward_coins', 0)
                    break
        except Exception as e:
            print(f"Error loading game info: {e}")

    def complete_game(self, score):
        """Handle game completion and reward."""
        if self.game_completed:
            return {'success': False, 'message': 'Already completed'}

        try:
            # Create reward transaction
            transaction = api.create_transaction(
                user_id=self.user_id,
                transaction_type='reward',
                amount=self.reward_coins,
                description=f"Completed {self.game_name} with score {score}"
            )

            # Update leaderboard score
            try:
                api.update_user_score(self.user_id, score)
            except:
                pass  # Leaderboard update is optional

            self.game_completed = True

            return {
                'success': True,
                'reward': self.reward_coins,
                'message': f"Earned {self.reward_coins} coins!"
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error processing reward: {str(e)}"
            }
```

---

## Error Handling Patterns

### Pattern 1: Graceful Degradation

```python
# Try to load from API, fall back to local data
try:
    pets = api.get_user_pets(user_id)
except ConnectionError:
    # Server offline - use cached data
    pets = load_cached_pets()
    show_offline_indicator()
except Exception as e:
    # Other error - log and use empty list
    print(f"Error: {e}")
    pets = []
```

### Pattern 2: User Feedback

```python
def purchase_item(item_id):
    try:
        result = api.buy_item(item_id)
        show_success_message("Purchase successful!")
        return True
    except ConnectionError:
        show_error_message("Server offline. Try again later.")
        return False
    except Exception as e:
        if "insufficient funds" in str(e).lower():
            show_error_message("Not enough coins!")
        else:
            show_error_message(f"Purchase failed: {e}")
        return False
```

### Pattern 3: Loading States

```python
class DataLoader:
    def __init__(self):
        self.loading = False
        self.error = None
        self.data = None

    def load_data(self):
        self.loading = True
        self.error = None

        try:
            self.data = api.get_some_data()
        except Exception as e:
            self.error = str(e)
        finally:
            self.loading = False

    def draw(self, screen):
        if self.loading:
            # Show spinner
            draw_loading_spinner(screen)
        elif self.error:
            # Show error
            draw_error_message(screen, self.error)
        else:
            # Show data
            draw_data(screen, self.data)
```

### Pattern 4: Retry Logic

```python
def fetch_with_retry(func, max_retries=3):
    """Retry a function call up to max_retries times."""
    for attempt in range(max_retries):
        try:
            return func()
        except ConnectionError:
            if attempt == max_retries - 1:
                raise
            time.sleep(1)  # Wait before retry
```

---

## Best Practices

### 1. Connection Checking

Always check connection before critical operations:

```python
if not api.check_connection():
    show_error_message("Cannot connect to server")
    return
```

### 2. Caching

Cache frequently accessed data:

```python
# Cache user data for 5 minutes
cached_user = None
cache_time = 0

def get_current_user(user_id):
    global cached_user, cache_time

    if cached_user and time.time() - cache_time < 300:
        return cached_user

    cached_user = api.get_user(user_id)
    cache_time = time.time()
    return cached_user
```

### 3. Background Loading

Load data in initialization, not during draw:

```python
# GOOD
def screen_init():
    global pets
    pets = api.get_user_pets(user_id)

def screen_draw(screen):
    draw_pets(screen, pets)

# BAD
def screen_draw(screen):
    pets = api.get_user_pets(user_id)  # Don't call API every frame!
    draw_pets(screen, pets)
```

### 4. Error Messages

Provide specific, actionable error messages:

```python
# GOOD
"Cannot connect to server. Make sure backend is running on port 8000."

# BAD
"Error"
```

### 5. Transaction Logging

Log important actions:

```python
def sell_pet(pet_id, price):
    # ... sell logic ...

    # Log transaction
    api.create_transaction(
        user_id=user_id,
        transaction_type='sale',
        amount=price,
        description=f"Sold pet {pet_id}"
    )
```

---

## Troubleshooting

### Issue: "Cannot connect to backend"

**Causes:**
- Backend server not running
- Wrong port (check if using 8000)
- Firewall blocking connection

**Solutions:**
1. Start backend: `uvicorn main:app --reload`
2. Check backend is on port 8000: visit `http://localhost:8000/docs`
3. Check firewall settings

---

### Issue: "HTTP 404: Not Found"

**Causes:**
- Endpoint not implemented in backend
- Wrong endpoint path
- Resource doesn't exist (e.g., pet_id=999)

**Solutions:**
1. Check backend has the endpoint implemented
2. Verify endpoint path in backend code
3. Check resource ID is valid

---

### Issue: "HTTP 422: Validation Error"

**Causes:**
- Missing required parameters
- Wrong parameter types
- Invalid data format

**Solutions:**
1. Check API client call has all required parameters
2. Verify data types match backend expectations
3. Check backend Pydantic schemas for requirements

---

### Issue: Data not updating

**Causes:**
- Caching old data
- Not refreshing after changes
- API call succeeding but not returning new data

**Solutions:**
1. Clear caches after mutations (create, update, delete)
2. Reload data after API calls that change state
3. Check backend is returning updated data

---

### Issue: Slow performance

**Causes:**
- Calling API every frame
- Loading too much data at once
- No caching

**Solutions:**
1. Load data once in initialization
2. Use pagination (skip/limit parameters)
3. Implement caching for static data
4. Only reload when necessary

---

### Issue: "Timeout Error"

**Causes:**
- Slow network
- Backend processing too long
- Database locked

**Solutions:**
1. Increase timeout in API client
2. Optimize backend queries
3. Check database isn't locked

---

## Additional Resources

- **Backend Documentation**: Check `backend/main.py` for available endpoints
- **Example Code**: See `api_example.py` for comprehensive usage examples
- **Connection Test**: Run `test_api_connection.py` to verify setup
- **FastAPI Docs**: Visit `http://localhost:8000/docs` for interactive API documentation

---

## Summary

The Guinea Games API client provides a complete interface to all backend functionality:

1. **User Management**: Create, authenticate, track balances
2. **Pet System**: Create, update, manage guinea pigs
3. **Genetics**: Breeding, inheritance, stat calculation
4. **Marketplace**: Buy, sell, valuate pets
5. **Inventory**: Items, feeding, equipment
6. **Transactions**: Financial tracking, history
7. **Leaderboards**: Rankings, scores
8. **Mini-Games**: Rewards, completion tracking

Integrate it into your Pygame frontend to create a full-featured, multiplayer-ready virtual pet game!

For questions or issues, check the troubleshooting section or review the example code in `api_example.py`.
