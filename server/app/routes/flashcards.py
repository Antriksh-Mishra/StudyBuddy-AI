from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from app.database import get_db
from app.models.auth import User
from app.models.flashcard_quiz import Flashcard
from app.schemas.all_schemas import FlashcardCreate, FlashcardUpdate, FlashcardOut
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/flashcards", tags=["Flashcards & Spaced Repetition"])

class ReviewRequest(BaseModel):
    quality: int # Quality rating from 0 to 5:
                 # 5: perfect response
                 # 4: correct response after a hesitation
                 # 3: correct response recalled with serious difficulty
                 # 2: incorrect response; where the correct one seemed easy to recall
                 # 1: incorrect response; the correct one remembered
                 # 0: complete blackout

@router.get("", response_model=List[FlashcardOut])
def get_flashcards(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cards = db.query(Flashcard).filter(Flashcard.user_id == current_user.id).order_by(Flashcard.next_review.asc()).all()
    return cards

@router.post("", response_model=FlashcardOut, status_code=status.HTTP_201_CREATED)
def create_flashcard(card_data: FlashcardCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_card = Flashcard(
        user_id=current_user.id,
        deck_name=card_data.deck_name,
        front=card_data.front,
        back=card_data.back
    )
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card

@router.post("/{card_id}/review", response_model=FlashcardOut)
def review_flashcard(
    card_id: int,
    review: ReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    card = db.query(Flashcard).filter(Flashcard.id == card_id, Flashcard.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
        
    q = review.quality
    if q < 0 or q > 5:
        raise HTTPException(status_code=400, detail="Review quality must be between 0 and 5")
        
    # --- SM-2 Algorithm ---
    # Update ease factor (EF)
    card.ease_factor = card.ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    if card.ease_factor < 1.3:
        card.ease_factor = 1.3
        
    # Update repetitions and interval
    if q >= 3:
        if card.repetition == 0:
            card.interval = 1
        elif card.repetition == 1:
            card.interval = 6
        else:
            card.interval = round(card.interval * card.ease_factor)
            
        card.repetition += 1
    else:
        # Incorrect answers reset repetitions
        card.repetition = 0
        card.interval = 1
        
    # Calculate next review date
    card.next_review = datetime.utcnow() + timedelta(days=card.interval)
    
    db.commit()
    db.refresh(card)
    return card

@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flashcard(card_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    card = db.query(Flashcard).filter(Flashcard.id == card_id, Flashcard.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
        
    db.delete(card)
    db.commit()
    return None
