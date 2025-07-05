# app/api/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from app.core.config import settings
from app.db.models import User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/auth/login"
)

async def get_current_user(token: str = Depends(reusable_oauth2)) -> User:
    """
    Entschlüsselt das JWT-Token und gibt den zugehörigen Benutzer aus der DB zurück.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials (user_id not in token)",
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials (token invalid)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await User.get(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or not active")
    
    return user