from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional, Any, Union

from app.core.config import settings


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def create_access_token(subject: Union[str,Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"exp": datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))}
    if subject:
        to_encode["sub"] = str(subject)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(subject: Union[str,Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"exp": datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES))}
    if subject:
        to_encode["sub"] = str(subject)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


