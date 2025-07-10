# app/api/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any

# KORRIGIERTE IMPORTE:
from app.core.security import authenticate_user, create_access_token
from app.schemas.auth import Token

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    Authentifiziert einen Benutzer und gibt ein JWT-Token zurück.
    Erwartet 'username' und 'password' als Formular-Daten.
    """
    # --- DEBUGGING-ZEILE BLEIBT ---
    print(f"--- [AUTH DEBUG] Empfangene Formulardaten: username='{form_data.username}', password='{'*' * len(form_data.password)}' ---")
    
    user = await authenticate_user(email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}