from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.auth import User
from app.models.note import Note
from app.schemas.all_schemas import NoteCreate, NoteUpdate, NoteOut
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/notes", tags=["Notes"])

@router.get("", response_model=List[NoteOut])
def get_notes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notes = db.query(Note).filter(Note.user_id == current_user.id).order_by(Note.updated_at.desc()).all()
    return notes

@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(note_data: NoteCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_note = Note(
        user_id=current_user.id,
        title=note_data.title,
        content=note_data.content,
        category=note_data.category,
        tags=note_data.tags
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

@router.put("/{note_id}", response_model=NoteOut)
def update_note(note_id: int, note_data: NoteUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        
    # Update note fields
    for field, value in note_data.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
        
    db.commit()
    db.refresh(note)
    return note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        
    db.delete(note)
    db.commit()
    return None
