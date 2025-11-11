# Guinea Games API Client - Quick Reference

Quick start guide for integrating the backend API with your Pygame frontend.

## Installation

1. **Install requests library**:
   ```bash
   pip install requests
   ```

2. **Start the backend**:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

3. **Test the connection**:
   ```bash
   cd frontend
   python test_api_connection.py
   ```

## Basic Usage

### Import the API Client

```python
from api_client import api
```

### Create a User

```python
user = api.create_user("username", "email@example.com", "password")
print(f"User ID: {user['user_id']}")
```

### Create a Pet

```python
pet = api.create_pet(user['user_id'], "Fluffy", "brown")
print(f"Pet ID: {pet['pet_id']}")
print(f"Health: {pet['health']}, Happiness: {pet['happiness']}")
```

### Get User's Pets

```python
pets = api.get_user_pets(user['user_id'])
for pet in pets:
    print(f"{pet['name']} - {pet['color']}")
```

### Update Pet Stats

```python
updated_pet = api.update_pet(
    pet['pet_id'],
    health=100,
    happiness=95,
    hunger=20
)
```

## Common Operations

### Marketplace

#### Get Pet Valuation
```python
valuation = api.get_pet_valuation(pet['pet_id'])
print(f"Pet is worth {valuation['final_price']} coins")
print(f"Genetics multiplier: {valuation['genetics_multiplier']}x")
```

#### List Pet for Sale
```python
listing = api.list_pet_for_sale(pet['pet_id'], asking_price=2000)
print(f"Listed with ID: {listing['listing_id']}")
```

#### Browse Marketplace
```python
listings = api.browse_marketplace(
    min_price=1000,
    max_price=5000,
    color="brown",
    sort_by="price_asc",
    limit=20
)
for listing in listings:
    print(f"{listing['pet_name']}: {listing['asking_price']} coins")
```

#### Buy a Pet
```python
transaction = api.buy_pet(pet['pet_id'], buyer_id=user['user_id'])
print(f"Purchased for {transaction['amount']} coins")
```

#### Get Portfolio Value
```python
portfolio = api.get_user_portfolio(user['user_id'])
print(f"Total pets: {portfolio['total_pets']}")
print(f"Total value: {portfolio['total_value']} coins")
```

### Breeding & Genetics

#### Breed Two Pets
```python
offspring = api.breed_pets(
    parent1_id=1,
    parent2_id=2,
    offspring_name="Baby Guinea",
    offspring_color="mixed"
)
print(f"New pet ID: {offspring['pet_id']}")
```

#### Get Pet Genetics
```python
genetics = api.get_pet_genetics(pet['pet_id'])
for gene in genetics:
    print(f"{gene['gene_name']}: {gene['allele1']}/{gene['allele2']}")
```

#### Calculate Punnett Square
```python
punnett = api.calculate_punnett_square(parent1_id, parent2_id, gene_id)
print(f"Probabilities: {punnett['probabilities']}")
# Example: {'AA': 25, 'Aa': 50, 'aa': 25}
```

#### Get Pet Stats
```python
stats = api.get_pet_stats(pet['pet_id'])
print(f"Speed: {stats['speed']}")
print(f"Strength: {stats['strength']}")
print(f"Intelligence: {stats['intelligence']}")
print(f"Cuteness: {stats['cuteness']}")
```

#### Compare Two Pets
```python
comparison = api.compare_pets(pet1_id, pet2_id)
print(f"Pet 1 speed: {comparison['pet1_stats']['speed']}")
print(f"Pet 2 speed: {comparison['pet2_stats']['speed']}")
```

### Inventory

#### Add Items
```python
item = api.add_inventory_item(
    user_id=user['user_id'],
    item_name="Premium Pellets",
    item_type="food",
    quantity=10
)
```

#### Get Inventory
```python
inventory = api.get_user_inventory(user['user_id'])
for item in inventory:
    print(f"{item['item_name']}: x{item['quantity']}")
```

#### Feed Pet
```python
updated_pet = api.feed_pet(pet['pet_id'], food_item_id=item['inventory_id'])
print(f"New hunger level: {updated_pet['hunger']}")
```

### Transactions

#### Create Transaction
```python
txn = api.create_transaction(
    user_id=user['user_id'],
    transaction_type="purchase",
    amount=-100,
    description="Bought food"
)
```

#### Get Transaction History
```python
transactions = api.get_user_transactions(user['user_id'], limit=10)
for txn in transactions:
    print(f"{txn['transaction_type']}: {txn['amount']} coins")
```

### Leaderboard

#### Get Top Players
```python
leaderboard = api.get_leaderboard(limit=10)
for i, entry in enumerate(leaderboard, 1):
    print(f"{i}. {entry['username']}: {entry['score']}")
```

#### Get User Rank
```python
rank_data = api.get_user_rank(user['user_id'])
print(f"Rank: {rank_data['rank']}, Score: {rank_data['score']}")
```

#### Update Score
```python
api.update_user_score(user['user_id'], new_score=1000)
```

## Integration with Pygame

### Basic Pattern

