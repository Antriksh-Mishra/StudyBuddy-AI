from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    deck_name = Column(String(100), default="Default Deck")
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    
    # SM-2 Spaced Repetition Variables
    interval = Column(Integer, default=1)      # interval in days
    repetition = Column(Integer, default=0)    # number of consecutive correct answers
    ease_factor = Column(Float, default=2.5)   # ease factor (EF)
    next_review = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="flashcards")

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    difficulty = Column(String(50), default="medium")
    score = Column(Integer, nullable=True) # score achieved
    total_questions = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), default="mcq") # mcq, true_false, short_answer
    options = Column(Text, nullable=True) # Comma-separated, or JSON string of choices
    correct_answer = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
