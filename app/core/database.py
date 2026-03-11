import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch the complete database connection string
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Create the database engine (connected to PostgreSQL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Session local class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for the database models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()