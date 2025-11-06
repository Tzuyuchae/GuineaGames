"""
Genetics system for guinea pig breeding simulation.
Implements Mendelian inheritance, Punnett squares, and stat derivation from genetic code.
"""

import random
import json
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
import models, schemas
from pricing import RarityCalculator

# =====================
# PUNNETT SQUARE LOGIC
# =====================

class PunnettSquare:
    """Handles Punnett square calculations for single gene inheritance"""

    @staticmethod
    def calculate(parent1_alleles: Tuple[str, str], parent2_alleles: Tuple[str, str]) -> Dict:
        """
        Calculate Punnett square for two parents.
        Handles both 2-allele and 3-allele (multi-allelic) genes.

        Args:
            parent1_alleles: Tuple of (allele1_symbol, allele2_symbol) for parent 1
            parent2_alleles: Tuple of (allele1_symbol, allele2_symbol) for parent 2

        Returns:
            Dictionary with punnett square, probabilities, and possible offspring
        """
        # Create 4x1 grid (parent1 gametes x parent2 gametes)
        p1_alleles = list(parent1_alleles)
        p2_alleles = list(parent2_alleles)

        punnett_grid = []
        offspring_genotypes = []

        # Generate all possible combinations
        for p1_allele in p1_alleles:
            row = []
            for p2_allele in p2_alleles:
                # Sort alphabetically for consistent representation (B before O before W)
                genotype = tuple(sorted([p1_allele, p2_allele]))
                row.append("".join(genotype))
                offspring_genotypes.append("".join(genotype))
            punnett_grid.append(row)

        # Calculate probabilities
        genotype_counts = {}
        for genotype in offspring_genotypes:
            genotype_counts[genotype] = genotype_counts.get(genotype, 0) + 1

        probabilities = {genotype: (count / len(offspring_genotypes)) * 100
                        for genotype, count in genotype_counts.items()}

        return {
            "punnett_square": punnett_grid,
            "possible_offspring": list(genotype_counts.keys()),
            "probabilities": probabilities,
            "offspring_genotypes": offspring_genotypes
        }

    @staticmethod
    def get_phenotype(allele1: models.Allele, allele2: models.Allele, gene_name: str = None) -> Dict:
        """
        Determine phenotype from two alleles based on dominance.
        Handles incomplete dominance for coat color gene (B, O, W).

        Args:
            allele1: First allele (SQLAlchemy model)
            allele2: Second allele (SQLAlchemy model)
            gene_name: Name of the gene (used for coat color special handling)

        Returns:
            Dictionary with phenotype and effect value
        """
        # Special handling for coat_color gene with 3 alleles and incomplete dominance
        if gene_name == "coat_color":
            a1_sym = allele1.symbol
            a2_sym = allele2.symbol

            # Dominance hierarchy: B > O > W
            dominance_order = {"B": 3, "O": 2, "W": 1}
            a1_dom = dominance_order.get(a1_sym, 0)
            a2_dom = dominance_order.get(a2_sym, 0)

            # Pure homozygous
            if a1_sym == a2_sym:
                return {
                    "phenotype": f"{allele1.name} (pure)",
                    "genotype": f"{a1_sym}{a2_sym}",
                    "effect_value": allele1.effect_value,
                    "inheritance_type": "homozygous",
                    "is_pure": True
                }

            # Heterozygous - incomplete dominance
            avg_effect = (allele1.effect_value + allele2.effect_value) / 2
            dominant = allele1 if a1_dom > a2_dom else allele2
            recessive = allele2 if a1_dom > a2_dom else allele1

            return {
                "phenotype": f"{dominant.name}-{recessive.name} mix",
                "genotype": "".join(sorted([a1_sym, a2_sym])),
                "effect_value": int(avg_effect),
                "inheritance_type": "heterozygous",
                "is_pure": False
            }

        # Standard dominance for 2-allele genes
        if allele1.dominance_level > allele2.dominance_level:
            dominant = allele1
            recessive = allele2
        elif allele2.dominance_level > allele1.dominance_level:
            dominant = allele2
            recessive = allele1
        else:
            # Co-dominant: blend effect values
            avg_effect = (allele1.effect_value + allele2.effect_value) / 2
            return {
                "phenotype": f"{allele1.symbol}/{allele2.symbol}",
                "effect_value": int(avg_effect),
                "inheritance_type": "co-dominant"
            }

        return {
            "phenotype": dominant.symbol,
            "effect_value": dominant.effect_value,
            "inheritance_type": "dominant"
        }


