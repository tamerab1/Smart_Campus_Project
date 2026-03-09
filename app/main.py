# app/main.py
from fastapi import FastAPI
from app.routes import ask_route

# Import the database engine and Base class
from app.database import engine, Base
# IMPORTANT: Import the models so SQLAlchemy knows about them before creating tables
from app.models import campus 

# This is the magic line that creates the tables in PostgreSQL
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Campus Assistant")

app.include_router(ask_route.router)

@app.get("/")
def read_root():
    return {"message": "Smart Campus Assistant is running!"}