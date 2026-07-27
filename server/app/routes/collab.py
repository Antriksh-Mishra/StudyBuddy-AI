from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.auth import User
from app.models.collab import Group, GroupMember, GroupMessage
from app.schemas.all_schemas import GroupCreate, GroupOut, MessageCreate, MessageOut
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/groups", tags=["Collaboration"])

@router.get("", response_model=List[GroupOut])
def get_groups(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    groups = db.query(Group).all()
    return groups

@router.post("", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
def create_group(group_data: GroupCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_group = Group(
        name=group_data.name,
        description=group_data.description
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    
    # Add creator as group admin
    member = GroupMember(
        group_id=new_group.id,
        user_id=current_user.id,
        role="admin"
    )
    db.add(member)
    db.commit()
    
    return new_group

@router.post("/{group_id}/join", status_code=status.HTTP_200_OK)
def join_group(group_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Study group not found")
        
    # Check if already a member
    is_member = db.query(GroupMember).filter(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id).first()
    if is_member:
        return {"message": "You are already a member of this study group"}
        
    new_member = GroupMember(
        group_id=group_id,
        user_id=current_user.id,
        role="member"
    )
    db.add(new_member)
    db.commit()
    return {"message": f"Successfully joined group: {group.name}"}

@router.get("/{group_id}/messages", response_model=List[MessageOut])
def get_messages(group_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify user is a member of the group
    is_member = db.query(GroupMember).filter(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id).first()
    if not is_member:
         raise HTTPException(status_code=403, detail="You must join this study group to read messages")
         
    messages = db.query(GroupMessage).filter(GroupMessage.group_id == group_id).order_by(GroupMessage.created_at.asc()).all()
    
    # Resolve sender username manually to map back to response schema
    out_messages = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.user_id).first()
        username = sender.username if sender else "Deleted User"
        if sender and sender.college_name:
            username = f"{username} ({sender.college_name})"
            
        out_messages.append({
            "id": msg.id,
            "group_id": msg.group_id,
            "user_id": msg.user_id,
            "username": username,
            "message_text": msg.message_text,
            "created_at": msg.created_at
        })
    return out_messages

@router.post("/{group_id}/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def send_message(group_id: int, msg_data: MessageCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify user is a member of the group
    is_member = db.query(GroupMember).filter(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id).first()
    if not is_member:
         raise HTTPException(status_code=403, detail="You must join this study group to post messages")
         
    new_msg = GroupMessage(
        group_id=group_id,
        user_id=current_user.id,
        message_text=msg_data.message_text
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    
    username = current_user.username
    if current_user.college_name:
        username = f"{username} ({current_user.college_name})"
        
    return {
        "id": new_msg.id,
        "group_id": new_msg.group_id,
        "user_id": new_msg.user_id,
        "username": username,
        "message_text": new_msg.message_text,
        "created_at": new_msg.created_at
    }
