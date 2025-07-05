# scripts/create_admin_user.py

import asyncio
from app.db.database import init_db
from app.db.models import User
from app.core.security import get_password_hash

async def create_admin_user():
    """
    Ein Skript, um einen ersten Admin-Benutzer in der Datenbank zu erstellen.
    """
    print("Initialisiere Datenbankverbindung für Admin-Erstellung...")
    await init_db()
    
    email = input("Geben Sie die E-Mail-Adresse für den Admin-Benutzer ein: ")
    password = input("Geben Sie ein sicheres Passwort für den Admin-Benutzer ein: ")
    
    # Prüfen, ob der Nutzer bereits existiert
    existing_user = await User.find_one(User.email == email)
    if existing_user:
        print(f"Fehler: Ein Benutzer mit der E-Mail '{email}' existiert bereits.")
        return

    # Passwort hashen
    hashed_password = get_password_hash(password)
    
    # Neuen Admin-Nutzer erstellen
    admin_user = User(
        email=email,
        hashed_password=hashed_password,
        role="admin",
        is_active=True
    )
    
    # Nutzer in der Datenbank speichern
    await admin_user.insert()
    
    print(f"✅ Admin-Benutzer '{email}' wurde erfolgreich erstellt!")

if __name__ == "__main__":
    asyncio.run(create_admin_user())