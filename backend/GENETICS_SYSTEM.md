# Genetics System Documentation

## Overview

The Guinea Games genetics system implements realistic Mendelian inheritance for guinea pig breeding. It tracks alleles, calculates Punnett squares, and derives pet stats based on genetic code with randomization bias.

## Key Components

### 1. Database Tables

#### GENES
Defines genetic traits available in the game.
- `id`: Primary key
- `name`: Unique gene identifier (e.g., "color", "agility")
- `trait`: Human-readable trait name (e.g., "Coat Color", "Movement Speed")
- `description`: Detailed description of the trait
- `default_allele_id`: Default allele for new pets (optional)

#### ALLELES
Variants of genes with dominance relationships.
- `id`: Primary key
- `gene_id`: Foreign key to GENES
- `name`: Allele name (e.g., "Brown", "White")
- `symbol`: Single character symbol (e.g., "B", "b")
- `dominance_level`: Numeric dominance (higher = more dominant)
- `effect_value`: Numeric modifier for stats
- `description`: Details about the allele

#### PET_GENETICS
Genetic code (genotype) for each pet (diploid - 2 alleles per gene).
- `id`: Primary key
- `pet_id`: Foreign key to PETS (unique)
- `gene_id`: Foreign key to GENES
- `allele1_id`: First allele (Foreign key to ALLELES)
- `allele2_id`: Second allele (Foreign key to ALLELES)

#### OFFSPRING
Tracks breeding outcomes and inheritance records.
- `id`: Primary key
- `parent1_id`: First parent (Foreign key to PETS)
- `parent2_id`: Second parent (Foreign key to PETS)
- `child_id`: Offspring (Foreign key to PETS)
- `breeding_date`: When breeding occurred
- `punnett_square_data`: JSON with Punnett square calculations
- `inheritance_notes`: Text description of inheritance

### 2. Pet Model Extensions

The Pet model was extended with genetics fields:
```python
points: int = 0                    # Player-earned points
genetic_code: str = None           # Encoded genetic information
speed: int = 50                    # Base 50, modified by genetics
strength: int = 50                 # Base 50, modified by genetics
intelligence: int = 50             # Base 50, modified by genetics
endurance: int = 50                # Base 50, modified by genetics
```

## Core Classes

### GeneticCode
Handles encoding/decoding of genetic information.

**encode(pet_genetics)**
- Converts genetic records to compact string format
- Format: `GENE1:allele1-allele2;GENE2:allele1-allele2;...`
- Example: `color:Bb;size:LL;agility:Ff`

**decode(genetic_code)**
- Reverse of encode, converts string to structured data
- Returns: `Dict[gene_name, (allele1, allele2)]`

**generate_random_genetic_code(db, num_genes=5)**
- Creates random genetic code for new pets
- Selects alleles from available gene pool

### PunnettSquare
Implements classical Punnett square genetics.

**calculate(parent1_alleles, parent2_alleles)**
- Takes two tuples of allele symbols: `("B", "b")`, `("B", "B")`
- Returns:
  - `punnett_square`: 2x2 grid of possible combinations
  - `possible_offspring`: List of unique genotypes
  - `probabilities`: Percentage chance for each offspring genotype
  - `offspring_genotypes`: All 4 possible combinations (for randomization)

**get_phenotype(allele1, allele2)**
- Determines observable traits from genotype
- Considers dominance levels
- Handles co-dominance (blended effect)
- Returns phenotype, effect value, and inheritance type

### BreedingEngine
Main logic for breeding and offspring generation.

**breed(db, parent1, parent2, child_name, child_species, child_color, owner_id)**
- Main breeding function
- Steps:
  1. Validates both parents have genetic information
  2. For each gene pair:
     - Calculates Punnett square
     - Randomly selects offspring genotype
     - Records inheritance data
  3. Creates offspring pet with inherited genetics
  4. Calculates stats based on genetics
  5. Records breeding in OFFSPRING table
- Returns: `(offspring_pet, punnett_squares, inheritance_summary)`

**update_stats_from_genetics(db, pet)**
- Derives pet stats from genetic code
- Formula: `stat = 50 + (genetic_modifier * bias) + random_offset`
- Bias: 70% genetic, 30% random variation
- Clamps stats to 0-100 range

## Default Genes System

The system initializes with 5 default genes:

| Gene | Trait | Alleles | Effect |
|------|-------|---------|--------|
| **color** | Coat Color | B (Brown, +10), b (White, -10) | Visual trait |
| **size** | Body Size | L (Large, +15), l (Small, -15) | Affects strength |
| **agility** | Movement Speed | F (Fast, +20), f (Slow, -20) | Affects speed |
| **intelligence** | Cognitive Ability | S (Smart, +15), s (Simple, -15) | Affects intelligence |
| **stamina** | Energy Level | E (Energetic, +20), e (Lazy, -20) | Affects endurance |

## API Endpoints