# =====================
# GENETIC CODE MANAGEMENT
# =====================

class GeneticCode:
    """Manages encoding and decoding of genetic information"""

    @staticmethod
    def encode(pet_genetics: List[models.PetGenetics]) -> str:
        """
        Encode pet's genetic information into a compact string.
        Format: GENE1:allele1-allele2;GENE2:allele1-allele2;...

        Args:
            pet_genetics: List of PetGenetics records

        Returns:
            Encoded genetic code string
        """
        genetic_codes = []
        for pg in pet_genetics:
            code = f"{pg.gene.name}:{pg.allele1.symbol}-{pg.allele2.symbol}"
            genetic_codes.append(code)

        return ";".join(genetic_codes)

    @staticmethod
    def decode(genetic_code: str) -> Dict[str, Tuple[str, str]]:
        """
        Decode genetic code string into structured data.

        Args:
            genetic_code: Encoded genetic code string

        Returns:
            Dictionary mapping gene names to allele tuples
        """
        genes = {}
        for gene_pair in genetic_code.split(";"):
            if ":" in gene_pair:
                gene_name, alleles = gene_pair.split(":")
                allele1, allele2 = alleles.split("-")
                genes[gene_name] = (allele1, allele2)

        return genes

    @staticmethod
    def generate_random_genetic_code(db: Session, num_genes: int = 5) -> str:
        """
        Generate a random genetic code for a new pet.

        Args:
            db: Database session
            num_genes: Number of genes to include

        Returns:
            Encoded genetic code string
        """
        genes = db.query(models.Gene).limit(num_genes).all()
        genetic_codes = []

        for gene in genes:
            if gene.alleles:
                # Pick two random alleles for diploid genotype
                allele1 = random.choice(gene.alleles)
                allele2 = random.choice(gene.alleles)
                code = f"{gene.name}:{allele1.symbol}-{allele2.symbol}"
                genetic_codes.append(code)

        return ";".join(genetic_codes) if genetic_codes else ""


# =====================
# BREEDING LOGIC
# =====================

