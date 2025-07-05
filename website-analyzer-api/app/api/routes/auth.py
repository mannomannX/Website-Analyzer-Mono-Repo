# app/api/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any

from app.core.security import create_access_token, verify_password
from app.db.models import User
from app.schemas.token import Token, LoginRequest # NEU: Importiert das neue Login-Schema

router = APIRouter()

# KORREKTUR: Verwendet jetzt ein Pydantic-Modell anstatt der Form-Daten
@router.post("/login", response_model=Token)
async def login_for_access_token(
    login_data: LoginRequest # Verwendet unser neues Schema
) -> Any:
    """
    Nimmt E-Mail, Passwort und remember_me Flag entgegen und gibt ein Token zurück.
    """
    user = await User.find_one(User.email == login_data.email)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        subject=user.id,
        remember_me=login_data.remember_me
    )
    return {"access_token": access_token, "token_type": "bearer"}