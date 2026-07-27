from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import sys

db_url = settings.DATABASE_URL

if db_url.startswith("sqlite"):
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    try:
        # Attempt to establish database connection with PostgreSQL
        engine = create_engine(db_url)
        # Test connection quickly
        with engine.connect() as conn:
            pass
    except Exception as e:
        print(f"[*] WARNING: Failed to connect to PostgreSQL at '{db_url}'.")
        print(f"[*] Reason: {e}")
        print("[*] FALLING BACK to local SQLite database (sqlite:///./studybuddy.db)")
        db_url = "sqlite:///./studybuddy.db"
        engine = create_engine(db_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
