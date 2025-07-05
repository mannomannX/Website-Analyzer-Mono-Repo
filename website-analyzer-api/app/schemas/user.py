# app/schemas/user.py

from pydantic import BaseModel, EmailStr

# Schema für die Erstellung eines neuen Nutzers durch einen Admin
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "user"

# Schema zur Anzeige eines Nutzers (ohne das Passwort zurückzugeben)
class UserOut(BaseModel):
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        from_attributes = True # Erlaubt die Konvertierung aus DB-Modellen