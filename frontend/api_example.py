"""
Guinea Games API Usage Examples
Comprehensive examples showing how to use the API client in your Pygame frontend.

This file demonstrates:
- User management
- Pet creation and management
- Genetics and breeding
- Marketplace operations
- Inventory management
- Transaction logging
- Error handling patterns

Usage:
    python api_example.py
"""

from api_client import api


def example_user_management():
    """Example: User Management"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: User Management")
    print("=" * 70)

    try:
        # Create a new user
        print("\n1. Creating a new user...")
        user = api.create_user(
            username="player_one",
            email="player1@guineagames.com",
            password="secure_password_123"
        )
        print(f"   Created user: {user['username']} (ID: {user['user_id']})")

        # Get all users
        print("\n2. Getting all users...")
        users = api.get_users(limit=5)
        print(f"   Found {len(users)} users")
        for u in users[:3]:
            print(f"   - {u['username']} ({u['email']})")

        # Get specific user
        print("\n3. Getting specific user...")
        user_details = api.get_user(user['user_id'])
        print(f"   User: {user_details['username']}")
        print(f"   Balance: {user_details.get('balance', 0)} coins")

        return user

    except Exception as e:
        print(f"   ERROR: {str(e)}")
        return None


def example_pet_creation(user):
    """Example: Pet Creation and Management"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Pet Creation and Management")
    print("=" * 70)

    if not user:
        print("   Skipping - no user available")
        return None

    try:
        # Create a pet
        print("\n1. Creating a pet...")
        pet = api.create_pet(
            user_id=user['user_id'],
            name="Fluffy",
            color="brown"
        )
        print(f"   Created pet: {pet['name']} (ID: {pet['pet_id']})")
        print(f"   Stats: Health={pet['health']}, Happiness={pet['happiness']}")

        # Get user's pets
        print("\n2. Getting all pets for user...")
        user_pets = api.get_user_pets(user['user_id'])
        print(f"   User has {len(user_pets)} pet(s)")
        for p in user_pets:
            print(f"   - {p['name']} ({p['color']})")

        # Update pet stats
        print("\n3. Updating pet stats...")
        updated_pet = api.update_pet(
            pet['pet_id'],
            health=95,
            happiness=90,
            hunger=20
        )
        print(f"   Updated {updated_pet['name']}")
        print(f"   New stats: Health={updated_pet['health']}, Happiness={updated_pet['happiness']}")

        # Get pet genetics
        print("\n4. Getting pet genetics...")
        genetics = api.get_pet_genetics(pet['pet_id'])
        if genetics:
            print(f"   Pet has {len(genetics)} genetic traits")
            for gen in genetics[:3]:
                print(f"   - {gen.get('gene_name', 'Unknown')}: {gen.get('allele1', '?')}/{gen.get('allele2', '?')}")

        return pet

    except Exception as e:
        print(f"   ERROR: {str(e)}")
        return None


