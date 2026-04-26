from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas
from utils.security import hash_password, verify_password
from auth import create_access_token
from deps import get_db

router = APIRouter()

@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(400, "User already exists")

    new_user = models.User(
        email=user.email,
        password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()

    return {"message": "User created"}


@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({"sub": db_user.email})

    return {"access_token": token}