"""
Seed test pets with various genetics combinations and rarity levels.
Creates sample pets across all rarity tiers for marketplace testing.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database import SessionLocal
import models
from genetics import BreedingEngine, GeneticCode
from pricing import RarityCalculator

def seed_test_pets():
    """Create test pets with diverse genetics for marketplace testing"""
    db = SessionLocal()

    # First, clear existing test pets
    db.query(models.Pet).delete()
    db.query(models.Offspring).delete()
    db.query(models.PetMarketplace).delete()
    db.query(models.PetSalesHistory).delete()
    db.commit()

    # Create test users
    test_users = [
        models.User(
            username="breeder1",
            email="breeder1@test.com",
            password_hash="hashed_password_1",
            balance=50000
        ),
        models.User(
            username="breeder2",
            email="breeder2@test.com",
            password_hash="hashed_password_2",
            balance=30000
        ),
        models.User(
            username="collector",
            email="collector@test.com",
            password_hash="hashed_password_3",
            balance=100000
        ),
    ]

    for user in test_users:
        db.add(user)

    db.commit()

    # Get genes for creating pets
    genes = db.query(models.Gene).all()
    if not genes:
        print("Error: No genes found. Run genetics initialization first.")
        return

    gene_map = {g.name: g for g in genes}
    coat_gene = gene_map.get("coat_color")
    hair_gene = gene_map.get("hair_length")
    speed_gene = gene_map.get("speed")
    endurance_gene = gene_map.get("endurance")

    if not all([coat_gene, hair_gene, speed_gene, endurance_gene]):
        print("Error: Missing required genes")
        return

    # Define test pet configurations
    # Each config: (name, coat_genotype, hair_genotype, speed_genotype, endurance_genotype, owner_id)
    test_configs = [
        # COMMON PETS (heterozygous, regular stats)
        ("Fluffy", coat_gene, "OW", hair_gene, "Hh", speed_gene, "Ff", endurance_gene, "Ee", 1),
        ("Snowball", coat_gene, "OW", hair_gene, "Hh", speed_gene, "Ff", endurance_gene, "Ee", 1),

        # UNCOMMON PETS (1-2 homozygous traits)
        ("Speedy", coat_gene, "BB", hair_gene, "Hh", speed_gene, "FF", endurance_gene, "Ee", 1),
        ("Energy", coat_gene, "OO", hair_gene, "Hh", speed_gene, "Ff", endurance_gene, "EE", 1),

        # RARE PETS (multiple homozygous or special combos)
        ("Fuzzball", coat_gene, "WW", hair_gene, "hh", speed_gene, "FF", endurance_gene, "EE", 2),
        ("Chocolate", coat_gene, "BB", hair_gene, "HH", speed_gene, "FF", endurance_gene, "EE", 2),
        ("Shadow", coat_gene, "WW", hair_gene, "hh", speed_gene, "ff", endurance_gene, "EE", 2),

        # LEGENDARY PETS (all homozygous + high stats)
        ("Perfection", coat_gene, "BB", hair_gene, "hh", speed_gene, "FF", endurance_gene, "EE", 3),
        ("Golden", coat_gene, "BB", hair_gene, "hh", speed_gene, "FF", endurance_gene, "EE", 3),
    ]

    # Helper to get allele by symbol
    def get_allele(gene, symbol):
        return db.query(models.Allele).filter(
            models.Allele.gene_id == gene.id,
            models.Allele.symbol == symbol
        ).first()

    # Create pets with genetics
    created_pets = []

    for i, config in enumerate(test_configs):
        name, coat_g, coat_geno, hair_g, hair_geno, speed_g, speed_geno, endurance_g, endurance_geno, owner_id = config

        pet = models.Pet(
            owner_id=owner_id,
            name=name,
            species="guinea_pig",
            color=name,
            age_days=30 + i * 10,
            health=100,
            happiness=100,
            hunger=0,
            cleanliness=100,
            points=0
        )
        db.add(pet)
        db.flush()

        # Create genetics for pet
        genetics_list = []

        # Coat color
        a1 = get_allele(coat_g, coat_geno[0])
        a2 = get_allele(coat_g, coat_geno[1])
        if a1 and a2:
            pg = models.PetGenetics(
                pet_id=pet.id,
                gene_id=coat_g.id,
                allele1_id=a1.id,
                allele2_id=a2.id
            )
            db.add(pg)
            genetics_list.append(pg)

        # Hair length
        a1 = get_allele(hair_g, hair_geno[0])
        a2 = get_allele(hair_g, hair_geno[1])
        if a1 and a2:
            pg = models.PetGenetics(
                pet_id=pet.id,
                gene_id=hair_g.id,
                allele1_id=a1.id,
                allele2_id=a2.id
            )
            db.add(pg)
            genetics_list.append(pg)

        # Speed
        a1 = get_allele(speed_g, speed_geno[0])
        a2 = get_allele(speed_g, speed_geno[1])
        if a1 and a2:
            pg = models.PetGenetics(
                pet_id=pet.id,
                gene_id=speed_g.id,
                allele1_id=a1.id,
                allele2_id=a2.id
            )
            db.add(pg)
            genetics_list.append(pg)

        # Endurance
        a1 = get_allele(endurance_g, endurance_geno[0])
        a2 = get_allele(endurance_g, endurance_geno[1])
        if a1 and a2:
            pg = models.PetGenetics(
                pet_id=pet.id,
                gene_id=endurance_g.id,
                allele1_id=a1.id,
                allele2_id=a2.id
            )
            db.add(pg)
            genetics_list.append(pg)

        db.flush()

        # Set genetic code
        pet.genetic_code = GeneticCode.encode(genetics_list)

        # Update stats from genetics
        BreedingEngine.update_stats_from_genetics(db, pet)

        # Calculate rarity and valuation
        valuation = RarityCalculator.calculate_and_store_valuation(pet, db)

        print(f"Created {name}: Rarity={pet.rarity_tier}, Score={pet.rarity_score}, Value={pet.market_value}")

        created_pets.append(pet)

    db.commit()

    # List some pets for sale (50% of them)
    for i, pet in enumerate(created_pets):
        if i % 2 == 0 and pet.owner_id != 3:  # Collector doesn't list
            listing = models.PetMarketplace(
                pet_id=pet.id,
                seller_id=pet.owner_id,
                asking_price=pet.market_value + (50 if i % 3 == 0 else -30)  # Vary prices
            )
            pet.for_sale = 1
            pet.asking_price = listing.asking_price
            db.add(listing)
            print(f"Listed {pet.name} for {listing.asking_price} coins")

    db.commit()

    print(f"\n✅ Successfully seeded {len(created_pets)} test pets")
    print("Pets created across all rarity tiers for marketplace testing")

    db.close()


if __name__ == "__main__":
    seed_test_pets()
