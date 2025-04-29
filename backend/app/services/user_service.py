from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from app.db.models.user import User
from app.schemas.user import UserCreate, UserOut
from fastapi import HTTPException, status


def create_user(db: Session, user_data: UserCreate):
    hashed = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
    )
    existing_user = (
        db.query(User)
        .filter((User.email == user_data.email) | (User.username == user_data.username))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists",
        )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None


def get_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()
