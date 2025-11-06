# Genetics System Quick Start Guide

## Setup (One Time)

### 1. Initialize Genetics System
When the backend starts, the genetics system auto-initializes with 5 default genes:
- **color** - Coat color (Brown/White)
- **size** - Body size (Large/Small)
- **agility** - Movement speed (Fast/Slow)
- **intelligence** - Cognitive ability (Smart/Simple)
- **stamina** - Energy level (Energetic/Lazy)

Or manually:
```bash
curl -X POST http://localhost:8000/genetics/genes/init
```

## Creating Genetically-Diverse Pets

### Method 1: Manual Genetics
```bash
# 1. Create a pet
POST /pets/
{
  "owner_id": 1,
  "name": "Fluffy",
  "species": "guinea_pig",
  "color": "brown"
}
# Response: pet_id = 10

# 2. Add genetics (repeat for each gene)
POST /genetics/pet-genetics/
{
  "pet_id": 10,
  "gene_id": 1,           # color gene
  "allele1_id": 1,        # Brown allele
  "allele2_id": 2         # White allele (heterozygous)
}
```

### Method 2: Breeding (Recommended)
```bash
POST /genetics/breed/
{
  "parent1_id": 10,
  "parent2_id": 11,
  "owner_id": 1,
  "child_name": "Mittens",
  "child_species": "guinea_pig",
  "child_color": "brown"
}
```

Response includes:
- New offspring ID and stats
- Punnett squares for each gene
- Probability of each trait
- Inheritance summary

## Understanding Genetics

### Genetic Code
String format: `GENE:allele1-allele2;GENE2:allele1-allele2;...`

Example:
```
color:Bb;size:LL;agility:Ff;intelligence:Ss;stamina:ee
```

Meaning:
- **color:Bb** - Heterozygous (Brown/White carrier)
- **size:LL** - Homozygous dominant (Large)
- **agility:Ff** - Heterozygous (Fast/Slow carrier)
- **intelligence:Ss** - Heterozygous (Smart/Simple carrier)
- **stamina:ee** - Homozygous recessive (Lazy)

### Punnett Square
Shows all possible offspring from two parents.

Example: Brown (Bb) × Brown (Bb)
```
      B    b
  B   BB   Bb
  b   Bb   bb
```

Results:
- 75% Brown (BB or Bb = dominant)
- 25% White (bb = recessive)

### Phenotype vs Genotype
- **Genotype**: Actual alleles (Bb)
- **Phenotype**: Observable trait (Brown color)

## Querying Genetics

### Get Pet's Genetic Code
```bash
GET /genetics/pet-genetics-decoded/10
```
Response:
```json
{
  "pet_id": 10,
  "pet_name": "Fluffy",
  "genetic_code": "color:Bb;size:LL;agility:Ff;intelligence:Ss;stamina:ee",
  "decoded_genetics": {
    "color": ["B", "b"],
    "size": ["L", "L"],
    "agility": ["F", "f"],
    "intelligence": ["S", "s"],
    "stamina": ["e", "e"]
  }
}
```

### Get Pet Stats
```bash
GET /genetics/pet-stats/10
```
Response:
```json
{
  "speed": 65,
  "strength": 72,
  "intelligence": 58,
  "endurance": 45,
  "genetic_score": 60
}
```

### Compare Two Pets
```bash
GET /genetics/compare-stats/10/11
```
Useful for breeding decisions!

### Calculate Punnett Square
```bash
GET /genetics/punnett-square/10/11/1
```
(Pet 10 × Pet 11 for gene 1)

Shows exact probabilities before breeding.

## Breeding Recommendations

### For High Stats
1. Compare potential parents: `GET /genetics/compare-stats/{pet1_id}/{pet2_id}`
2. Check Punnett squares: `GET /genetics/punnett-square/{p1}/{p2}/{gene_id}`
3. Breed if probabilities are favorable
4. Track offspring stats