class BreedingEngine:
    """Handles breeding calculations and offspring generation"""

    @staticmethod
    def breed(db: Session, parent1: models.Pet, parent2: models.Pet,
              child_name: str, child_species: str, child_color: str,
              owner_id: int) -> Tuple[models.Pet, List[Dict], str]:
        """
        Breed two pets and generate offspring with inherited genetics.

        Args:
            db: Database session
            parent1: First parent pet
            parent2: Second parent pet
            child_name: Name for offspring
            child_species: Species for offspring
            child_color: Color for offspring
            owner_id: Owner ID for offspring

        Returns:
            Tuple of (offspring_pet, punnett_squares, inheritance_summary)
        """
        # Get genetic information for both parents
        parent1_genetics = db.query(models.PetGenetics).filter(
            models.PetGenetics.pet_id == parent1.id
        ).all()

        parent2_genetics = db.query(models.PetGenetics).filter(
            models.PetGenetics.pet_id == parent2.id
        ).all()

        if not parent1_genetics or not parent2_genetics:
            raise ValueError("One or both parents lack genetic information")

        # Calculate Punnett squares for each gene
        punnett_squares = []
        offspring_alleles = {}
        inheritance_notes = []

        for p1_gene, p2_gene in zip(parent1_genetics, parent2_genetics):
            if p1_gene.gene_id != p2_gene.gene_id:
                continue

            gene = p1_gene.gene
            p1_alleles = (p1_gene.allele1.symbol, p1_gene.allele2.symbol)
            p2_alleles = (p2_gene.allele1.symbol, p2_gene.allele2.symbol)

            # Calculate Punnett square
            ps_result = PunnettSquare.calculate(p1_alleles, p2_alleles)

            # Randomly select offspring genotype from possibilities
            offspring_genotype = random.choice(ps_result["offspring_genotypes"])

            # Find corresponding alleles for offspring
            allele_symbols = list(offspring_genotype)
            allele1_obj = db.query(models.Allele).filter(
                models.Allele.gene_id == gene.id,
                models.Allele.symbol == allele_symbols[0]
            ).first()

            allele2_obj = db.query(models.Allele).filter(
                models.Allele.gene_id == gene.id,
                models.Allele.symbol == allele_symbols[1]
            ).first()

            if allele1_obj and allele2_obj:
                offspring_alleles[gene.id] = (allele1_obj, allele2_obj)

            # Record Punnett square
            punnett_squares.append({
                "gene_name": gene.name,
                "parent1_genotype": "".join(p1_alleles),
                "parent2_genotype": "".join(p2_alleles),
                "possible_offspring": ps_result["possible_offspring"],
                "probabilities": ps_result["probabilities"],
                "punnett_square": ps_result["punnett_square"],
                "offspring_genotype": offspring_genotype
            })

            inheritance_notes.append(
                f"{gene.trait}: {offspring_genotype} "
                f"(from {parent1.name}:{p1_alleles[0]}/{p1_alleles[1]} x "
                f"{parent2.name}:{p2_alleles[0]}/{p2_alleles[1]})"
            )

        # Create offspring pet
        offspring = models.Pet(
            owner_id=owner_id,
            name=child_name,
            species=child_species,
            color=child_color
        )
        db.add(offspring)
        db.flush()  # Get offspring ID

        # Create genetics for offspring
        for gene_id, (allele1, allele2) in offspring_alleles.items():
            pet_genetics = models.PetGenetics(
                pet_id=offspring.id,
                gene_id=gene_id,
                allele1_id=allele1.id,
                allele2_id=allele2.id
            )
            db.add(pet_genetics)

        # Set offspring genetic code
        offspring_genetics = db.query(models.PetGenetics).filter(
            models.PetGenetics.pet_id == offspring.id
        ).all()
        offspring.genetic_code = GeneticCode.encode(offspring_genetics)

        # Calculate stats based on genetics
        BreedingEngine.update_stats_from_genetics(db, offspring)

        # Calculate rarity score and market value
        valuation = RarityCalculator.calculate_and_store_valuation(offspring, db)

        # Create offspring record
        inheritance_summary = " | ".join(inheritance_notes)
        offspring_record = models.Offspring(
            parent1_id=parent1.id,
            parent2_id=parent2.id,
            child_id=offspring.id,
            punnett_square_data=json.dumps(punnett_squares),
            inheritance_notes=inheritance_summary
        )
        db.add(offspring_record)

        db.commit()
        db.refresh(offspring)

        return offspring, punnett_squares, inheritance_summary

    @staticmethod
    def update_stats_from_genetics(db: Session, pet: models.Pet) -> None:
        """
        Calculate and update pet stats based on genetic code.
        Stats influenced by allele effect values.
        Only uses speed and endurance stats.

        Args:
            db: Database session
            pet: Pet to update stats for
        """
        pet_genetics = db.query(models.PetGenetics).filter(
            models.PetGenetics.pet_id == pet.id
        ).all()

        if not pet_genetics:
            return

        # Calculate stat modifiers from genetics
        stat_modifiers = {
            "speed": 0,
            "endurance": 0
        }

        # Map genes to stats
        gene_stat_mapping = {
            "speed": ["speed", "agility", "movement"],
            "endurance": ["endurance", "stamina", "energy"]
        }

        for pg in pet_genetics:
            gene_trait = pg.gene.name.lower()  # Use gene name for mapping

            # Determine phenotype and its effect
            phenotype_info = PunnettSquare.get_phenotype(pg.allele1, pg.allele2, gene_name=pg.gene.name)
            effect_value = phenotype_info["effect_value"]

            # Apply to relevant stats
            for stat, trait_names in gene_stat_mapping.items():
                if any(trait in gene_trait for trait in trait_names):
                    stat_modifiers[stat] += effect_value

        # Apply modifiers with bias towards 50 (baseline)
        # Randomization bias ensures variation (70% genetic, 30% random)
        randomization_bias = 0.7

        pet.speed = int(50 + (stat_modifiers["speed"] * randomization_bias) +
                       random.randint(-5, 5))
        pet.endurance = int(50 + (stat_modifiers["endurance"] * randomization_bias) +
                           random.randint(-5, 5))

        # Clamp stats between 0-100
        pet.speed = max(0, min(100, pet.speed))
        pet.endurance = max(0, min(100, pet.endurance))


