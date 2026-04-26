from database import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from sqlalchemy.orm import Session
from auth import get_current_user

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Current user dependency
def get_current_user_dep(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    return get_current_user(token, db)