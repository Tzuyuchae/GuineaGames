"""
Guinea Games API Connection Test
Tests the connection to the backend API and validates basic functionality.

Run this script to verify your backend is running and the API client is working correctly.

Usage:
    python test_api_connection.py
"""

from api_client import api
import sys


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_stage(stage_num, title):
    """Print a stage header."""
    print(f"\n[STAGE {stage_num}] {title}")
    print("-" * 70)


def print_success(message):
    """Print a success message."""
    print(f"[SUCCESS] {message}")


def print_error(message):
    """Print an error message."""
    print(f"[ERROR] {message}")


def test_backend_connection():
    """Test Stage 1: Backend Connection"""
    print_stage(1, "Testing Backend Connection")

    try:
        connected = api.check_connection()
        if connected:
            print_success(f"Connected to backend at {api.base_url}")
            return True
        else:
            print_error("Backend is not responding")
            print("\nTroubleshooting:")
            print("  1. Make sure the backend is running:")
            print("     cd backend")
            print("     uvicorn main:app --reload")
            print("  2. Check that the backend is running on http://localhost:8000")
            print("  3. Try accessing http://localhost:8000/docs in your browser")
            return False
    except Exception as e:
        print_error(f"Connection failed: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Make sure the backend is running:")
        print("     cd backend")
        print("     uvicorn main:app --reload")
        print("  2. Check for firewall or port blocking issues")
        return False


def test_create_user():
    """Test Stage 2: Create Test User"""
    print_stage(2, "Creating Test User")

    try:
        # Create a test user with timestamp to avoid duplicates
        import time
        timestamp = int(time.time())
        username = f"test_user_{timestamp}"
        email = f"test_{timestamp}@example.com"

        print(f"  Creating user: {username}")
        print(f"  Email: {email}")

        user = api.create_user(username, email, "test_password_123")

        print_success("User created successfully")
        user_id = user.get('id')
        print(f"  User ID: {user_id}")
        print(f"  Username: {user.get('username')}")
        print(f"  Email: {user.get('email')}")

        return user
    except Exception as e:
        print_error(f"Failed to create user: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Check that the /users/ endpoint is implemented in the backend")
        print("  2. Verify the database is initialized (run backend/database/database.py)")
        print("  3. Check backend logs for errors")
        return None


def test_create_pet(user):
    """Test Stage 3: Create Test Pet"""
    print_stage(3, "Creating Test Pet")

    if not user:
        print_error("Cannot create pet without a user")
        return None

    try:
        user_id = user.get('id')
        pet_name = "Test_Guinea_Pig"
        pet_color = "brown"
        pet_species = "guinea_pig"  # or whatever you’re using

        print(f"  Creating pet: {pet_name}")
        print(f"  Owner: User ID {user_id}")
        print(f"  Species: {pet_species}")
        print(f"  Color: {pet_color}")

        pet = api.create_pet(user_id, pet_name, pet_species, pet_color)


        print_success("Pet created successfully")
        print(f"  Pet ID: {pet.get('id')}")
        print(f"  Name: {pet.get('name')}")
        print(f"  Color: {pet.get('color')}")
        print(f"  Health: {pet.get('health')}")
        print(f"  Happiness: {pet.get('happiness')}")

        return pet
    except Exception as e:
        print_error(f"Failed to create pet: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Check that the /pets/ endpoint is implemented in the backend")
        print("  2. Verify the pets table exists in the database")
        print("  3. Check that the user_id foreign key is set up correctly")
        print("  4. Check backend logs for errors")
        return None


def test_marketplace_valuation(pet):
    """Test Stage 4: Test Marketplace Valuation"""
    print_stage(4, "Testing Marketplace Valuation")

    if not pet:
        print_error("Cannot test valuation without a pet")
        return False

    try:
        pet_id = pet.get('id')

        # safety check
        if pet_id is None:
            raise ValueError("Pet dict has no 'id' field. "
                             "Check your create_pet() return value.")

        print(f"  Getting valuation for Pet ID: {pet_id}")

        valuation = api.get_pet_valuation(pet_id)

        print_success("Valuation calculated successfully")
        print(f"  Base Price: {valuation.get('base_price')} coins")
        print(f"  Genetics Multiplier: {valuation.get('genetics_multiplier')}x")
        print(f"  Final Price: {valuation.get('final_price')} coins")

        if 'breakdown' in valuation:
            print(f"  Breakdown:")
            for trait, value in valuation['breakdown'].items():
                print(f"    - {trait}: {value}")

        return True
    except Exception as e:
        print_error(f"Failed to get valuation: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Check that the /marketplace/valuation/{pet_id} endpoint is implemented")
        print("  2. Verify the genetics system is set up correctly")
        print("  3. Check that the pet has genetics data")
        print("  4. Check backend logs for errors")
        return False


def run_all_tests():
    """Run all API tests."""
    print_header("GUINEA GAMES API CONNECTION TEST")
    print(f"Backend URL: {api.base_url}")

    # Track test results
    results = {
        "connection": False,
        "user": False,
        "pet": False,
        "valuation": False
    }

    # Stage 1: Test connection
    results["connection"] = test_backend_connection()
    if not results["connection"]:
        print_header("TESTS FAILED - Backend Not Connected")
        sys.exit(1)

    # Stage 2: Create user
    user = test_create_user()
    results["user"] = user is not None
    if not results["user"]:
        print_header("TESTS FAILED - Cannot Create User")
        sys.exit(1)

    # Stage 3: Create pet
    pet = test_create_pet(user)
    results["pet"] = pet is not None
    if not results["pet"]:
        print_header("TESTS FAILED - Cannot Create Pet")
        sys.exit(1)

    # Stage 4: Test marketplace valuation
    results["valuation"] = test_marketplace_valuation(pet)

    # Print final results
    print_header("TEST RESULTS SUMMARY")

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    print(f"\nTests Passed: {passed}/{total}")
    print("\nDetailed Results:")
    print(f"  [{'PASS' if results['connection'] else 'FAIL'}] Backend Connection")
    print(f"  [{'PASS' if results['user'] else 'FAIL'}] User Creation")
    print(f"  [{'PASS' if results['pet'] else 'FAIL'}] Pet Creation")
    print(f"  [{'PASS' if results['valuation'] else 'FAIL'}] Marketplace Valuation")

    if all(results.values()):
        print_header("ALL TESTS PASSED!")
        print("\nYour Guinea Games backend is fully operational!")
        print("You can now use the API client in your Pygame frontend.")
        print("\nNext steps:")
        print("  1. Import the API client: from api_client import api")
        print("  2. Check out api_example.py for usage examples")
        print("  3. Read API_INTEGRATION_GUIDE.md for detailed documentation")
        return 0
    else:
        print_header("SOME TESTS FAILED")
        print("\nPlease fix the issues above before integrating with the frontend.")
        print("Check the troubleshooting tips for each failed test.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
