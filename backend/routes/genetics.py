from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, json, traceback
from genetics import BreedingEngine, GeneticCode, PunnettSquare, initialize_genetics_system

router = APIRouter(prefix="/genetics", tags=["Genetics"])

# =====================
# GENE ENDPOINTS
# =====================

@router.post("/genes/init")
def initialize_genetics(db: Session = Depends(get_db)):
    """Initialize the genetics system with default genes and alleles"""
    try:
        initialize_genetics_system(db)
        genes = db.query(models.Gene).all()
        return {
            "message": "Genetics system initialized successfully",
            "genes_created": len(genes),
            "genes": [{"id": g.id, "name": g.name, "trait": g.trait} for g in genes]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")

@router.post("/genes/", response_model=schemas.Gene)
def create_gene(gene: schemas.GeneCreate, db: Session = Depends(get_db)):
    """Create a new gene"""
    db_gene = models.Gene(
        name=gene.name,
        trait=gene.trait,
        description=gene.description
    )
    db.add(db_gene)
    db.commit()
    db.refresh(db_gene)
    return db_gene

@router.get("/genes/", response_model=list[schemas.Gene])
def get_all_genes(db: Session = Depends(get_db)):
    """Get all genes"""
    return db.query(models.Gene).all()

@router.get("/genes/{gene_id}", response_model=schemas.Gene)
def get_gene(gene_id: int, db: Session = Depends(get_db)):
    """Get a specific gene with its alleles"""
    gene = db.query(models.Gene).filter(models.Gene.id == gene_id).first()
    if not gene:
        raise HTTPException(status_code=404, detail="Gene not found")
    return gene

# =====================
# ALLELE ENDPOINTS
# =====================

@router.post("/alleles/", response_model=schemas.Allele)
def create_allele(allele: schemas.AlleleCreate, db: Session = Depends(get_db)):
    """Create a new allele for a gene"""
    gene = db.query(models.Gene).filter(models.Gene.id == allele.gene_id).first()
    if not gene:
        raise HTTPException(status_code=404, detail="Gene not found")

    db_allele = models.Allele(
        gene_id=allele.gene_id,
        name=allele.name,
        symbol=allele.symbol,
        dominance_level=allele.dominance_level,
        effect_value=allele.effect_value,
        description=allele.description
    )
    db.add(db_allele)
    db.commit()
    db.refresh(db_allele)
    return db_allele

@router.get("/alleles/gene/{gene_id}", response_model=list[schemas.Allele])
def get_gene_alleles(gene_id: int, db: Session = Depends(get_db)):
    """Get all alleles for a specific gene"""
    alleles = db.query(models.Allele).filter(models.Allele.gene_id == gene_id).all()
    return alleles

# =====================
# PET GENETICS ENDPOINTS
# =====================

@router.post("/pet-genetics/", response_model=schemas.PetGenetics)
def create_pet_genetics(genetics: schemas.PetGeneticsCreate, db: Session = Depends(get_db)):
    """Add genetic information to a pet"""
    pet = db.query(models.Pet).filter(models.Pet.id == genetics.pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    # Check if pet already has genetics for this gene
    existing = db.query(models.PetGenetics).filter(
        models.PetGenetics.pet_id == genetics.pet_id,
        models.PetGenetics.gene_id == genetics.gene_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Pet already has genetics for this gene")

    db_genetics = models.PetGenetics(
        pet_id=genetics.pet_id,
        gene_id=genetics.gene_id,
        allele1_id=genetics.allele1_id,
        allele2_id=genetics.allele2_id
    )
    db.add(db_genetics)
    db.commit()
    db.refresh(db_genetics)

    # Update pet's genetic code
    all_genetics = db.query(models.PetGenetics).filter(models.PetGenetics.pet_id == genetics.pet_id).all()
    pet.genetic_code = GeneticCode.encode(all_genetics)
    db.commit()

    return db_genetics

@router.get("/pet-genetics/{pet_id}", response_model=list[schemas.PetGenetics])
def get_pet_genetics(pet_id: int, db: Session = Depends(get_db)):
    """Get genetic information for a pet"""
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    return db.query(models.PetGenetics).filter(models.PetGenetics.pet_id == pet_id).all()

@router.get("/pet-genetics-decoded/{pet_id}")
def get_decoded_genetics(pet_id: int, db: Session = Depends(get_db)):
    """Get decoded genetic information for a pet"""
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    if not pet.genetic_code:
        raise HTTPException(status_code=404, detail="Pet has no genetic code")

    decoded = GeneticCode.decode(pet.genetic_code)
    return {
        "pet_id": pet_id,
        "pet_name": pet.name,
        "genetic_code": pet.genetic_code,
        "decoded_genetics": decoded
    }

# =====================
# BREEDING ENDPOINTS
# =====================

@router.post("/breed/", response_model=schemas.BreedingOutcome)
def breed_pets(breeding_request: schemas.BreedingRequest, db: Session = Depends(get_db)):
    """Breed two pets and generate offspring with inherited genetics"""
    try:
        # Verify both parents exist
        parent1 = db.query(models.Pet).filter(models.Pet.id == breeding_request.parent1_id).first()
        parent2 = db.query(models.Pet).filter(models.Pet.id == breeding_request.parent2_id).first()

        if not parent1 or not parent2:
            raise HTTPException(status_code=404, detail="One or both parents not found")

        # Use defaults if optional fields are missing
        child_species = breeding_request.child_species if breeding_request.child_species else "Guinea Pig"
        child_color = breeding_request.child_color if breeding_request.child_color else "Mixed"
        
        # --- FIX: Ensure child_name is passed explicitly from request ---
        # The BreedingEngine.breed function needs to accept the custom name
        offspring, punnett_squares, inheritance_summary = BreedingEngine.breed(
            db,
            parent1,
            parent2,
            breeding_request.child_name, # <--- Passing the custom name here
            child_species,
            child_color,
            breeding_request.owner_id
        )

        # Convert punnett squares to response format
        punnett_responses = []
        for ps in punnett_squares:
            punnett_responses.append(schemas.PunnettSquareResult(
                gene_name=ps["gene_name"],
                parent1_genotype=ps["parent1_genotype"],
                parent2_genotype=ps["parent2_genotype"],
                possible_offspring=ps["possible_offspring"],
                probabilities=ps["probabilities"],
                punnett_square=ps["punnett_square"]
            ))

        # Only use stats that exist in models.Pet
        estimated_stats = {
            "speed": offspring.speed,
            "endurance": offspring.endurance,
            "rarity": offspring.rarity_score
        }

        return schemas.BreedingOutcome(
            child_id=offspring.id,
            child_name=offspring.name, # This will now reflect the custom name
            child_genetics=offspring.genetic_code,
            punnett_squares=punnett_responses,
            estimated_stats=estimated_stats,
            inheritance_summary=inheritance_summary
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print("CRITICAL BREEDING ERROR:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Breeding failed: {str(e)}")

@router.get("/breeding-history/{pet_id}")
def get_breeding_history(pet_id: int, db: Session = Depends(get_db)):
    """Get breeding history for a pet (as parent or offspring)"""
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    # Get records where pet is a parent
    as_parent1 = db.query(models.Offspring).filter(models.Offspring.parent1_id == pet_id).all()
    as_parent2 = db.query(models.Offspring).filter(models.Offspring.parent2_id == pet_id).all()

    # Get record where pet is offspring
    as_offspring = db.query(models.Offspring).filter(models.Offspring.child_id == pet_id).first()

    breeding_data = {
        "pet_id": pet_id,
        "pet_name": pet.name,
        "offspring_as_parent": [
            {
                "breeding_id": o.id,
                "parent1": o.parent1.name,
                "parent2": o.parent2.name,
                "child": o.child.name,
                "breeding_date": o.breeding_date,
                "inheritance_notes": o.inheritance_notes
            }
            for o in as_parent1 + as_parent2
        ],
        "parentage": None
    }

    if as_offspring:
        breeding_data["parentage"] = {
            "parent1": as_offspring.parent1.name,
            "parent2": as_offspring.parent2.name,
            "breeding_date": as_offspring.breeding_date,
            "inheritance_notes": as_offspring.inheritance_notes
        }

    return breeding_data

# =====================
# PUNNETT SQUARE ENDPOINTS
# =====================

@router.get("/punnett-square/{parent1_id}/{parent2_id}/{gene_id}")
def calculate_punnett_square(parent1_id: int, parent2_id: int, gene_id: int, db: Session = Depends(get_db)):
    """Calculate Punnett square for two parents for a specific gene"""
    parent1 = db.query(models.Pet).filter(models.Pet.id == parent1_id).first()
    parent2 = db.query(models.Pet).filter(models.Pet.id == parent2_id).first()

    if not parent1 or not parent2:
        raise HTTPException(status_code=404, detail="One or both parents not found")

    # Get genetics for both parents for this gene
    p1_genetics = db.query(models.PetGenetics).filter(
        models.PetGenetics.pet_id == parent1_id,
        models.PetGenetics.gene_id == gene_id
    ).first()

    p2_genetics = db.query(models.PetGenetics).filter(
        models.PetGenetics.pet_id == parent2_id,
        models.PetGenetics.gene_id == gene_id
    ).first()

    if not p1_genetics or not p2_genetics:
        raise HTTPException(status_code=400, detail="One or both parents lack genetics for this gene")

    gene = db.query(models.Gene).filter(models.Gene.id == gene_id).first()

    p1_alleles = (p1_genetics.allele1.symbol, p1_genetics.allele2.symbol)
    p2_alleles = (p2_genetics.allele1.symbol, p2_genetics.allele2.symbol)

    ps_result = PunnettSquare.calculate(p1_alleles, p2_alleles)

    return schemas.PunnettSquareResult(
        gene_name=gene.name,
        parent1_genotype="".join(p1_alleles),
        parent2_genotype="".join(p2_alleles),
        possible_offspring=ps_result["possible_offspring"],
        probabilities=ps_result["probabilities"],
        punnett_square=ps_result["punnett_square"]
    )

# =====================
# STATS ENDPOINTS
# =====================

@router.get("/pet-stats/{pet_id}", response_model=schemas.PetStatsSchema)
def get_pet_stats(pet_id: int, db: Session = Depends(get_db)):
    """Get a pet's derived stats"""
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    # Fix: Calculate based on available stats
    genetic_score = int((pet.speed + pet.endurance) / 2)

    return schemas.PetStatsSchema(
        speed=pet.speed,
        endurance=pet.endurance,
        genetic_score=genetic_score
    )

@router.get("/compare-stats/{pet1_id}/{pet2_id}")
def compare_pet_stats(pet1_id: int, pet2_id: int, db: Session = Depends(get_db)):
    """Compare stats between two pets"""
    pet1 = db.query(models.Pet).filter(models.Pet.id == pet1_id).first()
    pet2 = db.query(models.Pet).filter(models.Pet.id == pet2_id).first()

    if not pet1 or not pet2:
        raise HTTPException(status_code=404, detail="One or both pets not found")

    # Fix: Calculate based on available stats
    pet1_score = (pet1.speed + pet1.endurance) / 2
    pet2_score = (pet2.speed + pet2.endurance) / 2

    return {
        "pet1": {
            "id": pet1.id,
            "name": pet1.name,
            "speed": pet1.speed,
            "endurance": pet1.endurance,
            "genetic_score": pet1_score
        },
        "pet2": {
            "id": pet2.id,
            "name": pet2.name,
            "speed": pet2.speed,
            "endurance": pet2.endurance,
            "genetic_score": pet2_score
        },
        "winner": pet1.name if pet1_score > pet2_score else (pet2.name if pet2_score > pet1_score else "Tie"),
        "score_difference": abs(pet1_score - pet2_score)
    }