# app/core/security.py

from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# KORREKTUR: Die Funktion akzeptiert jetzt ein `remember_me`-Flag
def create_access_token(subject: Union[str, Any], remember_me: bool = False) -> str:
    """
    Erstellt ein JWT-Zugangsticket mit kurzer oder langer Lebensdauer.
    """
    if remember_me:
        expires_delta = timedelta(days=settings.REMEMBER_ME_EXPIRE_DAYS)
    else:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt