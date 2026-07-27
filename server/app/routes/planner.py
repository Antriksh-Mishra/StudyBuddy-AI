from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.auth import User
from app.models.planner import Task, StudySession
from app.schemas.all_schemas import TaskCreate, TaskUpdate, TaskOut, StudySessionCreate, StudySessionOut
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/planner", tags=["Planner & Pomodoro"])

# --- TASKS ENDPOINTS ---
@router.get("/tasks", response_model=List[TaskOut])
def get_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.user_id == current_user.id).order_by(Task.due_date.asc().nullslast()).all()
    return tasks

@router.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_task = Task(
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task_data: TaskUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    for field, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
        
    db.commit()
    db.refresh(task)
    return task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    db.delete(task)
    db.commit()
    return None

# --- STUDY SESSIONS ENDPOINTS ---
@router.get("/sessions", response_model=List[StudySessionOut])
def get_study_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.query(StudySession).filter(StudySession.user_id == current_user.id).order_by(StudySession.created_at.desc()).all()
    return sessions

@router.post("/sessions", response_model=StudySessionOut, status_code=status.HTTP_201_CREATED)
def create_study_session(session_data: StudySessionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_session = StudySession(
        user_id=current_user.id,
        subject=session_data.subject,
        duration_minutes=session_data.duration_minutes
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session