# =====================
# GENETICS INITIALIZATION
# =====================

def initialize_genetics_system(db: Session) -> None:
    """
    Initialize the genetics system with default genes and alleles.
    Only runs if no genes exist.

    4 genes total:
    - coat_color: 3 alleles (B=Brown, O=Orange, W=White) with incomplete dominance
    - hair_length: 2 alleles (H=Short, h=Fluffy)
    - speed: 2 alleles (F=Fast, f=Slow)
    - endurance: 2 alleles (E=Energetic, e=Lazy)

    Args:
        db: Database session
    """
    existing_genes = db.query(models.Gene).count()
    if existing_genes > 0:
        return

    # Define base genes and their alleles
    genetics_data = [
        {
            "name": "coat_color",
            "trait": "Coat Color",
            "description": "Determines guinea pig coat color with 3 possible colors",
            "alleles": [
                {"name": "Brown", "symbol": "B", "dominance": 3, "effect": 20},
                {"name": "Orange", "symbol": "O", "dominance": 2, "effect": 10},
                {"name": "White", "symbol": "W", "dominance": 1, "effect": 0},
            ]
        },
        {
            "name": "hair_length",
            "trait": "Hair Length",
            "description": "Determines hair length (short vs fluffy/long)",
            "alleles": [
                {"name": "Short", "symbol": "H", "dominance": 2, "effect": 5},
                {"name": "Fluffy", "symbol": "h", "dominance": 1, "effect": 15},
            ]
        },
        {
            "name": "speed",
            "trait": "Movement Speed",
            "description": "Affects movement speed and agility",
            "alleles": [
                {"name": "Fast", "symbol": "F", "dominance": 2, "effect": 20},
                {"name": "Slow", "symbol": "f", "dominance": 1, "effect": -20},
            ]
        },
        {
            "name": "endurance",
            "trait": "Energy Level",
            "description": "Affects endurance and stamina",
            "alleles": [
                {"name": "Energetic", "symbol": "E", "dominance": 2, "effect": 20},
                {"name": "Lazy", "symbol": "e", "dominance": 1, "effect": -20},
            ]
        }
    ]

    for gene_data in genetics_data:
        gene = models.Gene(
            name=gene_data["name"],
            trait=gene_data["trait"],
            description=gene_data["description"]
        )
        db.add(gene)
        db.flush()

        for allele_data in gene_data["alleles"]:
            allele = models.Allele(
                gene_id=gene.id,
                name=allele_data["name"],
                symbol=allele_data["symbol"],
                dominance_level=allele_data["dominance"],
                effect_value=allele_data["effect"],
                description=f"{allele_data['name']} allele for {gene_data['trait']}"
            )
            db.add(allele)
            db.flush()

            # Set default allele for gene (first one)
            if not gene.default_allele_id:
                gene.default_allele_id = allele.id

        db.add(gene)

    db.commit()
