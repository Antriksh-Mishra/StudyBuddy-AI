from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.auth import User
from app.models.flashcard_quiz import Quiz, Question
from app.schemas.all_schemas import QuizOut, QuizSubmit
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/quizzes", tags=["Quizzes"])

@router.get("", response_model=List[QuizOut])
def get_quizzes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    quizzes = db.query(Quiz).filter(Quiz.user_id == current_user.id).order_by(Quiz.created_at.desc()).all()
    return quizzes

@router.get("/{quiz_id}", response_model=QuizOut)
def get_quiz(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@router.post("/{quiz_id}/submit", response_model=QuizOut)
def submit_quiz(
    quiz_id: int,
    submission: QuizSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
        
    score = 0
    
    # Process answers
    for ans in submission.answers:
        question = db.query(Question).filter(Question.id == ans.question_id, Question.quiz_id == quiz.id).first()
        if question:
            question.user_answer = ans.user_answer
            # Evaluate correctness
            is_correct = ans.user_answer.strip().lower() == question.correct_answer.strip().lower()
            question.is_correct = is_correct
            if is_correct:
                score += 1
                
    quiz.score = score
    db.commit()
    db.refresh(quiz)
    return quiz
