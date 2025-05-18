# db/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite adatbázis
SQLALCHEMY_DATABASE_URL = "sqlite:///./products.db"

# Engine létrehozása
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session gyár
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Alap osztály az adatmodellekhez
Base = declarative_base()
