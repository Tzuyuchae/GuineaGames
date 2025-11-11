from fastapi import FastAPI
from routes import users, pets, inventory, transactions, mini_games, leaderboard, genetics, marketplace
from database import Base, engine, SessionLocal
from genetics import initialize_genetics_system

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Guinea Games API")

# Initialize genetics system on startup
@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        initialize_genetics_system(db)
    finally:
        db.close()

app.include_router(users.router)
app.include_router(pets.router)
app.include_router(inventory.router)
app.include_router(transactions.router)
app.include_router(mini_games.router)
app.include_router(leaderboard.router)
app.include_router(genetics.router)
app.include_router(marketplace.router)

@app.get("/")
def root():
    return {"message": "Welcome to Guinea Games Backend"}