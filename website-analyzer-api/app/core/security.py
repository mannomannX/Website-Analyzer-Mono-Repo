# app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.core.config import settings
from app.db.models import User

# Kontext für das Hashen von Passwörtern
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Überprüft, ob ein Klartext-Passwort mit einem Hash übereinstimmt."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Erstellt einen Hash aus einem Klartext-Passwort."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Erstellt ein neues JWT Access Token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def authenticate_user(email: str, password: str) -> Optional[User]:
    """Sucht einen Benutzer in der DB und validiert das Passwort."""
    user = await User.find_one(User.email == email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user