def example_marketplace_operations(pet, user):
    """Example: Marketplace Operations"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Marketplace Operations")
    print("=" * 70)

    if not pet or not user:
        print("   Skipping - no pet/user available")
        return

    try:
        # Get pet valuation
        print("\n1. Getting pet valuation...")
        valuation = api.get_pet_valuation(pet['pet_id'])
        print(f"   Base Price: {valuation['base_price']} coins")
        print(f"   Genetics Multiplier: {valuation['genetics_multiplier']}x")
        print(f"   Final Price: {valuation['final_price']} coins")

        if 'breakdown' in valuation:
            print("   Price breakdown:")
            for trait, value in valuation['breakdown'].items():
                print(f"     - {trait}: +{value} coins")

        # List pet for sale
        print("\n2. Listing pet for sale...")
        asking_price = int(valuation['final_price'] * 1.2)  # 20% markup
        listing = api.list_pet_for_sale(pet['pet_id'], asking_price)
        print(f"   Listed {pet['name']} for {asking_price} coins")
        print(f"   Listing ID: {listing.get('listing_id')}")

        # Browse marketplace
        print("\n3. Browsing marketplace...")
        listings = api.browse_marketplace(
            min_price=0,
            max_price=10000,
            sort_by="price_asc",
            limit=5
        )
        print(f"   Found {len(listings)} listings")
        for item in listings[:3]:
            print(f"   - {item.get('pet_name')} ({item.get('pet_color')}): {item.get('asking_price')} coins")

        # Get user portfolio
        print("\n4. Getting user portfolio...")
        portfolio = api.get_user_portfolio(user['user_id'])
        print(f"   Total pets: {portfolio['total_pets']}")
        print(f"   Portfolio value: {portfolio['total_value']} coins")
        print(f"   Average pet value: {portfolio['average_value']} coins")

        # Unlist the pet
        print("\n5. Unlisting pet...")
        result = api.unlist_pet(pet['pet_id'])
        print(f"   {result.get('message', 'Pet unlisted')}")

    except Exception as e:
        print(f"   ERROR: {str(e)}")


def example_breeding_system(user):
    """Example: Genetics and Breeding"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Genetics and Breeding System")
    print("=" * 70)

    if not user:
        print("   Skipping - no user available")
        return

    try:
        # Create two parent pets
        print("\n1. Creating parent pets...")
        parent1 = api.create_pet(user['user_id'], "Mother", "white")
        parent2 = api.create_pet(user['user_id'], "Father", "brown")
        print(f"   Parent 1: {parent1['name']} (ID: {parent1['pet_id']})")
        print(f"   Parent 2: {parent2['name']} (ID: {parent2['pet_id']})")

        # Get available genes
        print("\n2. Getting available genes...")
        genes = api.get_genes()
        if genes:
            print(f"   Found {len(genes)} genes in the system")
            for gene in genes[:3]:
                print(f"   - {gene['name']}: {gene['trait']} ({gene['dominance']})")

            # Calculate Punnett square
            if len(genes) > 0:
                print("\n3. Calculating Punnett square...")
                gene_id = genes[0]['gene_id']
                punnett = api.calculate_punnett_square(
                    parent1['pet_id'],
                    parent2['pet_id'],
                    gene_id
                )
                print(f"   Gene: {genes[0]['name']}")
                print(f"   Probabilities:")
                for genotype, prob in punnett.get('probabilities', {}).items():
                    print(f"     - {genotype}: {prob}%")

        # Breed the pets
        print("\n4. Breeding pets...")
        offspring = api.breed_pets(
            parent1_id=parent1['pet_id'],
            parent2_id=parent2['pet_id'],
            offspring_name="Baby Guinea",
            offspring_color="mixed"
        )
        print(f"   Offspring created: {offspring['pet_id']}")
        print(f"   Name: {offspring['name']}")
        print(f"   Inherited genetics: {len(offspring.get('genetics', []))} traits")

        # Get pet stats
        print("\n5. Getting offspring stats...")
        stats = api.get_pet_stats(offspring['pet_id'])
        print(f"   Speed: {stats.get('speed', 0)}")
        print(f"   Strength: {stats.get('strength', 0)}")
        print(f"   Intelligence: {stats.get('intelligence', 0)}")
        print(f"   Cuteness: {stats.get('cuteness', 0)}")

        # Compare parent and offspring
        print("\n6. Comparing parent and offspring...")
        comparison = api.compare_pets(parent1['pet_id'], offspring['pet_id'])
        print(f"   Parent speed: {comparison['pet1_stats']['speed']}")
        print(f"   Offspring speed: {comparison['pet2_stats']['speed']}")

        return offspring

    except Exception as e:
        print(f"   ERROR: {str(e)}")
        return None