### Gene Management
- `POST /genetics/genes/init` - Initialize default genes
- `POST /genetics/genes/` - Create custom gene
- `GET /genetics/genes/` - List all genes
- `GET /genetics/genes/{gene_id}` - Get gene with alleles

### Allele Management
- `POST /genetics/alleles/` - Create allele
- `GET /genetics/alleles/gene/{gene_id}` - List gene alleles

### Pet Genetics
- `POST /genetics/pet-genetics/` - Add genetics to pet
- `GET /genetics/pet-genetics/{pet_id}` - Get pet's genetic records
- `GET /genetics/pet-genetics-decoded/{pet_id}` - Get decoded genetic code

### Breeding
- `POST /genetics/breed/` - Breed two pets
  - Request: parent IDs, child details
  - Response: Offspring data, Punnett squares, stats, inheritance notes
- `GET /genetics/breeding-history/{pet_id}` - Get breeding history

### Punnett Squares
- `GET /genetics/punnett-square/{parent1_id}/{parent2_id}/{gene_id}` - Calculate for specific gene

### Stats
- `GET /genetics/pet-stats/{pet_id}` - Get pet's derived stats
- `GET /genetics/compare-stats/{pet1_id}/{pet2_id}` - Compare two pets

## Example Workflow

### 1. Initialize System
```bash
POST /genetics/genes/init
```

### 2. Create Pets with Genetics
```bash
# Create pet
POST /pets/ → pet_id: 1

# Add genetics (must have genes initialized first)
POST /genetics/pet-genetics/
{
  "pet_id": 1,
  "gene_id": 1,
  "allele1_id": 1,
  "allele2_id": 1
}
```

### 3. Breed Pets
```bash
POST /genetics/breed/
{
  "parent1_id": 1,
  "parent2_id": 2,
  "owner_id": 100,
  "child_name": "Fuzzy",
  "child_species": "guinea_pig",
  "child_color": "brown"
}
```

Response includes:
- Offspring pet ID and details
- Punnett squares for each gene
- Calculated stats
- Inheritance summary

### 4. View Inheritance
```bash
GET /genetics/pet-genetics-decoded/3
# Returns: "color:Bb;size:Ll;agility:Ff;intelligence:Ss;stamina:Ee"

GET /genetics/breeding-history/3
# Returns: Parent info, breeding date, inheritance notes
```

## Inheritance Rules

### Dominance
- **Homozygous Dominant** (e.g., BB): Expresses dominant phenotype
- **Heterozygous** (e.g., Bb): Expresses dominant phenotype
- **Homozygous Recessive** (e.g., bb): Expresses recessive phenotype
- **Co-dominant**: Both alleles expressed equally (blended effect)

### Probability Example
Parents: Bb × Bb (Brown heterozygous × Brown heterozygous)

Punnett Square:
```
      B    b
  B   BB   Bb
  b   Bb   bb
```

Outcomes:
- 25% BB (Homozygous Dominant)
- 50% Bb (Heterozygous)
- 25% bb (Homozygous Recessive)

Phenotypes:
- 75% Brown (dominant B)
- 25% White (recessive bb)

## Stat Calculation

### Formula
```
stat = baseline(50) + (genetic_modifier * randomization_bias) + random_offset
randomization_bias = 0.7  # 70% genetic, 30% random
```

### Example
Pet with genetics:
- Color (Bb): effect_value = 0 (co-dominant)
- Size (LL): effect_value = 15
- Agility (Ff): effect_value = 20 (heterozygous average = 10)
- Intelligence (SS): effect_value = 15
- Stamina (ee): effect_value = -20

Speed stat:
```
speed = 50 + (10 * 0.7) + random(-5, 5)
speed = 50 + 7 + random = 57-67
```

## Randomization and Bias

The system balances genetics with randomization:
- **70% Genetic Influence**: Stats primarily determined by genes
- **30% Random Variation**: Natural variation ensures unpredictability
- **Random Offset**: ±5 points for each stat

This ensures:
- Genetic traits are meaningful and heritable
- Identical genetics don't guarantee identical offspring stats
- Natural variation in population

## Schema Files

- **Database**: `backend/database/database.py` (tables defined here)
- **Models**: `backend/models.py` (SQLAlchemy ORM models)
- **Schemas**: `backend/schemas.py` (Pydantic validation schemas)
- **Genetics**: `backend/genetics.py` (Breeding logic, Punnett squares)
- **Router**: `backend/routes/genetics.py` (API endpoints)

## Future Enhancements

1. **Complex Traits**: Multi-gene traits (polygenic inheritance)
2. **Mutations**: Spontaneous allele changes
3. **Breeding Restrictions**: Cooldown periods, fertility tracking
4. **Genetic Compatibility**: Inbreeding detection
5. **Evolution Tracking**: Generational analysis
6. **Visual Genetics**: Phenotype-based sprite generation
7. **Trading**: Genetic material as tradeable resource
