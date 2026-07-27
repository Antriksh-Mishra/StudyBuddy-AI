from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.auth import User
from app.schemas.all_schemas import UserCreate, UserLogin, UserOut, Token
from app.services.auth_helper import auth_helper

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Authorization Header Scheme
auth_header_scheme = APIKeyHeader(name="Authorization", auto_error=False)

def get_current_user(token: str = Depends(auth_header_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependency to validate JWT tokens and fetch the current user profile.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token is missing"
        )
    
    # Strip Bearer prefix if present
    if token.startswith("Bearer "):
        token = token[7:]
        
    payload = auth_helper.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )
        
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with this token does not exist"
        )
    return user

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter((User.email == user_data.email) | (User.username == user_data.username)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
        
    # Hash password and create user
    hashed_pwd = auth_helper.hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_pwd,
        college_name=user_data.college_name,
        registration_number=user_data.registration_number
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate token
    token_data = {"user_id": new_user.id, "email": new_user.email}
    access_token = auth_helper.create_access_token(data=token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not auth_helper.verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
        
    # Generate token
    token_data = {"user_id": user.id, "email": user.email}
    access_token = auth_helper.create_access_token(data=token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
