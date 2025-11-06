# CLAUDE.md

# Database Dave

**Role:** World-class database engineer.  
**Focus:** Design, build, and optimize databases from scratch.  
**Specialties:**
- SQL schema normalization
- Query optimization
- Indexing and partitioning
- ORM integration (SQLAlchemy, Prisma)
- Data migration and seeding
- Backup and replication strategy

**Personality:** Analytical, methodical, results-driven.

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Guinea Games is a full-stack Python application for a virtual pet game featuring guinea pigs. It consists of:
- **Backend**: FastAPI REST API with SQLAlchemy ORM and SQLite database
- **Frontend**: Pygame-based desktop application
- **Status**: Early development (foundation complete, core features in progress)

## Repository Structure

```
GuineaGames/
├── backend/                    # FastAPI REST API
│   ├── main.py                # App entry point, router registration
│   ├── models.py              # SQLAlchemy ORM models (User, Pet)
│   ├── schemas.py             # Pydantic validation schemas
│   ├── routes/
│   │   └── users.py           # User endpoints (POST /users, GET /users)
│   └── database/
│       ├── database.py        # SQLite schema and initialization
│       └── GuineaGames.db     # SQLite database
├── frontend/                   # Pygame desktop application
│   ├── main.py                # Window setup and game loop
│   ├── guineapig.py           # Guineapig sprite class
│   └── images/
│       └── guineapig.png      # Guinea pig sprite asset
└── requirements.txt           # Python dependencies
```

## Commands

### Run Backend API
```bash
cd backend
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`. Swagger documentation at `http://localhost:8000/docs`.

### Run Frontend
```bash
cd frontend
python main.py
```
Launches Pygame window (800x600) with guinea pig sprite.

### Initialize/Reset Database
```bash
cd backend/database
python database.py
```
Creates or resets the SQLite database with full schema.

## Architecture

### Backend (FastAPI)

**Entry Point**: `backend/main.py`

The FastAPI app registers 6 routers, though currently only the users router is implemented:
- `users` - User CRUD operations (partially implemented)
- `pets` - Pet management (not implemented)
- `inventory` - Item management (not implemented)
- `transactions` - Transaction history (not implemented)
- `mini_games` - Game mechanics (not implemented)
- `leaderboard` - Rankings (not implemented)

**Database Models** (`backend/models.py`):
- `User` - Player accounts with hashed passwords, email, timestamps
- `Pet` - Guinea pigs owned by users with stats (health, happiness, hunger, cleanliness, age)

**Database Schema** (`backend/database/database.py`):
Complete schema includes tables for users, pets, inventory, mini-games, leaderboards, transactions, and shop items. This is the reference for database operations.

**Router Conventions**:
- Store endpoint logic in `backend/routes/{resource}.py`
- Import and include routers in `main.py` using `app.include_router()`
- Use Pydantic schemas from `schemas.py` for request/response validation
- Use SQLAlchemy models from `models.py` for database operations

### Frontend (Pygame)

**Entry Point**: `frontend/main.py`

Currently a basic Pygame window with game loop structure. The `Guineapig` sprite class in `guineapig.py` provides a foundation for drawable sprites with position, but lacks update logic and animations.

**Frontend Status**:
- Window initialization and event handling: done
- Sprite rendering: done
- Game mechanics: not implemented
- API integration: not implemented
- Controls and input handling: not implemented

## Key Implementation Notes

### Backend Status
- Only `users.py` router is implemented with basic GET/POST endpoints
- Missing: Authentication/authorization, password hashing, input validation
- All other routers (`pets`, `inventory`, etc.) need to be created following the same pattern as `users.py`
- Each router should handle its own CRUD operations and validation

### Frontend Status
- Pygame window and sprite system are set up
- No connection to backend API yet
- Game loop exists but lacks mechanics implementation
- Need to add: API calls to backend, game logic, controls, animations

### Database
The database schema is comprehensive and ready for implementation. Reference `backend/database/database.py` for table definitions and relationships.

## Dependencies

All Python dependencies are listed in `requirements.txt`. Key ones:
- `fastapi` - Backend web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - ORM
- `pydantic` - Data validation
- `pygame` - Frontend game engine (needs verification in requirements.txt)

Install with:
```bash
pip install -r requirements.txt
```

## Recent Commits

The project was scaffolded recently with basic structure in place:
- Backend database schema and models
- FastAPI app structure with router registration
- Pygame window and sprite foundation
- Minimal user endpoints

Next development priorities should focus on:
1. Completing remaining router implementations (pets, inventory, transactions, mini_games, leaderboard)
2. Implementing frontend-backend API integration
3. Building game mechanics and UI
4. Adding authentication and proper error handling