### Tracking Lineages
```bash
GET /genetics/breeding-history/10
```

Shows:
- All offspring from this pet
- All parents (if offspring)
- Breeding dates
- Inheritance notes

## Tips & Tricks

### 1. Dominant vs Recessive Traits
- **Dominant traits**: BB or Bb shows dominant phenotype
- **Recessive traits**: bb only (must be homozygous)
- Heterozygous (Bb) are "carriers" of recessive trait

### 2. Selective Breeding
To get specific trait (e.g., Fast speed):
1. Breed pets with "F" alleles
2. Target parents with agility gene: FF or Ff
3. Use Punnett squares to maximize "F" chances
4. Repeat with best offspring

### 3. Stat Prediction
Stats = 50 + genetic_effect + random(±5)
- Perfect genetics: ~70-100 stats
- Poor genetics: ~0-30 stats
- Average genetics: ~45-55 stats

### 4. Genetic Diversity
More diverse genes = better adaptability
- Mix homozygous and heterozygous parents
- Don't breed identical genetics
- Rotate breeding pairs

## API Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/genetics/genes/init` | POST | Initialize system |
| `/genetics/breed/` | POST | Breed two pets |
| `/genetics/pet-genetics/` | POST | Add genetics to pet |
| `/genetics/pet-genetics/{pet_id}` | GET | Get raw genetics |
| `/genetics/pet-genetics-decoded/{pet_id}` | GET | Get readable genetics |
| `/genetics/pet-stats/{pet_id}` | GET | Get derived stats |
| `/genetics/compare-stats/{p1}/{p2}` | GET | Compare two pets |
| `/genetics/punnett-square/{p1}/{p2}/{gene}` | GET | Calculate probability |
| `/genetics/breeding-history/{pet_id}` | GET | View lineage |
| `/genetics/genes/` | GET | List all genes |
| `/genetics/alleles/gene/{gene_id}` | GET | List gene alleles |

## Example: Complete Breeding Workflow

```bash
# 1. Check if genetics initialized
curl http://localhost:8000/genetics/genes/

# 2. Create two parent pets
curl -X POST http://localhost:8000/pets/ \
  -H "Content-Type: application/json" \
  -d '{"owner_id": 1, "name": "Dad", "species": "guinea_pig", "color": "brown"}'
# pet_id: 1

curl -X POST http://localhost:8000/pets/ \
  -H "Content-Type: application/json" \
  -d '{"owner_id": 1, "name": "Mom", "species": "guinea_pig", "color": "white"}'
# pet_id: 2

# 3. Add genetics to parents (repeat for all 5 genes)
curl -X POST http://localhost:8000/genetics/pet-genetics/ \
  -H "Content-Type: application/json" \
  -d '{"pet_id": 1, "gene_id": 1, "allele1_id": 1, "allele2_id": 1}'

# 4. Breed them
curl -X POST http://localhost:8000/genetics/breed/ \
  -H "Content-Type: application/json" \
  -d '{
    "parent1_id": 1,
    "parent2_id": 2,
    "owner_id": 1,
    "child_name": "Baby",
    "child_species": "guinea_pig",
    "child_color": "brown"
  }'

# 5. Check offspring genetics
curl http://localhost:8000/genetics/pet-genetics-decoded/3

# 6. Compare stats
curl http://localhost:8000/genetics/compare-stats/1/3
```

## Troubleshooting

**Q: "Parent lacks genetic information"**
A: Add genetics to pet first using `POST /genetics/pet-genetics/`

**Q: Stats all show 50**
A: Stats are calculated during breeding. New pets have defaults. Breed offspring for calculated stats.

**Q: Punnett square request fails**
A: Ensure both parents have genetics for that gene ID.

**Q: Can't add genetics to existing pet**
A: Pet may already have genetics for that gene. Use `GET /genetics/pet-genetics/{pet_id}` to check.
