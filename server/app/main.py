from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import Base
from app.routes import auth, notes, documents, ai, flashcards, quizzes, planner, collab

# Automatically create database tables based on SQLAlchemy models
try:
    print("[*] Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    print("[*] Database tables initialized successfully.")
except Exception as e:
    print(f"[*] Database initialization error: {e}")

app = FastAPI(
    title="StudyBuddy AI API",
    description="Production-ready REST API powering the StudyBuddy AI academic platform.",
    version="2.0.0"
)

# CORS configuration to allow local Vite development server communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Route modules
app.include_router(auth.router)
app.include_router(notes.router)
app.include_router(documents.router)
app.include_router(ai.router)
app.include_router(flashcards.router)
app.include_router(quizzes.router)
app.include_router(planner.router)
app.include_router(collab.router)

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "service": "StudyBuddy AI Backend API",
        "version": "2.0.0",
        "docs_url": "/docs"
    }