```python
import pygame
from api_client import api

# Optional import for graceful fallback
try:
    from api_client import api
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

# Initialize your data
current_user = None
user_pets = []

def init_game():
    """Initialize game and load data from API."""
    global current_user, user_pets

    if API_AVAILABLE and api.check_connection():
        try:
            # Load or create user
            current_user = api.get_user(1)
            user_pets = api.get_user_pets(1)
        except:
            # Handle errors gracefully
            current_user = None
            user_pets = []

def update_game(events):
    """Update game logic."""
    # Handle events...
    pass

def draw_game(screen):
    """Draw game screen."""
    if current_user:
        # Draw user info
        font = pygame.font.Font(None, 24)
        balance_text = font.render(
            f"Balance: {current_user['balance']} coins",
            True, (0, 0, 0)
        )
        screen.blit(balance_text, (10, 10))

        # Draw pets
        for i, pet in enumerate(user_pets):
            pet_text = font.render(
                f"{pet['name']} - Health: {pet['health']}",
                True, (0, 0, 0)
            )
            screen.blit(pet_text, (10, 40 + i * 25))
```

### Error Handling Pattern

```python
def safe_api_call(func, default=None):
    """Safely call an API function with error handling."""
    try:
        return func()
    except ConnectionError:
        print("Server offline")
        show_error_message("Cannot connect to server")
        return default
    except Exception as e:
        print(f"API Error: {e}")
        show_error_message(f"Error: {e}")
        return default

# Usage
pets = safe_api_call(lambda: api.get_user_pets(user_id), default=[])
```

### Loading State Pattern

```python
class DataLoader:
    def __init__(self):
        self.loading = True
        self.data = None
        self.error = None

    def load(self):
        try:
            self.data = api.get_some_data()
            self.loading = False
        except Exception as e:
            self.error = str(e)
            self.loading = False

    def draw(self, screen):
        if self.loading:
            # Show loading spinner
            draw_text(screen, "Loading...", (400, 300))
        elif self.error:
            # Show error
            draw_text(screen, f"Error: {self.error}", (400, 300))
        else:
            # Show data
            draw_data(screen, self.data)
```

## Troubleshooting

### Problem: "Cannot connect to backend"

**Solution**:
1. Make sure backend is running:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```
2. Check backend is on port 8000: visit `http://localhost:8000/docs`
3. Check firewall isn't blocking the connection

### Problem: "HTTP 404: Not Found"

**Solution**:
- Endpoint might not be implemented yet in backend
- Check `backend/main.py` for available routes
- Check backend logs for errors

### Problem: "HTTP 422: Validation Error"

**Solution**:
- Missing required parameters in API call
- Wrong data types
- Check function signature in `api_client.py`

### Problem: Data not updating

**Solution**:
- Reload data after mutations (create/update/delete)
- Clear any caches
- Example:
  ```python
  api.create_pet(user_id, "Fluffy", "brown")
  # Reload pets after creating
  pets = api.get_user_pets(user_id)
  ```

### Problem: Slow performance

**Solution**:
- Don't call API in draw loop (call in init/event handlers)
- Use caching for frequently accessed data
- Use pagination (skip/limit parameters)

## Quick Reference: All Endpoints

### Users
- `create_user(username, email, password)`
- `get_users(skip=0, limit=100)`
- `get_user(user_id)`

### Pets
- `create_pet(user_id, name, color)`
- `get_pets(skip=0, limit=100)`
- `get_user_pets(user_id)`
- `get_pet(pet_id)`
- `update_pet(pet_id, **kwargs)`
- `delete_pet(pet_id)`
- `feed_pet(pet_id, food_item_id)`

### Inventory
- `add_inventory_item(user_id, item_name, item_type, quantity=1)`
- `get_user_inventory(user_id)`
- `update_inventory_item(inventory_id, quantity)`

### Transactions
- `create_transaction(user_id, transaction_type, amount, description="")`
- `get_user_transactions(user_id, skip=0, limit=50)`
- `get_transactions_by_type(transaction_type, skip=0, limit=50)`

### Leaderboard
- `get_leaderboard(skip=0, limit=10)`
- `get_user_rank(user_id)`
- `update_user_score(user_id, score)`

### Mini-Games
- `get_mini_games()`
- `create_mini_game(name, description, reward_coins)`

### Marketplace
- `get_pet_valuation(pet_id)`
- `list_pet_for_sale(pet_id, asking_price)`
- `unlist_pet(pet_id)`
- `buy_pet(pet_id, buyer_id)`
- `browse_marketplace(min_price=None, max_price=None, color=None, sort_by="price_asc", skip=0, limit=20)`
- `get_user_portfolio(user_id)`

### Genetics/Breeding
- `get_genes()`
- `get_gene(gene_id)`
- `get_pet_genetics(pet_id)`
- `breed_pets(parent1_id, parent2_id, offspring_name, offspring_color)`
- `get_breeding_history(pet_id)`
- `calculate_punnett_square(parent1_id, parent2_id, gene_id)`
- `get_pet_stats(pet_id)`
- `compare_pets(pet1_id, pet2_id)`

### Utility
- `check_connection()`

## Next Steps

1. **Run the test script**: `python test_api_connection.py`
2. **Explore examples**: `python api_example.py`
3. **Read full guide**: See `API_INTEGRATION_GUIDE.md` for detailed documentation
4. **Check backend docs**: Visit `http://localhost:8000/docs` for interactive API documentation

## Resources

- **Full Documentation**: `API_INTEGRATION_GUIDE.md`
- **Example Code**: `api_example.py`
- **Connection Test**: `test_api_connection.py`
- **Backend API Docs**: `http://localhost:8000/docs` (when backend is running)

---

**Need Help?**
- Check the troubleshooting section above
- Review the example code in `api_example.py`
- Read the detailed guide in `API_INTEGRATION_GUIDE.md`
- Check backend logs for error details
