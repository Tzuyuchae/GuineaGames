"""
Pricing and Rarity System for Guinea Pig Genetics
Calculates market value based on genetic rarity.
"""

from sqlalchemy.orm import Session
import models


class RarityCalculator:
    """Calculates rarity scores and pricing based on genetics"""

    @staticmethod
    def get_coat_phenotype(genetic_code: str) -> dict:
        """
        Extract coat color phenotype from genetic code.

        Args:
            genetic_code: Format "coat_color:BB;hair_length:Hh;speed:Ff;endurance:Ee"

        Returns:
            Dictionary with phenotype, genotype, and rarity info
        """
        genes = RarityCalculator.parse_genetic_code(genetic_code)
        coat_genotype = genes.get("coat_color", "WW")  # Default to white if not found

        # Parse alleles
        allele1 = coat_genotype[0]
        allele2 = coat_genotype[1]

        # Dominance order: B (3) > O (2) > W (1)
        dominance = {"B": 3, "O": 2, "W": 1}
        dom1 = dominance.get(allele1, 0)
        dom2 = dominance.get(allele2, 0)

        color_names = {"B": "Brown", "O": "Orange", "W": "White"}

        # Pure homozygous
        if allele1 == allele2:
            return {
                "phenotype": f"{color_names.get(allele1, 'Unknown')} (pure)",
                "genotype": coat_genotype,
                "is_pure": True,
                "rarity_bonus": 5  # Pure colors are rarer
            }

        # Heterozygous - incomplete dominance
        dominant = allele1 if dom1 > dom2 else allele2
        recessive = allele2 if dom1 > dom2 else allele1

        return {
            "phenotype": f"{color_names.get(dominant, 'Unknown')}-{color_names.get(recessive, 'Unknown')} mix",
            "genotype": coat_genotype,
            "is_pure": False,
            "rarity_bonus": 2  # Mixed colors are more common
        }

    @staticmethod
    def get_hair_type(genetic_code: str) -> dict:
        """
        Extract hair type from genetic code.

        Returns:
            Dictionary with hair type and rarity info
        """
        genes = RarityCalculator.parse_genetic_code(genetic_code)
        hair_genotype = genes.get("hair_length", "HH")  # Default to short

        is_fluffy = "h" in hair_genotype and hair_genotype.count("h") >= 1

        # hh (fluffy) is rarer
        is_homozygous_recessive = hair_genotype == "hh"

        return {
            "type": "fluffy" if is_fluffy else "short",
            "genotype": hair_genotype,
            "is_fluffy": is_fluffy,
            "rarity_bonus": 3 if is_homozygous_recessive else (1 if is_fluffy else 0)
        }

    @staticmethod
    def parse_genetic_code(genetic_code: str) -> dict:
        """
        Parse genetic code string into gene dictionary.

        Format: "coat_color:BB;hair_length:Hh;speed:Ff;endurance:Ee"
        """
        genes = {}
        if not genetic_code:
            return genes

        for gene_pair in genetic_code.split(";"):
            if ":" in gene_pair:
                gene_name, alleles = gene_pair.split(":")
                genes[gene_name.strip()] = alleles.strip()

        return genes

    @staticmethod
    def calculate_rarity_score(pet: models.Pet, db: Session) -> int:
        """
        Calculate rarity score (0-40+ points) based on:
        - Genotype rarity (homozygous vs heterozygous)
        - Coat color (pure colors are rarer)
        - Hair type (fluffy is rarer)
        - Stat quality

        Args:
            pet: Pet model instance
            db: Database session

        Returns:
            Rarity score as integer
        """
        score = 0

        if not pet.genetic_code:
            return score

        # Parse genetics
        genes = RarityCalculator.parse_genetic_code(pet.genetic_code)

        # 1. Coat color rarity (0-5 points)
        coat_info = RarityCalculator.get_coat_phenotype(pet.genetic_code)
        score += coat_info["rarity_bonus"]

        # 2. Hair type rarity (0-3 points)
        hair_info = RarityCalculator.get_hair_type(pet.genetic_code)
        score += hair_info["rarity_bonus"]

        # 3. Speed and Endurance rarity (0-8 points, 2 points each for homozygous)
        speed_genotype = genes.get("speed", "Ff")
        endurance_genotype = genes.get("endurance", "Ee")

        # Homozygous genes are rarer
        if speed_genotype in ["FF", "ff"]:
            score += 2
        else:
            score += 1

        if endurance_genotype in ["EE", "ee"]:
            score += 2
        else:
            score += 1

        # 4. Stat quality bonus (0-10 points)
        # Higher average stats indicate rare beneficial alleles
        stat_avg = (pet.speed + pet.endurance) / 2
        if stat_avg >= 80:
            score += 5
        elif stat_avg >= 70:
            score += 3
        elif stat_avg >= 60:
            score += 1

        return score

    @staticmethod
    def get_rarity_tier(rarity_score: int) -> str:
        """
        Classify rarity into tiers based on score.

        Args:
            rarity_score: Calculated rarity score

        Returns:
            Tier name: "Common", "Uncommon", "Rare", or "Legendary"
        """
        if rarity_score >= 16:
            return "Legendary"
        elif rarity_score >= 11:
            return "Rare"
        elif rarity_score >= 6:
            return "Uncommon"
        else:
            return "Common"

    @staticmethod
    def calculate_market_value(pet: models.Pet, db: Session) -> int:
        """
        Calculate market value based on rarity and stats.

        Formula:
        Base = tier_base_price
        Price = Base × stat_multiplier × color_multiplier × hair_multiplier

        Args:
            pet: Pet model instance
            db: Database session

        Returns:
            Market value as integer
        """
        # Calculate rarity if not already done
        if pet.rarity_score == 0:
            pet.rarity_score = RarityCalculator.calculate_rarity_score(pet, db)
            pet.rarity_tier = RarityCalculator.get_rarity_tier(pet.rarity_score)

        # Base prices by tier
        base_prices = {
            "Common": 100,
            "Uncommon": 500,
            "Rare": 2000,
            "Legendary": 10000
        }

        tier = pet.rarity_tier or "Common"
        base_price = base_prices.get(tier, 100)

        # 1. Stat multiplier (0.5x - 2.0x)
        # Average of speed and endurance (0-100 range)
        stat_avg = (pet.speed + pet.endurance) / 2
        stat_multiplier = 0.5 + (stat_avg / 100) * 1.5  # ranges 0.5 to 2.0

        # 2. Coat color premium
        coat_info = RarityCalculator.get_coat_phenotype(pet.genetic_code or "")
        if coat_info["is_pure"]:
            color_multiplier = 1.5  # Pure colors are more valuable
        else:
            color_multiplier = 1.0

        # 3. Hair type premium (fluffy is more desirable aesthetically)
        hair_info = RarityCalculator.get_hair_type(pet.genetic_code or "")
        if hair_info["is_fluffy"]:
            hair_multiplier = 1.3
        else:
            hair_multiplier = 1.0

        # Calculate final price
        price = int(base_price * stat_multiplier * color_multiplier * hair_multiplier)

        return max(price, 50)  # Minimum price of 50

    @staticmethod
    def calculate_and_store_valuation(pet: models.Pet, db: Session) -> dict:
        """
        Calculate rarity score and market value, update pet, and return full valuation info.

        Args:
            pet: Pet model instance
            db: Database session (should have pet attached)

        Returns:
            Dictionary with valuation details
        """
        # Calculate rarity
        pet.rarity_score = RarityCalculator.calculate_rarity_score(pet, db)
        pet.rarity_tier = RarityCalculator.get_rarity_tier(pet.rarity_score)

        # Calculate market value
        pet.market_value = RarityCalculator.calculate_market_value(pet, db)

        # Get phenotypes
        coat_info = RarityCalculator.get_coat_phenotype(pet.genetic_code or "")
        hair_info = RarityCalculator.get_hair_type(pet.genetic_code or "")

        # Update phenotype fields
        pet.color_phenotype = coat_info["phenotype"]
        pet.hair_type = hair_info["type"]

        db.add(pet)

        return {
            "rarity_score": pet.rarity_score,
            "rarity_tier": pet.rarity_tier,
            "market_value": pet.market_value,
            "coat_color": coat_info["phenotype"],
            "hair_type": hair_info["type"],
            "speed": pet.speed,
            "endurance": pet.endurance
        }