def example_inventory_management(user):
    """Example: Inventory Management"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Inventory Management")
    print("=" * 70)

    if not user:
        print("   Skipping - no user available")
        return

    try:
        # Add items to inventory
        print("\n1. Adding items to inventory...")
        food1 = api.add_inventory_item(
            user_id=user['user_id'],
            item_name="Premium Pellets",
            item_type="food",
            quantity=10
        )
        print(f"   Added: {food1['item_name']} x{food1['quantity']}")

        toy1 = api.add_inventory_item(
            user_id=user['user_id'],
            item_name="Exercise Wheel",
            item_type="toy",
            quantity=1
        )
        print(f"   Added: {toy1['item_name']} x{toy1['quantity']}")

        # Get user inventory
        print("\n2. Getting user inventory...")
        inventory = api.get_user_inventory(user['user_id'])
        print(f"   Inventory contains {len(inventory)} item types")
        for item in inventory:
            print(f"   - {item['item_name']} ({item['item_type']}): x{item['quantity']}")

        # Update inventory quantity
        print("\n3. Updating inventory (using food)...")
        updated_item = api.update_inventory_item(
            inventory_id=food1['inventory_id'],
            quantity=food1['quantity'] - 1
        )
        print(f"   {updated_item['item_name']}: {food1['quantity']} -> {updated_item['quantity']}")

    except Exception as e:
        print(f"   ERROR: {str(e)}")


def example_transactions(user):
    """Example: Transaction Logging"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Transaction Logging")
    print("=" * 70)

    if not user:
        print("   Skipping - no user available")
        return

    try:
        # Create transactions
        print("\n1. Creating transactions...")
        txn1 = api.create_transaction(
            user_id=user['user_id'],
            transaction_type="purchase",
            amount=-100,
            description="Bought Premium Pellets"
        )
        print(f"   Transaction 1: {txn1['transaction_type']} - {txn1['amount']} coins")

        txn2 = api.create_transaction(
            user_id=user['user_id'],
            transaction_type="reward",
            amount=50,
            description="Completed mini-game"
        )
        print(f"   Transaction 2: {txn2['transaction_type']} - {txn2['amount']} coins")

        # Get user transaction history
        print("\n2. Getting transaction history...")
        transactions = api.get_user_transactions(user['user_id'], limit=10)
        print(f"   Found {len(transactions)} transactions")
        total = 0
        for txn in transactions:
            print(f"   - {txn['transaction_type']}: {txn['amount']} coins - {txn.get('description', '')}")
            total += txn['amount']
        print(f"   Net change: {total} coins")

        # Get transactions by type
        print("\n3. Getting purchase transactions...")
        purchases = api.get_transactions_by_type("purchase", limit=5)
        print(f"   Found {len(purchases)} purchases")
        purchase_total = sum(txn['amount'] for txn in purchases)
        print(f"   Total spent: {purchase_total} coins")

    except Exception as e:
        print(f"   ERROR: {str(e)}")


def example_error_handling():
    """Example: Error Handling Patterns"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Error Handling Patterns")
    print("=" * 70)

    # Example 1: Connection error
    print("\n1. Handling connection errors...")
    try:
        # Try to connect to wrong URL
        from api_client import APIClient
        bad_api = APIClient(base_url="http://localhost:9999")
        bad_api.get_users()
    except ConnectionError as e:
        print(f"   Caught ConnectionError: {str(e)}")
        print("   Action: Display 'Server offline' message to user")

    # Example 2: Resource not found
    print("\n2. Handling 404 errors...")
    try:
        api.get_pet(999999)  # Non-existent pet
    except Exception as e:
        print(f"   Caught Exception: {str(e)}")
        print("   Action: Display 'Pet not found' message")

    # Example 3: Using try-except in game code
    print("\n3. Example game code pattern...")
    print("""
    def load_user_pets(user_id):
        try:
            pets = api.get_user_pets(user_id)
            return pets
        except ConnectionError:
            # Server is down
            show_error_message("Cannot connect to server")
            return []
        except Exception as e:
            # Other error
            show_error_message(f"Error loading pets: {e}")
            return []
    """)


def run_all_examples():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("GUINEA GAMES API CLIENT - USAGE EXAMPLES")
    print("=" * 70)
    print("\nThis script demonstrates how to use the API client in your Pygame game.")
    print("\nNOTE: Make sure the backend is running first:")
    print("  cd backend")
    print("  uvicorn main:app --reload")

    # Check connection
    if not api.check_connection():
        print("\nERROR: Cannot connect to backend!")
        print("Please start the backend server and try again.")
        return

    print("\nConnected to backend successfully!")

    # Run examples
    user = example_user_management()
    pet = example_pet_creation(user)
    example_marketplace_operations(pet, user)
    offspring = example_breeding_system(user)
    example_inventory_management(user)
    example_transactions(user)
    example_error_handling()

    print("\n" + "=" * 70)
    print("EXAMPLES COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Study these examples to understand the API patterns")
    print("  2. Integrate the API calls into your Pygame pages")
    print("  3. Add error handling for production use")
    print("  4. Check API_INTEGRATION_GUIDE.md for detailed documentation")
    print("\n")


if __name__ == "__main__":
    try:
        run_all_examples()
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
