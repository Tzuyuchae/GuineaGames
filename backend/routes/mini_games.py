from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(prefix="/mini-games", tags=["Mini Games"])

@router.post("/", response_model=schemas.MiniGame)
def create_mini_game(game: schemas.MiniGameCreate, db: Session = Depends(get_db)):
    """Create a new mini-game"""
    db_game = models.MiniGame(
        name=game.name,
        base_reward=game.base_reward,
        cooldown_sec=game.cooldown_sec
    )
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

@router.get("/", response_model=list[schemas.MiniGame])
def get_all_mini_games(db: Session = Depends(get_db)):
    """Get all available mini-games"""
    return db.query(models.MiniGame).all()

@router.get("/{game_id}", response_model=schemas.MiniGame)
def get_mini_game(game_id: int, db: Session = Depends(get_db)):
    """Get a specific mini-game by ID"""
    game = db.query(models.MiniGame).filter(models.MiniGame.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Mini-game not found")
    return game

@router.get("/name/{game_name}", response_model=schemas.MiniGame)
def get_mini_game_by_name(game_name: str, db: Session = Depends(get_db)):
    """Get a mini-game by name"""
    game = db.query(models.MiniGame).filter(models.MiniGame.name == game_name).first()
    if not game:
        raise HTTPException(status_code=404, detail="Mini-game not found")
    return game

@router.put("/{game_id}", response_model=schemas.MiniGame)
def update_mini_game(game_id: int, game_update: schemas.MiniGameBase, db: Session = Depends(get_db)):
    """Update a mini-game"""
    game = db.query(models.MiniGame).filter(models.MiniGame.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Mini-game not found")

    game.name = game_update.name
    game.base_reward = game_update.base_reward
    game.cooldown_sec = game_update.cooldown_sec

    db.commit()
    db.refresh(game)
    return game

@router.delete("/{game_id}")
def delete_mini_game(game_id: int, db: Session = Depends(get_db)):
    """Delete a mini-game"""
    game = db.query(models.MiniGame).filter(models.MiniGame.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Mini-game not found")

    db.delete(game)
    db.commit()
    return {"message": "Mini-game deleted successfully"}
