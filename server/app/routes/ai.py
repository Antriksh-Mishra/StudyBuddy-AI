from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models.auth import User
from app.models.document import Document
from app.models.flashcard_quiz import Flashcard, Quiz, Question
from app.schemas.all_schemas import FlashcardOut, QuizOut
from app.routes.auth import get_current_user
from app.services import ai_service, vector_db

router = APIRouter(prefix="/api/ai", tags=["AI Copilot"])

# Helper request schemas
class ChatRequest(BaseModel):
    query: str
    history: Optional[List[dict]] = None
    document_id: Optional[int] = None

class GenerateFlashcardsRequest(BaseModel):
    deck_name: Optional[str] = "AI Generated Deck"
    document_id: Optional[int] = None
    custom_topic: Optional[str] = None

class GenerateQuizRequest(BaseModel):
    title: str
    document_id: Optional[int] = None
    custom_topic: Optional[str] = None
    num_questions: Optional[int] = 5
    difficulty: Optional[str] = "medium"

@router.post("/chat")
def chat_copilot(req: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # RAG search if document context is selected
    if req.document_id:
        doc = db.query(Document).filter(Document.id == req.document_id, Document.user_id == current_user.id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Selected document not found")
            
        # Get query embedding
        query_vector = ai_service.get_embedding(req.query)
        
        # Search FAISS index
        raw_results = vector_db.search_similar(query_vector, k=4)
        
        # Filter matching chunks specifically for this document
        matching_chunks = []
        for res in raw_results:
            meta = res.get("metadata", {})
            if meta.get("document_id") == req.document_id:
                matching_chunks.append({
                    "text": meta.get("text", "")
                })
                
        # Generate response using RAG helper
        if matching_chunks:
            response_text = ai_service.answer_with_rag(req.query, matching_chunks)
        else:
            # Fallback to general explanation if no chunks matched
            response_text = ai_service.explain_concept(req.query, req.history)
    else:
        # Standard chat copilot query
        response_text = ai_service.explain_concept(req.query, req.history)
        
    return {"message": response_text}

@router.post("/flashcards/generate", response_model=List[FlashcardOut])
def generate_flashcards(req: GenerateFlashcardsRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    text_source = ""
    
    if req.document_id:
        doc = db.query(Document).filter(Document.id == req.document_id, Document.user_id == current_user.id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Selected document not found")
        text_source = doc.ocr_extracted_text or ""
    elif req.custom_topic:
        text_source = f"Generate study materials about the topic: {req.custom_topic}"
    else:
        raise HTTPException(status_code=400, detail="Must provide either document_id or custom_topic")
        
    if not text_source.strip():
        raise HTTPException(status_code=400, detail="Text source is empty")
        
    # Generate cards using AI
    cards = ai_service.generate_flashcards(text_source)
    
    saved_cards = []
    for card in cards:
        db_card = Flashcard(
            user_id=current_user.id,
            deck_name=req.deck_name,
            front=card.get("front", "Empty front"),
            back=card.get("back", "Empty back")
        )
        db.add(db_card)
        saved_cards.append(db_card)
        
    db.commit()
    for card in saved_cards:
        db.refresh(card)
        
    return saved_cards

@router.post("/quiz/generate", response_model=QuizOut)
def generate_quiz(req: GenerateQuizRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    text_source = ""
    
    if req.document_id:
        doc = db.query(Document).filter(Document.id == req.document_id, Document.user_id == current_user.id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Selected document not found")
        text_source = doc.ocr_extracted_text or ""
    elif req.custom_topic:
        text_source = f"Create assessment test questions about the topic: {req.custom_topic}"
    else:
        raise HTTPException(status_code=400, detail="Must provide either document_id or custom_topic")
        
    if not text_source.strip():
        raise HTTPException(status_code=400, detail="Text source has no content to generate quiz")
        
    # Generate questions using AI
    questions_list = ai_service.generate_quiz(text_source, req.num_questions, req.difficulty)
    
    # Create Quiz database model
    quiz = Quiz(
        user_id=current_user.id,
        title=req.title,
        difficulty=req.difficulty,
        total_questions=len(questions_list)
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    for q in questions_list:
        db_q = Question(
            quiz_id=quiz.id,
            question_text=q.get("question_text", "Missing question text"),
            question_type=q.get("question_type", "mcq"),
            options=q.get("options", ""),
            correct_answer=q.get("correct_answer", "")
        )
        db.add(db_q)
        
    db.commit()
    db.refresh(quiz)
    
    return quiz
