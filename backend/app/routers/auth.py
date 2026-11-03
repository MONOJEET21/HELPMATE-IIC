from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserOut, LoginInput, Token
from app.security import hash_password, verify_password, create_access_token, get_current_user
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if data.role not in {"customer", "worker", "farmer"}:
        raise HTTPException(400, "Role must be customer, worker or farmer")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(409, "Email already registered")
    user = User(name=data.name, email=data.email, hashed_password=hash_password(data.password), role=data.role, phone=data.phone)
    db.add(user); db.commit(); db.refresh(user)
    return Token(access_token=create_access_token(user.id), user=user)

@router.post("/login", response_model=Token)
def login(data: LoginInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Incorrect email or password")
    return Token(access_token=create_access_token(user.id), user=user)

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
