# app/schemas/token.py

from pydantic import BaseModel, EmailStr

# NEU: Ein Schema für die Login-Anfrage
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str