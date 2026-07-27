from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# --- AUTH SCHEMAS ---
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    college_name: Optional[str] = None
    registration_number: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    college_name: Optional[str]
    registration_number: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None

# --- NOTE SCHEMAS ---
class NoteCreate(BaseModel):
    title: str = Field(..., max_length=200)
    content: Optional[str] = None
    category: Optional[str] = "General"
    tags: Optional[str] = "" # comma-separated

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None

class NoteOut(BaseModel):
    id: int
    user_id: int
    title: str
    content: Optional[str]
    category: str
    tags: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- DOCUMENT SCHEMAS ---
class DocumentOut(BaseModel):
    id: int
    filename: str
    ocr_extracted_text: Optional[str]
    summary: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# --- FLASHCARD SCHEMAS ---
class FlashcardCreate(BaseModel):
    deck_name: Optional[str] = "Default Deck"
    front: str
    back: str

class FlashcardUpdate(BaseModel):
    deck_name: Optional[str] = None
    front: Optional[str] = None
    back: Optional[str] = None
    interval: Optional[int] = None
    repetition: Optional[int] = None
    ease_factor: Optional[float] = None

class FlashcardOut(BaseModel):
    id: int
    deck_name: str
    front: str
    back: str
    interval: int
    repetition: int
    ease_factor: float
    next_review: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# --- QUIZ SCHEMAS ---
class QuestionCreate(BaseModel):
    question_text: str
    question_type: str # mcq, true_false, short_answer
    options: Optional[str] = None
    correct_answer: str

class QuestionOut(BaseModel):
    id: int
    question_text: str
    question_type: str
    options: Optional[str]
    correct_answer: str
    user_answer: Optional[str]
    is_correct: Optional[bool]

    class Config:
        from_attributes = True

class QuizCreate(BaseModel):
    title: str
    difficulty: Optional[str] = "medium"
    topic: Optional[str] = None # Optional topic for AI generation

class QuizOut(BaseModel):
    id: int
    title: str
    difficulty: str
    score: Optional[int]
    total_questions: int
    created_at: datetime
    questions: List[QuestionOut] = []

    class Config:
        from_attributes = True

class QuestionSubmit(BaseModel):
    question_id: int
    user_answer: str

class QuizSubmit(BaseModel):
    answers: List[QuestionSubmit]

# --- PLANNER SCHEMAS ---
class TaskCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_completed: Optional[bool] = None

class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True

class StudySessionCreate(BaseModel):
    subject: str
    duration_minutes: int

class StudySessionOut(BaseModel):
    id: int
    subject: str
    duration_minutes: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- COLLABORATION SCHEMAS ---
class GroupCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None

class GroupOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    message_text: str

class MessageOut(BaseModel):
    id: int
    group_id: int
    user_id: int
    username: str # Custom resolved
    message_text: str
    created_at: datetime

    class Config:
        from_attributes = True
